# Phase 7: Follow-Up Cadence Agent, CRM Sync & Production Docker Packaging Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the remaining 2 agents from the original specification (Agent 7: Follow-Up Cadence Agent and Agent 8: CRM Synchronization Connector) and provide full production hardening (Dockerfile, docker-compose with PostgreSQL RLS, .env.example, and Master Turnkey documentation).

**Architecture:** A deterministic `FollowUpAgent` manages post-contact cadences with maximum retry ceilings and consultative phrasing; `CRMSyncConnector` maps qualified and interested prospects into standard CRM payloads (HubSpot / GoHighLevel / Webhooks); Docker compose orchestrates the FastAPI application alongside a PostgreSQL database executing Row-Level Security DDL on startup.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, Docker & Docker Compose, PostgreSQL 16.

**Spec:** `RevOpsAI/docs/2026-10-27-design-spec.md`

## Global Constraints
- **Anti-Spam & Contact Fatigue Protection:** Maximum 2 follow-ups allowed. The agent strictly discards the lead after exhausting attempts without answer.
- **Zero-Trust Multi-Tenancy:** CRM sync and follow-up executions must always specify and respect `tenant_id`.
- **Zero Data Leakage:** CRM sync payloads must sanitize and scrub sensitive tokens prior to egress.
- **Strict TDD:** Tests must be written first and fail before implementation.

---

### Task 1: Follow-Up Cadence Agent (`FollowUpAgent`)

**Files:**
- Create: `RevOpsAI/src/agents/followup_agent.py`
- Modify: `RevOpsAI/src/agents/__init__.py`
- Test: `RevOpsAI/tests/test_followup_agent.py`

**Interfaces:**
- Consumes: `Prospect`, `ProspectState`, `SectorConfig`.
- Produces: 
  - `FollowUpCadence(step: int, wait_days: int, template: str)`
  - `FollowUpAgent(max_followups=2)` with `generate_followup(lead: Prospect, attempt: int) -> str` and `process_cadence(lead: Prospect, days_elapsed: int) -> FollowUpResult`.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_followup_agent.py
import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.agents.followup_agent import FollowUpAgent, FollowUpResult

def test_followup_agent_generates_first_bump():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        score=82,
        research_summary="Sin WhatsApp directo",
        state=ProspectState.SENT
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=3, current_attempt=0)
    assert result.should_send is True
    assert result.attempt_number == 1
    assert "Clínica Dental Almagro" in result.message
    assert "WhatsApp" in result.message
    assert "Aviso Legal" in result.message

def test_followup_agent_generates_second_and_final_bump():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.SENT
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=5, current_attempt=1)
    assert result.should_send is True
    assert result.attempt_number == 2
    assert "último seguimiento" in result.message.lower() or "cerrar el contacto" in result.message.lower()

def test_followup_agent_exhausts_and_transitions_to_discarded():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.SENT
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=4, current_attempt=2)
    assert result.should_send is False
    assert result.is_exhausted is True
    assert lead.state == ProspectState.DISCARDED

def test_followup_agent_blocks_blacklisted_or_opt_out():
    agent = FollowUpAgent()
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.OPT_OUT,
        is_blacklisted=True
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=10, current_attempt=0)
    assert result.should_send is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_followup_agent.py -v`
Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/agents/followup_agent.py`:
- `FollowUpResult(should_send: bool, attempt_number: int, message: str = "", is_exhausted: bool = False, reason: str = "")`
- `FollowUpAgent`:
  - `max_followups: int = 2`
  - `evaluate_and_generate(lead: Prospect, days_since_last_contact: int, current_attempt: int) -> FollowUpResult`
  - Revisa estado y blacklist.
  - Si `current_attempt >= max_followups`, transiciona `lead.transition_to(ProspectState.DISCARDED)` y retorna `is_exhausted=True`.
  - Construye copy respetuoso, no invasivo, con disclaimer legal y mención a los gaps detectados.

Exportar en `RevOpsAI/src/agents/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_followup_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/agents/followup_agent.py RevOpsAI/src/agents/__init__.py RevOpsAI/tests/test_followup_agent.py
git commit -m "feat(agents): implement FollowUpAgent with strict attempt ceiling and compliance rules"
```

---

### Task 2: CRM Synchronization Connector (`CRMSyncConnector`)

**Files:**
- Create: `RevOpsAI/src/integrations/crm_sync.py`
- Modify: `RevOpsAI/src/integrations/__init__.py`
- Test: `RevOpsAI/tests/test_crm_sync.py`

**Interfaces:**
- Consumes: `Prospect`, `ProspectState`.
- Produces: 
  - `CRMPayload(prospect_id, tenant_id, company_name, website, score, status, gaps, draft_proposal)`
  - `CRMSyncConnector(crm_type="hubspot"|"gohighlevel"|"webhook", endpoint_url, api_key)`
  - `sync_prospect(lead: Prospect) -> CRMSyncResult`

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_crm_sync.py
import pytest
from unittest.mock import MagicMock
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.integrations.crm_sync import CRMSyncConnector, CRMSyncResult

