"""Tests for Lead Scoring Agent in RevOpsAI pipeline."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.agents.audit_agent import CommercialAuditResult
from RevOpsAI.src.agents.scoring_agent import ScoringAgent, ScoringResult


def test_scoring_agent_imports_from_agents_package():
    """Verify ScoringAgent and ScoringResult can be imported from agents root."""
    from RevOpsAI.src.agents import ScoringAgent as AgentExported
    from RevOpsAI.src.agents import ScoringResult as ResultExported

    assert AgentExported is not None
    assert ResultExported is not None


def test_scoring_qualifies_lead_with_high_gap_and_transitions_state():
    """Verify that a lead with significant digital gaps qualifies and transitions to QUALIFIED."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    lead.state = ProspectState.AUDITING

    audit = CommercialAuditResult(
        commercial_gaps=["Falta cita online", "Sin WhatsApp"],
        growth_opportunities=["Automatizar agenda"],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = ScoringAgent(config)
    result = agent.evaluate(lead, audit, estimated_size_score=70, reputation_score=80)

    assert result.is_qualified is True
    assert lead.state == ProspectState.QUALIFIED
    assert lead.score >= config.scoring.min_qualification_score
    assert result.score == lead.score
    assert "digital_gap_score" in result.breakdown
    assert "reputation_score" in result.breakdown
    assert "size_score" in result.breakdown


def test_scoring_discards_lead_with_low_score():
    """Verify that a lead failing to reach min_qualification_score transitions to DISCARDED."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Pequeña", url="https://clinicapq.es")
    lead.state = ProspectState.AUDITING

    audit = CommercialAuditResult(
        commercial_gaps=[],
        growth_opportunities=[],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = ScoringAgent(config)
    # With 0 gaps/opportunities, reputation=20, size=20:
    # gap_score = 0.0 * 0.5 = 0
    # rep = 20 * 0.3 = 6
    # size = 20 * 0.2 = 4
    # final_score = 10 < 65
    result = agent.evaluate(lead, audit, estimated_size_score=20.0, reputation_score=20.0)

    assert result.is_qualified is False
    assert lead.state == ProspectState.DISCARDED
    assert lead.score < config.scoring.min_qualification_score
    assert result.score == lead.score


def test_scoring_evaluates_lead_already_in_scoring_state():
    """Verify evaluate works if lead has already transitioned to SCORING state."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Central", url="https://central.es")
    lead.state = ProspectState.SCORING

    audit = CommercialAuditResult(
        commercial_gaps=["Falta cita online", "Sin WhatsApp"],
        growth_opportunities=["Automatizar agenda"],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = ScoringAgent(config)
    result = agent.evaluate(lead, audit, estimated_size_score=70, reputation_score=80)

    assert result.is_qualified is True
    assert lead.state == ProspectState.QUALIFIED


def test_scoring_invalid_initial_state_raises_error():
    """Verify evaluate raises ValueError if lead is in an invalid state like INGESTED."""
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Invalida", url="https://invalida.es")
    lead.state = ProspectState.INGESTED

    audit = CommercialAuditResult(
        commercial_gaps=["Falta cita online"],
        growth_opportunities=[],
        disclaimer=config.compliance.required_disclaimer,
    )

    agent = ScoringAgent(config)
    with pytest.raises(ValueError, match="Transición inválida"):
        agent.evaluate(lead, audit)
