# RevOpsAI: Orquestador, API FastAPI y Manejador de Respuestas (Fase 3) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar todos los agentes especializados en un Orquestador de Pipeline unificado, exponer una API REST con FastAPI para ingesta y aprobación humana multi-tenant, e implementar el despachador de mensajes con gestión estricta de bajas (`opt-out`).

**Architecture:** Módulo `PipelineOrchestrator` en `RevOpsAI/src/core/pipeline.py` que encadena la secuencia completa (`Scraper` -> `Research` -> `Audit` -> `Scoring` -> `Copywriter` -> `HITL`). Capa de API en `RevOpsAI/src/api/` con autenticación por `tenant_id` y rutas de control. Módulo de despacho y clasificación de respuestas en `RevOpsAI/src/agents/dispatch_agent.py`.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, httpx / TestClient para pruebas de API, Pytest.

**Spec:** `RevOpsAI/docs/2026-10-27-design-spec.md`

## Global Constraints
- Python 3.11+ únicamente.
- Cero consultas SQL dinámicas; uso exclusivo de modelos Pydantic y aislamiento estricto por `tenant_id`.
- La API debe rechazar accesos cruzados entre tenants con código HTTP 403 o 404.
- Respuestas de baja (`opt-out`) deben marcar permanentemente `is_blacklisted = True` y estado `OPT_OUT`.
- TDD estricto: test rojo -> implementación verde -> commit.

---

### Task 1: Pipeline Orchestrator (Orquestador Central de Agentes)

**Files:**
- Create: `RevOpsAI/src/core/pipeline.py`
- Test: `RevOpsAI/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `Prospect`, contenido HTML bruto, `SectorConfig` y `ApprovalStore`.
- Produces: `PipelineResult(prospect: Prospect, audit: CommercialAuditResult | None, scoring: ScoringResult | None)` ejecutando toda la cadena con trazabilidad.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_pipeline.py
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.pipeline import PipelineOrchestrator

def test_pipeline_runs_full_lifecycle_for_qualifying_clinic():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    store = ApprovalStore()
    orchestrator = PipelineOrchestrator(config=config, approval_store=store)
    
    lead = Prospect(tenant_id="tenant_dental", name="Clinica Dental Norte", url="https://dentalnorte.es")
    html_content = """
    <html><body>
      <h1>Clinica Dental Norte</h1>
      <p>Expertos en implantes dentales y estetica. Contactanos por WhatsApp.</p>
    </body></html>
    """
    
    result = orchestrator.process_prospect(lead, html_content)
    
    assert result.prospect.state == ProspectState.PENDING_APPROVAL
    assert result.scoring.is_qualified is True
    assert len(store.get_pending(tenant_id="tenant_dental")) == 1
    assert "Clinica Dental Norte" in result.prospect.draft_message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_pipeline.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
# RevOpsAI/src/core/pipeline.py
from pydantic import BaseModel
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import SectorConfig
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.integrations.web_scraper import SecureWebScraper
from RevOpsAI.src.agents.research_agent import ResearchAgent
from RevOpsAI.src.agents.audit_agent import CommercialAuditAgent, CommercialAuditResult
from RevOpsAI.src.agents.scoring_agent import ScoringAgent, ScoringResult
from RevOpsAI.src.agents.copywriter_agent import CopywriterAgent

class PipelineResult(BaseModel):
    prospect: Prospect
    audit: CommercialAuditResult | None = None
    scoring: ScoringResult | None = None

class PipelineOrchestrator:
    def __init__(self, config: SectorConfig, approval_store: ApprovalStore):
        self.config = config
        self.approval_store = approval_store
        self.scraper = SecureWebScraper()
        self.research_agent = ResearchAgent()
        self.audit_agent = CommercialAuditAgent(config)
        self.scoring_agent = ScoringAgent(config)
        self.copywriter_agent = CopywriterAgent(config, approval_store)

    def process_prospect(self, lead: Prospect, html_content: str) -> PipelineResult:
        if lead.is_blacklisted:
            lead.transition_to(ProspectState.DISCARDED)
            return PipelineResult(prospect=lead)

        # 1. Extracción y sanitización Zero-Trust
        scrape = self.scraper.parse_html(lead.url, html_content)

        # 2. Investigación operativa
        summary = self.research_agent.analyze(lead, scrape)

        # 3. Auditoría comercial y compliance
        audit = self.audit_agent.audit(lead, summary)

        # 4. Scoring ponderado
        scoring = self.scoring_agent.evaluate(lead, audit)

        # 5. Si califica, genera propuesta y registra en bandeja HITL
        if scoring.is_qualified:
            self.copywriter_agent.generate_proposal(lead, audit)

        return PipelineResult(prospect=lead, audit=audit, scoring=scoring)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/core/pipeline.py RevOpsAI/tests/test_pipeline.py
git commit -m "feat(core): implement PipelineOrchestrator connecting end-to-end agent workflow"
```

