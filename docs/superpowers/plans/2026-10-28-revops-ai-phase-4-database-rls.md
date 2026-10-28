# RevOpsAI: Base de Datos Persistente con RLS y Aislamiento Multi-Tenant (Fase 4) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el almacenamiento en memoria por una capa de base de datos relacional persistente con SQLAlchemy 2.0 y aislamiento estricto por `tenant_id`, incluyendo el esquema DDL de Row-Level Security (RLS) para PostgreSQL y el registro inmutable de auditoría (`audit_logs`).

**Architecture:** Capa de datos en `RevOpsAI/src/db/`. Patrón Repository scoped por tenant (`TenantScopedRepository`) que inyecta automáticamente el filtro de tenant en cada consulta. DDL formal con RLS en `schema_rls.sql` para despliegues PostgreSQL (Supabase/AWS) y compatibilidad con SQLite para ejecución local y tests sin dependencias de red.

**Tech Stack:** Python 3.11+, SQLAlchemy 2.0+, Pydantic v2, SQLite (local) / PostgreSQL (producción), Pytest.

**Spec:** `RevOpsAI/docs/2026-10-27-design-spec.md` (Sección 2.2 y 3: Aislamiento Multi-Tenant & RLS).

## Global Constraints
- Python 3.11+ únicamente.
- Cero consultas SQL dinámicas o concatenaciones de strings; uso estricto de SQLAlchemy 2.0 parametrizado.
- Todas las operaciones de lectura y escritura deben exigir y validar el `tenant_id`.
- Registro obligatorio en `audit_logs` ante cualquier acción de aprobación, rechazo o baja (`OPT_OUT`).
- TDD estricto: test rojo -> implementación verde -> commit.

---

### Task 1: Modelos Relacionales ORM y Conexión de Base de Datos

**Files:**
- Create: `RevOpsAI/src/db/session.py`
- Create: `RevOpsAI/src/db/models.py`
- Test: `RevOpsAI/tests/test_db_models.py`

**Interfaces:**
- Consumes: Configuración de conexión / SQLite URL.
- Produces: `Base`, `ProspectORM`, `AuditLogORM`, `get_engine()`, `get_session_factory()`.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_db_models.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base, ProspectORM, AuditLogORM
from RevOpsAI.src.core.models import ProspectState

def test_create_and_query_prospect_orm():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        lead = ProspectORM(
            id="lead_test_01",
            tenant_id="tenant_dental",
            name="Clinica Dental Norte",
            url="https://dentalnorte.es",
            state=ProspectState.INGESTED.value,
            score=75
        )
        session.add(lead)
        session.commit()
        
        queried = session.query(ProspectORM).filter_by(id="lead_test_01").first()
        assert queried is not None
        assert queried.tenant_id == "tenant_dental"
        assert queried.score == 75
        assert queried.is_blacklisted is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_db_models.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/db/models.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class ProspectORM(Base):
    __tablename__ = "prospects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="INGESTED")
    score: Mapped[int] = mapped_column(Integer, default=0)
    research_summary: Mapped[str] = mapped_column(Text, default="")
    draft_message: Mapped[str] = mapped_column(Text, default="")
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lead_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
```

Crear `RevOpsAI/src/db/session.py`:
```python
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from RevOpsAI.src.db.models import Base

def get_engine(db_url: str = "sqlite:///RevOpsAI/data/revops.db"):
    if db_url.startswith("sqlite"):
        # Asegurar directorio de datos si es local
        db_path = db_url.replace("sqlite:///", "")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(db_url, echo=False)

def init_db(engine):
    Base.metadata.create_all(engine)