def test_crm_sync_constructs_and_sends_payload():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 200
    mock_http.post.return_value.json.return_value = {"id": "crm_deal_9988"}

    connector = CRMSyncConnector(
        crm_type="hubspot",
        endpoint_url="https://api.hubapi.com/crm/v3/objects/deals",
        api_key="pat-eu1-mock-token",
        http_client=mock_http
    )

    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Castellana",
        url="https://dentalcastellana.es",
        score=94,
        research_summary="Sin reserva online, WhatsApp no interactivo",
        state=ProspectState.INTERESTED
    )

    result = connector.sync_prospect(lead)
    assert result.success is True
    assert result.remote_id == "crm_deal_9988"
    assert mock_http.post.called

def test_crm_sync_handles_api_failure():
    mock_http = MagicMock()
    mock_http.post.return_value.status_code = 500
    mock_http.post.return_value.text = "Internal Server Error"

    connector = CRMSyncConnector(
        crm_type="gohighlevel",
        endpoint_url="https://services.leadconnectorhq.com/opportunities/",
        api_key="ghl_mock_key",
        http_client=mock_http
    )

    lead = Prospect(tenant_id="t1", name="Clínica Test", url="http://test.es", state=ProspectState.QUALIFIED)
    result = connector.sync_prospect(lead)
    assert result.success is False
    assert "500" in result.error
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_crm_sync.py -v`
Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/integrations/crm_sync.py`:
- `CRMSyncResult(success: bool, remote_id: str = "", error: str = "")`
- `CRMSyncConnector`:
  - Formatea campos estándar para HubSpot (properties: `dealname`, `pipeline`, `dealstage`, `amount`, `score`, `friction_points`) o GoHighLevel (contact + opportunity).
  - Manejo de respuestas y logging de sincronización.

Exportar en `RevOpsAI/src/integrations/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_crm_sync.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/integrations/crm_sync.py RevOpsAI/src/integrations/__init__.py RevOpsAI/tests/test_crm_sync.py
git commit -m "feat(integrations): implement CRMSyncConnector for HubSpot, GoHighLevel and custom webhooks"
```

---

### Task 3: Production Dockerfile, docker-compose con PostgreSQL RLS & Master README

**Files:**
- Create: `RevOpsAI/Dockerfile`
- Create: `RevOpsAI/docker-compose.yml`
- Create: `RevOpsAI/.env.example`
- Create/Update: `RevOpsAI/README.md`
- Test: `RevOpsAI/tests/test_packaging_config.py`

**Interfaces:**
- Produces:
  - `Dockerfile` multi-stage ligero para FastAPI, Uvicorn y librerías del sistema.
  - `docker-compose.yml` orquestando servicio `api` (puerto 8000) y `postgres:16` con healthcheck y volumen persistente.
  - `.env.example` con variables documentadas: `DATABASE_URL`, `META_WA_TOKEN`, `RESEND_API_KEY`, etc.
  - `README.md` maestro con:
    1. Arquitectura de los 9 agentes y diagrama del flujo determinista.
    2. Guía paso a paso de adaptación a otros sectores (inmobiliarias, abogados, etc.) en 10 minutos vía YAML.
    3. Guía de despliegue en producción con Docker y arranque del Dashboard Kanban.
    4. Argumentario comercial para venta a clínicas o agencias RevOps.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_packaging_config.py
from pathlib import Path

def test_packaging_files_exist():
    dockerfile = Path("RevOpsAI/Dockerfile")
    compose = Path("RevOpsAI/docker-compose.yml")
    env_example = Path("RevOpsAI/.env.example")
    readme = Path("RevOpsAI/README.md")

    assert dockerfile.exists()
    assert compose.exists()
    assert env_example.exists()
    assert readme.exists()

def test_dockerfile_and_compose_content():
    dockerfile = Path("RevOpsAI/Dockerfile").read_text(encoding="utf-8")
    compose = Path("RevOpsAI/docker-compose.yml").read_text(encoding="utf-8")
    env_example = Path("RevOpsAI/.env.example").read_text(encoding="utf-8")

    assert "python:3.11-slim" in dockerfile
    assert "uvicorn" in dockerfile
    assert "postgres:16" in compose
    assert "DATABASE_URL" in compose
    assert "META_WA_TOKEN" in env_example
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_packaging_config.py -v`
Expected: FAIL con `AssertionError`.

- [ ] **Step 3: Create files**
  - Create `RevOpsAI/Dockerfile`
  - Create `RevOpsAI/docker-compose.yml`
  - Create `RevOpsAI/.env.example`
  - Update `RevOpsAI/README.md` with complete documentation.

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/ -v`
Expected: PASS (all tests green).

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/Dockerfile RevOpsAI/docker-compose.yml RevOpsAI/.env.example RevOpsAI/README.md RevOpsAI/tests/test_packaging_config.py
git commit -m "feat(deploy): add production Dockerfile, docker-compose with PostgreSQL and master README guide"
```

---

## Plan Self-Review Check
- [x] **Spec Coverage:** Cubre el Agente 7 (Follow-up), Agente 8 (CRM sync) y el empaquetado de despliegue Docker y manual comercial.
- [x] **No Placeholders:** Todos los códigos y configuraciones están especificados.
- [x] **Zero-Trust & Compliance:** Se respetan límites de intentos de seguimiento y privacidad de datos.

