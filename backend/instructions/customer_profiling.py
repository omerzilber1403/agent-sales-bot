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
        מחלץ מידע על הלקוח מההודעה - רק מידע ספציפי וברור
    """
    import re
    
    if not current_profile:
        current_profile = {}
    
    # רק חילוץ מידע ברור וספציפי
    message_lower = message.lower()
    
    # חילוץ שם - רק אם יש ביטוי ברור
    if any(phrase in message_lower for phrase in ['קוראים לי', 'השם שלי', 'אני נקרא']):
        for pattern in AUTO_DETECTION_PATTERNS["name"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match and len(match.group(1).strip()) < 50:  # שם לא יכול להיות ארוך
                current_profile["name"] = match.group(1).strip()
                break
    
    # חילוץ גיל - רק מספרים
    if any(phrase in message_lower for phrase in ['אני בן', 'בן', 'גיל']):
        for pattern in AUTO_DETECTION_PATTERNS["age"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    if 13 <= age <= 120:  # גיל הגיוני
                        current_profile["age"] = age
                        break
                except:
                    continue
    
    # חילוץ מיקום - רק ערים/מקומות
    if any(phrase in message_lower for phrase in ['אני מ', 'גר ב', 'נמצא ב', 'מ']):
        for pattern in AUTO_DETECTION_PATTERNS["location"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # בדיקה שזה לא הודעה ארוכה
                if len(location) < 30 and not any(word in location.lower() for word in ['שיווק', 'עסק', 'לקוח', 'שירות']):
                    current_profile["location"] = location
                    break
    
    # חילוץ תחום עיסוק - רק אם ברור
    if any(phrase in message_lower for phrase in ['אני עובד', 'עובד כ', 'תחום', 'מקצוע']):
        for pattern in AUTO_DETECTION_PATTERNS["occupation"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                occupation = match.group(1).strip()
                if len(occupation) < 50:  # מקצוע לא יכול להיות ארוך
                    current_profile["occupation"] = occupation
                    break
    
    # חילוץ תקציב - רק אם ברור
    if any(phrase in message_lower for phrase in ['תקציב', 'עד', 'בין', '₪', 'שקל']):
        for pattern in AUTO_DETECTION_PATTERNS["budget"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                budget = match.group(1).strip()
                if len(budget) < 30:  # תקציב לא יכול להיות ארוך
                    current_profile["budget"] = budget
                    break
    
    # חילוץ לוח זמנים - רק אם ברור
    if any(phrase in message_lower for phrase in ['עד', 'בתוך', 'לפני', 'מתי']):
        for pattern in AUTO_DETECTION_PATTERNS["timeline"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                timeline = match.group(1).strip()
                if len(timeline) < 30:  # לוח זמנים לא יכול להיות ארוך
                    current_profile["timeline"] = timeline
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