def get_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_db_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/db/ RevOpsAI/tests/test_db_models.py
git commit -m "feat(db): implement relational models and database session manager"
```

---

### Task 2: Repositorio con Aislamiento Estricto por Tenant (TenantScopedRepository)

**Files:**
- Create: `RevOpsAI/src/db/repository.py`
- Test: `RevOpsAI/tests/test_repository.py`

**Interfaces:**
- Consumes: `Session` de SQLAlchemy y `tenant_id` obligatorio.
- Produces: 
  - `save_prospect(Prospect) -> Prospect`
  - `get_prospect(lead_id: str) -> Prospect | None` (nunca retorna si el tenant_id no coincide)
  - `list_pending_approval() -> list[Prospect]`
  - `log_audit(lead_id: str, actor: str, action: str, reason: str)`

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_repository.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.core.models import Prospect, ProspectState

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_tenant_cannot_read_or_update_other_tenant_prospect(db_session):
    repo_alpha = TenantScopedRepository(session=db_session, tenant_id="tenant_alpha")
    repo_beta = TenantScopedRepository(session=db_session, tenant_id="tenant_beta")
    
    lead = Prospect(tenant_id="tenant_alpha", name="Clinica Alpha", url="http://alpha.es")
    repo_alpha.save_prospect(lead)
    
    # Tenant Alpha puede leer su lead
    assert repo_alpha.get_prospect(lead.id) is not None
    
    # Tenant Beta recibe None al intentar buscar el lead de Alpha
    assert repo_beta.get_prospect(lead.id) is None
    
    # Tenant Beta no ve el lead en su lista de pendientes
    lead.state = ProspectState.PENDING_APPROVAL
    repo_alpha.save_prospect(lead)
    assert len(repo_alpha.list_pending_approval()) == 1
    assert len(repo_beta.list_pending_approval()) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_repository.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

```python
# RevOpsAI/src/db/repository.py
import uuid
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import ProspectORM, AuditLogORM
from RevOpsAI.src.core.models import Prospect, ProspectState

class TenantScopedRepository:
    """Repository pattern strictly enforcing tenant boundaries across all operations."""

    def __init__(self, session: Session, tenant_id: str):
        if not tenant_id:
            raise ValueError("tenant_id obligatorio para operaciones de repositorio")
        self.session = session
        self.tenant_id = tenant_id

    def save_prospect(self, prospect: Prospect) -> Prospect:
        if prospect.tenant_id != self.tenant_id:
            raise PermissionError(f"Intento de persistir prospect con tenant_id mismatched: {prospect.tenant_id} != {self.tenant_id}")
        
        orm = self.session.query(ProspectORM).filter_by(id=prospect.id, tenant_id=self.tenant_id).first()
        if not orm:
            orm = ProspectORM(
                id=prospect.id,
                tenant_id=self.tenant_id,
                name=prospect.name,
                url=prospect.url,
            )
            self.session.add(orm)

        orm.state = prospect.state.value
        orm.score = prospect.score
        orm.research_summary = prospect.research_summary
        orm.draft_message = prospect.draft_message
        orm.is_blacklisted = prospect.is_blacklisted
        self.session.commit()
        return prospect

    def get_prospect(self, lead_id: str) -> Prospect | None:
        orm = self.session.query(ProspectORM).filter_by(id=lead_id, tenant_id=self.tenant_id).first()
        if not orm:
            return None
        return Prospect(
            id=orm.id,
            tenant_id=orm.tenant_id,
            name=orm.name,
            url=orm.url,
            state=ProspectState(orm.state),
            score=orm.score,
            research_summary=orm.research_summary,
            draft_message=orm.draft_message,
            is_blacklisted=orm.is_blacklisted,
        )

    def list_pending_approval(self) -> list[Prospect]:
        records = (
            self.session.query(ProspectORM)
            .filter_by(tenant_id=self.tenant_id, state=ProspectState.PENDING_APPROVAL.value)
            .all()
        )
        return [
            Prospect(
                id=r.id,
                tenant_id=r.tenant_id,
                name=r.name,
                url=r.url,
                state=ProspectState(r.state),
                score=r.score,
                research_summary=r.research_summary,
                draft_message=r.draft_message,
                is_blacklisted=r.is_blacklisted,
            )
            for r in records
        ]

    def log_audit(self, lead_id: str, actor: str, action: str, reason: str = "") -> None:
        log_entry = AuditLogORM(
            id=f"audit_{uuid.uuid4().hex[:12]}",
            tenant_id=self.tenant_id,
            lead_id=lead_id,
            actor=actor,
            action=action,
            reason=reason,
        )
        self.session.add(log_entry)
        self.session.commit()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_repository.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/db/repository.py RevOpsAI/tests/test_repository.py
git commit -m "feat(db): implement TenantScopedRepository with strict isolation and audit logs"
```

---

### Task 3: Esquema DDL de Row-Level Security (RLS) para PostgreSQL e Integración con ApprovalStore

**Files:**
- Create: `RevOpsAI/src/db/schema_rls.sql`
- Create: `RevOpsAI/src/db/persistent_approval_store.py`
- Test: `RevOpsAI/tests/test_persistent_approval_store.py`

**Interfaces:**
- Consumes: `TenantScopedRepository` y DDL SQL.
- Produces: `PersistentApprovalStore` que reemplaza o adapta el `ApprovalStore` con persistencia en BD y registro de auditoría.

- [ ] **Step 1: Write the failing test**

```python
# RevOpsAI/tests/test_persistent_approval_store.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from RevOpsAI.src.db.models import Base, AuditLogORM
from RevOpsAI.src.db.persistent_approval_store import PersistentApprovalStore
from RevOpsAI.src.core.models import Prospect, ProspectState

