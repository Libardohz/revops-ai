"""Tests for DispatchAgent and Reply Handler in RevOpsAI pipeline."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.agents.dispatch_agent import DispatchAgent, ReplyIntent


def test_dispatch_agent_imports_from_agents_package():
    """Verify DispatchAgent and ReplyIntent are properly exported."""
    from RevOpsAI.src.agents import DispatchAgent as AgentExported, ReplyIntent as IntentExported

    assert AgentExported is not None
    assert IntentExported is not None


def test_dispatch_message_successful_transition():
    """Verify dispatch_message transitions APPROVED prospect to SENT."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.APPROVED

    result = agent.dispatch_message(lead)

    assert result is True
    assert lead.state == ProspectState.SENT


def test_dispatch_message_fails_if_not_approved():
    """Verify dispatch_message returns False if prospect is not in APPROVED state."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.INGESTED

    result = agent.dispatch_message(lead)

    assert result is False
    assert lead.state == ProspectState.INGESTED


def test_dispatch_message_fails_if_blacklisted():
    """Verify dispatch_message returns False if prospect is blacklisted even if state is APPROVED."""
    agent = DispatchAgent()
    lead = Prospect(
        tenant_id="t1",
        name="Clinica Dental Norte",
        url="http://dentalnorte.es",
        is_blacklisted=True,
    )
    lead.state = ProspectState.APPROVED

    result = agent.dispatch_message(lead)

    assert result is False
    assert lead.state == ProspectState.APPROVED


def test_handle_incoming_reply_opt_out():
    """Verify strict compliance: opt-out phrases trigger blacklisting and transition to OPT_OUT."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.APPROVED
    assert agent.dispatch_message(lead) is True

    opt_out_messages = [
        "Por favor no me contacten mas, denme de baja",
        "Solicito la baja inmediata de su base de datos",
        "Borren mis datos por favor",
        "No me interesa en lo absoluto",
        "Esto es spam no deseado",
        "Favor desuscribir de esta lista",
    ]

    for msg in opt_out_messages:
        # Reset prospect for each test phrase
        test_lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
        test_lead.state = ProspectState.SENT

        intent = agent.handle_incoming_reply(test_lead, msg)

        assert intent == ReplyIntent.OPT_OUT
        assert test_lead.state == ProspectState.OPT_OUT
        assert test_lead.is_blacklisted is True


def test_handle_incoming_reply_interested():
    """Verify commercial interest intent detection without modifying opt-out status."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.SENT

    interested_messages = [
        "Me interesa su propuesta, ¿podemos coordinar una reunión?",
        "Hola, agendemos una llamada para ver detalles",
        "Estoy interesado en la solución",
        "Hablemos la próxima semana",
        "¿Cuál es el precio del servicio?",
        "¿Qué disponibilidad de agenda tienen?",
    ]

    for msg in interested_messages:
        intent = agent.handle_incoming_reply(lead, msg)

        assert intent == ReplyIntent.INTERESTED
        assert lead.state == ProspectState.SENT
        assert lead.is_blacklisted is False


def test_handle_incoming_reply_deferred():
    """Verify deferred intent detection when prospect requests later contact."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.SENT

    deferred_messages = [
        "Ahora no es buen momento, contáctenme más adelante",
        "Escríbannos el próximo mes por favor",
        "En otro momento lo revisamos",
    ]

    for msg in deferred_messages:
        intent = agent.handle_incoming_reply(lead, msg)

        assert intent == ReplyIntent.DEFERRED
        assert lead.state == ProspectState.SENT
        assert lead.is_blacklisted is False


def test_handle_incoming_reply_unknown():
    """Verify unclassified reply returns UNKNOWN intent."""
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
    lead.state = ProspectState.SENT

    intent = agent.handle_incoming_reply(lead, "Hola buenas tardes recibido")

    assert intent == ReplyIntent.UNKNOWN
    assert lead.state == ProspectState.SENT
    assert lead.is_blacklisted is False


def test_opt_out_compliance_variations_and_compound_phrases():
    """Verify specific compliance opt-out variations and compound deferred phrases."""
    agent = DispatchAgent()

    # Opt-out variations
    for msg in ["No estoy interesado", "No nos interesa", "no tenemos interes"]:
        lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
        lead.state = ProspectState.SENT
        intent = agent.handle_incoming_reply(lead, msg)
        assert intent == ReplyIntent.OPT_OUT
        assert lead.is_blacklisted is True
        assert lead.state == ProspectState.OPT_OUT

    # Compound phrases that must classify as DEFERRED rather than INTERESTED
    for msg in ["Hablemos más adelante", "Me interesa el próximo mes"]:
        lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dentalnorte.es")
        lead.state = ProspectState.SENT
        intent = agent.handle_incoming_reply(lead, msg)
        assert intent == ReplyIntent.DEFERRED
        assert lead.is_blacklisted is False
        assert lead.state == ProspectState.SENT
