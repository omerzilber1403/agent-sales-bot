from __future__ import annotations
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from ..services.llm import chat
from ..instructions import (
    GENERAL_INSTRUCTIONS,
    MESSAGE_QUALITY_INSTRUCTIONS,
    SALES_STRATEGY_INSTRUCTIONS,
    IMPORTANT_RULES,
    OPENING_MESSAGE_RULE,
    INFORMATION_FIRST_APPROACH,
    PRICING_AND_PRODUCTS_RULES,
    LANGUAGE_AND_TERMS_RULES,
    SYSTEM_BOUNDARIES,
    B2C_SPECIFIC_INSTRUCTIONS,
    B2C_QUESTION_GUIDELINES,
    B2B_SPECIFIC_INSTRUCTIONS,
    B2B_QUESTION_GUIDELINES,
    should_handoff,
    HANDOFF_RESPONSE,
    get_smart_question,
    get_contextual_question,
    should_ask_question,
    extract_customer_info,
    get_next_profiling_question,
    should_continue_profiling,
    get_customer_summary,
    get_conversation_stage,
    get_natural_transition,
    get_natural_bridge,
    should_use_bridge,
    get_conversation_flow_guidance
)
from ..instructions.learning_system import get_company_learning_instructions
import json
import re

def _contains_hebrew(text: str) -> bool:
    return bool(re.search(r'[\u0590-\u05FF]', text))

def _strip_markdown(text: str) -> str:
    """Strip most markdown but preserve **bold** — the chat UI renders it."""
    import re as _re
    # **bold** is preserved intentionally: product names and key metrics use it.
    # Remove underline-bold (__text__ → text) — not used by the instruction set.
    text = _re.sub(r'__(.+?)__', r'\1', text, flags=_re.DOTALL)
    # Remove single-asterisk italic (*text* → text) without touching **bold**.
    # Negative lookahead/lookbehind ensures lone * are matched, not **.
    text = _re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'\1', text, flags=_re.DOTALL)
    # Remove heading markers (### / ## / #)
    text = _re.sub(r'^#{1,6}\s+', '', text, flags=_re.MULTILINE)
    # Remove dash/bullet lines at line start (- item, • item).
    # Intentionally excludes * to avoid risk of clipping **bold** line starts.
    text = _re.sub(r'^\s*[-•]\s+', '', text, flags=_re.MULTILINE)
    # Remove numbered list markers (1. item → item)
    text = _re.sub(r'^\s*\d+\.\s+', '', text, flags=_re.MULTILINE)
    # Collapse excess blank lines (keep one blank line for paragraph separation)
    text = _re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def debug_bot_response(node_name: str, user_message: str, bot_response: str):
    """Simple debug function to show user message and bot response"""
    print(f"\n{'='*50}")
    print(f"👤 USER: {user_message}")
    print(f"🤖 BOT ({node_name}): {bot_response}")
    print(f"{'='*50}\n")


# ── Intent classification ──────────────────────────────────────────────────────
_INTENT_PROMPT = """\
You are an intent classifier for a B2B sales chatbot.

Read the FULL conversation, then classify the user's LATEST message into ONE label.

HANDOFF — The user is clearly agreeing to meet/connect with a human, OR is explicitly
requesting to be transferred to a human representative. Examples:
  • Agreeing to something the bot proposed ("כן", "בסדר", "אשמח", "sounds good", "sure")
    — ONLY when the immediately preceding bot message proposed a call/demo/meeting.
  • Explicit scheduling request: "נרצה לקבוע פגישה", "schedule a call", "lock in a demo"
  • Explicit human-transfer request: "דבר עם נציג", "connect me to your team"
  • Purchase/close signal: "אנחנו רוצים להמשיך", "we want to move forward"

SALES — User is still in information mode, OR is explicitly declining. Examples:
  • Any question about products, pricing, features, or comparisons
  • Any message containing negation: "לא", "no", "not now", "not interested", "אין צורך",
    "don't need", "לא צריך", "לא רוצה", "לא עכשיו", "maybe later"
  • Greetings or general inquiries with no meeting-acceptance intent
  • Pushback / objections

CRITICAL RULE: If the message contains ANY negation word — classify SALES unconditionally,
regardless of any other signals.

Respond with EXACTLY ONE WORD: HANDOFF or SALES (no punctuation, no explanation).\
"""

