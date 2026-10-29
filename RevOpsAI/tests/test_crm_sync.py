"""Tests for CRMSyncConnector bi-directional sync (HubSpot, GoHighLevel, generic webhooks)."""

import pytest
from unittest.mock import MagicMock
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.integrations.crm_sync import CRMSyncConnector, CRMSyncResult


def test_crm_sync_constructs_and_sends_payload_hubspot():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 200
    mock_http.post.return_value.json.return_value = {"id": "crm_deal_9988"}

    connector = CRMSyncConnector(
        crm_type="hubspot",
        endpoint_url="https://api.hubapi.com/crm/v3/objects/deals",
        api_key="pat-eu1-mock-token",
        http_client=mock_http,
    )

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Castellana",
        url="https://dentalcastellana.es",
        score=94,
        research_summary="Sin reserva online, WhatsApp no interactivo",
        state=ProspectState.INTERESTED,
    )

    result = connector.sync_prospect(lead)
    assert result.success is True
    assert result.remote_id == "crm_deal_9988"
    assert mock_http.post.called


def test_crm_sync_constructs_and_sends_payload_gohighlevel():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 201
    mock_http.post.return_value.json.return_value = {"opportunity": {"id": "ghl_opp_4455"}}

    connector = CRMSyncConnector(
        crm_type="gohighlevel",
        endpoint_url="https://services.leadconnectorhq.com/opportunities/",
        api_key="ghl_mock_key",
        http_client=mock_http,
    )

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Serrano",
        url="https://dentalserrano.es",
        score=88,
        research_summary="Sin WhatsApp directo",
        state=ProspectState.QUALIFIED,
    )

    result = connector.sync_prospect(lead)
    assert result.success is True
    assert result.remote_id == "ghl_opp_4455"
    assert mock_http.post.called


def test_crm_sync_handles_api_failure():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 500
    mock_http.post.return_value.text = "Internal Server Error"

    connector = CRMSyncConnector(
        crm_type="gohighlevel",
        endpoint_url="https://services.leadconnectorhq.com/opportunities/",
        api_key="ghl_mock_key",
        http_client=mock_http,
    )

    lead = Prospect(tenant_id="t1", name="Clínica Test", url="http://test.es", state=ProspectState.QUALIFIED)
    result = connector.sync_prospect(lead)
    assert result.success is False
    assert "500" in result.error
