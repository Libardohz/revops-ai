"""Tests for dashboard analytics and filtered lead query endpoints."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.api.routes import get_dashboard_stats, get_dashboard_leads


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_dashboard_stats_calculation(db_session):
    repo = TenantScopedRepository(session=db_session, tenant_id="t_stats")

    # 1 lead pending
    l1 = Prospect(tenant_id="t_stats", name="Clinica A", url="http://a.es", score=80, state=ProspectState.PENDING_APPROVAL)
    # 1 lead interested
    l2 = Prospect(tenant_id="t_stats", name="Clinica B", url="http://b.es", score=90, state=ProspectState.INTERESTED)
    # 1 lead discarded
    l3 = Prospect(tenant_id="t_stats", name="Clinica C", url="http://c.es", score=40, state=ProspectState.DISCARDED)

    repo.save_prospect(l1)
    repo.save_prospect(l2)
    repo.save_prospect(l3)

    stats = repo.get_stats()
    assert stats["total_leads"] == 3
    assert stats["pending_approval_count"] == 1
    assert stats["interested_count"] == 1
    assert stats["discarded_count"] == 1
    assert stats["qualified_count"] == 2
    assert stats["qualification_rate"] == 66.7


def test_dashboard_leads_filtered_by_state(db_session):
    repo = TenantScopedRepository(session=db_session, tenant_id="t_filter")
    l1 = Prospect(tenant_id="t_filter", name="Clinica 1", url="http://1.es", state=ProspectState.PENDING_APPROVAL)
    l2 = Prospect(tenant_id="t_filter", name="Clinica 2", url="http://2.es", state=ProspectState.SENT)
    repo.save_prospect(l1)
    repo.save_prospect(l2)

    pending = repo.list_prospects(state=ProspectState.PENDING_APPROVAL.value)
    assert len(pending) == 1
    assert pending[0].name == "Clinica 1"

    all_leads = repo.list_prospects()
    assert len(all_leads) == 2


def test_api_endpoints_return_stats_and_leads(db_session):
    repo = TenantScopedRepository(session=db_session, tenant_id="t_api")
    l1 = Prospect(tenant_id="t_api", name="Clinica Alpha", url="http://alpha.es", score=85, state=ProspectState.PENDING_APPROVAL)
    repo.save_prospect(l1)

    stats = get_dashboard_stats(tenant_id="t_api", repo=repo)
    assert stats["total_leads"] == 1
    assert stats["pending_approval_count"] == 1

    leads = get_dashboard_leads(tenant_id="t_api", state="PENDING_APPROVAL", repo=repo)
    assert len(leads) == 1
    assert leads[0]["name"] == "Clinica Alpha"