# Fast negation patterns — classify SALES before calling the LLM
_NEGATION_PATTERNS = [
    "לא רוצה", "לא צריך", "לא מעוניין", "לא עכשיו", "אין צורך",
    "no thanks", "not now", "not interested", "don't need", "i don't",
    "no, ", "לא, ", "נגיד שלא", "אולי בהמשך", "maybe later",
]

# Explicit human-agent request patterns — always HANDOFF, checked before LLM
# These phrases unambiguously mean "transfer me to a person" and must never
# be down-classified to SALES by the LLM, regardless of conversation history.
_EXPLICIT_HUMAN_REQUESTS = [
    "נציג אנושי",
    "תעביר אותי",
    "העבר אותי",
    "לדבר עם נציג",
    "לדבר עם מישהו",
    "connect me to",
    "speak to a human",
    "talk to someone real",
]

def _build_final_rules(company_name: str, b2b: bool = False, message_count: int = 0) -> str:
    """
    Build the ABSOLUTE FINAL RULES system message appended as the last item
    before LLM generation.  Always enforces Hebrew, includes SYSTEM_BOUNDARIES,
    and avoids hardcoding any specific company's product names.
    """
    base = (
        f"ABSOLUTE FINAL RULES — override everything above:\n"
        f"1. Language — HARD LOCK: respond in Hebrew ONLY. Every sentence must be in Hebrew.\n"
        f"   Even if the user writes in English — respond in Hebrew (technical terms and\n"
        f"   brand names remain in Latin characters).\n"
        f"1a. English terms — ZERO EXCEPTIONS: NEVER transliterate brand names, product names,\n"
        f"   or technical acronyms into Hebrew phonetics. Use Latin characters for all brand/tech terms.\n"
        f"   Numbers and percentages MUST be digits: 31% not 'שלושים ואחד אחוז'.\n"
        f"2. Format — HARD REQUIREMENT: near-plain text with controlled bold.\n"
        f"   ALLOWED: **product name** or **key metric** in double asterisks — ONLY on specific words.\n"
        f"   ALLOWED: 0–1 emojis per message from: 🎯 💡 🛡️ 👋 ✅ ⚡ — only where natural.\n"
        f"   ALLOWED: a blank line between paragraphs for readability.\n"
        f"   FORBIDDEN: single asterisks for bullets (*), hashes (#), dashes at line start (- ),\n"
        f"   backticks, numbered lists. Bold max 1–3 words — never a whole sentence.\n"
        f"3. Length — HARD LIMIT: roughly 60-80 words total.\n"
        f"   Match structure to message type:\n"
        f"   direct question → answer immediately with no preamble;\n"
        f"   pain point → one specific empathy sentence, then value;\n"
        f"   objection → acknowledge without apologizing, then reframe.\n"
        f"   Never open with a generic empathy phrase.\n"
        f"4. Conversational flow: vary your opening. Do not end every response with the\n"
        f"   same qualifying question. Move the conversation forward naturally.\n"
        f"5. Tone: confident, consultative, human. Senior solutions advisor, not a chatbot.\n"
        f"6. Links — HARD RULE: never invent a URL. Only share links that appear word-for-word\n"
        f"   in the product data. If asked, say you don't have a direct link and provide\n"
        f"   useful product info instead.\n"
        f"{SYSTEM_BOUNDARIES}\n"
    )
    if b2b:
        if message_count >= 5:
            base += (
                f"7. Late Stage — HARD RULE: this conversation already has {message_count} exchanges. "
                f"Do NOT ask another qualifying question of any kind.\n"
                f"   Instead: briefly confirm what was discussed (1 sentence), state clearly that a human "
                f"specialist from {company_name} will follow up directly to set next steps, and stop.\n"
                f"   Example: 'כיסינו את הצרכים שלכם — נציג מ-{company_name} יצור איתכם קשר ישירות לתיאום הצעד הבא.'\n"
                f"   No product lists, no stats, no new questions. Natural and conclusive.\n"
            )
        else:
            base += (
                f"7. Value-Based Elaboration — MANDATORY: whenever you mention a product or solution,\n"
                f"   go beyond naming it. Connect features to concrete business outcomes: risk reduction,\n"
                f"   compliance gains, productivity without security trade-offs, cost of breach avoided.\n"
                f"   Wrong: 'We offer X.' Right: 'X lets your team do Y, which means Z for the business.'\n"
                f"8. Closing Question — MANDATORY: every sales response must end with a strong,\n"
                f"   qualifying question that moves the lead toward a demo or handoff.\n"
                f"   NEVER use passive closers like 'יש לך עוד שאלות?' or 'Feel free to ask.'\n"
                f"   Use BANT-style questions or a direct demo push.\n"
                f"8a. Disengagement Pivot — CRITICAL: if the lead gives a short dismissive response\n"
                f"   ('no', 'ok', 'תודה', 'בסדר'), do NOT go passive. Pivot with energy:\n"
                f"   acknowledge in one sentence, then push for a demo or human handoff.\n"
                f"   Example: 'מעולה — כיסינו את הליבה. הצעד הבא הגיוני הוא שיחה קצרה עם\n"
                f"   הצוות הטכני שלנו — האם יתאים לך השבוע?'\n"
                f"   Never let a short reply be the last word.\n"
            )
    return base

