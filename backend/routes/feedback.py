"""
API routes for feedback and rating system
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from ..instructions.learning_system import (
    analyze_company_feedback,
    generate_learning_instructions,
    get_company_feedback_summary
)

router = APIRouter()

# Pydantic models
class RatingRequest(BaseModel):
    id: int
    messageId: int
    rating: int
    feedback: str
    timestamp: str
    companyId: int
    sessionId: str

class RatingResponse(BaseModel):
    id: int
    messageId: int
    rating: int
    feedback: str
    timestamp: str
    companyId: int
    sessionId: str
    created_at: str

class CompanyInstructionsRequest(BaseModel):
    companyId: int
    instructions: str
    source: str  # 'rating_feedback', 'manual', 'ai_learning'
    priority: int = 1  # 1-5, 5 being highest

class CompanyInstructionsResponse(BaseModel):
    id: int
    companyId: int
    instructions: str
    source: str
    priority: int
    created_at: str
    is_active: bool

# File paths for data storage
RATINGS_FILE = "data/ratings.json"
INSTRUCTIONS_FILE = "data/company_instructions.json"

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs("data", exist_ok=True)

def load_ratings() -> List[dict]:
    """Load ratings from file"""
    ensure_data_directory()
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_ratings(ratings: List[dict]):
    """Save ratings to file"""
    ensure_data_directory()
    with open(RATINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ratings, f, ensure_ascii=False, indent=2)

def load_instructions() -> List[dict]:
    """Load company instructions from file"""
    ensure_data_directory()
    if os.path.exists(INSTRUCTIONS_FILE):
        try:
            with open(INSTRUCTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_instructions(instructions: List[dict]):
    """Save company instructions to file"""
    ensure_data_directory()
    with open(INSTRUCTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(instructions, f, ensure_ascii=False, indent=2)

@router.post("/rating", response_model=RatingResponse)
async def submit_rating(rating: RatingRequest):
    """Submit a rating for a bot response"""
    try:
        ratings = load_ratings()
        
        # Create new rating entry
        new_rating = {
            "id": rating.id,
            "messageId": rating.messageId,
            "rating": rating.rating,
            "feedback": rating.feedback,
            "timestamp": rating.timestamp,
            "companyId": rating.companyId,
            "sessionId": rating.sessionId,
            "created_at": datetime.now().isoformat()
        }
        
        ratings.append(new_rating)
        save_ratings(ratings)
        
        return RatingResponse(**new_rating)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save rating: {str(e)}")

@router.get("/ratings/{company_id}", response_model=List[RatingResponse])
async def get_ratings(company_id: int, limit: int = 100):
    """Get ratings for a specific company"""
    try:
        ratings = load_ratings()
        company_ratings = [r for r in ratings if r["companyId"] == company_id]
        
        # Sort by created_at descending and limit
        company_ratings.sort(key=lambda x: x["created_at"], reverse=True)
        return company_ratings[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load ratings: {str(e)}")

@router.get("/ratings/stats/{company_id}")
async def get_rating_stats(company_id: int):
    """Get rating statistics for a company"""
    try:
        ratings = load_ratings()
        company_ratings = [r for r in ratings if r["companyId"] == company_id]
        
        if not company_ratings:
            return {
                "average_rating": 0,
                "total_ratings": 0,
                "rating_distribution": {str(i): 0 for i in range(1, 6)},
                "recent_feedback": []
            }
        
        # Calculate average rating
        total_rating = sum(r["rating"] for r in company_ratings)
        average_rating = round(total_rating / len(company_ratings), 2)
        
        # Calculate rating distribution
        distribution = {str(i): 0 for i in range(1, 6)}
        for rating in company_ratings:
            distribution[str(rating["rating"])] += 1
        
        # Get recent feedback (last 10 with feedback text)
        recent_feedback = [
            {
                "rating": r["rating"],
                "feedback": r["feedback"],
                "timestamp": r["created_at"]
            }
            for r in company_ratings[-10:]
            if r["feedback"].strip()
        ]
        
        return {
            "average_rating": average_rating,
            "total_ratings": len(company_ratings),
            "rating_distribution": distribution,
            "recent_feedback": recent_feedback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {str(e)}")

@router.post("/instructions", response_model=CompanyInstructionsResponse)
async def save_company_instructions(instructions: CompanyInstructionsRequest):
    """Save company-specific instructions based on feedback"""
    try:
        instructions_list = load_instructions()
        
        # Create new instruction entry
        new_instruction = {
            "id": len(instructions_list) + 1,
            "companyId": instructions.companyId,
            "instructions": instructions.instructions,
            "source": instructions.source,
            "priority": instructions.priority,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        instructions_list.append(new_instruction)
        save_instructions(instructions_list)
        
        return CompanyInstructionsResponse(**new_instruction)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save instructions: {str(e)}")

@router.get("/instructions/{company_id}", response_model=List[CompanyInstructionsResponse])
async def get_company_instructions(company_id: int, active_only: bool = True):
    """Get company-specific instructions"""
    try:
        instructions_list = load_instructions()
        company_instructions = [i for i in instructions_list if i["companyId"] == company_id]
        
        if active_only:
            company_instructions = [i for i in company_instructions if i["is_active"]]
        
        # Sort by priority (highest first) then by created_at
        company_instructions.sort(key=lambda x: (-x["priority"], x["created_at"]), reverse=True)
        
        return company_instructions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load instructions: {str(e)}")

@router.put("/instructions/{instruction_id}/toggle")
async def toggle_instruction(instruction_id: int):
    """Toggle instruction active status"""
    try:
        instructions_list = load_instructions()
        
        for instruction in instructions_list:
            if instruction["id"] == instruction_id:
                instruction["is_active"] = not instruction["is_active"]
                save_instructions(instructions_list)
                return {"message": "Instruction status updated", "is_active": instruction["is_active"]}
        
        raise HTTPException(status_code=404, detail="Instruction not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle instruction: {str(e)}")

@router.get("/feedback/summary/{company_id}")
async def get_feedback_summary(company_id: int):
    """Get comprehensive feedback summary for a company"""
    try:
        ratings = load_ratings()
        instructions = load_instructions()
        
        company_ratings = [r for r in ratings if r["companyId"] == company_id]
        company_instructions = [i for i in instructions if i["companyId"] == company_id and i["is_active"]]
        
        # Calculate rating stats
        if company_ratings:
            avg_rating = sum(r["rating"] for r in company_ratings) / len(company_ratings)
            low_ratings = [r for r in company_ratings if r["rating"] <= 2]
            high_ratings = [r for r in company_ratings if r["rating"] >= 4]
        else:
            avg_rating = 0
            low_ratings = []
            high_ratings = []
        
        # Get common feedback themes
        feedback_texts = [r["feedback"] for r in company_ratings if r["feedback"].strip()]
        
        return {
            "rating_stats": {
                "average_rating": round(avg_rating, 2),
                "total_ratings": len(company_ratings),
                "low_ratings_count": len(low_ratings),
                "high_ratings_count": len(high_ratings)
            },
            "instructions": {
                "total_active": len(company_instructions),
                "by_priority": {
                    str(i): len([inst for inst in company_instructions if inst["priority"] == i])
                    for i in range(1, 6)
                }
            },
            "feedback_insights": {
                "total_feedback": len(feedback_texts),
                "recent_feedback": feedback_texts[-5:] if feedback_texts else []
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@router.get("/feedback/analysis/{company_id}")
async def get_company_analysis(company_id: int):
    """Get detailed feedback analysis for a company"""
    try:
        analysis = analyze_company_feedback(company_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze feedback: {str(e)}")

@router.post("/feedback/learn/{company_id}")
async def generate_learning_for_company(company_id: int):
    """Generate learning instructions for a company based on feedback"""
    try:
        learning_instructions = generate_learning_instructions(company_id)
        return {
            "company_id": company_id,
            "learning_instructions": learning_instructions,
            "message": "Learning instructions generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate learning: {str(e)}")

@router.get("/feedback/company/{company_id}")
async def get_company_feedback(company_id: int):
    """Get all feedback for a specific company"""
    try:
        summary = get_company_feedback_summary(company_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get company feedback: {str(e)}")
