from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class MemoryStore:
    def __init__(self) -> None:
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.stats: Dict[str, Any] = {"total_messages": 0, "handoffs": 0}

    def log(
        self,
        user_id: str,
        role: str,
        text: str,
        *,
        handoff: bool = False,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "text": text,
        }
        if meta:
            entry["meta"] = meta
        self.conversations.setdefault(user_id, []).append(entry)
        self.stats["total_messages"] += 1
        if handoff:
            self.stats["handoffs"] += 1

store = MemoryStore()
