"""Research Agent module for analyzing prospect web scrape content and extracting business signals."""

import re
import unicodedata
from pydantic import BaseModel
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.integrations.web_scraper import ScrapeResult


def _normalize_text(text: str) -> str:
    """Normalize text: strip accents and lower-case for robust keyword and pattern matching."""
    return (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
    )


class ResearchSummary(BaseModel):
    """Structured summary of operational business signals extracted from a prospect's digital presence."""

    has_online_booking: bool
    has_whatsapp: bool
    detected_services: list[str]
    overview: str


class ResearchAgent:
    """Agent that analyzes clean web scrape text, extracts operational signals, and advances prospect state."""

    SERVICES_KEYWORDS = [
        "implantes",
        "ortodoncia",
        "estetica",
        "blanqueamiento",
        "cirugia",
        "pediatria",
        "endodoncia",
        "fisioterapia",
        "diseno de sonrisa",
        "rehabilitacion oral",
        "periodoncia",
        "armonizacion facial",
        "alineadores",
        "bichectomia",
        "protesis",
    ]

    HIGH_TICKET_KEYWORDS = [
        "implantes",
        "diseno de sonrisa",
        "cirugia",
        "ortodoncia",
        "alineadores",
        "armonizacion",
        "rehabilitacion oral",
    ]

    def analyze(self, lead: Prospect, scrape: ScrapeResult) -> ResearchSummary:
        """Analyze prospect website text, update prospect state, and generate research summary.

        Args:
            lead: Prospect instance currently in INGESTED state.
            scrape: ScrapeResult containing clean text from the prospect's website.

        Returns:
            ResearchSummary with detected operational signals and overview text.
        """
        normalized_text = _normalize_text(scrape.clean_text)

        # Detección heurística de señales operativas avanzadas
        has_online_booking = bool(
            re.search(r"cita\s+online|reserva\s+online|agendar\s+cita|agenda\s+tu\s+cita|reserva\s+tu\s+cita|agendamiento", normalized_text)
            and not re.search(r"no\s+(disponemos|contamos)\s+de\s+cita\s+online", normalized_text)
        )
        has_whatsapp = bool(re.search(r"whatsapp|chat|escribenos|wa\.me", normalized_text))

        # Detección de brechas comerciales críticas
        has_pricing_or_quotes = bool(re.search(r"precios|tarifas|cotiza|presupuesto|financiamiento", normalized_text))
        has_habeas_data = bool(re.search(r"politica\s+de\s+privacidad|habeas\s+data|tratamiento\s+de\s+datos|ley\s+1581", normalized_text))

        services = [kw for kw in self.SERVICES_KEYWORDS if kw in normalized_text]
        high_ticket_services = [kw for kw in self.HIGH_TICKET_KEYWORDS if kw in normalized_text]

        overview = f"Clínica con {len(services)} servicios clave detectados. "
        overview += "Dispone de WhatsApp. " if has_whatsapp else "Sin canal WhatsApp detectado. "
        overview += "Cuenta con cita online." if has_online_booking else "Carece de sistema de cita online."
        if high_ticket_services:
            overview += f" Tratamientos High-Ticket: {', '.join(high_ticket_services[:2])}."

        lead.transition_to(ProspectState.RESEARCHING)
        lead.research_summary = overview

        return ResearchSummary(
            has_online_booking=has_online_booking,
            has_whatsapp=has_whatsapp,
            detected_services=services,
            overview=overview,
        )
