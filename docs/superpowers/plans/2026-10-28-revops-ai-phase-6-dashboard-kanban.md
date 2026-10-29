# Phase 6: Human-in-the-Loop Web Dashboard & Kanban Review UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a bespoke, high-end Human-in-the-Loop web dashboard (Kanban pipeline, proposal review drawer, live RevOps KPIs, and multi-tenant switcher) adhering to Anti-AI-Slop design engineering standards.

**Architecture:** FastAPI serves high-performance dashboard analytics endpoints (`/api/v1/dashboard/stats`, `/api/v1/dashboard/leads`) backed by `TenantScopedRepository` and the persistence layer. A responsive, zero-build client-side application (`dashboard.html`, `dashboard.js`, `dashboard.css`) renders a Linear/Raycast-grade interactive workspace featuring a 4-column Kanban board, live KPI metric cards, and a microdiagnosis inspection drawer with one-click approval and rejection controls.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0, HTML5, Modern CSS3 with semantic tokens (hairline borders, physical depth, spring transitions), Vanilla ES6+ (reactive, zero layout shifts, zero external build dependencies).

**Spec:** `RevOpsAI/docs/2026-10-27-design-spec.md` & `anti-ai-design` skill guidelines.

## Global Constraints
- **Anti-AI-Slop Design:** No generic purple/neon gradients, no robotic layout templates, no blurry drop-shadows. Enforce 1px directional hairline borders, refined typography contrast, tactile micro-feedback (100-150ms), and semantic design tokens.
- **Zero-Trust Multi-Tenancy:** Dashboard views and actions must enforce `tenant_id` boundaries across all endpoints.
- **Audit Immutability:** Human actions (Approve / Reject with reason) must invoke `PersistentApprovalStore` to guarantee audit trail persistence.
- **Zero-Build Architecture:** The UI must run natively out of FastAPI without requiring node, npm, or complex build bundles.
- **Strict TDD:** Failing tests must be written first for API and web routes before implementation.

---

### Task 1: Dashboard Analytics & Lead Query Endpoints

**Files:**
- Modify: `RevOpsAI/src/api/routes.py`
- Modify: `RevOpsAI/src/db/repository.py`
- Test: `RevOpsAI/tests/test_dashboard_api.py`

**Interfaces:**
- Consumes: `TenantScopedRepository`, `PersistentApprovalStore`, `Session`.
- Produces: 
  - `GET /api/v1/dashboard/stats?tenant_id=...`: Returns KPI summary (`total_leads`, `qualified_count`, `pending_approval_count`, `sent_count`, `interested_count`, `opt_out_count`, `qualification_rate`).
  - `GET /api/v1/dashboard/leads?tenant_id=...&state=...`: Returns list of prospects filtered by tenant and optional lifecycle state.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_dashboard_api.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.api.routes import get_dashboard_stats, get_dashboard_leads

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_dashboard_stats_calculation(db_session):
    repo = TenantScopedRepository(session=db_session, tenant_id="t_stats")
    
    # 1 lead pending
    l1 = Prospect(tenant_id="t_stats", name="Clinica A", url="http://a.es", score=80, state=ProspectState.PENDING_APPROVAL)
    # 1 lead interested
    l2 = Prospect(tenant_id="t_stats", name="Clinica B", url="http://b.es", score=90, state=ProspectState.INTERESTED)
    # 1 lead discarded
    l3 = Prospect(tenant_id="t_stats", name="Clinica C", url="http://c.es", score=40, state=ProspectState.DISCARDED)
    
    repo.save_prospect(l1)
    repo.save_prospect(l2)
    repo.save_prospect(l3)
    
    stats = repo.get_stats()
    assert stats["total_leads"] == 3
    assert stats["pending_approval_count"] == 1
    assert stats["interested_count"] == 1
    assert stats["discarded_count"] == 1
    assert stats["qualified_count"] == 2
    assert stats["qualification_rate"] == 66.7

