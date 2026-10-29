import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base, AuditLogORM
from RevOpsAI.src.db.persistent_approval_store import PersistentApprovalStore
from RevOpsAI.src.core.models import Prospect, ProspectState

@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return lambda: Session(engine)

def test_persistent_approval_store_approves_and_logs_audit(session_factory):
    store = PersistentApprovalStore(session_factory=session_factory)
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dental.es")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)
    
    # 1. Recuperar pendientes desde la base de datos
    pending = store.get_pending(tenant_id="t1")
    assert len(pending) == 1
    assert pending[0].id == lead.id
    
    # 2. Aprobar prospecto
    approved = store.approve(lead_id=lead.id, tenant_id="t1", actor="operador_humano")
    assert approved.state == ProspectState.APPROVED
    assert len(store.get_pending(tenant_id="t1")) == 0
    
    # 3. Verificar registro inmutable en auditoría
    with session_factory() as sess:
        audit = sess.query(AuditLogORM).filter_by(lead_id=lead.id).first()
        assert audit is not None
        assert audit.action == "APPROVE"
        assert audit.actor == "operador_humano"

def test_persistent_approval_store_rejects_and_logs_audit(session_factory):
    store = PersistentApprovalStore(session_factory=session_factory)
    lead = Prospect(tenant_id="t1", name="Clinica Sur", url="http://sur.es")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)
    
    rejected = store.reject(lead_id=lead.id, tenant_id="t1", reason="No responde al perfil", actor="revisor_1")
    assert rejected.state == ProspectState.DISCARDED
    
    with session_factory() as sess:
        audit = sess.query(AuditLogORM).filter_by(lead_id=lead.id).first()
        assert audit is not None
        assert audit.action == "REJECT"
        assert audit.reason == "No responde al perfil"
        assert audit.actor == "revisor_1"

def test_persistent_approval_store_raises_on_not_found(session_factory):
    store = PersistentApprovalStore(session_factory=session_factory)
    with pytest.raises(KeyError):
        store.approve(lead_id="non_existent", tenant_id="t1")
