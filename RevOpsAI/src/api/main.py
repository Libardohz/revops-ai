"""Main FastAPI application entrypoint for RevOpsAI Control API."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from RevOpsAI.src.api.routes import router, web_router
from RevOpsAI.src.api.webhooks import webhook_router

app = FastAPI(
    title="RevOpsAI Control API",
    description="API de Control y Aprobación Humana Multi-Tenant",
    version="1.0.0",
)

app.include_router(router)
app.include_router(webhook_router)
app.include_router(web_router)

_static_dir = Path("RevOpsAI/src/web/static")
if not _static_dir.is_dir():
    _static_dir = Path(__file__).resolve().parent.parent / "web" / "static"

if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