def business_type_router(state: AgentState) -> Literal["b2c_sales_agent", "b2b_sales_agent"]:
    """Route to appropriate sales agent based on business type"""
    company_data = state.get("company_data", {})
    business_type = company_data.get("business_type", "B2B").upper()
    print(f"🔀 business_type_router: routing to {'b2c_sales_agent' if business_type == 'B2C' else 'b2b_sales_agent'}")
    return "b2c_sales_agent" if business_type == "B2C" else "b2b_sales_agent"

class AgentState(TypedDict):
    messages: List[BaseMessage]
    customer_context: str
    smart_questions: List[str]
    extracted_info: Dict[str, Any]
    response: str
    handoff: bool
    handoff_reason: str
    tone: str
    execution_path: List[str]
    company_data: Dict[str, Any]
    customer_profile: Dict[str, Any]
    conversation_stage: str
    message_count: int

def create_sales_graph(company_data: Dict[str, Any] = None):
    """Create the sales agent graph with customer profiling and company data"""
    
    def classify_intent(state: AgentState) -> AgentState:
        """
        PILLAR 1 — LLM-Driven Intent Router.

        Replaces keyword-matching with a structured 3-stage pipeline:
          Stage 1: Fast negation guard (regex, no LLM cost)
          Stage 2: Fast agreement-to-recent-proposal check (context-aware, no LLM cost)
          Stage 3: LLM classification with full conversation history
          Stage 4: Keyword fallback if LLM is unavailable / returns garbage

        Returns state with handoff=True (→ generate_handoff_response)
                              or handoff=False (→ update_customer_profile → sales agent).
        """
        execution_path = state.get("execution_path", [])
        execution_path.append("classify_intent")

        last_msg = state["messages"][-1].content
        last_lower = last_msg.lower().strip()

        # ── Stage 0: Explicit human-agent request — always HANDOFF ──────────
        # Must run before Stage 1 (negation guard) so that phrases like
        # "תעביר אותי לנציג" are never misclassified as SALES by the LLM.
        for phrase in _EXPLICIT_HUMAN_REQUESTS:
            if phrase in last_lower:
                print(f"🔍 classify_intent → HANDOFF (explicit human-agent: '{phrase}')")
                return {
                    **state,
                    "handoff": True,
                    "handoff_reason": f"Explicit human-agent request: '{phrase}'",
                    "execution_path": execution_path,
                }

        # ── Stage 1: Negation guard ──────────────────────────────────────────
        # Any explicit refusal or "not now" → SALES, skip LLM entirely.
        for pattern in _NEGATION_PATTERNS:
            if pattern in last_lower:
                print(f"🔍 classify_intent → SALES (negation: '{pattern}')")
                return {
                    **state,
                    "handoff": False,
                    "handoff_reason": None,
                    "execution_path": execution_path,
                }

        # ── Stage 2: Agreement-to-recent-proposal check ──────────────────────
        # If the bot's immediately preceding message proposed a meeting/call/demo
        # AND the user's reply is a short affirmative → HANDOFF without LLM.
        _short_affirmatives = {
            "כן", "בסדר", "אשמח", "נשמע טוב", "בהחלט", "למה לא",
            "yes", "sure", "sounds good", "why not", "ok", "okay", "good",
            "great", "absolutely", "let's do it", "let's", "מעולה",
        }
        _meeting_keywords = {
            "פגישה", "שיחה", "שיחת", "demo", "הדגמה", "דמו", "הדמו", "call", "לקבוע", "לתאם",
            "schedule", "meeting", "15 דקות", "half hour", "חצי שעה",
        }
        if any(a in last_lower for a in _short_affirmatives):
            # Check if the most recent bot message mentioned meeting/scheduling
            bot_msgs = [
                m for m in state["messages"]
                if hasattr(m, "type") and m.type == "ai"
            ]
            if bot_msgs:
                last_bot = bot_msgs[-1].content.lower()
                if any(k in last_bot for k in _meeting_keywords):
                    print("🔍 classify_intent → HANDOFF (affirmative to recent meeting proposal)")
                    return {
                        **state,
                        "handoff": True,
                        "handoff_reason": "User agreed to meeting/call",
                        "execution_path": execution_path,
                    }

        # ── Stage 3: LLM classification ──────────────────────────────────────
        # Build a concise conversation window (last 8 messages) for context.
        history_window = state["messages"][-8:]
        llm_messages = [{"role": "system", "content": _INTENT_PROMPT}]
        for msg in history_window:
            if hasattr(msg, "content"):
                role = "assistant" if (hasattr(msg, "type") and msg.type == "ai") else "user"
                llm_messages.append({"role": role, "content": msg.content})

        # The last user message is already in history_window; add a classifier cue.
        llm_messages.append({
            "role": "user",
            "content": "Classify the LAST user message above: HANDOFF or SALES?",
        })

        try:
            raw = (chat(llm_messages, model=None, max_completion_tokens=5) or "").strip().upper()
            # Accept only exact tokens; anything else → SALES (conservative default)
            intent = raw if raw in ("HANDOFF", "SALES") else "SALES"
            print(f"🔍 classify_intent → {intent} (LLM raw: '{raw}')")
        except Exception as exc:
            # ── Stage 4: Keyword fallback ────────────────────────────────────
            intent = "HANDOFF" if should_handoff(last_msg) else "SALES"
            print(f"🔍 classify_intent → {intent} (LLM error: {exc}; fallback to keyword)")

        is_handoff = intent == "HANDOFF"
        return {
            **state,
            "handoff": is_handoff,
            "handoff_reason": "Intent classified as HANDOFF by router" if is_handoff else None,
            "execution_path": execution_path,
        }
    
    def update_customer_profile(state: AgentState) -> AgentState:
        """Update customer profile with extracted information"""
        
        user_message = state["messages"][-1].content
        current_profile = state.get("customer_profile", {})
        
        print(f"👤 update_customer_profile: extracting info from: {user_message[:50]}...")
        
        # Extract customer information
        updated_profile = extract_customer_info(user_message, current_profile)
        
        # Update conversation stage
        conversation_history = [{"content": msg.content, "role": "user" if isinstance(msg, HumanMessage) else "bot"} 
                              for msg in state["messages"]]
        current_stage = get_conversation_stage(conversation_history, user_message)
        
        # Update message count
        message_count = state.get("message_count", 0) + 1
        
        print(f"👤 update_customer_profile: stage={current_stage}, profile={updated_profile}")
        
        return {
            **state,
            "customer_profile": updated_profile,
            "conversation_stage": current_stage,
            "message_count": message_count,
            "execution_path": state.get("execution_path", []) + ["profile_updated"]
        }
    
    def b2c_sales_agent(state: AgentState) -> AgentState:
        """B2C sales agent with friendly and personal approach"""

        execution_path = state.get("execution_path", [])
        execution_path.append("b2c_sales_agent")

        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})

        # Get company-specific fields to collect
        custom_fields = (company_data.get("custom_fields") or {}) if company_data else {}
        conversation_stage = state.get("conversation_stage", "greeting")
        message_count = state.get("message_count", 0)

        # Get learning instructions from feedback
        company_id = company_data.get("id") if company_data else None
        learning_instructions = ""
        if company_id:
            learning_instructions = get_company_learning_instructions(company_id)

        # Build system prompt for B2C approach
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            system_prompt = f"""{custom_prompt}

{GENERAL_INSTRUCTIONS}

{B2C_SPECIFIC_INSTRUCTIONS}

שדות מידע ספציפיים לחברה (אסוף רק את המידע הזה):
{custom_fields.get('description', 'אין שדות מידע ספציפיים מוגדרים')}

רשימת השדות לאסוף:
{chr(10).join([f"- {field}: {desc}" for field, desc in custom_fields.get('fields', {}).items()]) if custom_fields.get('fields') else "אין שדות מוגדרים"}

חשוב: שאל רק על השדות הרשומים למעלה! אל תשאל על מידע אחר!

{MESSAGE_QUALITY_INSTRUCTIONS}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "אין מידע נוסף על הלקוח"}

הקשר הלקוח:
{customer_context}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions]) if smart_questions else "אין שאלות ספציפיות"}

{IMPORTANT_RULES}

{B2C_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{PRICING_AND_PRODUCTS_RULES}

{OPENING_MESSAGE_RULE}

{learning_instructions}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2c_sales_agent: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = []
                    for p in products:
                        if isinstance(p, dict) and p.get('name'):
                            name = p.get('name', '')
                            description = p.get('summary', '') or p.get('description', '')
                            price = p.get('base_price', '')
                            
                            if price:
                                products_list.append(f"- {name}: {description} - {price} ₪")
                            else:
                                products_list.append(f"- {name}: {description}")
                    
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

{B2C_SPECIFIC_INSTRUCTIONS}

{one_line_value}

{products_info}

{GENERAL_INSTRUCTIONS}

{MESSAGE_QUALITY_INSTRUCTIONS}

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

{SALES_STRATEGY_INSTRUCTIONS}

{B2C_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{PRICING_AND_PRODUCTS_RULES}

{learning_instructions}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""

        try:
            # Call LLM with full conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (all messages)
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    # Determine role based on message type
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        messages.append({"role": "assistant", "content": msg.content})
                    else:
                        messages.append({"role": "user", "content": msg.content})
                else:
                    # Fallback for string messages
                    messages.append({"role": "user", "content": str(msg)})
            
            # ── Hebrew lock + ABSOLUTE FINAL RULES (B2C) ──────────────────
            # Language is locked to Hebrew — inject enforcement suffix.
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    messages[i] = {
                        "role": "user",
                        "content": messages[i]["content"] + " [ענה בעברית בלבד]",
                    }
                    break

            _company_name = (company_data or {}).get("name", "החברה")
            messages.append({
                "role": "system",
                "content": _build_final_rules(_company_name, b2b=False),
            })
            llm_response = _strip_markdown(chat(messages) or "")
            print(f"DEBUG: B2C LLM response: {llm_response}")

            result = {
                **state,
                "response": llm_response,
                "tone": "friendly",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2c_sales_agent", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2c_sales_agent: {e}")
            return {
                **state,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "tone": "apologetic",
                "execution_path": execution_path
            }
    
    def b2b_sales_agent(state: AgentState) -> AgentState:
        """B2B sales agent with professional and business-focused approach"""

        execution_path = state.get("execution_path", [])
        execution_path.append("b2b_sales_agent")

        # Get learning instructions from feedback
        company_id = company_data.get("id") if company_data else None
        learning_instructions = ""
        if company_id:
            learning_instructions = get_company_learning_instructions(company_id)
        
        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})
        
        # Get company-specific fields to collect
        custom_fields = (company_data.get("custom_fields") or {}) if company_data else {}
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            lang_instruction = (
                "CRITICAL — HARD LOCK: respond in Hebrew ONLY. "
                "Even if the user writes in English — respond in Hebrew. "
                "Technical terms, brand names, and product names remain in Latin characters."
            )

            # Build knowledge sections from company_data
            products = company_data.get("products") or []
            products_info = ""
            if products:
                lines = []
                for p in products:
                    if isinstance(p, dict) and p.get("name"):
                        line = f"- {p['name']}: {p.get('summary', '')}"
                        if p.get("details"):
                            line += f" | {p['details']}"
                        lines.append(line)
                if lines:
                    products_info = "PRODUCTS / SOLUTIONS:\n" + "\n".join(lines)

            differentiators = company_data.get("differentiators") or []
            diff_info = ""
            if differentiators:
                diff_info = "KEY DIFFERENTIATORS:\n" + "\n".join(f"- {d}" for d in differentiators)

            competitors = company_data.get("competitors_map") or {}
            comp_info = ""
            if competitors:
                lines = [f"- {k}: {v}" for k, v in competitors.items()]
                comp_info = "COMPETITIVE POSITIONING:\n" + "\n".join(lines)

            objections = company_data.get("objections_playbook") or []
            obj_info = ""
            if objections:
                if isinstance(objections, list):
                    lines = [f"- Q: {o.get('objection','')} → A: {o.get('response','')}" for o in objections if isinstance(o, dict)]
                    obj_info = "OBJECTION HANDLING:\n" + "\n".join(lines)

            faq = company_data.get("faq_kb_refs") or []
            faq_info = ""
            if faq:
                lines = [f"- Q: {f.get('q','')} → A: {f.get('a','')}" for f in faq if isinstance(f, dict)]
                faq_info = "FAQ:\n" + "\n".join(lines)

            system_prompt = f"""{lang_instruction}

