"""Tenant-scoped repository enforcing multi-tenant isolation boundaries."""
import uuid
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import ProspectORM, AuditLogORM
from RevOpsAI.src.core.models import Prospect, ProspectState


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
        records = (
            self.session.query(ProspectORM)
            .filter_by(
                tenant_id=self.tenant_id,
                state=ProspectState.PENDING_APPROVAL.value,
            )
            .all()
        )
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
