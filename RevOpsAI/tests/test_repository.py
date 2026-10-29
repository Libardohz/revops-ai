import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.core.models import Prospect, ProspectState


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_tenant_cannot_read_or_update_other_tenant_prospect(db_session):
    repo_alpha = TenantScopedRepository(session=db_session, tenant_id="tenant_alpha")
    repo_beta = TenantScopedRepository(session=db_session, tenant_id="tenant_beta")

    lead = Prospect(tenant_id="tenant_alpha", name="Clinica Alpha", url="http://alpha.es")
    repo_alpha.save_prospect(lead)

    # Tenant Alpha puede leer su lead
    assert repo_alpha.get_prospect(lead.id) is not None

    # Tenant Beta recibe None al intentar buscar el lead de Alpha
    assert repo_beta.get_prospect(lead.id) is None

    # Tenant Beta no ve el lead en su lista de pendientes
    lead.state = ProspectState.PENDING_APPROVAL
    repo_alpha.save_prospect(lead)
    assert len(repo_alpha.list_pending_approval()) == 1
    assert len(repo_beta.list_pending_approval()) == 0


def test_repository_enforces_tenant_match_on_save(db_session):
    repo_alpha = TenantScopedRepository(session=db_session, tenant_id="tenant_alpha")
    lead_beta = Prospect(tenant_id="tenant_beta", name="Clinica Beta", url="http://beta.es")
    with pytest.raises(PermissionError):
        repo_alpha.save_prospect(lead_beta)


def test_repository_logs_audit_trail(db_session):
    repo_alpha = TenantScopedRepository(session=db_session, tenant_id="tenant_alpha")
    repo_alpha.log_audit(lead_id="lead_123", actor="analyst_1", action="APPROVED", reason="Verified data")
    from RevOpsAI.src.db.models import AuditLogORM

    logs = db_session.query(AuditLogORM).filter_by(tenant_id="tenant_alpha").all()
    assert len(logs) == 1
    assert logs[0].action == "APPROVED"
    assert logs[0].actor == "analyst_1"


def test_repository_requires_tenant_id(db_session):
    with pytest.raises(ValueError):
        TenantScopedRepository(session=db_session, tenant_id="")
