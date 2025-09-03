from typing import Any, Dict, List
from fastapi import APIRouter

# ננסה להשתמש במחסן הזיכרון האמיתי אם קיים; אחרת פולבק ריק
try:
    from ..services.memory import store  # מצופה אובייקט עם conversations, stats
except Exception:
    class _FallbackStore:
        conversations: Dict[str, List[Dict[str, Any]]] = {}
        stats: Dict[str, Any] = {"total_messages": 0, "handoffs": 0}
    store = _FallbackStore()

router = APIRouter(prefix="/api/v1/coach", tags=["coach"])

@router.get("/conversations")
def list_conversations():
    return {
        "conversations": [
            {"user_id": user_id, "count": len(msgs)}
            for user_id, msgs in store.conversations.items()
        ]
    }

@router.get("/conversations/{user_id}")
def get_conversation(user_id: str):
    print(f"DEBUG: Coach route called for user_id: {user_id}")  # Debug info
    print(f"DEBUG: Available conversations: {list(store.conversations.keys())}")  # Debug info
    msgs = store.conversations.get(user_id, [])
    print(f"DEBUG: Found {len(msgs)} messages for user {user_id}")  # Debug info
    return {"user_id": user_id, "messages": msgs}

@router.get("/stats")
def stats():
    return store.stats
