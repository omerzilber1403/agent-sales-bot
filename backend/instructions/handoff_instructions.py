"""
הוראות לטיפול בהעברה לנציג אנושי
Handoff instructions
"""

HANDOFF_TRIGGERS = [
    "מנהל", "אחראי", "דבר עם מישהו", "נציג אנושי",
    "תעביר אותי לנציג", "תעביר אותי", "רוצה לדבר עם מישהו",
    "שגיאה טכנית", "בעיה טכנית", "לא עובד", "תקלה",
    "תלונה", "מרוצה לא", "לא רוצה", "תפסיק"
]

SALES_QUESTIONS = [
    "מחיר", "תמחור", "כמה עולה", "מה המחיר",
    "זמינות", "מתי זמין", "איזה תאריך",
    "איך זה עובד", "מה זה כולל", "מה היתרונות"
]

HANDOFF_RESPONSE = """תודה על העניין! אני אעביר אותך לנציג אנושי שיוכל לעזור לך בצורה מקצועית יותר.

הנציג יצור איתך קשר בקרוב. האם יש משהו נוסף שאני יכול לעזור בו בינתיים?"""

def should_handoff(message_content: str) -> bool:
    """
    בדוק אם ההודעה דורשת העברה לנציג אנושי
    """
    message_lower = message_content.lower()
    
    # בדוק אם יש טריגרים להעברה
    needs_handoff = any(trigger in message_lower for trigger in HANDOFF_TRIGGERS)
    
    # בדוק אם זו שאלת מכירות (לא דורשת העברה)
    is_sales_question = any(question in message_lower for question in SALES_QUESTIONS)
    
    # אל תעביר אם זו שאלת מכירות
    if is_sales_question:
        needs_handoff = False
    
    return needs_handoff

def should_handoff_with_llm(message_content: str) -> bool:
    """
    בדוק אם ההודעה דורשת העברה לנציג אנושי באמצעות LLM
    """
    from ..services.llm import chat
    
    # בדוק אם זו שאלת מכירות (לא דורשת העברה)
    message_lower = message_content.lower()
    is_sales_question = any(question in message_lower for question in SALES_QUESTIONS)
    
    if is_sales_question:
        return False
    
    # בדוק אם זו שאלה כללית על החברה/השירות (לא דורשת העברה)
    general_questions = [
        "מי אתם", "מה אתם עושים", "איך זה עובד", "מה התהליך",
        "איך התהליך", "איך עובד", "מה השירות", "מה המוצר",
        "איך זה מתחיל", "איך מתחילים", "מה כולל", "מה היתרונות",
        "אני לא מצליח", "אני רוצה", "אני צריך", "אני מחפש",
        "אני מעוניין", "אני חושב", "אני חושב על", "אני שוקל",
        "אני מתעניין", "אני מתעניין ב", "אני רוצה לדעת",
        "אני רוצה להבין", "אני רוצה ללמוד", "אני רוצה לשמוע"
    ]
    
    is_general_question = any(question in message_lower for question in general_questions)
    
    if is_general_question:
        return False
    
    # השתמש ב-LLM כדי להבין את הכוונה רק אם זה לא שאלה כללית
    prompt = f"""בדוק אם ההודעה הבאה מבקשת לדבר עם נציג אנושי או מישהו אמיתי:

הודעה: "{message_content}"

האם הלקוח מבקש לדבר עם:
- נציג אנושי
- מישהו אמיתי
- מנהל
- אחראי
- מישהו אחר במקום הבוט

השבת רק "כן" או "לא"."""

    try:
        response = chat([{"role": "user", "content": prompt}])
        return response and "כן" in response
    except:
        # אם יש בעיה עם LLM, חזור לשיטה הישנה
        return should_handoff(message_content)
