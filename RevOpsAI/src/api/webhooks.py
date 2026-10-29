"""Inbound Webhooks & Reply Processor with HMAC Verification for RevOpsAI."""

import hashlib
import hmac
import json
import os
from typing import Any
from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

from RevOpsAI.src.agents.dispatch_agent import DispatchAgent, ReplyIntent
from RevOpsAI.src.core.models import Prospect, ProspectState

webhook_router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_hmac_signature(raw_body: bytes, signature_header: str | None, secret: str) -> bool:
    """Verify HMAC SHA-256 signature from webhook payload.

    Args:
        raw_body: Raw byte array of incoming HTTP body.
        signature_header: Header value containing 'sha256=<digest>' or raw hex.
        secret: Secret key shared with the webhook provider.

    Returns:
        bool: True if signature matches, False otherwise.
    """
    if not signature_header or not secret:
        return False

    expected_hash = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if signature_header.startswith("sha256="):
        actual_hash = signature_header.split("sha256=", 1)[1]
    else:
        actual_hash = signature_header

    return hmac.compare_digest(actual_hash, expected_hash)


def verify_whatsapp_challenge(
    mode: str | None,
    token: str | None,
    challenge: str | None,
    expected_token: str,
) -> int:
    """Validate Meta WhatsApp webhook subscription verification request.

    Args:
        mode: hub.mode parameter (must be 'subscribe').
        token: hub.verify_token parameter.
        challenge: hub.challenge parameter.
        expected_token: Expected verification token.

    Returns:
        int: Converted challenge integer.

    Raises:
        HTTPException: 403 Forbidden if token or mode is invalid.
    """
    if mode == "subscribe" and token == expected_token and challenge:
        try:
            return int(challenge)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid challenge format")
    raise HTTPException(status_code=403, detail="Forbidden: verification token mismatch")


def process_whatsapp_webhook(
    tenant_id: str,
    raw_body: bytes,
    signature_header: str,
    secret: str,
    lead: Prospect | None = None,
    dispatcher: DispatchAgent | None = None,
) -> dict[str, Any]:
    """Process incoming WhatsApp webhook payload with signature validation and reply classification.

    Args:
        tenant_id: Tenant identifier.
        raw_body: Raw request body bytes.
        signature_header: X-Hub-Signature-256 header.
        secret: Webhook HMAC secret.
        lead: Optional target prospect to update state and compliance.
        dispatcher: Optional DispatchAgent instance.

    Returns:
        dict: Processing status and reply intent.

    Raises:
        HTTPException: 403 if signature verification fails.
    """
    if not verify_hmac_signature(raw_body, signature_header, secret):
        raise HTTPException(status_code=403, detail="Invalid HMAC signature")

    if dispatcher is None:
        dispatcher = DispatchAgent()

    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    body_text = None
    from_phone = None

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            val = change.get("value", {})
            for msg in val.get("messages", []):
                if "text" in msg and "body" in msg["text"]:
                    body_text = msg["text"]["body"]
                from_phone = msg.get("from")
                if body_text:
                    break

    if body_text is None:
        return {"status": "ignored", "reason": "no messages found"}

    intent = ReplyIntent.UNKNOWN
    if lead is not None:
        intent = dispatcher.handle_incoming_reply(lead, body_text)
        if intent == ReplyIntent.INTERESTED:
            if lead.state == ProspectState.SENT:
                lead.transition_to(ProspectState.INTERESTED)
            else:
                lead.state = ProspectState.INTERESTED

    return {
        "status": "processed",
        "tenant_id": tenant_id,
        "from": from_phone,
        "intent": intent.value if hasattr(intent, "value") else intent,
    }


def process_email_webhook(
    tenant_id: str,
    raw_body: bytes,
    signature_header: str | None = None,
    secret: str | None = None,
    lead: Prospect | None = None,
    dispatcher: DispatchAgent | None = None,
) -> dict[str, Any]:
    """Process incoming email webhook payload (replies, bounces, complaints).

    Args:
        tenant_id: Tenant identifier.
        raw_body: Raw request body bytes.
        signature_header: Optional HMAC signature or verification token.
        secret: Optional secret for signature verification.
        lead: Optional target prospect.
        dispatcher: Optional DispatchAgent instance.

    Returns:
        dict: Processing status, event and reply intent.

    Raises:
        HTTPException: 403 if signature is provided but invalid.
    """
    if signature_header and secret:
        if not verify_hmac_signature(raw_body, signature_header, secret):
            raise HTTPException(status_code=403, detail="Invalid HMAC signature")

    if dispatcher is None:
        dispatcher = DispatchAgent()

    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    event = str(data.get("event", "")).lower()

    # Bounces, complaints, or explicit unsubscribes trigger immediate opt-out
    if event in ["bounce", "complaint", "unsubscribe", "opt_out"]:
        if lead is not None:
            lead.is_blacklisted = True
            if lead.state == ProspectState.SENT:
                lead.transition_to(ProspectState.OPT_OUT)
            else:
                lead.state = ProspectState.OPT_OUT
        return {
            "status": "processed",
            "tenant_id": tenant_id,
            "event": event,
            "intent": ReplyIntent.OPT_OUT.value,
        }

    # Handle incoming email reply text
    reply_text = data.get("text") or data.get("body") or ""
    intent = ReplyIntent.UNKNOWN
    if lead is not None and reply_text:
        intent = dispatcher.handle_incoming_reply(lead, reply_text)
        if intent == ReplyIntent.INTERESTED:
            if lead.state == ProspectState.SENT:
                lead.transition_to(ProspectState.INTERESTED)
            else:
                lead.state = ProspectState.INTERESTED

    return {
        "status": "processed",
        "tenant_id": tenant_id,
        "event": event or "reply",
        "intent": intent.value if hasattr(intent, "value") else intent,
    }


# --- REST API Endpoints ---


@webhook_router.get("/{tenant_id}/whatsapp")
def whatsapp_verification(
    tenant_id: str,
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
) -> Response:
    """Meta WhatsApp Webhook challenge verification endpoint."""
    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "meta_token")
    challenge_val = verify_whatsapp_challenge(
        mode=hub_mode,
        token=hub_verify_token,
        challenge=hub_challenge,
        expected_token=expected_token,
    )
    return Response(content=str(challenge_val), media_type="text/plain")


@webhook_router.post("/{tenant_id}/whatsapp")
async def whatsapp_inbound_webhook(
    tenant_id: str,
    request: Request,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    """Inbound WhatsApp message webhook with HMAC SHA-256 validation."""
    raw_body = await request.body()
    secret = os.getenv("WHATSAPP_APP_SECRET", "meta_secret")
    return process_whatsapp_webhook(
        tenant_id=tenant_id,
        raw_body=raw_body,
        signature_header=x_hub_signature_256 or "",
        secret=secret,
    )


@webhook_router.post("/{tenant_id}/email")
async def email_inbound_webhook(
    tenant_id: str,
    request: Request,
    x_signature_256: str | None = Header(None, alias="X-Signature-256"),
) -> dict[str, Any]:
    """Inbound email webhook (replies, bounces, complaints)."""
    raw_body = await request.body()
    secret = os.getenv("EMAIL_WEBHOOK_SECRET", "email_secret")
    return process_email_webhook(
        tenant_id=tenant_id,
        raw_body=raw_body,
        signature_header=x_signature_256,
        secret=secret,
    )
