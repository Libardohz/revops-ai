"""REST API routes for RevOpsAI prospect processing and Human-in-the-Loop review."""

from pathlib import Path
from typing import Any, Generator
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from RevOpsAI.src.core.models import Prospect
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.pipeline import PipelineOrchestrator, PipelineResult
from RevOpsAI.src.api.webhooks import webhook_router
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.db.session import get_engine, init_db, get_session_factory

router = APIRouter(prefix="/api/v1")
router.include_router(webhook_router)

# Dependencias singleton en memoria para el runtime de la API
_default_config_path = Path("RevOpsAI/config/sectors/clinicas.yaml")
if not _default_config_path.is_file():
    _default_config_path = Path(__file__).resolve().parent.parent.parent / "config" / "sectors" / "clinicas.yaml"

_template_path = Path("RevOpsAI/src/web/templates/dashboard.html")
if not _template_path.is_file():
    _template_path = Path(__file__).resolve().parent.parent / "web" / "templates" / "dashboard.html"

_static_path = Path("RevOpsAI/src/web/static")
if not _static_path.is_dir():
    _static_path = Path(__file__).resolve().parent.parent / "web" / "static"

web_router = APIRouter()
if _static_path.is_dir():
    router.mount("/static", StaticFiles(directory=str(_static_path)), name="static_api")
    web_router.mount("/static", StaticFiles(directory=str(_static_path)), name="static_web")


