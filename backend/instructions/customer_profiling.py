"""
מערכת פרופיל לקוח - הבנת צרכים עמוקה יותר
"""

# מידע על לקוח
CUSTOMER_PROFILE_FIELDS = {
    "basic_info": {
        "name": "שם",
        "age": "גיל",
        "location": "מיקום",
        "occupation": "תחום עיסוק"
    },
    
    "business_info": {
        "company_size": "גודל החברה",
        "industry": "תחום עיסוק",
        "role": "תפקיד",
        "decision_maker": "מקבל החלטות"
    },
    
    "needs": {
        "primary_goal": "מטרה עיקרית",
        "pain_points": "בעיות/אתגרים",
        "budget_range": "טווח תקציב",
        "timeline": "לוח זמנים",
        "preferences": "העדפות"
    },
    
    "interaction": {
        "communication_style": "סגנון תקשורת",
        "technical_level": "רמה טכנית",
        "urgency": "דחיפות",
        "objections": "התנגדויות"
    }
}

# שאלות למילוי פרופיל
PROFILING_QUESTIONS = {
    "basic_info": [
        "איך קוראים לך?",
        "איזה גיל יש לך?",
        "איפה אתה נמצא?",
        "איזה תחום עיסוק?"
    ],
    
    "business_info": [
        "איזה גודל החברה שלך?",
        "איזה תחום עיסוק?",
        "איזה תפקיד יש לך?",
        "אתה מקבל החלטות?"
    ],
    
    "needs": [
        "מה המטרה העיקרית שלך?",
        "איזה בעיות אתה מנסה לפתור?",
        "איזה תקציב אתה חושב עליו?",
        "מתי אתה רוצה להתחיל?",
        "מה ההעדפות שלך?"
    ],
    
    "interaction": [
        "איך אתה מעדיף לתקשר?",
        "איזה רמה טכנית יש לך?",
        "כמה דחוף זה?",
        "איזה חששות יש לך?"
    ]
}

# זיהוי מידע אוטומטי
AUTO_DETECTION_PATTERNS = {
    "name": [
        r"קוראים לי (.+)",
        r"אני (.+)",
        r"השם שלי (.+)"
    ],
    
    "age": [
        r"אני בן (\d+)",
        r"אני (\d+) שנים",
        r"גיל (\d+)"
    ],
    
    "location": [
        r"אני מ(.+)",
        r"גר ב(.+)",
        r"נמצא ב(.+)"
    ],
    
    "occupation": [
        r"אני (.+)",
        r"עובד כ(.+)",
        r"תחום (.+)"
    ],
    
    "budget": [
        r"תקציב של (.+)",
        r"עד (.+)",
        r"בין (.+) ל(.+)"
    ],
    
    "timeline": [
        r"עד (.+)",
        r"בתוך (.+)",
        r"לפני (.+)"
    ]
}

def extract_customer_info(message: str, current_profile: dict = None) -> dict:
    """
    מחלץ מידע על הלקוח מההודעה
    """
    import re
    
    if not current_profile:
        current_profile = {}
    
    # חילוץ שם
    for pattern in AUTO_DETECTION_PATTERNS["name"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["name"] = match.group(1).strip()
            break
    
    # חילוץ גיל
    for pattern in AUTO_DETECTION_PATTERNS["age"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["age"] = int(match.group(1))
            break
    
    # חילוץ מיקום
    for pattern in AUTO_DETECTION_PATTERNS["location"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["location"] = match.group(1).strip()
            break
    
    # חילוץ תחום עיסוק
    for pattern in AUTO_DETECTION_PATTERNS["occupation"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["occupation"] = match.group(1).strip()
            break
    
    # חילוץ תקציב
    for pattern in AUTO_DETECTION_PATTERNS["budget"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["budget"] = match.group(1).strip()
            break
    
    # חילוץ לוח זמנים
    for pattern in AUTO_DETECTION_PATTERNS["timeline"]:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            current_profile["timeline"] = match.group(1).strip()
            break
    
    return current_profile

def get_next_profiling_question(current_profile: dict, conversation_history: list) -> str:
    """
    מחזיר את השאלה הבאה למילוי הפרופיל
    """
    # בדיקה איזה מידע חסר
    missing_fields = []
    
    for category, fields in CUSTOMER_PROFILE_FIELDS.items():
        for field, description in fields.items():
            if field not in current_profile:
                missing_fields.append((category, field, description))
    
    if not missing_fields:
        return None
    
    # בחירת השאלה הבאה
    category, field, description = missing_fields[0]
    
    if category in PROFILING_QUESTIONS:
        questions = PROFILING_QUESTIONS[category]
        return questions[0] if questions else f"מה {description} שלך?"
    
    return f"מה {description} שלך?"

def should_continue_profiling(current_profile: dict, conversation_length: int) -> bool:
    """
    קובע אם להמשיך לשאול שאלות פרופיל
    """
    # לא לשאול יותר מ-5 שאלות פרופיל
    if conversation_length > 10:
        return False
    
    # לא לשאול אם יש מספיק מידע בסיסי
    basic_info = ["name", "occupation", "primary_goal"]
    if all(field in current_profile for field in basic_info):
        return False
    
    return True

def get_customer_summary(profile: dict) -> str:
    """
    מחזיר סיכום של הפרופיל
    """
    if not profile:
        return "אין מידע על הלקוח"
    
    summary_parts = []
    
    if "name" in profile:
        summary_parts.append(f"שם: {profile['name']}")
    
    if "age" in profile:
        summary_parts.append(f"גיל: {profile['age']}")
    
    if "occupation" in profile:
        summary_parts.append(f"תחום עיסוק: {profile['occupation']}")
    
    if "primary_goal" in profile:
        summary_parts.append(f"מטרה: {profile['primary_goal']}")
    
    if "budget" in profile:
        summary_parts.append(f"תקציב: {profile['budget']}")
    
    if "timeline" in profile:
        summary_parts.append(f"לוח זמנים: {profile['timeline']}")
    
    return " | ".join(summary_parts)
