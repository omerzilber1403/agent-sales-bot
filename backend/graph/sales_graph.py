from __future__ import annotations
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from ..services.llm import chat
import json

def debug_bot_response(node_name: str, user_message: str, bot_response: str):
    """Simple debug function to show user message and bot response"""
    print(f"\n{'='*50}")
    print(f"👤 USER: {user_message}")
    print(f"🤖 BOT ({node_name}): {bot_response}")
    print(f"{'='*50}\n")

def business_type_router(state: AgentState) -> Literal["b2c_friendly_node", "b2b_friendly_node"]:
    """Route to appropriate node based on business type"""
    company_data = state.get("company_data", {})
    business_type = company_data.get("business_type", "B2B").upper()
    print(f"🔀 business_type_router: routing to {'b2c_friendly_node' if business_type == 'B2C' else 'b2b_friendly_node'}")
    return "b2c_friendly_node" if business_type == "B2C" else "b2b_friendly_node"

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

def create_sales_graph(company_data: Dict[str, Any] = None):
    """Create the sales agent graph with customer profiling and company data"""
    
    def detect_handoff(state: AgentState) -> AgentState:
        """Detect if the message requires human handoff"""

        
        # Add to execution path
        execution_path = state.get("execution_path", [])
        execution_path.append("detect_handoff")
        
        # Check for handoff triggers - only for real issues, not sales questions
        message_content = state["messages"][-1].content.lower()
        handoff_triggers = [
            "מנהל", "אחראי", "דבר עם מישהו", "נציג אנושי",
            "שגיאה טכנית", "בעיה טכנית", "לא עובד", "תקלה",
            "תלונה", "מרוצה לא", "לא רוצה", "תפסיק"
        ]
        
        # Don't handoff for sales questions - these should be handled by the agent
        sales_questions = [
            "מחיר", "תמחור", "כמה עולה", "מה המחיר",
            "זמינות", "מתי זמין", "איזה תאריך",
            "איך זה עובד", "מה זה כולל", "מה היתרונות"
        ]
        
        # Only handoff if it's a real issue, not a sales question
        needs_handoff = any(trigger in message_content for trigger in handoff_triggers)
        is_sales_question = any(question in message_content for question in sales_questions)
        
        # Don't handoff for sales questions
        if is_sales_question:
            needs_handoff = False
        
        result = {
            **state,
            "handoff": needs_handoff,
            "handoff_reason": "Handoff trigger detected" if needs_handoff else None,
            "execution_path": execution_path
        }
        
        print(f"🔍 detect_handoff result: handoff={needs_handoff}, reason={result.get('handoff_reason')}")
        return result
    
    def match_templates(state: AgentState) -> AgentState:
        """Match message to predefined templates"""

        
        execution_path = state.get("execution_path", [])
        execution_path.append("match_templates")
        
        message_content = state["messages"][-1].content.lower()
        
        # Simple template matching
        templates = {
            "greeting": ["שלום", "היי", "בוקר טוב", "ערב טוב"],
            "thanks": ["תודה", "תדה", "תודה רבה"],
            "goodbye": ["ביי", "להתראות", "נתראה", "ביי ביי"]
        }
        
        matched_template = None
        for template_name, keywords in templates.items():
            if any(keyword in message_content for keyword in keywords):
                matched_template = template_name
                break
        
        # Generate personalized responses based on company data
        if matched_template == "greeting":
            if company_data:
                company_name = company_data.get("name", "החברה")
                response = f"שלום! איך אני יכול לעזור לך?"
            else:
                response = "שלום! איך אני יכול לעזור לך?"
        elif matched_template == "thanks":
            response = "בשמחה! יש עוד משהו שאני יכול לעזור בו?"
        elif matched_template == "goodbye":
            response = "להתראות! היה נעים לעזור לך."
        else:
            response = None
        
        result = {
            **state,
            "response": response or state.get("response", ""),
            "execution_path": execution_path
        }
        
        print(f"🔍 match_templates result: response_length={len(result.get('response', ''))}")
        return result
    
    def b2c_friendly_node(state: AgentState) -> AgentState:
        """B2C friendly and interested sales approach"""

        
        execution_path = state.get("execution_path", [])
        execution_path.append("b2c_friendly_node")
        
        # If we already have a response from templates, use it
        if state.get("response"):
            return {
                **state,
                "execution_path": execution_path
            }
        
        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})
        
        # Get company-specific fields to collect
        custom_fields = company_data.get("custom_fields", {}) if company_data else {}
        
        # Build system prompt for B2C approach
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            system_prompt = f"""{custom_prompt}

הוראות כלליות לכל החברות:
- שאל רק שאלה אחת בכל הודעה
- אל תשאל מספר שאלות באותה הודעה
- התמקד בשאלה החשובה ביותר
- אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
- שאל שאלות רק אם באמת צריך מידע למכירה
- התמקד בפתרון הבעיות של הלקוח

הוראות ספציפיות ל-B2C (עסק לצרכן) - חובה:
- אתה מדבר עם לקוחות פרטיים, לא עם עסקים
- השתמש במילים כמו "אתה" ולא "החברה שלך"
- התמקד בצרכים אישיים ונוחות
- שאל על חוויות אישיות וצרכים פרטיים
- אל תשאל על תקציבים עסקיים או ROI
- אל תשאל "מה התפקיד שלך" או "איך העסק שלך עובד"
- התמקד בשירות האישי שאתה מציע

שדות מידע ספציפיים לחברה (אסוף רק את המידע הזה):
{custom_fields.get('description', 'אין שדות מידע ספציפיים מוגדרים')}

רשימת השדות לאסוף:
{chr(10).join([f"- {field}: {desc}" for field, desc in custom_fields.get('fields', {}).items()]) if custom_fields.get('fields') else "אין שדות מוגדרים"}

חשוב: שאל רק על השדות הרשומים למעלה! אל תשאל על מידע אחר!

הוראות איכות הודעות - חובה:
- כתב הודעות קצרות וברורות (1-2 שורות מקסימום)
- השתמש בשפה פשוטה ומובנת
- אל תחזור על מילים או ביטויים
- אל תכתוב הודעות ארוכות או מסובכות
- התמקד בנקודה אחת בכל הודעה
- השתמש בטון מקצועי אבל חם
- אל תכתוב הודעות תבניתיות או משעממות
- אל תכתוב הודעות פתיחה ארוכות
- התחל ישר לעניין

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "אין מידע נוסף על הלקוח"}

הקשר הלקוח:
{customer_context}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions]) if smart_questions else "אין שאלות ספציפיות"}

הוראות חשובות:
- אם הלקוח מזכיר מידע חדש (תפקיד, עסק, צרכים) - שמור אותו
- השתמש במידע שכבר יש לך על הלקוח
- אל תחזור על שאלות שכבר נשאלו
- התמקד בפתרון הבעיות של הלקוח
- שמור על טון ידידותי וקצר

הוראה חשובה: אם זו הודעת פתיחה (שלום/היי), תן תגובה קצרה של שורה אחת בלבד!

תגובה להודעת הלקוח: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2c_friendly_node: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = [f"- {p.get('name', '')}: {p.get('description', '')}" for p in products if isinstance(p, dict)]
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

הוראות ספציפיות ל-B2C (עסק לצרכן) - חובה:
- אתה מדבר עם לקוחות פרטיים, לא עם עסקים
- השתמש במילים כמו "אתה" ולא "החברה שלך"
- התמקד בצרכים אישיים ונוחות
- שאל על חוויות אישיות וצרכים פרטיים
- אל תשאל על תקציבים עסקיים או ROI
- אל תשאל "מה התפקיד שלך" או "איך העסק שלך עובד"
- התמקד בשירות האישי שאתה מציע

{one_line_value}

{products_info}

הוראות כלליות לכל החברות:
- שאל רק שאלה אחת בכל הודעה
- אל תשאל מספר שאלות באותה הודעה
- התמקד בשאלה החשובה ביותר
- אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
- שאל שאלות רק אם באמת צריך מידע למכירה
- התמקד בפתרון הבעיות של הלקוח

הוראות איכות הודעות - חובה:
- כתב הודעות קצרות וברורות (1-2 שורות מקסימום)
- השתמש בשפה פשוטה ומובנת
- אל תחזור על מילים או ביטויים
- אל תכתוב הודעות ארוכות או מסובכות
- התמקד בנקודה אחת בכל הודעה
- השתמש בטון מקצועי אבל חם
- אל תכתוב הודעות תבניתיות או משעממות
- אל תכתוב הודעות פתיחה ארוכות
- התחל ישר לעניין

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

הוראות:
1. תן תשובה קצרה וחמה (שורה אחת בדרך כלל)
2. אל תחזור על ברכות - אל תגיד "הי עומר" בכל הודעה
3. התמקד בפתרון הבעיה של הלקוח
4. השתמש בטון ידידותי ומקצועי
5. אם הלקוח מתעניין במוצר, תן מידע רלוונטי
6. הצג יתרונות המוצר/שירות
7. התקדם לקראת מכירה
8. אל תעביר לנציג אלא אם הלקוח מבקש במפורש
9. קרא את המידע על הלקוח לפני שתשאל שאלות
10. אל תשאל על מידע שכבר יש לך (גיל, תפקיד, עסק)
11. השתמש במידע שכבר יש לך על הלקוח
12. שאל שאלות רק אם באמת צריך מידע למכירה
13. אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
14. לפני שתשאל שאלה, שאל את עצמך: האם השאלה הזאת עוזרת לי למכור?
15. שאל רק שאלות שקשורות ישירות לצרכים או לבעיות של הלקוח
16. אל תשאל שאלות אישיות (נישואין, ילדים, גיל, מיקום) אלא אם הן רלוונטיות ישירות למוצר
17. התמקד בשאלות רלוונטיות: איזה בעיות יש, איך המוצר יכול לעזור
18. שאל רק שאלה אחת בכל הודעה - אל תשאל מספר שאלות
19. התמקד בשאלה החשובה ביותר

תגובה בהודעת הלקוח: {state["messages"][-1].content}"""

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
            
            print(f"DEBUG: Sending {len(messages)} messages to B2C LLM (including system prompt)")
            llm_response = chat(messages)
            print(f"DEBUG: B2C LLM response: {llm_response}")
            
            result = {
                **state,
                "response": llm_response,
                "tone": "friendly",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2c_friendly_node", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2c_friendly_node: {e}")
            return {
                **state,
                "response": "מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
                "tone": "apologetic",
                "execution_path": execution_path
            }
    
    def b2b_friendly_node(state: AgentState) -> AgentState:
        """B2B friendly and interested sales approach"""

        
        execution_path = state.get("execution_path", [])
        execution_path.append("b2b_friendly_node")
        
        # If we already have a response from templates, use it
        if state.get("response"):
            return {
                **state,
                "execution_path": execution_path
            }
        
        # Prepare context for LLM
        customer_context = state.get("customer_context", "")
        smart_questions = state.get("smart_questions", [])
        extracted_info = state.get("extracted_info", {})
        
        # Get company-specific fields to collect
        custom_fields = company_data.get("custom_fields", {}) if company_data else {}
        
        # Build system prompt for B2B approach
        if company_data and company_data.get("custom_prompt"):
            custom_prompt = company_data.get("custom_prompt")
            system_prompt = f"""{custom_prompt}

הוראות כלליות לכל החברות:
- שאל רק שאלה אחת בכל הודעה
- אל תשאל מספר שאלות באותה הודעה
- התמקד בשאלה החשובה ביותר
- אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
- שאל שאלות רק אם באמת צריך מידע למכירה
- התמקד בפתרון הבעיות של הלקוח

הוראות ספציפיות ל-B2B (עסק לעסק) - חובה:
- אתה מדבר עם נציגי חברות ועסקים
- השתמש במילים כמו "החברה שלך" או "העסק שלך"
- התמקד בתועלות עסקיות ו-ROI
- שאל על תהליכים עסקיים ואתגרים ארגוניים
- התמקד בפתרונות מקצועיים
- שאל על תפקיד, גודל חברה, ענף, תהליך רכישה

שדות מידע ספציפיים לחברה (אסוף רק את המידע הזה):
{custom_fields.get('description', 'אין שדות מידע ספציפיים מוגדרים')}

רשימת השדות לאסוף:
{chr(10).join([f"- {field}: {desc}" for field, desc in custom_fields.get('fields', {}).items()]) if custom_fields.get('fields') else "אין שדות מוגדרים"}

חשוב: שאל רק על השדות הרשומים למעלה! אל תשאל על מידע אחר!

הוראות איכות הודעות - חובה:
- כתב הודעות קצרות וברורות (1-2 שורות מקסימום)
- השתמש בשפה פשוטה ומובנת
- אל תחזור על מילים או ביטויים
- אל תכתוב הודעות ארוכות או מסובכות
- התמקד בנקודה אחת בכל הודעה
- השתמש בטון מקצועי אבל חם
- אל תכתוב הודעות תבניתיות או משעממות
- אל תכתוב הודעות פתיחה ארוכות
- התחל ישר לעניין

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()]) if extracted_info else "אין מידע נוסף על הלקוח"}

הקשר הלקוח:
{customer_context}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions]) if smart_questions else "אין שאלות ספציפיות"}

הוראות חשובות:
- אם הלקוח מזכיר מידע חדש (תפקיד, עסק, צרכים) - שמור אותו
- השתמש במידע שכבר יש לך על הלקוח
- אל תחזור על שאלות שכבר נשאלו
- התמקד בפתרון הבעיות של הלקוח
- שמור על טון ידידותי וקצר

הוראה חשובה: אם זו הודעת פתיחה (שלום/היי), תן תגובה קצרה של שורה אחת בלבד!

תגובה להודעת הלקוח: {state["messages"][-1].content}"""
        else:
            # Build system prompt using company data even without custom_prompt
            if company_data:
                company_name = company_data.get("name", "החברה")
                business_type = company_data.get("business_type", "B2B")
                one_line_value = company_data.get("one_line_value", "")
                products = company_data.get("products", [])
                
                print(f"DEBUG b2b_friendly_node: Company={company_name}, Business Type={business_type}")
                
                products_info = ""
                if products:
                    products_list = [f"- {p.get('name', '')}: {p.get('description', '')}" for p in products if isinstance(p, dict)]
                    if products_list:
                        products_info = f"""
מוצרים/שירותים:
{chr(10).join(products_list)}
"""
                
                system_prompt = f"""אתה נציג מכירות של {company_name}.

הוראות ספציפיות ל-B2B (עסק לעסק) - חובה:
- אתה מדבר עם נציגי חברות ועסקים
- השתמש במילים כמו "החברה שלך" או "העסק שלך"
- התמקד בתועלות עסקיות ו-ROI
- שאל על תהליכים עסקיים ואתגרים ארגוניים
- התמקד בפתרונות מקצועיים
- שאל על תפקיד, גודל חברה, ענף, תהליך רכישה

{one_line_value}

{products_info}

הוראות כלליות לכל החברות:
- שאל רק שאלה אחת בכל הודעה
- אל תשאל מספר שאלות באותה הודעה
- התמקד בשאלה החשובה ביותר
- אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
- שאל שאלות רק אם באמת צריך מידע למכירה
- התמקד בפתרון הבעיות של הלקוח

הוראות איכות הודעות - חובה:
- כתב הודעות קצרות וברורות (1-2 שורות מקסימום)
- השתמש בשפה פשוטה ומובנת
- אל תחזור על מילים או ביטויים
- אל תכתוב הודעות ארוכות או מסובכות
- התמקד בנקודה אחת בכל הודעה
- השתמש בטון מקצועי אבל חם
- אל תכתוב הודעות תבניתיות או משעממות
- אל תכתוב הודעות פתיחה ארוכות
- התחל ישר לעניין

{customer_context}

מידע על הלקוח שנאסף:
{chr(10).join([f"- {key}: {value}" for key, value in extracted_info.items()])}

שאלות חכמות לשאול (אם רלוונטי):
{chr(10).join([f"- {q}" for q in smart_questions])}

הוראות:
1. תן תשובה קצרה וחמה (שורה אחת בדרך כלל)
2. אל תחזור על ברכות - אל תגיד "הי עומר" בכל הודעה
3. התמקד בפתרון הבעיה של הלקוח
4. השתמש בטון ידידותי ומקצועי
5. אם הלקוח מתעניין במוצר, תן מידע רלוונטי
6. הצג יתרונות המוצר/שירות
7. התקדם לקראת מכירה
8. אל תעביר לנציג אלא אם הלקוח מבקש במפורש
9. קרא את המידע על הלקוח לפני שתשאל שאלות
10. שאל על תפקיד, גודל חברה, ענף, תהליך רכישה
11. השתמש במידע שכבר יש לך על הלקוח
12. שאל שאלות רק אם באמת צריך מידע למכירה
13. אם התשובה פשוטה - תן תשובה פשוטה ללא שאלות נוספות
14. לפני שתשאל שאלה, שאל את עצמך: האם השאלה הזאת עוזרת לי למכור?
15. שאל רק שאלות שקשורות ישירות לצרכים או לבעיות של הלקוח
16. התמקד בשאלות עסקיות: איך העסק עובד, איזה בעיות יש, איך המוצר יכול לעזור
17. שאל רק שאלה אחת בכל הודעה - אל תשאל מספר שאלות
18. התמקד בשאלה החשובה ביותר

תגובה בהודעת הלקוח: {state["messages"][-1].content}"""

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
            
            print(f"DEBUG: Sending {len(messages)} messages to B2B LLM (including system prompt)")
            llm_response = chat(messages)
            print(f"DEBUG: B2B LLM response: {llm_response}")
            
            result = {
                **state,
                "response": llm_response,
                "tone": "professional",
                "execution_path": execution_path
            }
            
            # Debug: Show user message and bot response
            user_message = state["messages"][-1].content
            debug_bot_response("b2b_friendly_node", user_message, llm_response)
            
            return result
        except Exception as e:
            print(f"DEBUG: Error in b2b_friendly_node: {e}")
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
    
    def handoff_response(state: AgentState) -> AgentState:
        """Generate handoff response"""

        
        execution_path = state.get("execution_path", [])
        execution_path.append("handoff_response")
        
        handoff_message = """תודה על העניין! אני אעביר אותך לנציג אנושי שיוכל לעזור לך בצורה מקצועית יותר.

הנציג יצור איתך קשר בקרוב. האם יש משהו נוסף שאני יכול לעזור בו בינתיים?"""
        
        result = {
            **state,
            "response": handoff_message,
            "tone": "professional",
            "execution_path": execution_path
        }
        
        # Debug: Show user message and bot response
        user_message = state["messages"][-1].content
        debug_bot_response("handoff_response", user_message, handoff_message)
        
        return result
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("detect_handoff", detect_handoff)
    workflow.add_node("match_templates", match_templates)
    workflow.add_node("b2c_friendly_node", b2c_friendly_node)
    workflow.add_node("b2b_friendly_node", b2b_friendly_node)
    workflow.add_node("handoff_response", handoff_response)
    
    # Add edges
    workflow.add_edge("detect_handoff", "match_templates")
    workflow.add_conditional_edges(
        "match_templates",
        business_type_router,
        {
            "b2c_friendly_node": "b2c_friendly_node",
            "b2b_friendly_node": "b2b_friendly_node"
        }
    )
    workflow.add_conditional_edges(
        "b2c_friendly_node",
        should_continue,
        {
            "handoff": "handoff_response",
            "continue": END
        }
    )
    workflow.add_conditional_edges(
        "b2b_friendly_node",
        should_continue,
        {
            "handoff": "handoff_response",
            "continue": END
        }
    )
    workflow.add_edge("handoff_response", END)
    
    # Set entry point
    workflow.set_entry_point("detect_handoff")
    
    # Compile and return the graph
    return workflow.compile()
