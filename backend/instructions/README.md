# הוראות מערכת המכירות
# Sales System Instructions

## מבנה התיקייה
## Directory Structure

```
backend/instructions/
├── __init__.py                    # ייבוא כל ההוראות
├── general_instructions.py        # הוראות כלליות לכל החברות
├── b2c_instructions.py           # הוראות ספציפיות ל-B2C
├── b2b_instructions.py           # הוראות ספציפיות ל-B2B
├── handoff_instructions.py       # הוראות להעברה לנציג אנושי
├── template_instructions.py      # הוראות לטיפול בתבניות הודעות
└── README.md                     # קובץ זה
```

## שימוש בהוראות
## Using the Instructions

### ייבוא הוראות
### Importing Instructions

```python
from backend.instructions import (
    GENERAL_INSTRUCTIONS,
    B2C_SPECIFIC_INSTRUCTIONS,
    B2B_SPECIFIC_INSTRUCTIONS,
    should_handoff,
    match_template
)
```

### דוגמאות שימוש
### Usage Examples

#### בדיקת העברה לנציג
#### Checking for Handoff

```python
from backend.instructions import should_handoff

message = "אני רוצה לדבר עם מנהל"
needs_handoff = should_handoff(message)  # True
```

#### התאמת תבניות הודעות
#### Matching Message Templates

```python
from backend.instructions import match_template, get_template_response

message = "שלום"
template = match_template(message)  # "greeting"
response = get_template_response(template, company_data)
```

## הוראות זמינות
## Available Instructions

### הוראות כלליות (general_instructions.py)
### General Instructions

- `GENERAL_INSTRUCTIONS` - הוראות בסיסיות לכל החברות
- `MESSAGE_QUALITY_INSTRUCTIONS` - הוראות איכות הודעות
- `SALES_STRATEGY_INSTRUCTIONS` - אסטרטגיית מכירות
- `IMPORTANT_RULES` - כללים חשובים
- `OPENING_MESSAGE_RULE` - כלל הודעות פתיחה

### הוראות B2C (b2c_instructions.py)
### B2C Instructions

- `B2C_SPECIFIC_INSTRUCTIONS` - הוראות ספציפיות ל-B2C
- `B2C_QUESTION_GUIDELINES` - הנחיות שאלות ל-B2C

### הוראות B2B (b2b_instructions.py)
### B2B Instructions

- `B2B_SPECIFIC_INSTRUCTIONS` - הוראות ספציפיות ל-B2B
- `B2B_QUESTION_GUIDELINES` - הנחיות שאלות ל-B2B

### הוראות העברה (handoff_instructions.py)
### Handoff Instructions

- `HANDOFF_TRIGGERS` - רשימת טריגרים להעברה
- `SALES_QUESTIONS` - שאלות מכירות (לא דורשות העברה)
- `HANDOFF_RESPONSE` - תגובת העברה
- `should_handoff(message)` - פונקציה לבדיקת העברה

### הוראות תבניות (template_instructions.py)
### Template Instructions

- `TEMPLATE_PATTERNS` - תבניות הודעות
- `get_template_response(template, company_data)` - קבלת תגובה לתבנית
- `match_template(message)` - התאמת הודעה לתבנית

## יתרונות המערכת החדשה
## Benefits of the New System

1. **ארגון טוב יותר** - כל סוג הוראות בקובץ נפרד
2. **קלות תחזוקה** - שינוי הוראות במקום אחד
3. **קריאות משופרת** - קוד נקי ומאורגן
4. **גמישות** - הוספת הוראות חדשות בקלות
5. **שימוש חוזר** - הוראות זמינות בכל המערכת

## הוספת הוראות חדשות
## Adding New Instructions

1. צור קובץ חדש בתיקיית `instructions/`
2. הוסף את ההוראות שלך
3. עדכן את `__init__.py` לייבא את ההוראות החדשות
4. השתמש בהוראות בקוד שלך

## דוגמאות מתקדמות
## Advanced Examples

### יצירת הוראות מותאמות אישית
### Creating Custom Instructions

```python
# ב-sales_graph_v2.py
from backend.instructions import GENERAL_INSTRUCTIONS, B2C_SPECIFIC_INSTRUCTIONS

custom_instructions = """
הוראות מותאמות לחברה:
- תמיד תזכיר את שם החברה
- השתמש בטון חם וידידותי
"""

system_prompt = f"""{custom_instructions}

{GENERAL_INSTRUCTIONS}

{B2C_SPECIFIC_INSTRUCTIONS}

תגובה להודעת הלקוח: {message}"""
```

### שילוב עם נתוני חברה
### Integration with Company Data

```python
def build_system_prompt(company_data, business_type):
    base_instructions = GENERAL_INSTRUCTIONS
    
    if business_type == "B2C":
        specific_instructions = B2C_SPECIFIC_INSTRUCTIONS
    else:
        specific_instructions = B2B_SPECIFIC_INSTRUCTIONS
    
    return f"""{base_instructions}
    
{specific_instructions}

מידע על החברה: {company_data.get('name', '')}
"""
```
