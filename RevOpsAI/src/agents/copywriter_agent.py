"""Consultative copywriter agent for RevOpsAI pipeline.

Crafts customized outreach proposals based on commercial audit findings
and sector compliance rules, transitioning qualified leads to drafting and
registering them directly in the human-in-the-loop (HITL) approval store.
"""

import unicodedata
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import SectorConfig
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.agents.audit_agent import CommercialAuditResult


def _normalize_text(text: str) -> str:
    """Normalize text: strip accents, lower-case, and replace underscores with spaces."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return normalized.lower().replace("_", " ")


class CopywriterAgent:
    """Agent responsible for drafting consultative proposals and submitting to HITL review."""

    def __init__(self, config: SectorConfig, approval_store: ApprovalStore) -> None:
        """Initialize CopywriterAgent with sector configuration and approval store.

        Args:
            config: Sector configuration containing compliance disclaimers and settings.
            approval_store: Human-in-the-loop approval store for review tray tracking.
        """
        self.config = config
        self.approval_store = approval_store

    def generate_proposal(self, lead: Prospect, audit: CommercialAuditResult) -> str:
        """Generate a consultative proposal, transition state, and register for HITL approval.

        Args:
            lead: Prospect in QUALIFIED state.
            audit: Commercial audit result containing identified gaps and disclaimer.

        Returns:
            str: Generated outreach message proposal.

        Raises:
            ValueError: If the prospect is not in a valid state to transition to DRAFTING.
        """
        lead.transition_to(ProspectState.DRAFTING)

        main_gap = (
            audit.commercial_gaps[0]
            if audit.commercial_gaps
            else "optimización operativa"
        )
        formatted_gap = main_gap[0].lower() + main_gap[1:] if main_gap else main_gap

        draft = (
            f"Estimado equipo directivo de {lead.name},\n\n"
            f"Al analizar los puntos de contacto digitales de su sede web, detectamos una oportunidad directa: {formatted_gap}.\n"
            f"Implementar un canal de seguimiento y reserva ágil permite recuperar pacientes con presupuestos no confirmados.\n\n"
            f"¿Tendrían disponibilidad para una breve llamada técnica de 10 minutos la próxima semana?\n\n"
            f"---\n"
            f"{self.config.compliance.required_disclaimer}"
        )

        # Defense-in-depth: verify no strictly forbidden topic exists in proposal draft
        norm_draft = _normalize_text(draft)
        for forbidden in self.config.compliance.strictly_forbidden_topics:
            norm_forbidden = _normalize_text(forbidden)
            if norm_forbidden in norm_draft:
                raise ValueError(f"Violación de compliance en propuesta: {forbidden}")

        lead.draft_message = draft
        lead.transition_to(ProspectState.PENDING_APPROVAL)
        self.approval_store.add(lead)

        return draft