def test_dashboard_leads_filtered_by_state(db_session):
    repo = TenantScopedRepository(session=db_session, tenant_id="t_filter")
    l1 = Prospect(tenant_id="t_filter", name="Clinica 1", url="http://1.es", state=ProspectState.PENDING_APPROVAL)
    l2 = Prospect(tenant_id="t_filter", name="Clinica 2", url="http://2.es", state=ProspectState.SENT)
    repo.save_prospect(l1)
    repo.save_prospect(l2)
    
    pending = repo.list_prospects(state=ProspectState.PENDING_APPROVAL.value)
    assert len(pending) == 1
    assert pending[0].name == "Clinica 1"
    
    all_leads = repo.list_prospects()
    assert len(all_leads) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_dashboard_api.py -v`
Expected: FAIL con `AttributeError: 'TenantScopedRepository' object has no attribute 'get_stats'`.

- [ ] **Step 3: Write minimal implementation**

En `RevOpsAI/src/db/repository.py`:
- Implementar `get_stats() -> dict[str, Any]` calculando conteos por estado y tasa de calificación.
- Implementar `list_prospects(state: str | None = None) -> list[Prospect]`.

En `RevOpsAI/src/api/routes.py`:
- Agregar endpoints:
  - `@app.get("/api/v1/dashboard/stats")`
  - `@app.get("/api/v1/dashboard/leads")`

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_dashboard_api.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/db/repository.py RevOpsAI/src/api/routes.py RevOpsAI/tests/test_dashboard_api.py
git commit -m "feat(api): implement dashboard analytics stats and filtered lead query endpoints"
```

---

### Task 2: High-End Anti-AI-Slop Web Dashboard Frontend

**Files:**
- Create: `RevOpsAI/src/web/templates/dashboard.html`
- Create: `RevOpsAI/src/web/static/dashboard.css`
- Create: `RevOpsAI/src/web/static/dashboard.js`
- Modify: `RevOpsAI/src/api/routes.py` (mount static files directory and serve `/dashboard`)
- Test: `RevOpsAI/tests/test_web_routes.py`

**Interfaces:**
- Consumes: `/api/v1/dashboard/stats`, `/api/v1/dashboard/leads`, `/api/v1/approval/action`.
- Produces:
  - `GET /dashboard`: Returns high-end HTML dashboard interface.
  - Interactive UI:
    - 4 Metric cards (Total Procesados, % Calificación, En Revisión Humana, Interesados).
    - 4-column Kanban board (Pendientes de Revisión, Enviados, Interesados, Descartados/Opt-Out).
    - Slide-over Inspection Drawer for detailed microdiagnosis, gap breakdown, proposal preview, and approval/rejection actions.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_web_routes.py
import pytest
from fastapi.testclient import TestClient
from RevOpsAI.src.api.routes import app

client = TestClient(app)

def test_dashboard_page_serves_html():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RevOps AI" in response.text
    assert "Human-in-the-Loop" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_web_routes.py -v`
Expected: FAIL con 404 (ruta no existe).

- [ ] **Step 3: Write minimal implementation**

Crear:
- `RevOpsAI/src/web/static/dashboard.css`:
  - Diseño monocromático profundo inspirado en Linear/Raycast (`--bg-primary: #0a0a0c`, `--surface-1: #121216`, `--surface-2: #18181f`).
  - Bordes hairline de 1px (`rgba(255, 255, 255, 0.08)`).
  - Acentos sobrios: esmeralda (`#10b981`) para calificados/interesados, ámbar (`#f59e0b`) para pendientes, carmesí (`#ef4444`) para bajas/opt-out.
  - Transiciones snappies con curvas físicas `cubic-bezier(0.16, 1, 0.3, 1)`.
- `RevOpsAI/src/web/static/dashboard.js`:
  - Carga asíncrona de métricas y leads por tenant.
  - Renderizado reactivo sin parpadeos (*Zero Layout Shift*).
  - Apertura fluida de modal/drawer de inspección de microdiagnóstico y propuesta.
  - Ejecución de acciones de aprobación y rechazo en un clic con retroalimentación inmediata en la UI.
