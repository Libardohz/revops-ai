"""Commercial audit and microdiagnosis agent for RevOpsAI pipeline.

Analyzes commercial and operational digital gaps from research findings
while strictly enforcing sector legal compliance boundaries (e.g. no medical diagnoses).
"""

import unicodedata
from pydantic import BaseModel, Field
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import SectorConfig
from RevOpsAI.src.agents.research_agent import ResearchSummary


def _normalize_text(text: str) -> str:
    """Normalize text: strip accents, lower-case, and replace underscores with spaces."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return normalized.lower().replace("_", " ")


class CommercialAuditResult(BaseModel):
    """Output schema for commercial audit findings."""

    commercial_gaps: list[str] = Field(
        default_factory=list,
        description="Identified operational and digital gaps."
    )
    growth_opportunities: list[str] = Field(
        default_factory=list,
        description="Actionable commercial growth opportunities."
    )
    disclaimer: str = Field(
        ...,
        description="Mandatory legal disclaimer for the sector."
    )


class CommercialAuditAgent:
    """Agent responsible for identifying operational digital gaps and opportunities."""

    def __init__(self, config: SectorConfig) -> None:
        """Initialize the auditor with sector configuration."""
        self.config = config

    def audit(self, lead: Prospect, summary: ResearchSummary) -> CommercialAuditResult:
        """Perform a commercial gap analysis and transition prospect state to AUDITING.

        Args:
            lead: The prospect under review (must be in RESEARCHING state).
            summary: Synthesized research signals for the prospect.

        Returns:
            CommercialAuditResult: Detected gaps, opportunities, and required disclaimer.

        Raises:
            ValueError: If compliance boundary is violated or state transition is invalid.
        """
        gaps: list[str] = []
        opportunities: list[str] = []

        if not summary.has_online_booking:
            gaps.append("Falta agendamiento directo de citas online")
            opportunities.append("Integración de reserva de consultas automatizada")

        if not summary.has_whatsapp:
            gaps.append("Ausencia de canal conversacional ágil en web")
            opportunities.append("Habilitación de canal de mensajería directa para presupuestos")

        if len(summary.detected_services) >= 2:
            opportunities.append(
                f"Campaña de reactivación enfocada en {', '.join(summary.detected_services[:2])}"
            )

        # Strict compliance enforcement: verify no forbidden topic appears in gaps or opportunities
        all_findings = gaps + opportunities
        for finding in all_findings:
            normalized_finding = _normalize_text(finding)
            for forbidden in self.config.compliance.strictly_forbidden_topics:
                normalized_forbidden = _normalize_text(forbidden)
                if normalized_forbidden in normalized_finding:
                    raise ValueError(f"Violación de compliance en auditoría: {forbidden}")

        # State transition to AUDITING
        lead.transition_to(ProspectState.AUDITING)

        return CommercialAuditResult(
            commercial_gaps=gaps,
            growth_opportunities=opportunities,
            disclaimer=self.config.compliance.required_disclaimer,
        )
