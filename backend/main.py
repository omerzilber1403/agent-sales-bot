from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes.agent import router as agent_router
from .routes.webhook import router as webhook_router
from .routes.coach import router as coach_router
from .routes.admin import router as admin_router
from .routes.company_dashboard import router as company_dashboard_router
from .routes.dev import router as dev_router
from .routes.feedback import router as feedback_router
from .config import get_settings
from .database.init_db import init_db, seed_all

class JSONUTF8Response(JSONResponse):
    media_type = "application/json; charset=utf-8"

app = FastAPI(title="AGENT Backend", version="0.3", default_response_class=JSONUTF8Response)

# Add CORS middleware — origins configurable via CORS_ORIGINS env var
_settings = get_settings()
_origins = [o.strip() for o in _settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=("*" not in _origins),  # credentials can't be used with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Initialize DB tables and seed demo companies on every startup."""
    init_db()
    seed_all()

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
app.include_router(feedback_router, prefix="/api/v1/feedback", tags=["feedback"])
