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
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from RevOpsAI.src.api.routes import router, web_router
from RevOpsAI.src.api.webhooks import webhook_router

app = FastAPI(
    title="hzSaaS Enterprise API",
    description="API de Control y Aprobación Humana Multi-Tenant",
    version="1.0.0",
)

_landing_template = Path("RevOpsAI/src/web/templates/landing.html")
if not _landing_template.is_file():
    _landing_template = Path(__file__).resolve().parent.parent / "web" / "templates" / "landing.html"

@app.get("/health", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Liveness probe for Render, cloud monitors, and container orchestrators."""
    return {
        "status": "healthy",
        "service": "hzSaaS-RevOpsAI",
        "version": "2.2-pro",
        "environment": "production",
    }

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_landing() -> HTMLResponse:
    """Serve the official hzSaaS enterprise landing page."""
    if _landing_template.is_file():
        content = _landing_template.read_text(encoding="utf-8")
    else:
        content = "<html><body><h1>hzSaaS Studio</h1></body></html>"
    return HTMLResponse(
        content=content,
        status_code=200,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )

app.include_router(router)
app.include_router(webhook_router)
app.include_router(web_router)

_static_dir = Path("RevOpsAI/src/web/static")
if not _static_dir.is_dir():
    _static_dir = Path(__file__).resolve().parent.parent / "web" / "static"

if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
