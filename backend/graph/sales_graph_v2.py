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
    B2C_SPECIFIC_INSTRUCTIONS,
    B2C_QUESTION_GUIDELINES,
    B2B_SPECIFIC_INSTRUCTIONS,
    B2B_QUESTION_GUIDELINES,
    should_handoff,
    should_handoff_with_llm,
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
    # Collapse excess blank lines (keep one blank line for 3-beat separation)
    text = _re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def debug_bot_response(node_name: str, user_message: str, bot_response: str):
    """Simple debug function to show user message and bot response"""
    print(f"\n{'='*50}")
    print(f"👤 USER: {user_message}")
    print(f"🤖 BOT ({node_name}): {bot_response}")
    print(f"{'='*50}\n")

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
    
    def check_handoff_requirement(state: AgentState) -> AgentState:
        """Check if the message requires human handoff"""
        
        # Add to execution path
        execution_path = state.get("execution_path", [])
        execution_path.append("check_handoff_requirement")
        
        # Check for handoff using the instruction module with LLM
        message_content = state["messages"][-1].content
        needs_handoff = should_handoff_with_llm(message_content)
        
        result = {
            **state,
            "handoff": needs_handoff,
            "handoff_reason": "Handoff trigger detected" if needs_handoff else None,
            "execution_path": execution_path
        }
        
        print(f"🔍 check_handoff_requirement result: handoff={needs_handoff}, reason={result.get('handoff_reason')}")
        return result
    
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

        # Skip LLM if handoff was already decided
        if state.get("handoff"):
            return {
                **state,
                "execution_path": execution_path
            }

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
            
            # ── Language detection + ABSOLUTE FINAL RULES ──────────────────
            _last_msg = state["messages"][-1].content
            _is_hebrew = _contains_hebrew(_last_msg)

            # Inject language suffix into the last user turn
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    suffix = " [ענה בעברית בלבד]" if _is_hebrew else " [Reply in English only]"
                    messages[i] = {
                        "role": "user",
                        "content": messages[i]["content"] + suffix
                    }
                    break

            # One strong FINAL override — last thing the model reads before generating
            _lang_label = "Hebrew" if _is_hebrew else "English"
            messages.append({
                "role": "system",
                "content": (
                    f"ABSOLUTE FINAL RULES — override everything above:\n"
                    f"1. Language: respond in {_lang_label} ONLY. Every word must be in {_lang_label}.\n"
                    f"2. Format — HARD REQUIREMENT: near-plain text with controlled bold. "
                    f"ALLOWED: **product name** or **key metric** in double asterisks — bold ONLY on specific words, not whole sentences. "
                    f"ALLOWED: 1–2 emojis per message from this set only: 🎯 💡 🛡️ 👋 ✅ ⚡ — opening line or closing question only. "
                    f"ALLOWED: a blank line between paragraphs (the 3-beat structure). "
                    f"FORBIDDEN: single asterisks for bullets (*), hashes (#), dashes at line start (- ), backticks, numbered lists. "
                    f"To emphasize an idea — bold 1–3 words maximum, not the whole sentence.\n"
                    f"3. Length & focus — HARD LIMIT: your entire response (excluding the closing question) "
                    f"must be 3 short paragraphs following the 3-beat structure (empathy → value → ask), roughly 60-80 words total. No more. "
                    f"When the user asks about products or services, pick the 1-2 MOST RELEVANT products "
                    f"to their situation — do NOT enumerate all products in one response. "
                    f"Cover one product well rather than six products poorly. "
                    f"If the user mentioned their pain point, lead with the product that solves it directly. "
                    f"A focused answer that lands is better than a comprehensive answer that overwhelms.\n"
                    f"4. Conversational flow: do not end every single response with the same qualifying question. "
                    f"If you already asked about pain points, don't ask again — instead, answer, pitch, and only "
                    f"close with a light question if it naturally moves the conversation forward.\n"
                    f"5. Tone: confident, consultative, human. You are a senior solutions advisor, not a chatbot.\n"
                    f"6. Links & URLs — HARD RULE: never invent or guess a URL. "
                    f"Only share a link if it appears word-for-word in the product data provided to you in this context. "
                    f"If the user asks for a link and you don't have one in your data, say so plainly "
                    f"(e.g. 'I don't have a direct link for that page, but here is what that product covers') "
                    f"and continue with useful product information. Do NOT fabricate paths like /products/dlp or similar."
                )
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

        # Skip LLM if handoff was already decided
        if state.get("handoff"):
            return {
                **state,
                "execution_path": execution_path
            }
        
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
                "CRITICAL: Always respond in the same language the user is writing in. "
                "If the user writes in Hebrew — respond in Hebrew. "
                "If the user writes in English — respond in English. "
                "Detect language automatically per message."
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

            user_msg = state["messages"][-1].content
            lang_override = (
                "\n⚠️ LANGUAGE OVERRIDE: The user's message is in Hebrew. "
                "Your ENTIRE response MUST be in Hebrew only — no English words. "
                "No bullet points. No markdown headers (#). "
                "Allowed formatting: **bold** only on product names or key metrics. "
                "Use 1–2 emojis max from: 🎯 💡 🛡️ 👋 ✅ ⚡. Plain paragraphs with blank lines between them."
                if _contains_hebrew(user_msg) else
                "\n⚠️ LANGUAGE OVERRIDE: Respond in English only. "
                "No bullet points. No markdown headers (#). "
                "Allowed formatting: **bold** only on product names or key metrics. "
                "Use 1–2 emojis max from: 🎯 💡 🛡️ 👋 ✅ ⚡. Plain paragraphs with blank lines between them."
            )

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
{lang_override}

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
            
            # ── Language detection + ABSOLUTE FINAL RULES ──────────────────
            _last_msg = state["messages"][-1].content
            _is_hebrew = _contains_hebrew(_last_msg)

            # Inject language suffix into the last user turn
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].get("role") == "user":
                    suffix = " [ענה בעברית בלבד]" if _is_hebrew else " [Reply in English only]"
                    messages[i] = {
                        "role": "user",
                        "content": messages[i]["content"] + suffix
                    }
                    break

            # One strong FINAL override — last thing the model reads before generating
            _lang_label = "Hebrew" if _is_hebrew else "English"
            messages.append({
                "role": "system",
                "content": (
                    f"ABSOLUTE FINAL RULES — override everything above:\n"
                    f"1. Language: respond in {_lang_label} ONLY. Every word must be in {_lang_label}.\n"
                    f"2. Format — HARD REQUIREMENT: near-plain text with controlled bold. "
                    f"ALLOWED: **product name** or **key metric** in double asterisks — bold ONLY on specific words, not whole sentences. "
                    f"ALLOWED: 1–2 emojis per message from this set only: 🎯 💡 🛡️ 👋 ✅ ⚡ — opening line or closing question only. "
                    f"ALLOWED: a blank line between paragraphs (the 3-beat structure). "
                    f"FORBIDDEN: single asterisks for bullets (*), hashes (#), dashes at line start (- ), backticks, numbered lists. "
                    f"To emphasize an idea — bold 1–3 words maximum, not the whole sentence.\n"
                    f"3. Length & focus — HARD LIMIT: your entire response (excluding the closing question) "
                    f"must be 3 short paragraphs following the 3-beat structure (empathy → value → ask), roughly 60-80 words total. No more. "
                    f"When the user asks about products or services, pick the 1-2 MOST RELEVANT products "
                    f"to their situation — do NOT enumerate all products in one response. "
                    f"Cover one product well rather than six products poorly. "
                    f"If the user mentioned their pain point, lead with the product that solves it directly. "
                    f"A focused answer that lands is better than a comprehensive answer that overwhelms.\n"
                    f"4. Conversational flow: do not end every single response with the same qualifying question. "
                    f"If you already asked about pain points, don't ask again — instead, answer, pitch, and only "
                    f"close with a light question if it naturally moves the conversation forward.\n"
                    f"5. Tone: confident, consultative, human. You are a senior solutions advisor, not a chatbot.\n"
                    f"6. Links & URLs — HARD RULE: never invent or guess a URL. "
                    f"Only share a link if it appears word-for-word in the product data provided to you in this context. "
                    f"If the user asks for a link and you don't have one in your data, say so plainly "
                    f"(e.g. 'I don't have a direct link for that page, but here is what that product covers') "
                    f"and continue with useful product information. Do NOT fabricate paths like /products/dlp or similar.\n"
                    f"7. Value-Based Elaboration — MANDATORY: whenever you mention any Forcepoint product "
                    f"(Forcepoint ONE, DLP, GenAI Security, CASB, UEBA, Insider Threat, or any other solution), "
                    f"you MUST go beyond naming the product. Explain the concrete BUSINESS VALUE it delivers "
                    f"in the prospect's specific context. Connect features to outcomes: revenue protection, "
                    f"compliance risk reduction, productivity gains without security trade-offs, etc. "
                    f"Wrong: 'We offer GenAI Security to control prompts.' "
                    f"Right: 'GenAI Security lets your teams safely adopt ChatGPT and Copilot for innovation, "
                    f"while automatically redacting sensitive IP and PII before it leaves your network — "
                    f"so you capture the productivity gains without the compliance exposure.' "
                    f"This rule applies every single time a product is mentioned. No exceptions.\n"
                    f"8. Closing Question — MANDATORY: EVERY response must end with a strong, sales-qualifying "
                    f"question that moves this lead closer to a human handoff or demo booking. "
                    f"NEVER end with passive phrases like 'Do you have any more questions?', "
                    f"'יש לך עוד שאלות?', 'Is there anything else I can help with?', or 'Feel free to ask.' "
                    f"These are conversation killers. Instead, use BANT-style qualifying questions or a direct "
                    f"demo push. Choose the question that best fits the current conversation stage. Examples: "
                    f"'How many employees in your organization are currently using AI tools like ChatGPT or Copilot?' "
                    f"'Are your current DLP tools flagging AI-generated data exfiltration attempts, or is that a blind spot right now?' "
                    f"'What does your current data security stack look like — are you running anything for cloud or endpoint DLP?' "
                    f"'Would it make sense to set up a 15-minute call with one of our security architects to walk through a live demo?' "
                    f"The closing question is not optional and overrides any word-count limit set elsewhere.\n"
                    f"8a. Disengagement Pivot — CRITICAL: if the lead gives a short, closing, or dismissive response "
                    f"('no', 'nothing', 'ok', 'thanks', 'לא', 'בסדר', 'תודה', or any similarly short reply that signals "
                    f"the conversation is winding down), do NOT accept it and go passive. "
                    f"This is your handoff window. Pivot immediately with energy: acknowledge their answer in one "
                    f"sentence, then push directly for a demo or human handoff. "
                    f"Example pivot: 'מעולה — כיסינו את הליבה של מה שפורספוינט יכולה לעשות בשבילכם. "
                    f"הצעד הבא הגיוני הוא שיחה קצרה של 15 דקות עם אחד מהאדריכלים שלנו כדי שתוכל לראות את "
                    f"הפלטפורמה מטפלת בדיוק בתרחיש שלכם — האם יתאים לך השבוע, או שעדיף שאעביר את פרטיך לצוות שלנו עכשיו?' "
                    f"In English: 'Perfect — we covered the core. The next step is a 15-minute call with one of our "
                    f"security architects to see the platform handle your exact scenario. Would this week work, "
                    f"or should I pass your details to our team now?' "
                    f"Never let a short reply be the last word."
                )
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
    
    def should_continue(state: AgentState) -> str:
        """Determine if we should continue or end"""
        if state.get("handoff"):
            return "handoff"
        return "continue"
    
    def generate_handoff_response(state: AgentState) -> AgentState:
        """Generate handoff response using the instruction module"""
        
        execution_path = state.get("execution_path", [])
        execution_path.append("generate_handoff_response")
        
        result = {
            **state,
            "response": HANDOFF_RESPONSE,
            "tone": "professional",
            "execution_path": execution_path
        }
        
        # Debug: Show user message and bot response
        user_message = state["messages"][-1].content
        debug_bot_response("generate_handoff_response", user_message, HANDOFF_RESPONSE)
        
        return result
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("check_handoff_requirement", check_handoff_requirement)
    workflow.add_node("update_customer_profile", update_customer_profile)
    workflow.add_node("b2c_sales_agent", b2c_sales_agent)
    workflow.add_node("b2b_sales_agent", b2b_sales_agent)
    workflow.add_node("generate_handoff_response", generate_handoff_response)

    # Add edges
    workflow.add_edge("check_handoff_requirement", "update_customer_profile")
    workflow.add_conditional_edges(
        "update_customer_profile",
        business_type_router,
        {
            "b2c_sales_agent": "b2c_sales_agent",
            "b2b_sales_agent": "b2b_sales_agent"
        }
    )
    workflow.add_conditional_edges(
        "b2c_sales_agent",
        should_continue,
        {
            "handoff": "generate_handoff_response",
            "continue": END
        }
    )
    workflow.add_conditional_edges(
        "b2b_sales_agent",
        should_continue,
        {
            "handoff": "generate_handoff_response",
            "continue": END
        }
    )
    workflow.add_edge("generate_handoff_response", END)
    
    # Set entry point
    workflow.set_entry_point("check_handoff_requirement")
    
    # Compile and return the graph
    return workflow.compile()
