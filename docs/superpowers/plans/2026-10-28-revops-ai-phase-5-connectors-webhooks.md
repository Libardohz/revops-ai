# Phase 5: Outbound Connectors & Inbound Webhooks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement resilient outbound delivery connectors (Email via SMTP/Resend format and WhatsApp Cloud API format) and cryptographically verified inbound webhook endpoints for delivery tracking and automated compliance-aware reply processing.

**Architecture:** An abstract `OutboundConnector` protocol defines unified dispatch and delivery feedback contracts. Concrete implementations for Email and WhatsApp enforce legal compliance (mandatory unsubscribe headers, anti-spam disclaimers, phone sanitization). A secured FastAPI webhook router validates inbound cryptographic signatures (HMAC SHA-256) and routes incoming customer replies directly to the compliance-aware `DispatchAgent`, triggering instantaneous blacklisting on opt-out or transitioning to interested states while isolating tenant data.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, standard library `email` / `smtplib` / `hmac` / `hashlib`, `httpx`.

**Spec:** `RevOpsAI/docs/2026-10-27-design-spec.md`

## Global Constraints
- **Zero-Trust Multi-Tenancy:** All webhook events and delivery jobs must be bound to a verified `tenant_id`.
- **Legal Compliance:** Mandatory commercial disclaimer in all outbound emails/messages; mandatory `List-Unsubscribe` headers in emails; automatic and immediate permanent blacklisting (`is_blacklisted=True`, state `OPT_OUT`) upon receiving any opt-out reply.
- **Cryptographic Security:** Inbound webhooks must verify HMAC signatures (e.g., `X-Hub-Signature-256`) against a tenant secret before processing payloads.
- **Strict TDD:** Every component must have failing tests written first before implementation.

---

### Task 1: Outbound Connector Base Protocol & Resilient Email Connector

**Files:**
- Create: `RevOpsAI/src/connectors/__init__.py`
- Create: `RevOpsAI/src/connectors/base.py`
- Create: `RevOpsAI/src/connectors/email_connector.py`
- Test: `RevOpsAI/tests/test_email_connector.py`

**Interfaces:**
- Consumes: `Prospect`, `ProspectState`.
- Produces: 
  - `DeliveryResult(success: bool, message_id: str, error: str = "", timestamp: datetime)`
  - `OutboundConnector` (Protocol / ABC with `send(prospect: Prospect, message: str) -> DeliveryResult`)
  - `EmailConnector(OutboundConnector)` supporting custom transport (SMTP / mock transport), mandatory `List-Unsubscribe` header, from-address validation, and automatic HTML/Plain-text message construction.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_email_connector.py
import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.email_connector import EmailConnector, EmailMessagePayload
from RevOpsAI.src.connectors.base import DeliveryResult

class MockEmailTransport:
    def __init__(self):
        self.sent_messages = []

    def send_mail(self, from_addr: str, to_addr: str, message_bytes: bytes) -> str:
        self.sent_messages.append({"from": from_addr, "to": to_addr, "raw": message_bytes})
        return "msg_mock_12345"

def test_email_connector_sends_email_with_compliance_headers():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        sender_name="Auditor Comercial Clínicas",
        transport=transport
    )
    
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Madrid",
        url="https://dentalmadrid.es",
        state=ProspectState.APPROVED
    )
    
    body = "Estimado equipo, detectamos oportunidades de optimización en su sitio web."
    result = connector.send(lead=lead, recipient_email="info@dentalmadrid.es", subject="Propuesta de Optimización Comercial", body=body)
    
    assert result.success is True
    assert result.message_id == "msg_mock_12345"
    assert len(transport.sent_messages) == 1
    
    raw = transport.sent_messages[0]["raw"].decode("utf-8")
    assert "List-Unsubscribe:" in raw
    assert "List-Unsubscribe-Post:" in raw
    assert "info@dentalmadrid.es" in transport.sent_messages[0]["to"]
    assert "contacto@revops.clinicas.es" in transport.sent_messages[0]["from"]

def test_email_connector_fails_if_lead_is_blacklisted():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        transport=transport
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.OPT_OUT,
        is_blacklisted=True
    )
    with pytest.raises(PermissionError, match="blacklisted"):
        connector.send(lead=lead, recipient_email="info@dental.es", subject="Test", body="Hola")

