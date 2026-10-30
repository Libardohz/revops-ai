"""Main FastAPI application entrypoint for RevOpsAI Control API."""

from pathlib import Path
from dotenv import load_dotenv

# Load production or local .env before configuring engines
_env_path = Path("RevOpsAI/.env")
if not _env_path.is_file():
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.is_file():
    load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from RevOpsAI.src.api.routes import router, web_router
from RevOpsAI.src.api.webhooks import webhook_router

app = FastAPI(
    title="RevOpsAI Control API",
    description="API de Control y Aprobación Humana Multi-Tenant",
    version="1.0.0",
)

@app.get("/health", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Liveness probe for Render, cloud monitors, and container orchestrators."""
    return {
        "status": "healthy",
        "service": "RevOpsAI",
        "version": "2.2-pro",
        "environment": "production",
    }

@app.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    """Redirect root requests to the Human-in-the-Loop Kanban dashboard."""
    return RedirectResponse(url="/dashboard", status_code=307)

app.include_router(router)
app.include_router(webhook_router)
app.include_router(web_router)

_static_dir = Path("RevOpsAI/src/web/static")
if not _static_dir.is_dir():
    _static_dir = Path(__file__).resolve().parent.parent / "web" / "static"

if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
