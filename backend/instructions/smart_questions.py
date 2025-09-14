"""
מערכת שאלות חכמות - איסוף מידע רלוונטי מהלקוח
"""

# שאלות חכמות לפי הקשר
SMART_QUESTIONS = {
    "greeting": [
        "איך אני יכול לעזור לך היום?",
        "מה מביא אותך אלינו?",
        "איך אני יכול לשרת אותך?"
    ],
    
    "interest_expression": [
        "זה נשמע מעניין! איזה חלק במיוחד מעניין אותך?",
        "מעולה! איך אתה רואה את זה מתאים לצרכים שלך?",
        "זה בדיוק מה שאנחנו עושים! איזה שאלות יש לך?"
    ],
    
    "need_analysis": [
        "איזה בעיה אתה מנסה לפתור?",
        "מה המטרה שלך עם זה?",
        "איך זה יסייע לך?",
        "מה הצרכים הספציפיים שלך?"
    ],
    
    "budget_timing": [
        "איזה תקציב אתה חושב עליו?",
        "מתי אתה רוצה להתחיל?",
        "איזה לוח זמנים יש לך?",
        "מה העדיפות שלך?"
    ],
    
    "objection_handling": [
        "אני מבין את החשש שלך. איך אני יכול לעזור לך להבין את זה טוב יותר?",
        "זה שאלה מצוינת! בואו נדבר על זה",
        "אני רואה שיש לך חששות. איזה מידע נוסף יעזור לך?"
    ],
    
    "closing": [
        "איך זה נשמע לך?",
        "מה אתה חושב על זה?",
        "איזה שאלות נוספות יש לך?",
        "איך אתה רוצה להמשיך?"
    ]
}

# שאלות מעקב חכמות
FOLLOW_UP_QUESTIONS = {
    "after_info": [
        "זה עונה על השאלה שלך?",
        "איזה מידע נוסף אתה צריך?",
        "איך זה נשמע לך עד כה?"
    ],
    
    "after_handoff": [
        "האם יש משהו נוסף שאוכל לעזור לך לפני שאעביר אותך?",
        "איזה מידע חשוב לך שהנציג ידע?",
        "מה השאלה הכי חשובה שלך?"
    ],
    
    "after_solution": [
        "איך זה נשמע לך?",
        "מה אתה חושב על הפתרון הזה?",
        "איזה שאלות נוספות יש לך?"
    ]
}

# שאלות לפי סוג לקוח
CUSTOMER_TYPE_QUESTIONS = {
    "b2c": [
        "איזה גיל יש לך?",
        "איזה תחום עיסוק?",
        "איזה ניסיון יש לך עם זה?",
        "מה המטרה שלך?"
    ],
    
    "b2b": [
        "איזה גודל החברה שלך?",
        "איזה תחום עיסוק?",
        "איזה תפקיד יש לך?",
        "מה המטרה העסקית שלך?"
    ]
}

# שאלות לפי מוצר/שירות
PRODUCT_QUESTIONS = {
    "pricing": [
        "איזה תקציב אתה חושב עליו?",
        "מה הערך שאתה מחפש?",
        "איזה ROI אתה מצפה?"
    ],
    
    "implementation": [
        "איזה לוח זמנים יש לך?",
        "איזה משאבים יש לך?",
        "איזה אתגרים אתה רואה?"
    ],
    
    "support": [
        "איזה תמיכה אתה צריך?",
        "איזה הכשרה אתה רוצה?",
        "איזה ליווי אתה מצפה?"
    ]
}

def get_smart_question(context: str, customer_type: str = None, product_type: str = None) -> str:
    """
    מחזיר שאלה חכמה לפי הקשר
    """
    import random
    
    # בחירת שאלה לפי הקשר
    if context in SMART_QUESTIONS:
        questions = SMART_QUESTIONS[context]
    elif context in FOLLOW_UP_QUESTIONS:
        questions = FOLLOW_UP_QUESTIONS[context]
    elif customer_type and customer_type in CUSTOMER_TYPE_QUESTIONS:
        questions = CUSTOMER_TYPE_QUESTIONS[customer_type]
    elif product_type and product_type in PRODUCT_QUESTIONS:
        questions = PRODUCT_QUESTIONS[product_type]
    else:
        questions = SMART_QUESTIONS["greeting"]
    
    return random.choice(questions)

def get_contextual_question(conversation_history: list, current_message: str) -> str:
    """
    מחזיר שאלה חכמה לפי היסטוריית השיחה
    """
    # ניתוח הקשר פשוט
    if not conversation_history:
        return get_smart_question("greeting")
    
    last_message = conversation_history[-1].get('content', '').lower()
    
    # זיהוי הקשר
    if any(word in last_message for word in ['מחיר', 'עלות', 'תקציב']):
        return get_smart_question("budget_timing")
    elif any(word in last_message for word in ['מתי', 'זמן', 'לוח']):
        return get_smart_question("budget_timing")
    elif any(word in last_message for word in ['בעיה', 'אתגר', 'קושי']):
        return get_smart_question("need_analysis")
    elif any(word in last_message for word in ['חשש', 'פחד', 'דאגה']):
        return get_smart_question("objection_handling")
    elif any(word in last_message for word in ['מעולה', 'נשמע טוב', 'מעניין']):
        return get_smart_question("interest_expression")
    else:
        return get_smart_question("greeting")

def should_ask_question(conversation_history: list, message_count: int) -> bool:
    """
    קובע אם לשאול שאלה או לא
    """
    # לא לשאול שאלות מיד
    if message_count < 2:
        return False
    
    # לא לשאול שאלות אחרי handoff
    if conversation_history and conversation_history[-1].get('handoff'):
        return False
    
    # לשאול שאלה כל 2-3 הודעות
    return message_count % 3 == 0