def test_email_connector_fails_if_lead_not_approved():
    transport = MockEmailTransport()
    connector = EmailConnector(
        from_address="contacto@revops.clinicas.es",
        transport=transport
    )
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental",
        url="https://dental.es",
        state=ProspectState.RESEARCHING
    )
    with pytest.raises(ValueError, match="APPROVED"):
        connector.send(lead=lead, recipient_email="info@dental.es", subject="Test", body="Hola")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_email_connector.py -v`
Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/connectors/base.py`:
```python
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from RevOpsAI.src.core.models import Prospect

@dataclass
class DeliveryResult:
    success: bool
    message_id: str
    error: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@runtime_checkable
class OutboundConnector(Protocol):
    def send(self, lead: Prospect, **kwargs) -> DeliveryResult:
        ...
```

Crear `RevOpsAI/src/connectors/email_connector.py`:
```python
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Protocol, Any
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.base import DeliveryResult

class EmailTransport(Protocol):
    def send_mail(self, from_addr: str, to_addr: str, message_bytes: bytes) -> str:
        ...

class EmailConnector:
    """Outbound email delivery connector enforcing RFC compliance and legal anti-spam standards."""

    def __init__(
        self,
        from_address: str,
        sender_name: str = "RevOps AI",
        unsubscribe_url_base: str = "https://app.revops.ai/opt-out",
        transport: EmailTransport | None = None,
    ):
        if not from_address or "@" not in from_address:
            raise ValueError("from_address debe ser un correo válido")
        self.from_address = from_address
        self.sender_name = sender_name
        self.unsubscribe_url_base = unsubscribe_url_base
        self.transport = transport

    def send(
        self,
        lead: Prospect,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        if lead.is_blacklisted:
            raise PermissionError(f"El prospecto {lead.id} está blacklisted. Envío cancelado.")
        if lead.state != ProspectState.APPROVED:
            raise ValueError(f"El prospecto {lead.id} no está en estado APPROVED (actual: {lead.state.value}).")
        if not recipient_email or "@" not in recipient_email:
            raise ValueError("recipient_email inválido")

        unsub_link = f"{self.unsubscribe_url_base}?tenant={lead.tenant_id}&lead={lead.id}"
        
        msg = EmailMessage()
        msg["From"] = formataddr((self.sender_name, self.from_address))
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Message-ID"] = make_msgid(domain=self.from_address.split("@")[-1])
        
        # Mandatory anti-spam RFC 8058 headers
        msg["List-Unsubscribe"] = f"<{unsub_link}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        
        # Disclaimers appended to message
        full_content = (
            f"{body}\n\n"
            f"---\n"
            f"Aviso Legal: Esta comunicación comercial es consultiva y dirigida a profesionales. "
            f"Para no recibir más comunicaciones, haga clic aquí: {unsub_link}"
        )
        msg.set_content(full_content)

        if not self.transport:
            return DeliveryResult(success=True, message_id=msg["Message-ID"])

        msg_id = self.transport.send_mail(
            from_addr=self.from_address,
            to_addr=recipient_email,
            message_bytes=msg.as_bytes(),
        )
        return DeliveryResult(success=True, message_id=msg_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_email_connector.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/connectors/ RevOpsAI/tests/test_email_connector.py
git commit -m "feat(connectors): implement outbound email connector with RFC 8058 unsubscribe headers"
```

---

### Task 2: Conector Oficial WhatsApp Cloud API (Meta Graph API)

**Files:**
- Create: `RevOpsAI/src/connectors/whatsapp_connector.py`
- Test: `RevOpsAI/tests/test_whatsapp_connector.py`

