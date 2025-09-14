"""
מערכת זרימת שיחה טבעית - הודעות יותר זורמות וטבעיות
"""

# שלבי שיחה
CONVERSATION_STAGES = {
    "greeting": {
        "name": "ברכה",
        "description": "הודעת פתיחה קצרה וחמה",
        "next_stages": ["interest_discovery", "need_analysis"]
    },
    
    "interest_discovery": {
        "name": "גילוי עניין",
        "description": "הבנת מה מעניין את הלקוח",
        "next_stages": ["need_analysis", "information_provision"]
    },
    
    "need_analysis": {
        "name": "ניתוח צרכים",
        "description": "הבנת הצרכים והבעיות של הלקוח",
        "next_stages": ["information_provision", "solution_presentation"]
    },
    
    "information_provision": {
        "name": "מתן מידע",
        "description": "מתן מידע רלוונטי על המוצר/שירות",
        "next_stages": ["solution_presentation", "objection_handling"]
    },
    
    "solution_presentation": {
        "name": "הצגת פתרון",
        "description": "הצגת הפתרון המתאים",
        "next_stages": ["objection_handling", "closing"]
    },
    
    "objection_handling": {
        "name": "טיפול בהתנגדויות",
        "description": "טיפול בחששות והתנגדויות",
        "next_stages": ["solution_presentation", "closing", "handoff"]
    },
    
    "closing": {
        "name": "סגירה",
        "description": "הצעת פעולה הבאה",
        "next_stages": ["handoff", "follow_up"]
    },
    
    "handoff": {
        "name": "העברה לנציג",
        "description": "העברה לנציג אנושי",
        "next_stages": []
    },
    
    "follow_up": {
        "name": "מעקב",
        "description": "מעקב אחרי השיחה",
        "next_stages": ["closing", "handoff"]
    }
}

# מעברים טבעיים בין שלבים
NATURAL_TRANSITIONS = {
    "greeting_to_interest": [
        "איך אני יכול לעזור לך היום?",
        "מה מביא אותך אלינו?",
        "איך אני יכול לשרת אותך?"
    ],
    
    "interest_to_needs": [
        "זה נשמע מעניין! איזה חלק במיוחד מעניין אותך?",
        "מעולה! איך אתה רואה את זה מתאים לצרכים שלך?",
        "זה בדיוק מה שאנחנו עושים! איזה שאלות יש לך?"
    ],
    
    "needs_to_info": [
        "תבסס על מה שסיפרת לי, אני חושב שיש לנו משהו שיכול לעזור לך",
        "זה בדיוק מה שאנחנו עושים! בואו נדבר על זה",
        "יש לנו פתרון שיכול לענות על הצרכים שלך"
    ],
    
    "info_to_solution": [
        "איך זה נשמע לך?",
        "מה אתה חושב על זה?",
        "איזה שאלות יש לך על זה?"
    ],
    
    "solution_to_closing": [
        "איך זה נשמע לך?",
        "מה אתה חושב על זה?",
        "איזה שאלות נוספות יש לך?"
    ]
}

# הודעות מעבר טבעיות
NATURAL_BRIDGES = {
    "acknowledgment": [
        "אני מבין",
        "זה מעניין",
        "זה הגיוני",
        "זה נשמע טוב"
    ],
    
    "empathy": [
        "אני מבין את החשש שלך",
        "זה שאלה מצוינת",
        "זה בדיוק מה שאני חושב",
        "זה נשמע הגיוני"
    ],
    
    "encouragement": [
        "זה נשמע מעולה",
        "זה בדיוק מה שאנחנו עושים",
        "זה בדיוק מה שאתה צריך",
        "זה נשמע מושלם"
    ],
    
    "clarification": [
        "בואו נבין את זה טוב יותר",
        "זה שאלה מצוינת",
        "זה בדיוק מה שאני חושב",
        "זה נשמע הגיוני"
    ]
}

def get_conversation_stage(conversation_history: list, current_message: str) -> str:
    """
    קובע את השלב הנוכחי של השיחה
    """
    if not conversation_history:
        return "greeting"
    
    # ניתוח הודעות אחרונות
    recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
    
    # זיהוי שלב לפי מילות מפתח
    for message in recent_messages:
        content = message.get('content', '').lower()
        
        if any(word in content for word in ['מחיר', 'עלות', 'תקציב']):
            return "solution_presentation"
        elif any(word in content for word in ['מתי', 'זמן', 'לוח']):
            return "solution_presentation"
        elif any(word in content for word in ['בעיה', 'אתגר', 'קושי']):
            return "need_analysis"
        elif any(word in content for word in ['חשש', 'פחד', 'דאגה']):
            return "objection_handling"
        elif any(word in content for word in ['מעולה', 'נשמע טוב', 'מעניין']):
            return "interest_discovery"
        elif any(word in content for word in ['איך', 'מה', 'למה']):
            return "information_provision"
    
    # שלב ברירת מחדל
    return "interest_discovery"

def get_natural_transition(from_stage: str, to_stage: str) -> str:
    """
    מחזיר מעבר טבעי בין שלבים
    """
    transition_key = f"{from_stage}_to_{to_stage}"
    
    if transition_key in NATURAL_TRANSITIONS:
        import random
        return random.choice(NATURAL_TRANSITIONS[transition_key])
    
    # מעבר ברירת מחדל
    return "איך זה נשמע לך?"

def get_natural_bridge(bridge_type: str) -> str:
    """
    מחזיר גשר טבעי להודעה
    """
    if bridge_type in NATURAL_BRIDGES:
        import random
        return random.choice(NATURAL_BRIDGES[bridge_type])
    
    return ""

def should_use_bridge(conversation_history: list, current_message: str) -> bool:
    """
    קובע אם להשתמש בגשר טבעי
    """
    if not conversation_history:
        return False
    
    # השתמש בגשר אם ההודעה הקודמת הייתה שאלה
    last_message = conversation_history[-1].get('content', '')
    if '?' in last_message:
        return True
    
    # השתמש בגשר אם ההודעה הקודמת הייתה התנגדות
    if any(word in last_message.lower() for word in ['לא', 'חשש', 'דאגה', 'בעיה']):
        return True
    
    return False

def get_conversation_flow_guidance(stage: str, customer_profile: dict = None) -> str:
    """
    מחזיר הנחיות לזרימת השיחה לפי השלב
    """
    stage_info = CONVERSATION_STAGES.get(stage, {})
    
    guidance = f"שלב נוכחי: {stage_info.get('name', stage)}\n"
    guidance += f"תיאור: {stage_info.get('description', '')}\n\n"
    
    if stage == "greeting":
        guidance += "הוראות: הודעה קצרה וחמה, שאל איך אתה יכול לעזור"
    elif stage == "interest_discovery":
        guidance += "הוראות: גלה מה מעניין את הלקוח, שאל שאלות פתוחות"
    elif stage == "need_analysis":
        guidance += "הוראות: הבן את הצרכים והבעיות, שאל שאלות מעמיקות"
    elif stage == "information_provision":
        guidance += "הוראות: תן מידע רלוונטי, השתמש במידע מהמסד נתונים"
    elif stage == "solution_presentation":
        guidance += "הוראות: הצג פתרון מתאים, השתמש במידע על מוצרים/מחירים"
    elif stage == "objection_handling":
        guidance += "הוראות: טפל בחששות, השתמש באמפתיה"
    elif stage == "closing":
        guidance += "הוראות: הצע פעולה הבאה, שאל איך להמשיך"
    elif stage == "handoff":
        guidance += "הוראות: העבר לנציג אנושי, תן מידע רלוונטי"
    
    return guidance