@pytest.fixture
def session_factory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return lambda: Session(engine)

def test_persistent_approval_store_approves_and_logs_audit(session_factory):
    store = PersistentApprovalStore(session_factory=session_factory)
    lead = Prospect(tenant_id="t1", name="Clinica Dental Norte", url="http://dental.es")
    lead.state = ProspectState.PENDING_APPROVAL
    store.add(lead)
    
    # 1. Recuperar pendientes desde la base de datos
    pending = store.get_pending(tenant_id="t1")
    assert len(pending) == 1
    assert pending[0].id == lead.id
    
    # 2. Aprobar prospecto
    approved = store.approve(lead_id=lead.id, tenant_id="t1", actor="operador_humano")
    assert approved.state == ProspectState.APPROVED
    assert len(store.get_pending(tenant_id="t1")) == 0
    
    # 3. Verificar registro inmutable en auditoría
    with session_factory() as sess:
        audit = sess.query(AuditLogORM).filter_by(lead_id=lead.id).first()
        assert audit is not None
        assert audit.action == "APPROVE"
        assert audit.actor == "operador_humano"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest RevOpsAI/tests/test_persistent_approval_store.py -v`
Expected: FAIL con `ImportError`.

- [ ] **Step 3: Write minimal implementation**

Crear `RevOpsAI/src/db/schema_rls.sql`:
```sql
-- RevOpsAI: Esquema PostgreSQL con Row-Level Security (RLS) Mandatorio

CREATE TABLE IF NOT EXISTS prospects (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    state VARCHAR(32) NOT NULL DEFAULT 'INGESTED',
    score INT DEFAULT 0,
    research_summary TEXT DEFAULT '',
    draft_message TEXT DEFAULT '',
    is_blacklisted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    lead_id VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    reason TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1. Habilitar RLS en tablas críticas
ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 2. Crear políticas de aislamiento estricto por sesión
-- El tenant_id debe coincidir exactamente con la variable de sesión inyectada por la conexión
CREATE POLICY tenant_isolation_prospects ON prospects
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_audit ON audit_logs
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
```

Crear `RevOpsAI/src/db/persistent_approval_store.py`:
```python
from collections.abc import Callable
from sqlalchemy.orm import Session
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.db.repository import TenantScopedRepository

class PersistentApprovalStore:
    """Persistent storage backed by relational database with tenant isolation and audit trails."""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def add(self, lead: Prospect) -> None:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=lead.tenant_id)
            repo.save_prospect(lead)

    def get_pending(self, tenant_id: str) -> list[Prospect]:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            return repo.list_pending_approval()

    def approve(self, lead_id: str, tenant_id: str, actor: str = "human_operator") -> Prospect:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            lead = repo.get_prospect(lead_id)
            if not lead:
                raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
            lead.transition_to(ProspectState.APPROVED)
            repo.save_prospect(lead)
            repo.log_audit(lead_id=lead_id, actor=actor, action="APPROVE", reason="")
            return lead

    def reject(self, lead_id: str, tenant_id: str, reason: str = "", actor: str = "human_operator") -> Prospect:
        with self.session_factory() as session:
            repo = TenantScopedRepository(session, tenant_id=tenant_id)
            lead = repo.get_prospect(lead_id)
            if not lead:
                raise KeyError(f"Prospecto {lead_id} no encontrado para este tenant")
            lead.transition_to(ProspectState.DISCARDED)
            repo.save_prospect(lead)
            repo.log_audit(lead_id=lead_id, actor=actor, action="REJECT", reason=reason)
            return lead
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest RevOpsAI/tests/test_persistent_approval_store.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add RevOpsAI/src/db/schema_rls.sql RevOpsAI/src/db/persistent_approval_store.py RevOpsAI/tests/test_persistent_approval_store.py
git commit -m "feat(db): implement PersistentApprovalStore with audit logging and PostgreSQL RLS schema"
```

---

## Plan Self-Review Check
- [x] **Spec Coverage:** Cubre persistencia relacional con SQLAlchemy (Task 1), aislamiento estricto por tenant en repositorio (Task 2), DDL de Row-Level Security en PostgreSQL y `PersistentApprovalStore` con auditoría inmutable (Task 3).
- [x] **No Placeholders:** Todos los códigos de modelos, repositorio y pruebas están completos y sin texto ambiguo.
- [x] **Type Consistency:** Modelos compatibles con `Prospect`, `ProspectState` y transiciones FSM validadas.