@web_router.get("/dashboard", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard() -> HTMLResponse:
    """Serve the Human-in-the-Loop Kanban dashboard frontend."""
    if _template_path.is_file():
        content = _template_path.read_text(encoding="utf-8")
    else:
        content = "<html><body><h1>RevOps AI Dashboard</h1></body></html>"
    return HTMLResponse(
        content=content,
        status_code=200,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )

config = load_sector_config(_default_config_path)
shared_store = ApprovalStore()
orchestrator = PipelineOrchestrator(config=config, approval_store=shared_store)


def get_approval_store() -> ApprovalStore:
    """Dependency provider for ApprovalStore."""
    return shared_store


def get_orchestrator() -> PipelineOrchestrator:
    """Dependency provider for PipelineOrchestrator."""
    return orchestrator


class IngestRequest(BaseModel):
    """Payload for prospect ingestion and automated pipeline processing."""

    tenant_id: str
    name: str
    url: str
    html_content: str


class AuditUrlRequest(BaseModel):
    """Payload for live website audit triggered by URL."""

    tenant_id: str
    name: str
    url: str


def fetch_remote_html(url: str, timeout: int = 15) -> str:
    """Safely fetch HTML content from a remote clinic website with strict timeout and headers."""
    import urllib.request
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL inválida: Debe comenzar con http:// o https://")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read(2_000_000)  # Max 2MB limit
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()
            return raw.decode(charset, errors="ignore")
    except Exception as exc:
        raise RuntimeError(f"Fallo al conectar con el sitio web: {exc}")


class ApprovalActionRequest(BaseModel):
    """Payload for Human-in-the-Loop approval or rejection."""

    tenant_id: str
    lead_id: str
    action: str  # "APPROVE" o "REJECT"
    reason: str = ""


@router.post("/prospects/process", response_model=PipelineResult)
def process_prospect(
    req: IngestRequest,
    orch: PipelineOrchestrator = Depends(get_orchestrator),
) -> PipelineResult:
    """Ingest and run the multi-agent enrichment pipeline for a prospect."""
    lead = Prospect(tenant_id=req.tenant_id, name=req.name, url=req.url)
    result = orch.process_prospect(lead, req.html_content)
    try:
        factory = get_default_session_factory()
        with factory() as session:
            repo = TenantScopedRepository(session=session, tenant_id=req.tenant_id)
            repo.save_prospect(result.prospect)
    except Exception:
        pass
    return result


@router.post("/prospects/audit-url", response_model=PipelineResult)
def audit_prospect_url(
    req: AuditUrlRequest,
    orch: PipelineOrchestrator = Depends(get_orchestrator),
) -> PipelineResult:
    """Perform real-time remote fetch and end-to-end multi-agent pipeline audit."""
    try:
        html = fetch_remote_html(req.url)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as net_err:
        raise HTTPException(status_code=502, detail=f"No se pudo descargar el sitio web: {net_err}")

    lead = Prospect(tenant_id=req.tenant_id, name=req.name, url=req.url)
    result = orch.process_prospect(lead, html)
    try:
        factory = get_default_session_factory()
        with factory() as session:
            repo = TenantScopedRepository(session=session, tenant_id=req.tenant_id)
            repo.save_prospect(result.prospect)
            repo.log_audit(
                lead_id=result.prospect.id,
                actor="system_pipeline",
                action="AUDIT_URL",
                reason=f"Auditoría en vivo completada. Score: {result.prospect.score}/100",
            )
    except Exception:
        pass
    return result


@router.get("/approval/pending", response_model=list[Prospect])
def get_pending(
    tenant_id: str = Query(..., description="ID del tenant a filtrar"),
    store: ApprovalStore = Depends(get_approval_store),
) -> list[Prospect]:
    """Retrieve pending approval prospects strictly isolated by tenant."""
    return store.get_pending(tenant_id=tenant_id)


@router.post("/approval/action", response_model=Prospect)
def handle_action(
    req: ApprovalActionRequest,
    store: ApprovalStore = Depends(get_approval_store),
) -> Prospect:
    """Approve or reject a prospect pending review, enforcing tenant isolation."""
    try:
        action_upper = req.action.upper()
        if action_upper == "APPROVE":
            lead = store.approve(lead_id=req.lead_id, tenant_id=req.tenant_id)
        elif action_upper == "REJECT":
            lead = store.reject(lead_id=req.lead_id, tenant_id=req.tenant_id, reason=req.reason)
        else:
            raise HTTPException(status_code=400, detail="Acción inválida. Use APPROVE o REJECT")

        try:
            factory = get_default_session_factory()
            with factory() as session:
                repo = TenantScopedRepository(session=session, tenant_id=req.tenant_id)
                repo.save_prospect(lead)
                repo.log_audit(lead_id=lead.id, actor="human_operator", action=action_upper, reason=req.reason)
        except Exception:
            pass

        return lead
    except KeyError:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado para este tenant")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=f"Transición no permitida: {exc}")


_default_engine = None
_default_session_factory = None


def get_default_session_factory():
    """Retrieve or initialize the default database session factory."""
    global _default_engine, _default_session_factory
    if _default_session_factory is None:
        _default_engine = get_engine()
        init_db(_default_engine)
        _default_session_factory = get_session_factory(_default_engine)
    return _default_session_factory


def get_repository(
    tenant_id: str = Query(..., description="ID del tenant a filtrar")
) -> Generator[TenantScopedRepository, None, None]:
    """Dependency provider yielding a tenant-scoped database repository."""
    factory = get_default_session_factory()
    with factory() as session:
        yield TenantScopedRepository(session=session, tenant_id=tenant_id)


@router.get("/dashboard/stats", response_model=dict[str, Any])
def get_dashboard_stats(
    tenant_id: str = Query(..., description="ID del tenant a filtrar"),
    repo: TenantScopedRepository = Depends(get_repository),
) -> dict[str, Any]:
    """Retrieve aggregated RevOps KPI statistics for the tenant."""
    return repo.get_stats()


@router.get("/dashboard/leads", response_model=list[dict[str, Any]])
def get_dashboard_leads(
    tenant_id: str = Query(..., description="ID del tenant a filtrar"),
    state: str | None = Query(None, description="Filtro opcional por estado de ciclo de vida"),
    repo: TenantScopedRepository = Depends(get_repository),
) -> list[dict[str, Any]]:
    """Retrieve prospects strictly isolated by tenant, optionally filtered by state."""
    leads = repo.list_prospects(state=state)
    return [lead.model_dump() for lead in leads]


@router.get("/audit/logs", response_model=list[dict[str, Any]])
def get_audit_logs(
    tenant_id: str = Query(..., description="ID del tenant a filtrar"),
    lead_id: str | None = Query(None, description="Filtro opcional por ID de prospecto"),
    repo: TenantScopedRepository = Depends(get_repository),
) -> list[dict[str, Any]]:
    """Retrieve historical audit trails strictly scoped to the tenant."""
    return repo.list_audit_logs(lead_id=lead_id)

