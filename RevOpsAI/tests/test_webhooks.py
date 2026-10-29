"""Tests for Inbound Webhooks & Reply Processor with HMAC Verification."""

import hashlib
import hmac
import json
import pytest
from fastapi import HTTPException

from RevOpsAI.src.api.webhooks import (
    verify_whatsapp_challenge,
    process_whatsapp_webhook,
    process_email_webhook,
    verify_hmac_signature,
    whatsapp_verification,
    webhook_router,
)
from RevOpsAI.src.agents.dispatch_agent import DispatchAgent
from RevOpsAI.src.core.models import Prospect, ProspectState


def test_verify_whatsapp_challenge_success():
    mode = "subscribe"
    token = "secret_meta_token_123"
    challenge = "1158201444"
    result = verify_whatsapp_challenge(
        mode=mode,
        token=token,
        challenge=challenge,
        expected_token="secret_meta_token_123",
    )
    assert result == 1158201444


def test_verify_whatsapp_challenge_forbidden():
    with pytest.raises(HTTPException) as exc_info:
        verify_whatsapp_challenge(
            mode="subscribe",
            token="wrong_token",
            challenge="1158201444",
            expected_token="secret_meta_token_123",
        )
    assert exc_info.value.status_code == 403


def test_hmac_signature_validation():
    secret = "my_webhook_secret_key"
    payload = b'{"event":"test"}'
    signature = "sha256=" + hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    assert verify_hmac_signature(payload, signature, secret) is True
    assert verify_hmac_signature(payload, "sha256=invalidhex", secret) is False


def test_whatsapp_webhook_opt_out_triggers_instant_blacklist():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "34612345678",
                                    "text": {"body": "Por favor no me contacten más, darme de baja"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "meta_secret"
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dental.es",
        state=ProspectState.SENT,
    )
    dispatcher = DispatchAgent()

    result = process_whatsapp_webhook(
        tenant_id="tenant_dental",
        raw_body=raw_body,
        signature_header=sig,
        secret=secret,
        lead=lead,
        dispatcher=dispatcher,
    )
    assert result["status"] == "processed"
    assert result["intent"] == "OPT_OUT"
    assert lead.state == ProspectState.OPT_OUT
    assert lead.is_blacklisted is True


def test_whatsapp_webhook_interested_reply():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "34612345678",
                                    "text": {"body": "Hola, me interesa mucho su propuesta, hablemos"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "meta_secret"
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dental.es",
        state=ProspectState.SENT,
    )
    dispatcher = DispatchAgent()

    result = process_whatsapp_webhook(
        tenant_id="tenant_dental",
        raw_body=raw_body,
        signature_header=sig,
        secret=secret,
        lead=lead,
        dispatcher=dispatcher,
    )
    assert result["status"] == "processed"
    assert result["intent"] == "INTERESTED"
    assert lead.state == ProspectState.INTERESTED


def test_email_webhook_bounce_or_complaint_opts_out():
    payload = {
        "event": "bounce",
        "email": "contacto@clinica.es",
        "reason": "Hard bounce - mailbox does not exist",
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "email_secret"
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dental.es",
        state=ProspectState.SENT,
    )

    result = process_email_webhook(
        tenant_id="tenant_dental",
        raw_body=raw_body,
        signature_header=sig,
        secret=secret,
        lead=lead,
    )
    assert result["status"] == "processed"
    assert result["intent"] == "OPT_OUT"
    assert lead.state == ProspectState.OPT_OUT
    assert lead.is_blacklisted is True


def test_email_webhook_reply_intent():
    payload = {
        "event": "reply",
        "email": "contacto@clinica.es",
        "text": "Nos interesa agendar una reunión la próxima semana",
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "email_secret"
    sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dental.es",
        state=ProspectState.SENT,
    )
    dispatcher = DispatchAgent()

    result = process_email_webhook(
        tenant_id="tenant_dental",
        raw_body=raw_body,
        signature_header=sig,
        secret=secret,
        lead=lead,
        dispatcher=dispatcher,
    )
    assert result["status"] == "processed"
    assert result["intent"] == "INTERESTED"
    assert lead.state == ProspectState.INTERESTED


def test_whatsapp_webhook_invalid_signature_raises_403():
    payload = b'{"test": 1}'
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dental.es",
        state=ProspectState.SENT,
    )
    with pytest.raises(HTTPException) as exc_info:
        process_whatsapp_webhook(
            tenant_id="tenant_dental",
            raw_body=payload,
            signature_header="sha256=invalid",
            secret="meta_secret",
            lead=lead,
        )
    assert exc_info.value.status_code == 403


def test_whatsapp_verification_endpoint():
    resp = whatsapp_verification(
        tenant_id="tenant_dental",
        hub_mode="subscribe",
        hub_challenge="987654321",
        hub_verify_token="meta_token",
    )
    assert resp.body.decode() == "987654321"


def test_router_configuration():
    assert webhook_router.prefix == "/webhooks"
    routes = [r.path for r in webhook_router.routes]
    assert "/webhooks/{tenant_id}/whatsapp" in routes
    assert "/webhooks/{tenant_id}/email" in routes
