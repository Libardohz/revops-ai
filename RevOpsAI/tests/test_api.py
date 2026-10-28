"""Tests for FastAPI REST API endpoints with multi-tenant isolation."""

import pytest
from fastapi.testclient import TestClient
from RevOpsAI.src.api.main import app

client = TestClient(app)


def test_api_ingest_and_pending_approval_flow():
    payload = {
        "tenant_id": "tenant_api_test",
        "name": "Clinica Estetica Centro",
        "url": "https://esteticacentro.es",
        "html_content": "<html><body><h1>Clinica Estetica Centro</h1><p>Implantes y estetica dental. Contacto por whatsapp.</p></body></html>"
    }
    # 1. Ingesta
    res = client.post("/api/v1/prospects/process", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["prospect"]["state"] == "PENDING_APPROVAL"
    lead_id = data["prospect"]["id"]

    # 2. Consultar bandeja de pendientes
    res_pending = client.get("/api/v1/approval/pending?tenant_id=tenant_api_test")
    assert res_pending.status_code == 200
    pending_list = res_pending.json()
    assert len(pending_list) >= 1
    assert any(p["id"] == lead_id for p in pending_list)

    # 3. Aprobar prospecto
    action_payload = {
        "tenant_id": "tenant_api_test",
        "lead_id": lead_id,
        "action": "APPROVE"
    }
    res_action = client.post("/api/v1/approval/action", json=action_payload)
    assert res_action.status_code == 200
    assert res_action.json()["state"] == "APPROVED"


def test_api_rejection_flow():
    payload = {
        "tenant_id": "tenant_reject_test",
        "name": "Clinica Dental Norte",
        "url": "https://dentalnorte.es",
        "html_content": "<html><body><h1>Clinica Dental Norte</h1><p>Ortodoncia invisible.</p></body></html>"
    }
    res = client.post("/api/v1/prospects/process", json=payload)
    assert res.status_code == 200
    lead_id = res.json()["prospect"]["id"]

    # Descartar
    action_payload = {
        "tenant_id": "tenant_reject_test",
        "lead_id": lead_id,
        "action": "REJECT",
        "reason": "Fuera de alcance"
    }
    res_action = client.post("/api/v1/approval/action", json=action_payload)
    assert res_action.status_code == 200
    assert res_action.json()["state"] == "DISCARDED"


def test_api_multi_tenant_isolation():
    payload_a = {
        "tenant_id": "tenant_alpha",
        "name": "Clinica Alpha",
        "url": "https://alpha.es",
        "html_content": "<html><body><h1>Clinica Alpha</h1><p>Cirugia maxilofacial.</p></body></html>"
    }
    res_a = client.post("/api/v1/prospects/process", json=payload_a)
    lead_id_a = res_a.json()["prospect"]["id"]

    # Tenant Beta consulta pendientes y no debe ver lead_id_a
    res_beta = client.get("/api/v1/approval/pending?tenant_id=tenant_beta")
    assert res_beta.status_code == 200
    beta_pending_ids = [p["id"] for p in res_beta.json()]
    assert lead_id_a not in beta_pending_ids

    # Tenant Beta intenta aprobar lead de Tenant Alpha -> 404
    action_payload = {
        "tenant_id": "tenant_beta",
        "lead_id": lead_id_a,
        "action": "APPROVE"
    }
    res_cross_action = client.post("/api/v1/approval/action", json=action_payload)
    assert res_cross_action.status_code == 404


def test_api_invalid_action():
    payload = {
        "tenant_id": "tenant_invalid_action",
        "name": "Clinica Test Action",
        "url": "https://testaction.es",
        "html_content": "<html><body><h1>Clinica</h1><p>Dental</p></body></html>"
    }
    res = client.post("/api/v1/prospects/process", json=payload)
    lead_id = res.json()["prospect"]["id"]

    action_payload = {
        "tenant_id": "tenant_invalid_action",
        "lead_id": lead_id,
        "action": "EXPLODE"
    }
    res_action = client.post("/api/v1/approval/action", json=action_payload)
    assert res_action.status_code == 400
