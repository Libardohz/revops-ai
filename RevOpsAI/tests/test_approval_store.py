import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.approval_store import ApprovalStore


def test_approve_lead_transitions_to_approved():
    store = ApprovalStore()
    lead = Prospect(tenant_id="t1", name="Clinica A", url="http://a.com")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)

    assert len(store.get_pending(tenant_id="t1")) == 1
    approved_lead = store.approve(lead_id=lead.id, tenant_id="t1")
    assert approved_lead.state == ProspectState.APPROVED
    assert lead.state == ProspectState.APPROVED
    assert len(store.get_pending(tenant_id="t1")) == 0


def test_reject_lead_transitions_to_discarded():
    store = ApprovalStore()
    lead = Prospect(tenant_id="t1", name="Clinica B", url="http://b.com")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)

    assert len(store.get_pending(tenant_id="t1")) == 1
    rejected_lead = store.reject(lead_id=lead.id, tenant_id="t1", reason="No encaja con el perfil ideal")
    assert rejected_lead.state == ProspectState.DISCARDED
    assert lead.state == ProspectState.DISCARDED
    assert len(store.get_pending(tenant_id="t1")) == 0


def test_strict_tenant_isolation_in_get_pending():
    store = ApprovalStore()
    lead_t1 = Prospect(tenant_id="t1", name="Clinica 1", url="http://1.com")
    lead_t1.state = ProspectState.PENDING_APPROVAL
    store.add(lead_t1)

    lead_t2 = Prospect(tenant_id="t2", name="Clinica 2", url="http://2.com")
    lead_t2.state = ProspectState.PENDING_APPROVAL
    store.add(lead_t2)

    t1_pending = store.get_pending(tenant_id="t1")
    assert len(t1_pending) == 1
    assert t1_pending[0].id == lead_t1.id

    t2_pending = store.get_pending(tenant_id="t2")
    assert len(t2_pending) == 1
    assert t2_pending[0].id == lead_t2.id

    t3_pending = store.get_pending(tenant_id="t3")
    assert len(t3_pending) == 0


def test_cross_tenant_approval_prevented():
    store = ApprovalStore()
    lead = Prospect(tenant_id="tenant_secret", name="Clinica Privada", url="http://secret.com")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)

    # Attempt to approve or reject with another tenant ID must raise KeyError
    with pytest.raises(KeyError, match="no encontrado para este tenant"):
        store.approve(lead_id=lead.id, tenant_id="tenant_attacker")

    with pytest.raises(KeyError, match="no encontrado para este tenant"):
        store.reject(lead_id=lead.id, tenant_id="tenant_attacker", reason="Malicious reject")

    # The lead should remain untouched in PENDING_APPROVAL
    assert lead.state == ProspectState.PENDING_APPROVAL


def test_nonexistent_lead_raises_key_error():
    store = ApprovalStore()
    with pytest.raises(KeyError, match="no encontrado para este tenant"):
        store.approve(lead_id="nonexistent_id", tenant_id="t1")

    with pytest.raises(KeyError, match="no encontrado para este tenant"):
        store.reject(lead_id="nonexistent_id", tenant_id="t1")


def test_get_pending_only_returns_pending_approval_state():
    store = ApprovalStore()
    lead_ingested = Prospect(tenant_id="t1", name="Lead Ingested", url="http://ingested.com")
    lead_pending = Prospect(tenant_id="t1", name="Lead Pending", url="http://pending.com")
    lead_pending.state = ProspectState.PENDING_APPROVAL

    store.add(lead_ingested)
    store.add(lead_pending)

    pending_list = store.get_pending(tenant_id="t1")
    assert len(pending_list) == 1
    assert pending_list[0].id == lead_pending.id
