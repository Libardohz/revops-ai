"""Main FastAPI application entrypoint for hzSaaS Enterprise & RevOpsAI Control API."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load production or local .env before configuring engines (skip during pytest runs)
_env_path = Path("RevOpsAI/.env")
if not _env_path.is_file():
    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.is_file() and "pytest" not in sys.modules:
    load_dotenv(_env_path)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from RevOpsAI.src.api.routes import router, web_router
from RevOpsAI.src.api.webhooks import webhook_router

# Hide Swagger / OpenAPI endpoints in production unless explicitly enabled
_enable_docs = os.getenv("ENABLE_SWAGGER_DOCS", "false").lower() in ("true", "1", "yes")

app = FastAPI(
    title="hzSaaS Enterprise Platform",
    description="Plataforma Empresarial Multi-Tenant",
    version="3.0.0",
    docs_url="/docs" if _enable_docs else None,
    redoc_url="/redoc" if _enable_docs else None,
    openapi_url="/openapi.json" if _enable_docs else None,
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Apply strict enterprise security headers to prevent framing, sniffing, XSS, and data leaks."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


_landing_template = Path("RevOpsAI/src/web/templates/landing.html")
if not _landing_template.is_file():
    _landing_template = Path(__file__).resolve().parent.parent / "web" / "templates" / "landing.html"


@app.get("/health", tags=["Monitoring"], include_in_schema=False)
def health_check() -> dict[str, str]:
    """Liveness probe for cloud monitors and container orchestrators."""
    return {
        "status": "healthy",
        "service": "hzSaaS-Enterprise",
        "version": "3.0-pro",
        "environment": "production",
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_landing() -> HTMLResponse:
    """Serve the official hzSaaS enterprise landing page."""
    if _landing_template.is_file():
        content = _landing_template.read_text(encoding="utf-8")
    else:
        content = "<html><body><h1>hzSaaS Enterprise</h1></body></html>"
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
    app.mount("/images", StaticFiles(directory=str(_static_dir)), name="images")
