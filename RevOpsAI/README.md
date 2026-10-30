# RevOps AI: Master Template — Departamento Digital de Ingresos Multi-Agente

> **Plantilla Maestra de Ingeniería de Ingresos B2B Multi-Agente con Perímetro Zero-Trust, Gobernanza Human-in-the-Loop y Arquitectura 70/30 Reutilizable.**

---

## 1. Visión General del Sistema

**RevOps AI** es una solución empresarial de prospección comercial, auditoría técnica y captación de clientes de ciclo cerrado diseñada para operar como un **Departamento de Ingresos Digital Autónomo**.

Inicialmente calibrado para el sector de **Clínicas Médicas y Odontológicas**, el sistema implementa una arquitectura modular donde el **70% del núcleo (FSM, orquestación, seguridad, persistencia, dashboard y conectores) es agnóstico**, y el **30% restante se define declarativamente en archivos YAML** para adaptarse a cualquier otra vertical (Inmobiliarias, Despachos de Abogados, Consultoría B2B) en menos de 10 minutos.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               PERÍMETRO ZERO-TRUST                    │
                    │   InputSanitizer ──────► PIIScrubber (Masking DNI/Tel) │
                    └───────────────────────────┬────────────────────────────┘
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PIPELINE DETERMINISTA DE 9 AGENTES                               │
│                                                                                                     │
│  [1. Oportunidades] ──► [2. Investigación] ──► [3. Microdiagnóstico] ──► [4. Scoring Ponderado]     │
│       (Scraper)              (Keywords)             (AuditAgent)               (Gap Formula)        │
│                                                                                      │              │
│  [8. Sync CRM]      ◄── [7. Seguimiento]   ◄── [6. Despacho Multi]   ◄── [5. Copywriter Consultivo] │
│   (HubSpot/GHL)         (FollowUpAgent)        (Email RFC / WA Meta)          (Borrador Propuesta)  │
│                                                                                      ▲              │
└──────────────────────────────────────────────────────────────────────────────────────┼──────────────┘
                                                                                       │
                                                                           ┌───────────┴──────────┐
                                                                           │  BANDEJA HUMAN-IN-    │
                                                                           │  THE-LOOP (KANBAN)   │
                                                                           │  Aprobar / Descartar │
                                                                           └──────────────────────┘
```

---

## 2. Los 9 Agentes Especializados

| # | Agente | Responsabilidad Técnica |
|---|---|---|
| **1** | **Scraper de Oportunidades** | Ingesta segura de HTML/sitio web, saneamiento y eliminación de scripts maliciosos. |
| **2** | **Research Agent** | Detección de canales activos (WhatsApp, Reserva Online, Diacríticos españoles y especialidades). |
| **3** | **Commercial Audit Agent** | Análisis de fricciones comerciales con **Guardarraíl Legal**: aborta de inmediato ante diagnósticos médicos. |
| **4** | **Scoring Agent** | Evaluación numérica (0-100) ponderada por YAML (`min_qualification_score: 65`). Descarte preventivo. |
| **5** | **Copywriter Consultivo** | Redacción de propuesta personalizada con disclaimers legales, registrando en bandeja de aprobación. |
| **6** | **Dispatch Agent** | Despacho outbound (Email con cabeceras RFC 8058 `List-Unsubscribe` y WhatsApp Cloud API v21.0). |
| **7** | **Follow-Up Cadence Agent** | Seguimiento a 3 y 7 días con límite estricto de 2 reintentos para prevenir fatiga y spam. |
| **8** | **CRM Sync Connector** | Sincronización bidireccional automática hacia **HubSpot**, **GoHighLevel** o Webhooks corporativos. |
| **9** | **Supervisor / Orchestrator** | Control del ciclo de vida FSM determinista, manejo de fallos y aislamiento por inquilino (`tenant_id`). |

---

## 3. Perímetro Zero-Trust & Blindaje Legal

1. **Cero Responsabilidad Médica:** El agente auditor tiene prohibido terminantemente emitir opiniones o diagnósticos de salud (`diagnósticos_médicos_específicos`, `tratamientos_farmacológicos`). Solo audita canales digitales de captación.
2. **Cumplimiento Anti-Spam (RGPD & LSSI-CE):**
   - Correo saliente con cabeceras estándar **RFC 8058** (`List-Unsubscribe: <One-Click>`).
   - Disclaimers consultivos profesionales obligatorios.
3. **Baja Automática Instantánea (*Opt-Out*):** Cualquier respuesta del cliente solicitando la baja ("no me interesa", "baja", "no enviar más") activa de inmediato `is_blacklisted = True` y pasa el prospecto al estado terminal `OPT_OUT`.
4. **Row-Level Security (RLS) en PostgreSQL:** Las consultas filtran a nivel de motor de base de datos (`ALTER TABLE prospects ENABLE ROW LEVEL SECURITY`) mediante variables de sesión multi-inquilino.

---

## 4. Cómo Adaptar a Otro Sector en 10 Minutos (70/30)

Para usar esta misma infraestructura con otro tipo de clientes (ej. **Despachos de Abogados**):

1. Crea un archivo YAML en `RevOpsAI/config/sectors/abogados.yaml`:
```yaml
sector: "abogados_y_despachos"
min_qualification_score: 70

