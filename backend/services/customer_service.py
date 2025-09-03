from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from datetime import datetime, date
import json

class CustomerService:
    """Service for customer management and profiling"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_customer_profile(self, user_id: int) -> Dict[str, Any]:
        """Get complete customer profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get conversation history
        conversations = self.db.query(Conversation).filter(Conversation.user_id == user_id).all()
        total_messages = 0
        if conversations:
            for conv in conversations:
                messages = self.db.query(Message).filter(Message.conversation_id == conv.id).count()
                total_messages += messages
        
        return {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "age": user.age,
            "gender": user.gender,
            "location": user.location,
            "occupation": user.occupation,
            "interests": user.interests or [],
            "budget_range": user.budget_range,
            "family_status": user.family_status,
            "preferred_contact": user.preferred_contact,
            "first_contact_date": user.first_contact_date.isoformat() if user.first_contact_date else None,
            "last_contact_date": user.last_contact_date.isoformat() if user.last_contact_date else None,
            "total_interactions": user.total_interactions,
            "conversion_stage": user.conversion_stage,
            "preferences": user.preferences or {},
            "notes": user.notes,
            "reason_for_interest": user.reason_for_interest,
            "specific_need": user.specific_need,
            "total_conversations": len(conversations),
            "total_messages": total_messages
        }
    
    def update_customer_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update customer profile with new information"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Update basic fields
        if "name" in profile_data:
            user.name = profile_data["name"]
        if "phone" in profile_data:
            user.phone = profile_data["phone"]
        if "email" in profile_data:
            user.email = profile_data["email"]
        if "age" in profile_data:
            user.age = profile_data["age"]
        if "gender" in profile_data:
            user.gender = profile_data["gender"]
        if "location" in profile_data:
            user.location = profile_data["location"]
        if "occupation" in profile_data:
            user.occupation = profile_data["occupation"]
        if "interests" in profile_data:
            user.interests = profile_data["interests"]
        if "budget_range" in profile_data:
            user.budget_range = profile_data["budget_range"]
        if "family_status" in profile_data:
            user.family_status = profile_data["family_status"]
        if "preferred_contact" in profile_data:
            user.preferred_contact = profile_data["preferred_contact"]
        if "preferences" in profile_data:
            user.preferences = profile_data["preferences"]
        if "notes" in profile_data:
            user.notes = profile_data["notes"]
        if "reason_for_interest" in profile_data:
            user.reason_for_interest = profile_data["reason_for_interest"]
        if "specific_need" in profile_data:
            user.specific_need = profile_data["specific_need"]
        
        # Update tracking fields
        user.last_contact_date = date.today()
        user.total_interactions += 1
        
        # Set first contact date if not set
        if not user.first_contact_date:
            user.first_contact_date = date.today()
        
        self.db.commit()
        return True
    
    def extract_customer_info_from_message(self, user_id: int, message_content: str) -> Dict[str, Any]:
        """Extract customer information from message content using simple patterns"""
        extracted_info = {}
        
        # Simple pattern matching for common information
        import re
        
        # Age patterns
        age_patterns = [
            r'אני בן (\d+)',
            r'אני בת (\d+)',
            r'גיל (\d+)',
            r'(\d+) שנים',
            r'^(\d+)$',  # Just a number
            r'הגיל שלי (\d+)',
            r'אני (\d+)'
        ]
        for pattern in age_patterns:
            match = re.search(pattern, message_content)
            if match:
                extracted_info["age"] = int(match.group(1))
                break
        
        # Location patterns
        location_patterns = [
            r'אני מ([\u0590-\u05FF\w\s]+)',
            r'גר ב([\u0590-\u05FF\w\s]+)',
            r'מתגורר ב([\u0590-\u05FF\w\s]+)'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, message_content)
            if match:
                extracted_info["location"] = match.group(1).strip()
                break
        
        # Reason for interest patterns - why they came to us
        reason_patterns = [
            r'רוצה ללמוד ([^,\n]+)',  # "רוצה ללמוד לגלוש"
            r'מעוניין ב([^,\n]+)',    # "מעוניין בגלישה"
            r'רוצה ([^,\n]+)',        # "רוצה לגלוש"
            r'צריך ([^,\n]+)',        # "צריך שיעורים"
            r'מחפש ([^,\n]+)',        # "מחפש שיעורי גלישה"
            r'בא לי ([^,\n]+)',       # "בא לי לגלוש"
            r'אני רוצה ([^,\n]+)',    # "אני רוצה ללמוד"
            r'אני מעוניין ([^,\n]+)', # "אני מעוניין בגלישה"
        ]
        for pattern in reason_patterns:
            match = re.search(pattern, message_content)
            if match:
                extracted_info["reason_for_interest"] = match.group(1).strip()
                break
        
        # Occupation patterns - improved to catch "מנהל מועדון גלישה"
        occupation_patterns = [
            r'אני מנהל ([^,\n]+)',  # "אני מנהל מועדון גלישה"
            r'אני בעל ([^,\n]+)',   # "אני בעל עסק"
            r'עובד כ([^,\n]+)',     # "עובד כמנהל"
            r'תפקיד ([^,\n]+)',     # "תפקיד מנהל"
            r'יש לי ([^,\n]+)',     # "יש לי עסק"
            r'אני ([^,\n]+)'        # "אני מנהל"
        ]
        for pattern in occupation_patterns:
            match = re.search(pattern, message_content)
            if match:
                occupation = match.group(1).strip()
                # Filter out common words that aren't occupations, but allow business types
                if (len(occupation) > 2 and 
                    not any(word in occupation.lower() for word in ['אני', 'רוצה', 'צריך', 'עזרה', 'עושה', 'לכם', 'השירותים', 'להציע']) and
                    not occupation.startswith('חברה')):
                    extracted_info["occupation"] = occupation
                    print(f"DEBUG: Extracted occupation: {occupation}")
                break
        
        # Budget indicators
        budget_indicators = {
            'low': ['זול', 'מחיר נמוך', 'תקציב מוגבל', 'לא יקר'],
            'medium': ['מחיר סביר', 'תקציב בינוני', 'איכות טובה'],
            'high': ['איכות גבוהה', 'הכי טוב', 'לא משנה המחיר', 'פרימיום']
        }
        
        for budget_level, keywords in budget_indicators.items():
            if any(keyword in message_content for keyword in keywords):
                extracted_info["budget_range"] = budget_level
                break
        
        # Family status
        family_indicators = {
            'single': ['רווק', 'רווקה', 'בלי ילדים'],
            'married': ['נשוי', 'נשואה', 'זוג'],
            'parent': ['אבא', 'אמא', 'הורה', 'ילד', 'ילדים']
        }
        
        for status, keywords in family_indicators.items():
            if any(keyword in message_content for keyword in keywords):
                extracted_info["family_status"] = status
                break
        
        # Update customer profile with extracted information
        if extracted_info:
            self.update_customer_profile(user_id, extracted_info)
        
        return extracted_info
    
    def get_smart_questions(self, user_id: int, company_data: dict = None) -> List[str]:
        """DISABLED: Let the LLM handle questions naturally instead of forced questions"""
        # Return empty list - let the LLM ask questions naturally based on context
        return []
    
    def get_personalized_response_context(self, user_id: int) -> str:
        """Get personalized context for the AI to generate better responses"""
        profile = self.get_customer_profile(user_id)
        
        context_parts = []
        
        if profile.get("name"):
            context_parts.append(f"הלקוח קוראים לו {profile['name']}")
        
        if profile.get("age"):
            if profile["age"] < 25:
                context_parts.append("זה לקוח צעיר")
            elif profile["age"] < 50:
                context_parts.append("זה לקוח בגיל העבודה")
            else:
                context_parts.append("זה לקוח מבוגר")
        
        if profile.get("budget_range"):
            if profile["budget_range"] == "low":
                context_parts.append("הלקוח מתעניין במחירים נמוכים")
            elif profile["budget_range"] == "high":
                context_parts.append("הלקוח מתעניין באיכות גבוהה, לא משנה המחיר")
        
        if profile.get("family_status"):
            if profile["family_status"] == "parent":
                context_parts.append("הלקוח הוא הורה, חשוב לו על המשפחה")
        
        if profile.get("occupation"):
            context_parts.append(f"הלקוח עובד כ-{profile['occupation']}")
        
        if profile.get("location"):
            context_parts.append(f"הלקוח נמצא ב-{profile['location']}")
        
        if profile.get("conversion_stage"):
            if profile["conversion_stage"] == "new":
                context_parts.append("זה לקוח חדש, צריך לבנות אמון")
            elif profile["conversion_stage"] == "interested":
                context_parts.append("הלקוח מתעניין, צריך לחזק את העניין")
            elif profile["conversion_stage"] == "qualified":
                context_parts.append("הלקוח מוכן לרכישה, צריך לסגור עסקה")
        
        return ". ".join(context_parts) if context_parts else "זה לקוח חדש"

def get_customer_service(db: Session) -> CustomerService:
    """Get customer service instance"""
    return CustomerService(db)
