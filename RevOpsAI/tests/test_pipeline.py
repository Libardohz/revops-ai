"""Integration tests for the PipelineOrchestrator."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.pipeline import PipelineOrchestrator, PipelineResult


def test_pipeline_runs_full_lifecycle_for_qualifying_clinic():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    orchestrator = PipelineOrchestrator(config=config, approval_store=store)

    lead = Prospect(tenant_id="tenant_dental", name="Clinica Dental Norte", url="https://dentalnorte.es")
    html_content = """
    <html><body>
      <h1>Clinica Dental Norte</h1>
      <p>Expertos en implantes dentales y estetica. Contactanos por WhatsApp.</p>
    </body></html>
    """

    result = orchestrator.process_prospect(lead, html_content)

    assert isinstance(result, PipelineResult)
    assert result.prospect.state == ProspectState.PENDING_APPROVAL
    assert result.scoring is not None
    assert result.scoring.is_qualified is True
    assert len(store.get_pending(tenant_id="tenant_dental")) == 1
    assert "Clinica Dental Norte" in result.prospect.draft_message


def test_pipeline_discards_blacklisted_prospect_immediately():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    orchestrator = PipelineOrchestrator(config=config, approval_store=store)

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clinica Bloqueada",
        url="https://bloqueada.es",
        is_blacklisted=True,
    )
    html_content = "<html><body><h1>Clinica Bloqueada</h1></body></html>"

    result = orchestrator.process_prospect(lead, html_content)

    assert result.prospect.state == ProspectState.DISCARDED
    assert result.audit is None
    assert result.scoring is None
    assert len(store.get_pending(tenant_id="tenant_dental")) == 0


def test_pipeline_handles_unqualified_prospect():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    orchestrator = PipelineOrchestrator(config=config, approval_store=store)

    # A clinic with booking and whatsapp has no digital gaps (gap_score=0).
    # With default size/rep, score = 0*0.5 + 70*0.3 + 50*0.2 = 31 < 60 threshold
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clinica Digitalizada",
        url="https://digitalizada.es",
    )
    html_content = """
    <html><body>
      <h1>Clinica Digitalizada</h1>
      <p>Cita online disponible de inmediato. Contacto por WhatsApp para presupuestos.</p>
    </body></html>
    """

    result = orchestrator.process_prospect(lead, html_content)

    assert result.prospect.state == ProspectState.DISCARDED
    assert result.scoring is not None
    assert result.scoring.is_qualified is False
    assert len(store.get_pending(tenant_id="tenant_dental")) == 0
    assert result.prospect.draft_message == ""
