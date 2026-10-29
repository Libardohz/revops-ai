"""Main FastAPI application entrypoint for RevOpsAI Control API."""

from fastapi import FastAPI
from RevOpsAI.src.api.routes import router
from RevOpsAI.src.api.webhooks import webhook_router

app = FastAPI(
    title="RevOpsAI Control API",
    description="API de Control y Aprobación Humana Multi-Tenant",
    version="1.0.0",
)

app.include_router(router)
app.include_router(webhook_router)
