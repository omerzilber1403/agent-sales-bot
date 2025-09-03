from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes.agent import router as agent_router
from .routes.webhook import router as webhook_router
from .routes.coach import router as coach_router
from .routes.admin import router as admin_router
from .routes.company_dashboard import router as company_dashboard_router
from .routes.dev import router as dev_router
from .config import get_settings

class JSONUTF8Response(JSONResponse):
    media_type = "application/json; charset=utf-8"

app = FastAPI(title="AGENT Backend", version="0.3", default_response_class=JSONUTF8Response)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    s = get_settings()
    if s.LLM_PROVIDER == "openai":
        model = s.OPENAI_MODEL or "unset"
    return {"status": "ok", "provider": s.LLM_PROVIDER, "model": model}

app.include_router(agent_router)
app.include_router(webhook_router)
app.include_router(coach_router)
app.include_router(admin_router)
app.include_router(company_dashboard_router)
app.include_router(dev_router)

