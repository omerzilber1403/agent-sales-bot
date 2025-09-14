from __future__ import annotations
from fastapi import APIRouter, Request, Header
from ..schemas import MessageOut
from ..services.whatsapp_parser import parse_whatsapp_webhook
from ..graph.sales_graph_v2 import create_sales_graph

router = APIRouter(tags=["webhook"])

@router.post("/webhook/whatsapp", response_model=MessageOut)
async def whatsapp_webhook(request: Request, x_signature: str | None = Header(default=None)):
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": await request.body()}
    
    msg_in = parse_whatsapp_webhook(payload)
    
    # Create graph instance
    graph = create_sales_graph()
    
    # Prepare input for the graph
    graph_input = {
        "messages": [{"role": "user", "content": msg_in.text}],
        "customer_context": "",
        "smart_questions": [],
        "extracted_info": {}
    }
    
    try:
        state = graph.invoke(graph_input)
        return MessageOut(
            channel="whatsapp",
            to_user=msg_in.from_user,
            text=state.get("response") or "קיבלתי.",
            handoff=bool(state.get("handoff")),
            handoff_reason=state.get("handoff_reason"),
            tone=state.get("tone", "guide"),
        )
    except Exception as e:
        print(f"Error in webhook: {e}")
        return MessageOut(
            channel="whatsapp",
            to_user=msg_in.from_user,
            text="מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.",
            handoff=False,
            handoff_reason="Technical error",
            tone="apologetic",
        )
