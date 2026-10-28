"""Tests for Copywriter Agent and HITL Approval Store Integration in RevOpsAI pipeline."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.agents.audit_agent import CommercialAuditResult
from RevOpsAI.src.agents.copywriter_agent import CopywriterAgent


def test_copywriter_agent_imports_from_agents_package():
    """Verify CopywriterAgent can be imported directly from RevOpsAI.src.agents."""
    from RevOpsAI.src.agents import CopywriterAgent as AgentExported

    assert AgentExported is not None


def test_copywriter_generates_draft_and_registers_in_approval_store():
    """Verify consultative proposal generation, disclaimer inclusion, and HITL registration."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    lead.state = ProspectState.QUALIFIED

    audit = CommercialAuditResult(
        commercial_gaps=["Falta agendamiento directo de citas online"],
        growth_opportunities=["Integración de reserva automatizada"],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = CopywriterAgent(config, store)
    draft = agent.generate_proposal(lead, audit)

    assert lead.state == ProspectState.PENDING_APPROVAL
    assert "Clinica Dental Norte" in lead.draft_message
    assert config.compliance.required_disclaimer in lead.draft_message
    assert draft == lead.draft_message
    assert len(store.get_pending(tenant_id="t1")) == 1
    assert store.get_pending(tenant_id="t1")[0].id == lead.id


def test_copywriter_fallback_when_no_gaps():
    """Verify proposal generation when audit has empty commercial gaps."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    lead = Prospect(tenant_id="t1", name="Clinica Sur", url="https://clinicasur.es")
    lead.state = ProspectState.QUALIFIED

    audit = CommercialAuditResult(
        commercial_gaps=[],
        growth_opportunities=[],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = CopywriterAgent(config, store)
    draft = agent.generate_proposal(lead, audit)

    assert lead.state == ProspectState.PENDING_APPROVAL
    assert "optimización operativa" in draft
    assert config.compliance.required_disclaimer in draft
    assert len(store.get_pending(tenant_id="t1")) == 1


def test_copywriter_invalid_initial_state_raises_error():
    """Verify that a lead not in QUALIFIED state raises ValueError."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    lead = Prospect(tenant_id="t1", name="Clinica Ingested", url="https://clinicaingested.es")
    # lead.state is INGESTED by default

    audit = CommercialAuditResult(
        commercial_gaps=["Falta agendamiento directo de citas online"],
        growth_opportunities=[],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = CopywriterAgent(config, store)
    with pytest.raises(ValueError):
        agent.generate_proposal(lead, audit)
