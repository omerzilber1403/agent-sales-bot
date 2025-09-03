from __future__ import annotations
from typing import Tuple, Dict

DEFAULT_HANDOFF_KEYWORDS = ["נציג", "בן אדם", "איש מכירות", "תדבר איתי", "טלפון"]
NO_INVENTION_TERMS_HE = {
    "price": ["מחיר", "כמה", "עלות", "תמחור"],
    "discount": ["הנחה", "קופון", "קוד", "מבצע"],
    "availability": ["זמינות", "מתי אפשר", "יש מלאי", "תאריך פנוי"],
}

def need_handoff(text: str, cfg: Dict) -> Tuple[bool, str | None]:
    text = (text or "").lower()
    kws = (cfg.get("whatsapp", {}) or {}).get("handoff_keywords") or DEFAULT_HANDOFF_KEYWORDS
    for kw in kws:
        if kw.lower() in text:
            return True, "user_requested_human"
    no_invention = (cfg.get("agent", {}) or {}).get("no_invention_fields") or ["price","discount","availability"]
    for field in no_invention:
        for term in NO_INVENTION_TERMS_HE.get(field, []):
            if term.lower() in text:
                return True, f"guardrails_{field}"
    return False, None
