"""REST API routes for RevOpsAI prospect processing and Human-in-the-Loop review."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from RevOpsAI.src.core.models import Prospect
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.pipeline import PipelineOrchestrator, PipelineResult

router = APIRouter(prefix="/api/v1")

# Dependencias singleton en memoria para el runtime de la API
_default_config_path = Path("RevOpsAI/config/sectors/clinicas.yaml")
if not _default_config_path.is_file():
    _default_config_path = Path(__file__).resolve().parent.parent.parent / "config" / "sectors" / "clinicas.yaml"

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
    return orch.process_prospect(lead, req.html_content)


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
            return store.approve(lead_id=req.lead_id, tenant_id=req.tenant_id)
        elif action_upper == "REJECT":
            return store.reject(lead_id=req.lead_id, tenant_id=req.tenant_id, reason=req.reason)
        else:
            raise HTTPException(status_code=400, detail="Acción inválida. Use APPROVE o REJECT")
    except KeyError:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado para este tenant")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=f"Transición no permitida: {exc}")