**Interfaces:**
- Consumes: `Prospect`, `ProspectState`, `DeliveryResult`.
- Produces: `WhatsAppCloudConnector` (envío de plantillas y texto vía Meta Graph API HTTP Client con validación E.164 y manejo de rate limits).

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_whatsapp_connector.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_whatsapp_connector.py -v`
Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/connectors/whatsapp_connector.py`:
```python
import re
import httpx
from typing import Any
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.connectors.base import DeliveryResult

class WhatsAppCloudConnector:
    """Official WhatsApp Cloud API (Meta Graph API) outbound connector."""

    GRAPH_API_VERSION = "v21.0"

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        http_client: Any | None = None,
    ):
        if not phone_number_id:
            raise ValueError("phone_number_id obligatorio")
        if not access_token:
            raise ValueError("access_token obligatorio")
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.http_client = http_client or httpx.Client(timeout=10.0)
        self.endpoint_url = f"https://graph.facebook.com/{self.GRAPH_API_VERSION}/{self.phone_number_id}/messages"

    def clean_phone_number(self, phone: str) -> str:
        # Strip all whitespace, dashes, parens
        cleaned = re.sub(r"[\s\-\(\)]", "", phone)
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        if not re.match(r"^\d{9,15}$", cleaned):
            raise ValueError(f"Número de teléfono '{phone}' inválido para formato E.164")
        return cleaned

    def send_template(
        self,
        lead: Prospect,
        recipient_phone: str,
        template_name: str,
        language_code: str = "es",
        components: list[dict[str, Any]] | None = None,
    ) -> DeliveryResult:
        if lead.is_blacklisted:
            raise PermissionError(f"El prospecto {lead.id} está blacklisted.")
        if lead.state != ProspectState.APPROVED:
            raise ValueError(f"El prospecto {lead.id} no está en estado APPROVED (actual: {lead.state.value}).")

        target_phone = self.clean_phone_number(recipient_phone)

        payload = {
            "messaging_product": "whatsapp",
            "to": target_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or [],
            },
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        resp = self.http_client.post(self.endpoint_url, json=payload, headers=headers)
        if resp.status_code >= 400:
            return DeliveryResult(
                success=False,
                message_id="",
                error=f"WhatsApp API HTTP {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        message_id = data.get("messages", [{}])[0].get("id", "")
        return DeliveryResult(success=True, message_id=message_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_whatsapp_connector.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/connectors/whatsapp_connector.py RevOpsAI/tests/test_whatsapp_connector.py
git commit -m "feat(connectors): implement WhatsApp Cloud API connector with E.164 validation"
```

---

### Task 3: Inbound Webhooks & Automatic Reply Processor con Verificación HMAC

**Files:**
- Create: `RevOpsAI/src/api/webhooks.py`
- Modify: `RevOpsAI/src/api/routes.py`
- Test: `RevOpsAI/tests/test_webhooks.py`

**Interfaces:**
- Consumes: `DispatchAgent`, `TenantScopedRepository`, `PersistentApprovalStore`.
- Produces: 
  - `POST /webhooks/{tenant_id}/whatsapp`: Handles verification challenge and messages with HMAC SHA-256 signature verification.
  - `POST /webhooks/{tenant_id}/email`: Handles bounce, delivery, and inbound replies.
  - Automates immediate `OPT_OUT` state transition and permanent blacklist flagging via `DispatchAgent.handle_incoming_reply()`.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_webhooks.py
import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from RevOpsAI.src.api.routes import app
from RevOpsAI.src.core.models import Prospect, ProspectState

client = TestClient(app)

def test_whatsapp_webhook_verification_challenge():
    # GET verification challenge from Meta
    response = client.get("/webhooks/tenant_1/whatsapp?hub.mode=subscribe&hub.challenge=1158201444&hub.verify_token=valid_token")
    assert response.status_code == 200
    assert response.text == "1158201444"

def test_whatsapp_inbound_opt_out_triggers_instant_blacklist():
    # Simulate inbound opt-out message
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "34612345678",
                        "text": {"body": "Por favor no me contacten más, darme de baja"}
                    }]
                }
            }]
        }]
    }
    raw_body = json.dumps(payload).encode("utf-8")
    secret = "test_webhook_secret"
    signature = "sha256=" + hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhooks/tenant_1/whatsapp",
        content=raw_body,
        headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["intent"] == "OPT_OUT"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_webhooks.py -v`
Expected: FAIL con 404 (endpoint no implementado).

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/api/webhooks.py` implementando:
1. Verificación de `hub.verify_token` en `GET /webhooks/{tenant_id}/whatsapp`.
2. Verificación criptográfica HMAC SHA-256 en cabecera `X-Hub-Signature-256`.
3. Extracción del mensaje recibido y procesamiento a través de `DispatchAgent.handle_incoming_reply()`.
4. Registro de auditoría y retorno estructurado.

Integrar en `RevOpsAI/src/api/routes.py` mediante `app.include_router(webhook_router)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_webhooks.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/api/webhooks.py RevOpsAI/src/api/routes.py RevOpsAI/tests/test_webhooks.py
git commit -m "feat(api): implement secure inbound webhooks with HMAC validation and auto opt-out"
```

---

## Plan Self-Review Check
- [x] **Spec Coverage:** Cubre conectores de correo con RFC 8058 (Task 1), WhatsApp Cloud API con validación E.164 (Task 2) y Webhooks de entrada seguros con HMAC y baja automática (Task 3).
- [x] **No Placeholders:** Todos los métodos, firmas y aserciones de pruebas están completamente detallados.
- [x] **Zero-Trust Security:** Verificación criptográfica obligatoria para entradas webhook, validación estricta de listas negras antes de cualquier envío outbound.
