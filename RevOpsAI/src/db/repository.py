"""Tenant-scoped repository enforcing multi-tenant isolation boundaries."""
import uuid
from typing import Any
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import ProspectORM, AuditLogORM
from RevOpsAI.src.core.models import Prospect, ProspectState

QUALIFIED_STATES = {
    ProspectState.QUALIFIED.value,
    ProspectState.DRAFTING.value,
    ProspectState.PENDING_APPROVAL.value,
    ProspectState.APPROVED.value,
    ProspectState.SENT.value,
    ProspectState.INTERESTED.value,
    ProspectState.OPT_OUT.value,
}


class TenantScopedRepository:
    """Repository pattern strictly enforcing tenant boundaries across all operations."""

    def __init__(self, session: Session, tenant_id: str):
        if not tenant_id:
            raise ValueError("tenant_id obligatorio para operaciones de repositorio")
        self.session = session
        self.tenant_id = tenant_id

    def save_prospect(self, prospect: Prospect) -> Prospect:
        """Persist or update a prospect, ensuring it belongs to the active tenant."""
        if prospect.tenant_id != self.tenant_id:
            raise PermissionError(
                f"Intento de persistir prospect con tenant_id mismatched: {prospect.tenant_id} != {self.tenant_id}"
            )

        orm = (
            self.session.query(ProspectORM)
            .filter_by(id=prospect.id, tenant_id=self.tenant_id)
            .first()
        )
        if not orm:
            orm = ProspectORM(
                id=prospect.id,
                tenant_id=self.tenant_id,
                name=prospect.name,
                url=prospect.url,
            )
            self.session.add(orm)

        orm.state = prospect.state.value
        orm.score = prospect.score
        orm.research_summary = prospect.research_summary
        orm.draft_message = prospect.draft_message
        orm.is_blacklisted = prospect.is_blacklisted
        self.session.commit()
        return prospect

    def get_prospect(self, lead_id: str) -> Prospect | None:
        """Retrieve a prospect by ID strictly within the active tenant boundary."""
        orm = (
            self.session.query(ProspectORM)
            .filter_by(id=lead_id, tenant_id=self.tenant_id)
            .first()
        )
        if not orm:
            return None
        return Prospect(
            id=orm.id,
            tenant_id=orm.tenant_id,
            name=orm.name,
            url=orm.url,
            state=ProspectState(orm.state),
            score=orm.score,
            research_summary=orm.research_summary,
            draft_message=orm.draft_message,
            is_blacklisted=orm.is_blacklisted,
        )

    def list_pending_approval(self) -> list[Prospect]:
        """List all prospects in PENDING_APPROVAL state for this tenant."""
        return self.list_prospects(state=ProspectState.PENDING_APPROVAL.value)

    def list_prospects(self, state: str | ProspectState | None = None) -> list[Prospect]:
        """List prospects for this tenant, optionally filtered by state."""
        query = self.session.query(ProspectORM).filter_by(tenant_id=self.tenant_id)
        if state is not None:
            state_val = state.value if hasattr(state, "value") else str(state)
            query = query.filter_by(state=state_val)
        records = query.all()
        return [
            Prospect(
                id=r.id,
                tenant_id=r.tenant_id,
                name=r.name,
                url=r.url,
                state=ProspectState(r.state),
                score=r.score,
                research_summary=r.research_summary,
                draft_message=r.draft_message,
                is_blacklisted=r.is_blacklisted,
            )
            for r in records
        ]

    def get_stats(self) -> dict[str, Any]:
        """Compute KPI summary statistics strictly scoped to this tenant."""
        records = (
            self.session.query(ProspectORM)
            .filter_by(tenant_id=self.tenant_id)
            .all()
        )
        total_leads = len(records)
        pending_approval_count = sum(1 for r in records if r.state == ProspectState.PENDING_APPROVAL.value)
        sent_count = sum(1 for r in records if r.state == ProspectState.SENT.value)
        interested_count = sum(1 for r in records if r.state == ProspectState.INTERESTED.value)
        discarded_count = sum(1 for r in records if r.state == ProspectState.DISCARDED.value)
        opt_out_count = sum(1 for r in records if r.state == ProspectState.OPT_OUT.value)
        qualified_count = sum(1 for r in records if r.state in QUALIFIED_STATES)
        qualification_rate = (
            round((qualified_count / total_leads) * 100, 1) if total_leads > 0 else 0.0
        )

        return {
            "total_leads": total_leads,
            "qualified_count": qualified_count,
            "pending_approval_count": pending_approval_count,
            "sent_count": sent_count,
            "interested_count": interested_count,
            "discarded_count": discarded_count,
            "opt_out_count": opt_out_count,
            "qualification_rate": qualification_rate,
        }


    def log_audit(self, lead_id: str, actor: str, action: str, reason: str = "") -> None:
        """Create an audit log entry scoped to this tenant."""
        log_entry = AuditLogORM(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            tenant_id=self.tenant_id,
            lead_id=lead_id,
            actor=actor,
            action=action,
            reason=reason,
        )
        self.session.add(log_entry)
        self.session.commit()

    def list_audit_logs(self, lead_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieve audit log entries scoped to this tenant."""
        query = self.session.query(AuditLogORM).filter_by(tenant_id=self.tenant_id)
        if lead_id:
            query = query.filter_by(lead_id=lead_id)
        records = query.order_by(AuditLogORM.timestamp.desc()).all()
        return [
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "lead_id": r.lead_id,
                "actor": r.actor,
                "action": r.action,
                "reason": r.reason,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in records
        ]