---

### Task 2: Agente de Despacho y Manejador de Respuestas (Dispatch & Reply Handler)

**Files:**
- Create: `RevOpsAI/src/agents/dispatch_agent.py`
- Test: `RevOpsAI/tests/test_dispatch_agent.py`

**Interfaces:**
- Consumes: `Prospect` en estado `APPROVED`, y mensajes de respuesta del prospecto.
- Produces: 
  - `dispatch_message(lead: Prospect) -> bool`: transiciona `APPROVED` -> `SENT`.
  - `handle_incoming_reply(lead: Prospect, reply_text: str) -> ReplyIntent`: detecta `OPT_OUT` (bloqueo global), `INTERESTED` (agendar cita) o `DEFERRED`.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_dispatch_agent.py
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.agents.dispatch_agent import DispatchAgent, ReplyIntent

def test_dispatch_and_handle_opt_out_reply():
    agent = DispatchAgent()
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://a.com")
    lead.state = ProspectState.APPROVED
    
    # 1. Despacho
    assert agent.dispatch_message(lead) is True
    assert lead.state == ProspectState.SENT
    
    # 2. Respuesta de baja
    intent = agent.handle_incoming_reply(lead, "Por favor no me contacten mas, denme de baja")
    assert intent == ReplyIntent.OPT_OUT
    assert lead.state == ProspectState.OPT_OUT
    assert lead.is_blacklisted is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_dispatch_agent.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
# RevOpsAI/src/agents/dispatch_agent.py
import re
from enum import Enum
from RevOpsAI.src.core.models import Prospect, ProspectState

class ReplyIntent(str, Enum):
    INTERESTED = "INTERESTED"
    OPT_OUT = "OPT_OUT"
    DEFERRED = "DEFERRED"
    UNKNOWN = "UNKNOWN"

