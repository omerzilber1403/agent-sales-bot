from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, Any, List, Optional
from langchain_core.messages import BaseMessage
from ..services import llm as llm_service
import json

# State מורחב לתמיכה ב-guardrails_router
class SimpleState(TypedDict):
    # Input fields
    user_message: str
    company_data: Dict[str, Any]
    
    # Output fields
    response: str
    handoff: bool
    
    # Routing fields
    route: Optional[str]
    persona: Optional[str]  # b2b/b2c
    intent: Optional[str]   # sales/support/admin
    
    # Debug fields
    debug_info: Optional[str]

def simple_hello_node(state: SimpleState) -> SimpleState:
    """
    צומת פשוט שמחזיר תשובה קבועה
    """
    print(f"🔥 SIMPLE NODE: Received message: {state['user_message']}")
    
    # תשובה פשוטה לפי הודעת המשתמש
    user_msg = state['user_message'].lower()
    
    if 'שלום' in user_msg or 'היי' in user_msg:
        response = "שלום! איך אני יכול לעזור לך היום?"
    elif 'מחיר' in user_msg or 'כמה' in user_msg:
        response = "אני יכול לעזור לך עם מידע על המחירים. איזה מוצר מעניין אותך?"
    elif 'תודה' in user_msg or 'bye' in user_msg:
        response = "תודה לך! נשמח לעזור בעתיד."
    else:
        response = "אני כאן לעזור! איך אני יכול לסייע לך?"
    
    print(f"🔥 SIMPLE NODE: Returning response: {response}")
    
    return {
        **state,
        "response": response,
        "handoff": False,
        "debug_info": f"Processed message: {user_msg[:20]}..."
    }

def simple_guardrails_router(state: SimpleState) -> SimpleState:
    """
    צומת router פשוט שקובע persona ו-intent באמצעות LLM
    """
    print(f"🔥 GUARDRAILS ROUTER: Processing message: {state['user_message']}")
    
    user_message = state['user_message']
    company_data = state.get('company_data', {})
    business_type = company_data.get('business_type', 'B2B')
    
    # קביעת persona לפי business_type
    persona = "b2c" if business_type.upper() == "B2C" else "b2b"
    
    # LLM prompt פשוט לקביעת intent
    system_prompt = f"""אתה מנתב הודעות. החזר JSON תקין בלבד.

הודעת המשתמש: {user_message}
סוג עסק: {business_type}

קבע את ה-intent:
- sales: אם המשתמש מעוניין במוצרים/שירותים/מחירים/רכישה
- support: אם יש בעיה טכנית/תלונה/עזרה
- admin: אם מבקש לדבר עם מנהל/ביטול/החזר
- offtopic: אם לא קשור לעסק

החזר JSON בפורמט:
{{"intent": "sales", "route": "sales_discovery", "reason": "המשתמש מעוניין במוצר"}}

אם sales - route יהיה sales_discovery
אם support - route יהיה support_entry  
אם admin - route יהיה admin_entry
אם offtopic - route יהיה handoff_response"""

    try:
        # קריאה ל-LLM
        llm_response = llm_service.chat(
            [{"role": "system", "content": system_prompt}],
            temperature=0.2,
            max_tokens=100
        )
        
        print(f"🔥 LLM Response: {llm_response}")
        
        # פרסור התשובה
        try:
            routing_data = json.loads(llm_response.strip())
            intent = routing_data.get("intent", "sales")
            route = routing_data.get("route", "sales_discovery")
            reason = routing_data.get("reason", "Default routing")
        except json.JSONDecodeError:
            print("⚠️ JSON parsing failed, using defaults")
            intent = "sales"
            route = "sales_discovery"
            reason = "JSON parsing failed"
            
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        intent = "sales"
        route = "sales_discovery" 
        reason = f"LLM error: {e}"
    
    print(f"🔀 GUARDRAILS ROUTER: persona={persona}, intent={intent}, route={route}")
    print(f"🔀 REASON: {reason}")
    
    return {
        **state,
        "persona": persona,
        "intent": intent,
        "route": route,
        "debug_info": f"Routed to {route} (intent: {intent}, persona: {persona})"
    }

def compile_simple_graph():
    """
    בניית גרף עם guardrails_router + routing
    """
    print("🏗️ Building simple graph with routing...")
    
    g = StateGraph(SimpleState)
    
    # הוספת צמתים
    g.add_node("guardrails_router", simple_guardrails_router)
    g.add_node("hello_node", simple_hello_node)
    
    # חיבור עם routing
    g.add_edge(START, "guardrails_router")
    
    # Conditional routing מ-guardrails_router
    def router(state: SimpleState) -> str:
        route = state.get("route", "hello_node")
        print(f"🔀 ROUTER: Routing to {route}")
        
        # כרגע נתמוך רק ב-sales_discovery (hello_node)
        if route == "sales_discovery":
            return "hello_node"
        else:
            return "hello_node"  # Default fallback
    
    g.add_conditional_edges("guardrails_router", router, {
        "hello_node": "hello_node"
    })
    
    g.add_edge("hello_node", END)
    
    print("✅ Simple graph with routing built successfully")
    return g.compile()

# פונקציה לבדיקה מהירה
def test_simple_graph():
    """
    בדיקה מהירה של הגרף הפשוט
    """
    graph = compile_simple_graph()
    
    test_input = {
        "user_message": "שלום",
        "company_data": {"name": "Test Company"},
        "response": "",
        "handoff": False,
        "debug_info": None
    }
    
    result = graph.invoke(test_input)
    print(f"Test result: {result}")
    return result

if __name__ == "__main__":
    test_simple_graph()