scoring_weights:
  missing_whatsapp: 30
  missing_online_booking: 35
  no_clear_specialties: 25
  bad_mobile_ux: 10

forbidden_topics:
  - "asesoramiento_juridico_vinculante"
  - "promesa_de_ganar_juicio"
  - "litigios_penales_especificos"
```
2. Instancia el orquestador apuntando al nuevo sector:
```python
from RevOpsAI.src.core.config_loader import load_sector_config
from RevOpsAI.src.core.pipeline import PipelineOrchestrator

legal_config = load_sector_config("RevOpsAI/config/sectors/abogados.yaml")
orchestrator = PipelineOrchestrator(config=legal_config)
```
¡Todo el resto del sistema (Scraper, Scoring, Base de datos, Dashboard Kanban y conectores) funciona sin modificar una sola línea de código!

---

## 5. Guía de Inicio Rápido (Local)

### Requisitos
- Python 3.11+

### 1. Ejecutar el Demo Interactivo
El script demuestra los 6 casos de estudio (clínica con gaps, clínica ya optimizada, intento de inyección de prompt, intento de diagnóstico médico, baja automática y siembra del dashboard):
```bash
python RevOpsAI/demo.py
```

### 2. Iniciar el Servidor y Panel Kanban
```bash
python -m uvicorn RevOpsAI.src.api.main:app --port 8000 --reload
```
Abre en tu navegador:
👉 **[http://localhost:8000/dashboard](http://localhost:8000/dashboard)**

- Inspecciona las métricas de captación en vivo.
- Haz clic en cualquier tarjeta para abrir el **Drawer Lateral de Inspección** con el desglose de fricciones y el borrador de propuesta.
- Haz clic en **"Aprobar y Despachar"** para lanzar el mensaje con trazabilidad de auditoría.

### 3. Ejecutar la Suite de Pruebas Automatizadas
```bash
python -m pytest RevOpsAI/tests/ -v
# 120 tests pasando al 100%
```

---

## 6. Despliegue en la Nube y Producción

### Opción A: Despliegue en Render (Recomendado para Beta Pública)

El repositorio incluye soporte nativo para **Render** con infraestructura declarativa (`render.yaml`) y contenedor Docker optimizado con puerto dinámico:

1. **Subir cambios a GitHub**:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin master
   ```
2. **Crear Web Service en Render**:
   - Conecta tu cuenta de GitHub en [dashboard.render.com](https://dashboard.render.com).
   - Crea un **Web Service** apuntando al repositorio con Runtime **Docker** y `Dockerfile Path`: `RevOpsAI/Dockerfile`.
3. **Variables de Entorno en Render**:
   - `DATABASE_URL`: URI de conexión Session Pooler de Supabase PostgreSQL (puerto 5432).
   - `ENVIRONMENT`: `production`
   - `DASHBOARD_AUTH_ENABLED`: `true`
   - `DASHBOARD_USERNAME`: `admin`
   - `DASHBOARD_PASSWORD`: *(tu clave segura)*
   - `CRON_SECRET_TOKEN`: *(tu token secreto para tareas cron)*
4. **Verificación**: Render monitorea el endpoint `/health` y genera automáticamente una URL con certificado SSL gratuito (`https://...onrender.com/dashboard`).

### Opción B: Despliegue Local con Docker Compose

Para entornos locales o servidores dedicados (VPS/On-Premise):

```bash
# 1. Configurar variables de entorno
cp RevOpsAI/.env.example RevOpsAI/.env

# 2. Levantar API, Dashboard y PostgreSQL con RLS
cd RevOpsAI
docker compose up -d --build
```
La aplicación estará disponible en `http://localhost:8000/dashboard` y la base de datos aplicará automáticamente el esquema con RLS `01_schema_rls.sql`.

---

## 7. Modelo de Comercialización & Monetización

Este sistema está diseñado para ser comercializado bajo tres modalidades de alto margen:

1. **Agencia RevOps As-a-Service:**
   - **Retainer mensual:** 1.500 € – 3.500 €/mes por clínica/franquicia.
   - **Propuesta de valor:** "Garantizamos 15 a 30 primeras citas de implantes y estética al mes auditando y contactando clínicamente a los pacientes que hoy abandonan tu web".
2. **Plantilla de Software / SaaS White-Label:**
   - Licencia de uso para otras agencias de marketing médico por 299 € – 599 €/mes por tenant.
3. **Comisión por Paciente Cualificado (Pay-per-Show):**
   - Cobro de 50 € – 100 € por cada paciente que asista a su cita valorativa gestionada por el conector de WhatsApp.

---

### Licencia & Autoría
Desarrollado bajo metodología **Superpowers** con estándares de **Anti-AI Design Engineering** y **Zero-Trust Security**.
