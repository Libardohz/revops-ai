"""In-memory Human-in-the-Loop review tray with strict tenant isolation."""

from RevOpsAI.src.core.models import Prospect, ProspectState


class ApprovalStore:
    """Store for managing prospects awaiting human review and approval."""

    def __init__(self) -> None:
        self._leads: dict[str, Prospect] = {}

    def add(self, lead: Prospect) -> None:
        """Add a prospect to the approval store.

        Args:
            lead: Prospect instance to track.
        """
        self._leads[lead.id] = lead

    def get_pending(self, tenant_id: str) -> list[Prospect]:
        """Retrieve all prospects in PENDING_APPROVAL state for a specific tenant.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            List of Prospect instances pending approval for this tenant.
        """
        return [
            lead for lead in self._leads.values()
            if lead.tenant_id == tenant_id and lead.state == ProspectState.PENDING_APPROVAL
        ]

    def approve(self, lead_id: str, tenant_id: str) -> Prospect:
        """Approve a prospect, transitioning its state to APPROVED.

        Args:
            lead_id: Identifier of the prospect.
            tenant_id: Identifier of the tenant owning the prospect.

        Returns:
            The updated Prospect instance.

        Raises:
            KeyError: If the prospect does not exist or does not belong to the given tenant.
        """
        lead = self._leads.get(lead_id)
        if not lead or lead.tenant_id != tenant_id:
            raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
        lead.transition_to(ProspectState.APPROVED)
        return lead

    def reject(self, lead_id: str, tenant_id: str, reason: str = "") -> Prospect:
        """Reject a prospect, transitioning its state to DISCARDED.

        Args:
            lead_id: Identifier of the prospect.
            tenant_id: Identifier of the tenant owning the prospect.
            reason: Optional explanation for rejection.

        Returns:
            The updated Prospect instance.

        Raises:
            KeyError: If the prospect does not exist or does not belong to the given tenant.
        """
        lead = self._leads.get(lead_id)
        if not lead or lead.tenant_id != tenant_id:
            raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
        lead.transition_to(ProspectState.DISCARDED)
        return lead
