"""Integration tests for the RevOpsAI Dashboard & Kanban lifecycle."""
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.db.persistent_approval_store import PersistentApprovalStore
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.demo import seed_dashboard_database


def test_end_to_end_dashboard_approval_lifecycle():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = lambda: Session(engine)

    store = PersistentApprovalStore(session_factory=session_factory)

    # 1. Ingest lead
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Provenza",
        url="https://dentalprovenza.es",
        score=85,
        research_summary="Sin WhatsApp ni cita online",
        draft_message="Estimado equipo de Clínica Dental Provenza...",
        state=ProspectState.PENDING_APPROVAL,
    )
    store.add(lead)

    # 2. Check pending
    pending = store.get_pending("tenant_dental")
    assert len(pending) == 1
    assert pending[0].id == lead.id

    # 3. Approve via store
    approved = store.approve(lead_id=lead.id, tenant_id="tenant_dental", actor="Dr. Juan Martinez")
    assert approved.state == ProspectState.APPROVED

    # 4. Verify no longer pending
    assert len(store.get_pending("tenant_dental")) == 0

    # 5. Check stats in repository
    with session_factory() as session:
        repo = TenantScopedRepository(session, "tenant_dental")
        stats = repo.get_stats()
        assert stats["pending_approval_count"] == 0
        assert stats["qualified_count"] == 1


def test_seed_dashboard_database(tmp_path: Path):
    test_db = tmp_path / "test_revops.db"
    seeded = seed_dashboard_database(db_url=f"sqlite:///{test_db}")

    assert len(seeded) >= 4
    states = {p.state for p in seeded}
    assert ProspectState.PENDING_APPROVAL in states
    assert ProspectState.SENT in states
    assert ProspectState.INTERESTED in states
    assert ProspectState.DISCARDED in states
    assert all(p.tenant_id == "tenant_clinicas_madrid" for p in seeded)
