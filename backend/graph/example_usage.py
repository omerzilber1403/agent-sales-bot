"""
דוגמה לשימוש ב-Sales Graph החדש
Example usage of the new Sales Graph
"""

from sales_graph_v2 import create_sales_graph
from langchain_core.messages import HumanMessage

def example_b2c_conversation():
    """דוגמה לשיחה B2C"""
    
    # נתוני חברה לדוגמה
    company_data = {
        "name": "חנות האופנה הטובה",
        "business_type": "B2C",
        "one_line_value": "אנחנו מציעים בגדים איכותיים במחירים נוחים",
        "products": [
            {"name": "חולצות", "description": "חולצות איכותיות מבדים טבעיים"},
            {"name": "מכנסיים", "description": "מכנסיים נוחים וטרנדיים"}
        ]
    }
    
    # יצירת הגרף
    graph = create_sales_graph(company_data)
    
    # מצב התחלתי
    initial_state = {
        "messages": [HumanMessage(content="שלום, אני מחפש חולצה חדשה")],
        "customer_context": "",
        "smart_questions": [],
        "extracted_info": {},
        "response": "",
        "handoff": False,
        "handoff_reason": None,
        "tone": "",
        "execution_path": [],
        "company_data": company_data
    }
    
    # הרצת הגרף
    result = graph.invoke(initial_state)
    
    print("תגובת הבוט:")
    print(result["response"])
    print(f"\nנתיב ביצוע: {' -> '.join(result['execution_path'])}")
    
    return result

def example_b2b_conversation():
    """דוגמה לשיחה B2B"""
    
    # נתוני חברה לדוגמה
    company_data = {
        "name": "פתרונות עסקיים מתקדמים",
        "business_type": "B2B",
        "one_line_value": "אנחנו מספקים פתרונות תוכנה מתקדמים לעסקים",
        "products": [
            {"name": "מערכת CRM", "description": "מערכת ניהול לקוחות מתקדמת"},
            {"name": "מערכת ERP", "description": "מערכת ניהול משאבי ארגון"}
        ]
    }
    
    # יצירת הגרף
    graph = create_sales_graph(company_data)
    
    # מצב התחלתי
    initial_state = {
        "messages": [HumanMessage(content="שלום, אני מחפש פתרון CRM לחברה שלנו")],
        "customer_context": "",
        "smart_questions": [],
        "extracted_info": {},
        "response": "",
        "handoff": False,
        "handoff_reason": None,
        "tone": "",
        "execution_path": [],
        "company_data": company_data
    }
    
    # הרצת הגרף
    result = graph.invoke(initial_state)
    
    print("תגובת הבוט:")
    print(result["response"])
    print(f"\nנתיב ביצוע: {' -> '.join(result['execution_path'])}")
    
    return result

def example_handoff_scenario():
    """דוגמה לתרחיש העברה לנציג"""
    
    # נתוני חברה לדוגמה
    company_data = {
        "name": "שירותי תמיכה",
        "business_type": "B2C"
    }
    
    # יצירת הגרף
    graph = create_sales_graph(company_data)
    
    # מצב התחלתי עם בקשה להעברה
    initial_state = {
        "messages": [HumanMessage(content="אני רוצה לדבר עם מנהל")],
        "customer_context": "",
        "smart_questions": [],
        "extracted_info": {},
        "response": "",
        "handoff": False,
        "handoff_reason": None,
        "tone": "",
        "execution_path": [],
        "company_data": company_data
    }
    
    # הרצת הגרף
    result = graph.invoke(initial_state)
    
    print("תגובת הבוט:")
    print(result["response"])
    print(f"\nנתיב ביצוע: {' -> '.join(result['execution_path'])}")
    print(f"האם דורש העברה: {result['handoff']}")
    
    return result

if __name__ == "__main__":
    print("=== דוגמה לשיחה B2C ===")
    example_b2c_conversation()
    
    print("\n=== דוגמה לשיחה B2B ===")
    example_b2b_conversation()
    
    print("\n=== דוגמה לתרחיש העברה ===")
    example_handoff_scenario()
