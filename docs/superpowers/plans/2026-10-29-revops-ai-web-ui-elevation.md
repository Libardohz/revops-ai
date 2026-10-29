# RevOps AI Web UI Elevation & Live Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the RevOps AI Human-in-the-Loop web console into a high-density, tactile, anti-AI-slop command center (Linear/Bloomberg aesthetic) featuring in-app live URL audits, real-time filtering, multi-channel outreach preview (Email/WhatsApp), and audit trail inspection.

**Architecture:** Extend FastAPI routes with `/api/v1/prospects/audit-url` and `/api/v1/audit/logs`. Redesign `dashboard.html`, `dashboard.css`, and `dashboard.js` with strict design token discipline, 1px hairline borders, dark zinc palette (`#09090b`), vector SVG icons, zero generic gradients/emojis, and modular state-driven client logic.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 ORM, Vanilla ECMAScript 2024, CSS Modern Custom Properties, SVG Icons (Lucide-style vectors).

---

### File Structure Map

- **Backend API & Data:**
  - `RevOpsAI/src/api/routes.py`: Add `POST /api/v1/prospects/audit-url` (live URL fetching + multi-agent execution) and `GET /api/v1/audit/logs` (tenant audit logs).
  - `RevOpsAI/tests/test_api_audit_routes.py`: Unit and integration tests for audit routes and tenant isolation.
- **Frontend Architecture:**
  - `RevOpsAI/src/web/templates/dashboard.html`: Complete semantic redesign without emojis, strictly vector SVGs, live audit modal, search & chip filter bar, card micro-tags, multi-tab slide drawer, discard modal.
  - `RevOpsAI/src/web/static/dashboard.css`: Hardcore anti-AI design system, dark zinc tokens (`#09090b` / `#18181b`), hairline 1px borders, tabular figures, cubic-bezier transitions, zero layout shift, responsive breakpoints.
  - `RevOpsAI/src/web/static/dashboard.js`: State manager, live URL audit stepper, instant search/filter, quick card actions, multi-channel outreach preview, CSV/JSON export, audit log renderer.

---

### Task 1: Backend Audit URL & Audit Logs Endpoints

- [x] **Step 1.1**: Write failing unit tests in `RevOpsAI/tests/test_api_audit_routes.py` verifying `POST /api/v1/prospects/audit-url` and `GET /api/v1/audit/logs`.
- [x] **Step 1.2**: Implement `AuditUrlRequest` model, URL fetcher with timeout/sanitization, and `/prospects/audit-url` route in `RevOpsAI/src/api/routes.py`.
- [x] **Step 1.3**: Implement `/audit/logs` route in `RevOpsAI/src/api/routes.py` querying `AuditLogORM` through `TenantScopedRepository`.
- [x] **Step 1.4**: Run pytest to confirm all tests in `test_api_audit_routes.py` pass.
- [x] **Step 1.5**: Commit Task 1 changes.

---

### Task 2: Strict Anti-AI Design System & Layout Structure (`dashboard.html` & `dashboard.css`)

- [x] **Step 2.1**: Update `RevOpsAI/src/web/templates/dashboard.html` to eliminate all emojis, insert clean vector SVGs, add "+ Auditar Clínica" modal trigger, search toolbar, quick-action card slots, and 3-tab slide-over drawer (`Microdiagnóstico`, `Copy & Canales`, `Historial`).
- [x] **Step 2.2**: Refactor `RevOpsAI/src/web/static/dashboard.css` using strict Dark Zinc tokens (`#09090b`, `#121215`, `#18181b`, `#27272a`), hairline borders (`rgba(255, 255, 255, 0.08)`), tabular figures, no generic drop shadows, and responsive grid layout.
- [x] **Step 2.3**: Verify CSS against Anti-AI Slop checklist (no purple gradients, no glow, no emojis, clean WCAG AA contrast).
- [x] **Step 2.4**: Commit Task 2 changes.

---

### Task 3: Interactive Command Center Logic & Features (`dashboard.js`)

- [x] **Step 3.1**: Implement live URL audit modal handler in `RevOpsAI/src/web/static/dashboard.js` with stage-by-stage multi-agent stepper.
- [x] **Step 3.2**: Implement real-time instant search and chip filtering (`Todos`, `Score ≥ 80`, `Sin WhatsApp`, `Sin Cita Online`).
- [x] **Step 3.3**: Implement card quick-actions (1-click Approve/Reject directly from Kanban cards).
- [x] **Step 3.4**: Implement multi-tab slide drawer with Channel Switcher (Email vs WhatsApp preview) and live audit log viewer.
- [x] **Step 3.5**: Implement CSV/JSON pipeline export utility.
- [x] **Step 3.6**: Commit Task 3 changes.

---

### Task 4: End-to-End Verification & Live Testing

- [x] **Step 4.1**: Run complete pytest suite (`pytest RevOpsAI/tests/ -v`) ensuring zero regressions.
- [x] **Step 4.2**: Test live URL audit endpoint via HTTP request and verify card appears in Kanban and database.
- [x] **Step 4.3**: Verify responsive layout and tactile UI at `http://localhost:8000/dashboard`.
- [x] **Step 4.4**: Final commit and summary report.