- `RevOpsAI/src/web/templates/dashboard.html`:
  - Encabezado con selector de tenant, estado del sistema y métricas KPI.
  - Tablero Kanban organizado por columnas de estado.
  - Drawer lateral para revisión de microdiagnóstico y edición/aprobación de copy.
- En `RevOpsAI/src/api/routes.py`:
  - Montar `StaticFiles(directory="RevOpsAI/src/web/static")` en `/static`.
  - Servir `dashboard.html` en `GET /dashboard`.

- [ ] **Step 4: Run test to verify it passes**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_web_routes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/web/ RevOpsAI/src/api/routes.py RevOpsAI/tests/test_web_routes.py
git commit -m "feat(web): implement bespoke human-in-the-loop dashboard with kanban board and inspection drawer"
```

---

### Task 3: Interactive Verification & Demo Integration

**Files:**
- Modify: `RevOpsAI/demo.py`
- Test: `RevOpsAI/tests/test_dashboard_integration.py`

**Interfaces:**
- Consumes: Pipeline, Repository, Database Session, Web UI.
- Produces:
  - Integration test verifying end-to-end flow: Ingest -> Pending on Kanban -> Approve via API -> Move to Sent/Interested.
  - Updated `demo.py` with option to seed sample clinics directly into the database for live visual inspection in the dashboard.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_dashboard_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.db.persistent_approval_store import PersistentApprovalStore
from RevOpsAI.src.core.models import Prospect, ProspectState

def test_end_to_end_dashboard_approval_lifecycle():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = lambda: Session(engine)
    
    store = PersistentApprovalStore(session_factory=session_factory)
    
    # 1. Ingest lead
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Provenza",
        url="https://dentalprovenza.es",
        score=85,
        research_summary="Sin WhatsApp ni cita online",
        draft_message="Estimado equipo de Clínica Dental Provenza...",
        state=ProspectState.PENDING_APPROVAL
    )
    store.add(lead)
    
    # 2. Check pending
    pending = store.get_pending("tenant_dental")
    assert len(pending) == 1
    assert pending[0].id == lead.id
    
    # 3. Approve via store
    approved = store.approve(lead_id=lead.id, tenant_id="tenant_dental", actor="Dr. Juan Martinez")
    assert approved.state == ProspectState.APPROVED
    
    # 4. Verify no longer pending
    assert len(store.get_pending("tenant_dental")) == 0
    
    # 5. Check stats in repository
    with session_factory() as session:
        repo = TenantScopedRepository(session, "tenant_dental")
        stats = repo.get_stats()
        assert stats["pending_approval_count"] == 0
        assert stats["qualified_count"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/test_dashboard_integration.py -v`
Expected: PASS/FAIL depending on session setup.

- [ ] **Step 3: Update demo.py and verify all integration tests pass**

- [ ] **Step 4: Run full test suite**

Run: `& "C:\Users\JESUS\AppData\Local\Programs\Python\Python311\python.exe" -m pytest RevOpsAI/tests/ -v`
Expected: PASS (all tests green).

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/demo.py RevOpsAI/tests/test_dashboard_integration.py
git commit -m "feat(demo): update interactive demo with dashboard seeding and end-to-end integration tests"
```

---

## Plan Self-Review Check
- [x] **Spec Coverage:** Cubre endpoints de analíticas (Task 1), Dashboard UI Kanban con diseño Anti-AI-Slop (Task 2) y pruebas integradas end-to-end con script demo (Task 3).
- [x] **Anti-AI Design Rules:** Estricto cumplimiento de paleta monocromática física, bordes hairline, sin gradientes púrpuras genéricos ni tarjetas plantilla.
- [x] **No Placeholders:** Todos los métodos, CSS y JavaScript están planificados para ser autónomos y completos.
