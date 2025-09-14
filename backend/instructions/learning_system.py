"""
מערכת למידה מהדירוגים והפידבק
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta

# File paths
RATINGS_FILE = "data/ratings.json"
INSTRUCTIONS_FILE = "data/company_instructions.json"

def load_ratings() -> List[dict]:
    """Load ratings from file"""
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def load_instructions() -> List[dict]:
    """Load company instructions from file"""
    if os.path.exists(INSTRUCTIONS_FILE):
        try:
            with open(INSTRUCTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_instructions(instructions: List[dict]):
    """Save company instructions to file"""
    os.makedirs("data", exist_ok=True)
    with open(INSTRUCTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(instructions, f, ensure_ascii=False, indent=2)

def analyze_company_feedback(company_id: int) -> Dict[str, Any]:
    """
    מנתח את הפידבק של חברה ספציפית ויוצר הוראות למידה
    """
    ratings = load_ratings()
    company_ratings = [r for r in ratings if r["companyId"] == company_id]
    
    if not company_ratings:
        return {
            "learning_instructions": [],
            "common_issues": [],
            "improvement_suggestions": []
        }
    
    # ניתוח דירוגים נמוכים (1-3)
    low_ratings = [r for r in company_ratings if r["rating"] <= 3]
    high_ratings = [r for r in company_ratings if r["rating"] >= 4]
    
    # ניתוח פידבק
    feedback_analysis = {
        "pricing_issues": [],
        "tone_issues": [],
        "content_issues": [],
        "handoff_issues": [],
        "general_improvements": []
    }
    
    for rating in company_ratings:
        feedback = rating.get("feedback", "").lower()
        if not feedback:
            continue
            
        # זיהוי נושאים ספציפיים
        if any(word in feedback for word in ["מחיר", "תגיד מחירים", "מחירים"]):
            feedback_analysis["pricing_issues"].append(rating)
        elif any(word in feedback for word in ["טון", "אופן", "דרך", "איך"]):
            feedback_analysis["tone_issues"].append(rating)
        elif any(word in feedback for word in ["תוכן", "מידע", "פרטים", "הסבר"]):
            feedback_analysis["content_issues"].append(rating)
        elif any(word in feedback for word in ["העברה", "נציג", "handoff"]):
            feedback_analysis["handoff_issues"].append(rating)
        else:
            feedback_analysis["general_improvements"].append(rating)
    
    # יצירת הוראות למידה
    learning_instructions = []
    
    # הוראות מחירים
    if feedback_analysis["pricing_issues"]:
        pricing_feedback = [r["feedback"] for r in feedback_analysis["pricing_issues"]]
        learning_instructions.append({
            "type": "pricing",
            "instruction": "אל תגיד מחירים אלא אם הלקוח שואל עליהם במפורש",
            "source": "user_feedback",
            "priority": 4,
            "examples": pricing_feedback[:3]
        })
    
    # הוראות טון
    if feedback_analysis["tone_issues"]:
        tone_feedback = [r["feedback"] for r in feedback_analysis["tone_issues"]]
        learning_instructions.append({
            "type": "tone",
            "instruction": "שפר את הטון והאופן שבו אתה מציג מידע",
            "source": "user_feedback",
            "priority": 3,
            "examples": tone_feedback[:3]
        })
    
    # הוראות תוכן
    if feedback_analysis["content_issues"]:
        content_feedback = [r["feedback"] for r in feedback_analysis["content_issues"]]
        learning_instructions.append({
            "type": "content",
            "instruction": "שפר את התוכן והמידע שאתה מספק",
            "source": "user_feedback",
            "priority": 3,
            "examples": content_feedback[:3]
        })
    
    # הוראות העברה
    if feedback_analysis["handoff_issues"]:
        handoff_feedback = [r["feedback"] for r in feedback_analysis["handoff_issues"]]
        learning_instructions.append({
            "type": "handoff",
            "instruction": "שפר את אופן ההעברה לנציג אנושי",
            "source": "user_feedback",
            "priority": 4,
            "examples": handoff_feedback[:3]
        })
    
    return {
        "learning_instructions": learning_instructions,
        "common_issues": list(feedback_analysis.keys()),
        "improvement_suggestions": [r["feedback"] for r in company_ratings if r["rating"] <= 3],
        "stats": {
            "total_ratings": len(company_ratings),
            "low_ratings": len(low_ratings),
            "high_ratings": len(high_ratings),
            "avg_rating": sum(r["rating"] for r in company_ratings) / len(company_ratings)
        }
    }

def generate_learning_instructions(company_id: int) -> List[Dict[str, Any]]:
    """
    יוצר הוראות למידה ספציפיות לחברה בהתבסס על הפידבק
    """
    analysis = analyze_company_feedback(company_id)
    instructions = load_instructions()
    
    # הוסף הוראות למידה חדשות
    for learning_instruction in analysis["learning_instructions"]:
        new_instruction = {
            "id": len(instructions) + 1,
            "companyId": company_id,
            "instructions": learning_instruction["instruction"],
            "source": "ai_learning",
            "priority": learning_instruction["priority"],
            "type": learning_instruction["type"],
            "examples": learning_instruction.get("examples", []),
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        instructions.append(new_instruction)
    
    save_instructions(instructions)
    return analysis["learning_instructions"]

def get_company_learning_instructions(company_id: int) -> str:
    """
    מחזיר הוראות למידה ספציפיות לחברה כטקסט
    """
    analysis = analyze_company_feedback(company_id)
    
    if not analysis["learning_instructions"]:
        return ""
    
    instructions_text = "\nהוראות למידה מהפידבק של הלקוחות:\n"
    
    for instruction in analysis["learning_instructions"]:
        instructions_text += f"- {instruction['instruction']}\n"
        if instruction.get("examples"):
            instructions_text += f"  דוגמאות מהפידבק: {', '.join(instruction['examples'][:2])}\n"
    
    return instructions_text

def get_company_feedback_summary(company_id: int) -> Dict[str, Any]:
    """
    מחזיר סיכום פידבק לחברה
    """
    analysis = analyze_company_feedback(company_id)
    
    return {
        "company_id": company_id,
        "total_ratings": analysis["stats"]["total_ratings"],
        "average_rating": round(analysis["stats"]["avg_rating"], 2),
        "low_ratings_count": analysis["stats"]["low_ratings"],
        "high_ratings_count": analysis["stats"]["high_ratings"],
        "learning_instructions": analysis["learning_instructions"],
        "common_issues": analysis["common_issues"],
        "improvement_suggestions": analysis["improvement_suggestions"][:5]  # Top 5
    }
