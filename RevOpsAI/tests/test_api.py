"""Tests for FastAPI REST API endpoints with multi-tenant isolation."""

import pytest
from fastapi import HTTPException
from RevOpsAI.src.api.routes import (
    process_prospect,
    get_pending,
    handle_action,
    IngestRequest,
    ApprovalActionRequest,
    get_orchestrator,
    get_approval_store,
)


def test_api_ingest_and_pending_approval_flow():
    req = IngestRequest(
        tenant_id="tenant_api_test",
        name="Clinica Estetica Centro",
        url="https://esteticacentro.es",
        html_content="<html><body><h1>Clinica Estetica Centro</h1><p>Implantes y estetica dental. Contacto por whatsapp.</p></body></html>",
    )
    orch = get_orchestrator()
    store = get_approval_store()

    # 1. Ingesta
    result = process_prospect(req, orch=orch)
    assert result.prospect.state == "PENDING_APPROVAL"
    lead_id = result.prospect.id

    # 2. Consultar bandeja de pendientes
    pending_list = get_pending(tenant_id="tenant_api_test", store=store)
    assert len(pending_list) >= 1
    assert any(p.id == lead_id for p in pending_list)

    # 3. Aprobar prospecto
    action_req = ApprovalActionRequest(
        tenant_id="tenant_api_test",
        lead_id=lead_id,
        action="APPROVE",
    )
    approved_lead = handle_action(action_req, store=store)
    assert approved_lead.state == "APPROVED"


def test_api_rejection_flow():
    req = IngestRequest(
        tenant_id="tenant_reject_test",
        name="Clinica Dental Norte",
        url="https://dentalnorte.es",
        html_content="<html><body><h1>Clinica Dental Norte</h1><p>Ortodoncia invisible.</p></body></html>",
    )
    orch = get_orchestrator()
    store = get_approval_store()

    result = process_prospect(req, orch=orch)
    lead_id = result.prospect.id

    # Descartar
    action_req = ApprovalActionRequest(
        tenant_id="tenant_reject_test",
        lead_id=lead_id,
        action="REJECT",
        reason="Fuera de alcance",
    )
    rejected_lead = handle_action(action_req, store=store)
    assert rejected_lead.state == "DISCARDED"


def test_api_multi_tenant_isolation():
    req_a = IngestRequest(
        tenant_id="tenant_alpha",
        name="Clinica Alpha",
        url="https://alpha.es",
        html_content="<html><body><h1>Clinica Alpha</h1><p>Cirugia maxilofacial.</p></body></html>",
    )
    orch = get_orchestrator()
    store = get_approval_store()

    res_a = process_prospect(req_a, orch=orch)
    lead_id_a = res_a.prospect.id

    # Tenant Beta consulta pendientes y no debe ver lead_id_a
    beta_pending = get_pending(tenant_id="tenant_beta", store=store)
    beta_pending_ids = [p.id for p in beta_pending]
    assert lead_id_a not in beta_pending_ids

    # Tenant Beta intenta aprobar lead de Tenant Alpha -> 404
    action_req = ApprovalActionRequest(
        tenant_id="tenant_beta",
        lead_id=lead_id_a,
        action="APPROVE",
    )
    with pytest.raises(HTTPException) as exc_info:
        handle_action(action_req, store=store)
    assert exc_info.value.status_code == 404


def test_api_invalid_action():
    req = IngestRequest(
        tenant_id="tenant_invalid_action",
        name="Clinica Test Action",
        url="https://testaction.es",
        html_content="<html><body><h1>Clinica</h1><p>Dental</p></body></html>",
    )
    orch = get_orchestrator()
    store = get_approval_store()

    result = process_prospect(req, orch=orch)
    lead_id = result.prospect.id

    action_req = ApprovalActionRequest(
        tenant_id="tenant_invalid_action",
        lead_id=lead_id,
        action="EXPLODE",
    )
    with pytest.raises(HTTPException) as exc_info:
        handle_action(action_req, store=store)
    assert exc_info.value.status_code == 400


def test_api_disallowed_state_transition_returns_409():
    req = IngestRequest(
        tenant_id="tenant_transition_error",
        name="Clinica Estado",
        url="https://clinicaestado.es",
        html_content="<html><body><h1>Clinica Estado</h1><p>Implantes y ortodoncia. Whatsapp.</p></body></html>",
    )
    orch = get_orchestrator()
    store = get_approval_store()

    result = process_prospect(req, orch=orch)
    lead_id = result.prospect.id

    # 1. Primera aprobación -> pasa a APPROVED
    action_req = ApprovalActionRequest(
        tenant_id="tenant_transition_error",
        lead_id=lead_id,
        action="APPROVE",
    )
    approved_lead = handle_action(action_req, store=store)
    assert approved_lead.state == "APPROVED"

    # 2. Segunda aprobación -> 409 Conflict (transición no permitida)
    with pytest.raises(HTTPException) as exc_info:
        handle_action(action_req, store=store)
    assert exc_info.value.status_code == 409
    assert "Transición no permitida" in exc_info.value.detail


def test_api_contact_update_and_batch_audit_flow():
    from RevOpsAI.src.api.routes import (
        update_prospect_details,
        batch_audit_urls,
        ProspectUpdateRequest,
        BatchAuditRequest,
    )
    orch = get_orchestrator()
    store = get_approval_store()

    # 1. Batch audit endpoint
    batch_req = BatchAuditRequest(
        tenant_id="tenant_batch_test",
        sector="clinicas",
        urls=[
            "https://odontologiamonteria.co",
            "https://implantessinu.com",
        ],
    )
    batch_res = batch_audit_urls(batch_req, orch=orch)
    assert batch_res["processed_count"] == 2
    lead_id = batch_res["results"][0]["id"]

    # 2. Update contact details (WhatsApp, Decisor, Copy)
    upd_req = ProspectUpdateRequest(
        tenant_id="tenant_batch_test",
        contact_name="Dra. Valentina Vega",
        contact_phone="+57 300 987 6543",
        draft_message="Mensaje personalizado para la Dra. Valentina.",
    )
    updated = update_prospect_details(lead_id=lead_id, req=upd_req, store=store)
    assert updated.contact_name == "Dra. Valentina Vega"
    assert updated.contact_phone == "+573009876543"
    assert updated.draft_message == "Mensaje personalizado para la Dra. Valentina."

    # 3. Mark interested transition
    action_interested = ApprovalActionRequest(
        tenant_id="tenant_batch_test",
        lead_id=lead_id,
        action="MARK_INTERESTED",
    )
    interested_lead = handle_action(action_interested, store=store)
    assert interested_lead.state == "INTERESTED"


def test_api_autonomous_prospecting_scout_flow():
    from RevOpsAI.src.api.routes import (
        run_autonomous_prospecting,
        AutoDiscoverRequest,
    )
    orch = get_orchestrator()

    scout_req = AutoDiscoverRequest(
        tenant_id="tenant_scout_test",
        city="Montería",
        sector="clinicas",
        limit=3,
    )
    res = run_autonomous_prospecting(scout_req, orch=orch)
    assert res["tenant_id"] == "tenant_scout_test"
    assert res["discovered_count"] >= 1
    assert res["audited_count"] >= 1
    assert len(res["results"]) >= 1
    assert res["results"][0]["score"] > 0
    assert "Montería" in res["city"]
