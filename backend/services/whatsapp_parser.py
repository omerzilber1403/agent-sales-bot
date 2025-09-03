from __future__ import annotations
from typing import Any, Optional, Dict
from ..schemas import MessageIn

def extract_text(body: Dict[str, Any]) -> Optional[str]:
    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        msgs = value.get("messages") or []
        if msgs:
            msg = msgs[0]
            if "text" in msg and "body" in msg["text"]:
                return msg["text"]["body"]
    except Exception:
        return None
    return None

def parse_whatsapp_webhook(body: Dict[str, Any]) -> MessageIn:
    text = extract_text(body) or ""
    try:
        from_user = body["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    except Exception:
        from_user = "unknown"
    return MessageIn(
        channel="whatsapp",
        from_user=from_user,
        text=text,
        metadata={"raw": body},
    )
