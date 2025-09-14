"""
הוראות לטיפול בתבניות הודעות
Template handling instructions
"""

TEMPLATE_PATTERNS = {
    "greeting": ["שלום", "היי", "בוקר טוב", "ערב טוב"],
    "thanks": ["תודה", "תדה", "תודה רבה"],
    "goodbye": ["ביי", "להתראות", "נתראה", "ביי ביי"]
}

def get_template_response(template_name: str, company_data: dict = None) -> str:
    """
    קבל תגובה מתאימה לתבנית
    """
    if template_name == "greeting":
        if company_data:
            company_name = company_data.get("name", "החברה")
            return f"שלום! איך אני יכול לעזור לך?"
        else:
            return "שלום! איך אני יכול לעזור לך?"
    elif template_name == "thanks":
        return "בשמחה! יש עוד משהו שאני יכול לעזור בו?"
    elif template_name == "goodbye":
        return "להתראות! היה נעים לעזור לך."
    else:
        return None

def match_template(message_content: str) -> str:
    """
    התאם הודעה לתבנית ידועה
    """
    message_lower = message_content.lower()
    
    for template_name, keywords in TEMPLATE_PATTERNS.items():
        if any(keyword in message_lower for keyword in keywords):
            return template_name
    
    return None
