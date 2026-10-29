from collections.abc import Callable
from sqlalchemy.orm import Session
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.db.repository import TenantScopedRepository


class PersistentApprovalStore:
    """Persistent storage backed by relational database with tenant isolation and audit trails."""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def add(self, lead: Prospect) -> None:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=lead.tenant_id)
            repo.save_prospect(lead)

    def get_pending(self, tenant_id: str) -> list[Prospect]:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            return repo.list_pending_approval()

    def approve(self, lead_id: str, tenant_id: str, actor: str = "human_operator") -> Prospect:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            lead = repo.get_prospect(lead_id)
            if not lead:
                raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
            lead.transition_to(ProspectState.APPROVED)
            repo.save_prospect(lead)
            repo.log_audit(lead_id=lead_id, actor=actor, action="APPROVE", reason="")
            return lead

    def reject(self, lead_id: str, tenant_id: str, reason: str = "", actor: str = "human_operator") -> Prospect:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            lead = repo.get_prospect(lead_id)
            if not lead:
                raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
            lead.transition_to(ProspectState.DISCARDED)
            repo.save_prospect(lead)
            repo.log_audit(lead_id=lead_id, actor=actor, action="REJECT", reason=reason)
            return lead
