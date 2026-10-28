from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.integrations.web_scraper import ScrapeResult
from RevOpsAI.src.agents import ResearchAgent, ResearchSummary


def test_research_agent_imports_from_agents_package():
    agent = ResearchAgent()
    assert agent is not None


def test_research_agent_detects_signals_and_transitions_state():
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    scrape = ScrapeResult(
        url="https://dentalnorte.es",
        clean_text="Clinica Dental Norte. Especialistas en Implantes Dentales y Ortodoncia. Contacto por whatsapp. No disponemos de cita online.",
        detected_injection=False,
        pii_redacted=False
    )
    agent = ResearchAgent()
    summary = agent.analyze(lead, scrape)

    assert lead.state == ProspectState.RESEARCHING
    assert summary.has_online_booking is False
    assert summary.has_whatsapp is True
    assert "implantes" in [s.lower() for s in summary.detected_services]
    assert "ortodoncia" in [s.lower() for s in summary.detected_services]
    assert len(lead.research_summary) > 0
    assert lead.research_summary == summary.overview


def test_research_agent_detects_online_booking_positive():
    lead = Prospect(tenant_id="t2", name="Clinica Estetica Sur", url="https://esteticasur.es")
    scrape = ScrapeResult(
        url="https://esteticasur.es",
        clean_text="Clinica Estetica Sur. Reserva online tu cita facilmente. Tratamientos de estetica y blanqueamiento.",
        detected_injection=False,
        pii_redacted=False
    )
    agent = ResearchAgent()
    summary = agent.analyze(lead, scrape)

    assert lead.state == ProspectState.RESEARCHING
    assert summary.has_online_booking is True
    assert summary.has_whatsapp is False
    assert "estetica" in summary.detected_services
    assert "blanqueamiento" in summary.detected_services
    assert "Cuenta con cita online." in summary.overview
    assert "Sin canal WhatsApp detectado." in summary.overview


def test_research_agent_detects_signals_with_spanish_diacritics():
    lead = Prospect(tenant_id="t3", name="Clinica Dental Avanzada", url="https://avanzada.es")
    scrape = ScrapeResult(
        url="https://avanzada.es",
        clean_text="Especialistas en estética dental y cirugía. ¡Escríbenos para agendar cita online!",
        detected_injection=False,
        pii_redacted=False,
    )
    agent = ResearchAgent()
    summary = agent.analyze(lead, scrape)

    assert lead.state == ProspectState.RESEARCHING
    assert summary.has_online_booking is True
    assert summary.has_whatsapp is True
    assert "estetica" in summary.detected_services
    assert "cirugia" in summary.detected_services
    assert "Cuenta con cita online." in summary.overview
    assert "Dispone de WhatsApp." in summary.overview
