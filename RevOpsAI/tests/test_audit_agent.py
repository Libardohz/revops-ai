"""Tests for CommercialAuditAgent in RevOpsAI pipeline."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import load_sector_config, SectorConfig, ComplianceConfig, ResearchConfig, ScoringConfig
from RevOpsAI.src.agents.research_agent import ResearchSummary
from RevOpsAI.src.agents.audit_agent import CommercialAuditAgent, CommercialAuditResult


def test_audit_agent_imports_from_agents_package():
    from RevOpsAI.src.agents import CommercialAuditAgent as AgentClass, CommercialAuditResult as ResultClass
    assert AgentClass is not None
    assert ResultClass is not None


def test_audit_identifies_commercial_gap_without_medical_diagnosis():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    lead.state = ProspectState.RESEARCHING

    summary = ResearchSummary(
        has_online_booking=False,
        has_whatsapp=True,
        detected_services=["implantes", "ortodoncia"],
        overview="Sin cita online"
    )

    auditor = CommercialAuditAgent(config)
    audit = auditor.audit(lead, summary)

    assert lead.state == ProspectState.AUDITING
    assert "Falta agendamiento directo de citas online" in audit.commercial_gaps
    assert "Integración de reserva de consultas automatizada" in audit.growth_opportunities
    assert "Campaña de reactivación enfocada en implantes, ortodoncia" in audit.growth_opportunities
    assert audit.disclaimer == config.compliance.required_disclaimer

    # Verify that no forbidden medical statements are emitted
    for forbidden in config.compliance.strictly_forbidden_topics:
        assert forbidden not in " ".join(audit.commercial_gaps).lower()
        assert forbidden not in " ".join(audit.growth_opportunities).lower()


def test_audit_detects_missing_whatsapp_channel():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    lead.state = ProspectState.RESEARCHING

    summary = ResearchSummary(
        has_online_booking=True,
        has_whatsapp=False,
        detected_services=["limpieza"],
        overview="Sin canal WhatsApp"
    )

    auditor = CommercialAuditAgent(config)
    audit = auditor.audit(lead, summary)

    assert lead.state == ProspectState.AUDITING
    assert "Ausencia de canal conversacional ágil en web" in audit.commercial_gaps
    assert "Habilitación de canal de mensajería directa para presupuestos" in audit.growth_opportunities
    assert "Falta agendamiento directo de citas online" not in audit.commercial_gaps


def test_audit_raises_value_error_on_compliance_violation():
    # Setup config where forbidden topic is deliberately triggered
    forbidden_config = SectorConfig(
        sector_id="test_sector",
        compliance=ComplianceConfig(
            strictly_forbidden_topics=["reserva de consultas"],
            required_disclaimer="Disclaimer"
        ),
        research=ResearchConfig(
            primary_sources=["web"],
            signals_to_detect=["booking"]
        ),
        scoring=ScoringConfig(
            weights={"gap": 1.0},
            min_qualification_score=50
        )
    )

    lead = Prospect(tenant_id="t1", name="Clinica Test", url="https://test.es")
    lead.state = ProspectState.RESEARCHING

    summary = ResearchSummary(
        has_online_booking=False,
        has_whatsapp=True,
        detected_services=[],
        overview="Overview"
    )

    auditor = CommercialAuditAgent(forbidden_config)
    with pytest.raises(ValueError, match="Violación de compliance en auditoría"):
        auditor.audit(lead, summary)


def test_audit_raises_compliance_violation_for_snake_case_and_accents():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Test", url="https://test.es")
    lead.state = ProspectState.RESEARCHING

    summary = ResearchSummary(
        has_online_booking=False,
        has_whatsapp=True,
        detected_services=["diagnósticos médicos específicos", "consulta general"],
        overview="Overview"
    )

    auditor = CommercialAuditAgent(config)
    with pytest.raises(ValueError, match="Violación de compliance en auditoría: diagnosticos_medicos_especificos"):
        auditor.audit(lead, summary)


def test_audit_fails_if_lead_not_in_researching_state():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    # lead.state defaults to INGESTED

    summary = ResearchSummary(
        has_online_booking=False,
        has_whatsapp=True,
        detected_services=[],
        overview=""
    )

    auditor = CommercialAuditAgent(config)
    with pytest.raises(ValueError, match="Transición inválida"):
        auditor.audit(lead, summary)