{MESSAGE_QUALITY_INSTRUCTIONS}

{B2B_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{custom_prompt}

{products_info}

{diff_info}

{comp_info}

{obj_info}

{faq_info}

{GENERAL_INSTRUCTIONS}

{B2B_SPECIFIC_INSTRUCTIONS}

Customer context collected:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "None yet"}

{customer_context}

{IMPORTANT_RULES}

{PRICING_AND_PRODUCTS_RULES}

{OPENING_MESSAGE_RULE}

{learning_instructions}

Respond to: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2b_sales_agent: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = []
                    for p in products:
                        if isinstance(p, dict) and p.get('name'):
                            name = p.get('name', '')
                            description = p.get('summary', '') or p.get('description', '')
                            price = p.get('base_price', '')
                            
                            if price:
                                products_list.append(f"- {name}: {description} - {price} ₪")
                            else:
                                products_list.append(f"- {name}: {description}")
                    
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

{B2B_SPECIFIC_INSTRUCTIONS}

{one_line_value}

{products_info}

{GENERAL_INSTRUCTIONS}

{MESSAGE_QUALITY_INSTRUCTIONS}

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

{SALES_STRATEGY_INSTRUCTIONS}

{B2B_QUESTION_GUIDELINES}

{INFORMATION_FIRST_APPROACH}

