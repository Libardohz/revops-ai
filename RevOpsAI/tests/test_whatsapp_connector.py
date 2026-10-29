import pytest
from unittest.mock import MagicMock
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.whatsapp_connector import WhatsAppCloudConnector

def test_whatsapp_connector_sends_template_message():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 200
    mock_http.post.return_value.json.return_value = {
        "messages": [{"id": "wamid.HBgLMTIzNDU2Nzg5AA=="}]
    }

    connector = WhatsAppCloudConnector(
        phone_number_id="10987654321",
        access_token="EAABmockToken",
        http_client=mock_http
    )

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Sur",
        url="https://dentalsur.es",
        state=ProspectState.APPROVED
    )

    result = connector.send_template(
        lead=lead,
        recipient_phone="+34612345678",
        template_name="prospeccion_clinicas_v1",
        language_code="es",
        components=[{"type": "body", "parameters": [{"type": "text", "text": "Clínica Dental Sur"}]}]
    )

    assert result.success is True
    assert result.message_id == "wamid.HBgLMTIzNDU2Nzg5AA=="
    assert mock_http.post.called

def test_whatsapp_connector_formats_and_validates_e164_phone():
    connector = WhatsAppCloudConnector(
        phone_number_id="10987654321",
        access_token="mockToken"
    )
    cleaned = connector.clean_phone_number("  +34 612 34 56 78  ")
    assert cleaned == "34612345678"

    with pytest.raises(ValueError, match="formato E.164"):
        connector.clean_phone_number("not_a_phone")

def test_whatsapp_connector_blocks_blacklisted_lead():
    connector = WhatsAppCloudConnector(
        phone_number_id="10987654321",
        access_token="mockToken"
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.OPT_OUT,
        is_blacklisted=True
    )
    with pytest.raises(PermissionError, match="blacklisted"):
        connector.send_template(lead=lead, recipient_phone="+34600000000", template_name="test")

def test_whatsapp_connector_fails_if_lead_not_approved():
    connector = WhatsAppCloudConnector(
        phone_number_id="10987654321",
        access_token="mockToken"
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.RESEARCHING
    )
    with pytest.raises(ValueError, match="APPROVED"):
        connector.send_template(lead=lead, recipient_phone="+34600000000", template_name="test")