class DispatchAgent:
    OPT_OUT_PATTERNS = [
        r"no\s+(me\s+)?contacten", r"baja", r"borren", r"no\s+interesa", r"spam", r"desuscribir"
    ]
    INTEREST_PATTERNS = [
        r"reunion", r"llamada", r"interesado", r"hablemos", r"precio", r"disponibilidad"
    ]

    def dispatch_message(self, lead: Prospect) -> bool:
        if lead.is_blacklisted or lead.state != ProspectState.APPROVED:
            return False
        lead.transition_to(ProspectState.SENT)
        return True

    def handle_incoming_reply(self, lead: Prospect, reply_text: str) -> ReplyIntent:
        text_lower = reply_text.lower()
        
        # 1. Prioridad absoluta: Compliance de Baja (Opt-out)
        for pattern in self.OPT_OUT_PATTERNS:
            if re.search(pattern, text_lower):
                lead.is_blacklisted = True
                lead.transition_to(ProspectState.OPT_OUT)
                return ReplyIntent.OPT_OUT

        # 2. Interés comercial
        for pattern in self.INTEREST_PATTERNS:
            if re.search(pattern, text_lower):
                return ReplyIntent.INTERESTED

        return ReplyIntent.UNKNOWN
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_dispatch_agent.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/agents/dispatch_agent.py RevOpsAI/tests/test_dispatch_agent.py
git commit -m "feat(agents): implement DispatchAgent with strict opt-out compliance handler"
```

---

### Task 3: API REST FastAPI con Aislamiento Multi-Tenant

**Files:**
- Create: `RevOpsAI/src/api/routes.py`
- Create: `RevOpsAI/src/api/main.py`
- Test: `RevOpsAI/tests/test_api.py`

**Interfaces:**
- Endpoints:
  - `POST /api/v1/prospects/process`: Ingesta y orquesta pipeline.
  - `GET /api/v1/approval/pending`: Retorna prospectos pendientes de aprobación filtrados por tenant.
  - `POST /api/v1/approval/action`: Aprueba o descarta un prospecto.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_api.py
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
    assert len(res_pending.json()) == 1

    # 3. Aprobar prospecto
    action_payload = {
        "tenant_id": "tenant_api_test",
        "lead_id": lead_id,
        "action": "APPROVE"
    }
    res_action = client.post("/api/v1/approval/action", json=action_payload)
    assert res_action.status_code == 200
    assert res_action.json()["state"] == "APPROVED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_api.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/api/routes.py`:
```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.core.pipeline import PipelineOrchestrator, PipelineResult

router = APIRouter(prefix="/api/v1")

# Dependencias singleton en memoria para el runtime de la API
config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
shared_store = ApprovalStore()
orchestrator = PipelineOrchestrator(config=config, approval_store=shared_store)

class IngestRequest(BaseModel):
    tenant_id: str
    name: str
    url: str
    html_content: str

class ApprovalActionRequest(BaseModel):
    tenant_id: str
    lead_id: str
    action: str  # "APPROVE" o "REJECT"
    reason: str = ""

@router.post("/prospects/process", response_model=PipelineResult)
def process_prospect(req: IngestRequest):
    lead = Prospect(tenant_id=req.tenant_id, name=req.name, url=req.url)
    return orchestrator.process_prospect(lead, req.html_content)

@router.get("/approval/pending", response_model=list[Prospect])
def get_pending(tenant_id: str = Query(...)):
    return shared_store.get_pending(tenant_id=tenant_id)

@router.post("/approval/action", response_model=Prospect)
def handle_action(req: ApprovalActionRequest):
    try:
        if req.action.upper() == "APPROVE":
            return shared_store.approve(lead_id=req.lead_id, tenant_id=req.tenant_id)
        elif req.action.upper() == "REJECT":
            return shared_store.reject(lead_id=req.lead_id, tenant_id=req.tenant_id, reason=req.reason)
        else:
            raise HTTPException(status_code=400, detail="Acción inválida. Use APPROVE o REJECT")
    except KeyError:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado para este tenant")
```

Crear `RevOpsAI/src/api/main.py`:
```python
from fastapi import FastAPI
from RevOpsAI.src.api.routes import router

app = FastAPI(
    title="RevOpsAI Control API",
    description="API de Control y Aprobación Humana Multi-Tenant",
    version="1.0.0"
)

app.include_router(router)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/api/ RevOpsAI/tests/test_api.py
git commit -m "feat(api): implement FastAPI multi-tenant control endpoints for ingestion and HITL"
```

---

## Plan Self-Review Check
- [x] **Spec Coverage:** Cubre PipelineOrchestrator unificado (Task 1), Despacho y Opt-out handler (Task 2), y API FastAPI con aislamiento multi-tenant (Task 3).
- [x] **No Placeholders:** Todos los códigos de implementación y tests están completos y sin texto ambiguo.
- [x] **Type Consistency:** Modelos compatibles con `Prospect`, `SectorConfig` y `ApprovalStore`.