{PRICING_AND_PRODUCTS_RULES}

{learning_instructions}

תגובה להודעת הלקוח: {state["messages"][-1].content}"""

        try:
            # Call LLM with full conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (all messages)
            for msg in state["messages"]:
                if hasattr(msg, 'content'):
                    # Determine role based on message type
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        messages.append({"role": "assistant", "content": msg.content})
                    else:
                        messages.append({"role": "user", "content": msg.content})
                else:
                    # Fallback for string messages
                    messages.append({"role": "user", "content": str(msg)})
            
            # ── Hebrew lock + ABSOLUTE FINAL RULES (B2B) ──────────────────
            # Language is locked to Hebrew — inject enforcement suffix.
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    messages[i] = {
                        "role": "user",
                        "content": messages[i]["content"] + " [ענה בעברית בלבד]",
                    }
                    break

            _company_name = (company_data or {}).get("name", "החברה")
            _msg_count = state.get("message_count", 0)
            messages.append({
                "role": "system",
                "content": _build_final_rules(_company_name, b2b=True, message_count=_msg_count),
            })

            print(f"DEBUG: Sending {len(messages)} messages to B2B LLM (including system prompt)")
            llm_response = _strip_markdown(chat(messages) or "")
            print(f"DEBUG: B2B LLM response: {llm_response}")
            
            result = {
                **state,
                "response": llm_response,
                "tone": "professional",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2b_sales_agent", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2b_sales_agent: {e}")
            return {
                **state,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "tone": "apologetic",
                "execution_path": execution_path
            }
    
    def generate_handoff_response(state: AgentState) -> AgentState:
        """Generate a contextual handoff message via LLM — not a static template."""

        execution_path = state.get("execution_path", [])
        execution_path.append("generate_handoff_response")

        user_message = state["messages"][-1].content
        _company_name = (company_data or {}).get("name", "הצוות שלנו")

        system_prompt = (
            f"You are wrapping up a sales conversation on behalf of {_company_name}.\n"
            f"Write a brief, warm, contextual handoff message (2–3 sentences) that:\n"
            f"1. Acknowledges the specific topic or need the user raised in this conversation.\n"
            f"2. Tells them a human specialist from our team will follow up shortly.\n"
            f"3. Sets a confident, positive expectation — no vague promises.\n\n"
            f"STRICT RULES:\n"
            f"- Respond in Hebrew ONLY. Even if the user wrote in English — respond in Hebrew.\n"
            f"- Do NOT ask any questions. This is a closing statement.\n"
            f"- No bullet points, no numbered lists, no markdown headers.\n"
            f"- Bold (**) is allowed ONLY on product names if you mention one.\n"
            f"- Zero emojis.\n"
            f"- 30–50 words maximum. Short and conclusive.\n"
            f"- Sound like a professional human, not a bot."
        )

        # Build message list: system + full conversation history
        messages = [{"role": "system", "content": system_prompt}]
        for msg in state["messages"]:
            if hasattr(msg, "content"):
                role = "assistant" if (hasattr(msg, "type") and msg.type == "ai") else "user"
                messages.append({"role": role, "content": msg.content})
            else:
                messages.append({"role": "user", "content": str(msg)})

        # Hard final instruction — last thing the model reads
        messages.append({
            "role": "system",
            "content": (
                "FINAL INSTRUCTION: Write the handoff message now. "
                "Respond in Hebrew only. 2–3 sentences, no questions. "
                "Reference what the user actually discussed. "
                "Confirm that a human specialist will follow up."
            ),
        })

        try:
            llm_response = _strip_markdown(chat(messages) or "").strip()
            if not llm_response:
                llm_response = HANDOFF_RESPONSE
        except Exception:
            llm_response = HANDOFF_RESPONSE

        debug_bot_response("generate_handoff_response", user_message, llm_response)

        return {
            **state,
            "response": llm_response,
            "tone": "professional",
            "execution_path": execution_path,
        }
    
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("update_customer_profile", update_customer_profile)
    workflow.add_node("b2c_sales_agent", b2c_sales_agent)
    workflow.add_node("b2b_sales_agent", b2b_sales_agent)
    workflow.add_node("generate_handoff_response", generate_handoff_response)

    # Add edges
    # classify_intent routes: HANDOFF → generate_handoff_response, SALES → update_customer_profile
    workflow.add_conditional_edges(
        "classify_intent",
        lambda s: "generate_handoff_response" if s.get("handoff") else "update_customer_profile",
        {
            "generate_handoff_response": "generate_handoff_response",
            "update_customer_profile": "update_customer_profile",
        }
    )
    workflow.add_conditional_edges(
        "update_customer_profile",
        business_type_router,
        {
            "b2c_sales_agent": "b2c_sales_agent",
            "b2b_sales_agent": "b2b_sales_agent"
        }
    )
    workflow.add_edge("b2c_sales_agent", END)
    workflow.add_edge("b2b_sales_agent", END)
    workflow.add_edge("generate_handoff_response", END)

    # Set entry point
    workflow.set_entry_point("classify_intent")

    # Compile and return the graph
    return workflow.compile()
