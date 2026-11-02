"""
Generador Maestro de la Enciclopedia Técnica y Operativa de RevOps AI
Genera en Word (.docx) y PDF (.pdf) la documentación exhaustiva del SaaS:
- Guía operativa completa de usuario (paso a paso)
- Manual técnico interno de arquitectura, código, seguridad y bases de datos
- Guía de customización y mantenimiento (Front CSS/HTML/JS y Back Python/SQL)
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tc_pr.append(tcMar)

# ==============================================================================
# 1. MANUAL DE USUARIO EXHAUSTIVO (WORD)
# ==============================================================================
def generate_user_manual_docx(filepath):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        
    # Título Principal
    p = doc.add_paragraph()
    r0 = p.add_run("REVOPS AI · PLATAFORMA DE GENERACIÓN Y CONVERSIÓN DE PIPELINE B2B\n")
    r0.font.bold = True
    r0.font.size = Pt(10)
    r0.font.color.rgb = RGBColor(16, 185, 129)
    
    r1 = p.add_run("MANUAL DE USUARIO Y GUÍA DE OPERACIONES INTEGRAL")
    r1.font.bold = True
    r1.font.size = Pt(22)
    r1.font.color.rgb = RGBColor(15, 23, 42)
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(16)
    r_meta = p_meta.add_run("Versión Oficial 2.4 · Manual de Operación de Campo para SDRs, Closers y Gerentes Comerciales")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    
    # Cuadro Informativo
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    set_cell_background(c, "F8FAFC")
    set_cell_margins(c, 120, 120, 160, 160)
    cp = c.paragraphs[0]
    r_c = cp.add_run("PROPÓSITO DE ESTE MANUAL:\n")
    r_c.font.bold = True
    r_c.font.size = Pt(9.5)
    r_c.font.color.rgb = RGBColor(15, 23, 42)
    r_c2 = cp.add_run(
        "Esta guía instruye a los usuarios en la operativa diaria de RevOps AI: desde cómo ingresar a la plataforma y seleccionar unidades de negocio multi-tenant, hasta el uso del Bot Autónomo de descubrimiento territorial, auditorías masivas de páginas web, personalización de propuestas comerciales, despacho a WhatsApp con prefijo inteligente (+57), gestión de notas internas, cadencias de seguimiento (Día 1 / 3 / 7), exportación profesional a Excel y protocolos de Habeas Data (Ley 1581 de 2012)."
    )
    r_c2.font.size = Pt(9)
    r_c2.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # Capítulos
    chapters = [
        ("CAPÍTULO 1: ACCESO Y SEGURIDAD AL SISTEMA", [
            ("1.1 Inicio de Sesión", "Ingrese a la URL de su despliegue (ej. https://su-dominio.com/login). Ingrese el correo corporativo autorizado (ej. admin@hzsaas.com) y su contraseña de acceso maestro."),
            ("1.2 Protección Anti-Fuerza Bruta", "El sistema cuenta con un monitor de seguridad activo. Si se introducen 5 contraseñas incorrectas de manera consecutiva para una cuenta, el acceso se bloqueará temporalmente durante 5 minutos para salvaguardar la información."),
            ("1.3 Sesión Segura y Cierre", "Al autenticarse, el servidor emite una cookie cifrada HttpOnly imposible de interceptar por scripts maliciosos. Al finalizar su jornada, presione 'Cerrar sesión' en la esquina superior derecha para revocar el token.")
        ]),
        ("CAPÍTULO 2: GESTIÓN DE UNIDADES DE NEGOCIO (MULTI-TENANT)", [
            ("2.1 Selector de Tenant", "En la esquina superior izquierda del Command Center encontrará el desplegable 'Unidad de Negocio'. Permite alternar entre diferentes carteras o clientes (ej. 'Clínicas Privadas Madrid' y 'SaaS B2B Colombia')."),
            ("2.2 Aislamiento Absoluto de Datos", "Al cambiar de tenant, todo el tablero se recarga instantáneamente: las métricas de telemetría, el embudo de ventas, las tarjetas del Kanban y los historiales de auditoría quedan estrictamente limitados al tenant activo sin riesgo de mezcla de información.")
        ]),
        ("CAPÍTULO 3: PROSPECCIÓN Y AUDITORÍA DIGITAL (TRES MODOS)", [
            ("3.1 Modo 1: Bot de Prospección Autónoma (Piloto Automático)", "Ideal para abrir nuevos mercados sin listas previas. Haga clic en 'Bot Prospección Autónoma'. Seleccione la Ciudad (Montería, Medellín, Bogotá, Cali, Barranquilla), el Sector (Clínicas Odontológicas, Abogados, etc.) y la cantidad de empresas. Presione 'Lanzar Descubrimiento'. El bot buscará los dominios, auditará su infraestructura web en paralelo y cargará los prospectos listos con su diagnóstico en la columna de revisión."),
            ("3.2 Modo 2: Auditoría Masiva en Lote (Batch Audit)", "Ideal si usted ya tiene una lista de empresas extraída de Google Maps o directorios. Haga clic en 'Auditoría Masiva (Batch)'. Pegue las URLs (una por línea, ej: https://clinicaejemplo.com). Seleccione el sector y presione 'Procesar Lote'. El sistema analizará hasta 20 empresas de manera simultánea."),
            ("3.3 Modo 3: Auditoría Unitaria en Vivo", "Haga clic en 'Auditar URL en Vivo' o use un preset rápido. Ingrese el nombre de la empresa y la URL exacta. En menos de 3 segundos obtendrá el diagnóstico completo, la puntuación obtenida y el borrador de propuesta comercial.")
        ]),
        ("CAPÍTULO 4: TELEMETRÍA OPERATIVA Y FILTRADO AVANZADO", [
            ("4.1 Gráficos en Tiempo Real", "• Embudo HITL: Monitorea cuántas empresas se auditaron, cuántas precalificaron (score ≥ 70), cuántas están en seguimiento y cuántas confirmaron interés.\n• Radar de Brechas Digitales: Porcentaje exacto de empresas sin botón de WhatsApp y sin agenda en línea.\n• Histograma de Puntuación: Distribución visual de leads de Alto Valor (≥80 pts), Medios (65-79 pts) y Descartables (<65 pts)."),
            ("4.2 Barra de Filtros Rápidos", "• Chips de Brecha: Filtre con 1 clic entre 'Score ≥ 80', 'Sin WhatsApp' y 'Sin agenda en línea'.\n• Chips de Territorio: Aísle el tablero seleccionando 'Montería', 'Medellín', 'Bogotá' o 'Todas'.\n• Buscador Reactivo: Escriba cualquier término en el buscador (nombre, teléfono, URL, especialidad médica) para un filtrado instantáneo sin recargar la página.")
        ]),
        ("CAPÍTULO 5: REVISIÓN HUMANA (HITL) Y DESPACHO POR WHATSAPP", [
            ("5.1 El Cajón Lateral (Slide-Over Drawer)", "Al hacer clic en cualquier tarjeta del tablero se desplegará el panel de detalle con 4 pestañas especializadas: Diagnóstico, Propuesta, Notas & Cadencia y Trazabilidad."),
            ("5.2 Pestaña 1: Diagnóstico Técnico", "Revise el resumen de investigación elaborado por el scraper y la IA, la lista de brechas comerciales detectadas y los controles de seguridad aplicados."),
            ("5.3 Pestaña 2: Propuesta y Enriquecimiento de Decisor", "• Nombre del Decisor: Asigne el nombre del médico, gerente o director (ej. Dr. Carlos Pérez).\n• WhatsApp Celular: Ingrese el número (formato nacional 3001234567 o internacional +57 300 123 4567).\n• Edición de Propuesta: Ajuste el texto del mensaje si desea añadir un saludo personalizado.\n• Presione 'Guardar datos de contacto' para persistir los cambios."),
            ("5.4 Despacho Asistido en 1 Clic", "Presione el botón verde 'Abrir WhatsApp con Decisor'. El sistema validará el formato, añadirá automáticamente el prefijo de Colombia (+57), codificará el mensaje personalizado junto con la cláusula legal y abrirá la conversación en WhatsApp Web o la App de escritorio.\nPresione luego 'Aprobar y programar envío' para mover el prospecto a la columna '02. En seguimiento'."),
            ("5.5 Pestaña 3: Bitácora de Notas y Cadencia (Día 1 / 3 / 7)", "• Registre anotaciones comerciales: Disponibilidad de la recepcionista, horarios de llamada sugeridos u objeciones telefónicas.\n• Seleccione la fase de la cadencia: Día 1 (Primer contacto), Día 3 (Bump de seguimiento) o Día 7 (Cierre cordial).\n• Al guardar, la tarjeta en el tablero mostrará una insignia destacando su fase activa."),
            ("5.6 Oportunidad Ganada en 1 Clic", "Cuando un cliente responda positivamente en WhatsApp, presione directamente el botón verde 'Marcar Interesado' ubicado en la tarjeta. El prospecto se trasladará automáticamente a la columna '03. Interesados' y actualizará los KPIs en vivo."),
            ("5.7 Descarte y Lista Negra", "Si una empresa no encaja o está cerrada, presione 'Descartar' e indique el motivo. Si solicitan no recibir mensajes, el sistema la registrará en la lista de exclusión definitiva.")
        ]),
        ("CAPÍTULO 6: EXPORTACIÓN A EXCEL Y MANTENIMIENTO DE DATOS", [
            ("6.1 Exportación Nativa a Microsoft Excel (.xls)", "Haga clic en 'Exportar Excel' en la barra superior. Se descargará un archivo estructurado con codificación UTF-8 pura (tildes y eñes intactas) donde cada propuesta comercial preserva sus saltos de línea internos sin desordenar las filas."),
            ("6.2 Desactivar Datos Demo", "Haga clic en 'Desactivar datos demo' si desea vaciar los registros de demostración iniciales y dejar la bandeja lista para operar prospectos 100% reales.")
        ]),
        ("CAPÍTULO 7: PROTOCOLO LEGAL DE HABEAS DATA (COLOMBIA)", [
            ("7.1 Cumplimiento de la Ley 1581 de 2012", "Todo mensaje emitido por el sistema adjunta obligatoriamente al final: 'Comunicación comercial B2B conforme a la Ley 1581 de 2012 (Habeas Data Colombia). Responda BAJA para excluir su contacto.'"),
            ("7.2 Procedimiento ante Solicitud de Baja", "Si un destinatario responde 'BAJA', el operador debe descartar el prospecto con el motivo 'Baja legal'. El sistema nunca volverá a auditar ni redactar mensajes para ese dominio en dicho tenant.")
        ])
    ]
    
    for ch_title, sections in chapters:
        h1 = doc.add_heading(ch_title, level=1)
        h1.paragraph_format.space_before = Pt(16)
        h1.paragraph_format.space_after = Pt(6)
        for s_title, s_desc in sections:
            h2 = doc.add_heading(s_title, level=2)
            h2.paragraph_format.space_before = Pt(10)
            h2.paragraph_format.space_after = Pt(3)
            p = doc.add_paragraph(s_desc)
            p.paragraph_format.space_after = Pt(6)
            p.style.font.size = Pt(9.5)
            
    doc.save(filepath)
    print(f"Manual de usuario guardado en: {filepath}")

# ==============================================================================
# 2. MANUAL TÉCNICO INTERNO EXHAUSTIVO (WORD)
# ==============================================================================
def generate_technical_manual_docx(filepath):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        
    p = doc.add_paragraph()
    r0 = p.add_run("ARQUITECTURA DE SOFTWARE · SEGURIDAD ENTERPRISE · GUÍA DE MODIFICACIONES\n")
    r0.font.bold = True
    r0.font.size = Pt(10)
    r0.font.color.rgb = RGBColor(37, 99, 235)
    
    r1 = p.add_run("MANUAL TÉCNICO INTERNO, ARQUITECTURA Y GUÍA DE MODIFICACIÓN DEL SAAS")
    r1.font.bold = True
    r1.font.size = Pt(22)
    r1.font.color.rgb = RGBColor(15, 23, 42)
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(16)
    r_meta = p_meta.add_run("Especificación Completa de Ingeniería v2.4 · Audiencia: CTO, Desarrolladores Fullstack y DevOps")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    set_cell_background(c, "F1F5F9")
    set_cell_margins(c, 120, 120, 160, 160)
    cp = c.paragraphs[0]
    r_c = cp.add_run("SINOPSIS INTEGRAL DE INGENIERÍA:\n")
    r_c.font.bold = True
    r_c.font.size = Pt(9.5)
    r_c.font.color.rgb = RGBColor(15, 23, 42)
    r_c2 = cp.add_run(
        "Este documento constituye la enciclopedia técnica total de RevOps AI. Contiene la explicación exhaustiva de la arquitectura del micro-kernel FastAPI, el árbol completo de directorios y archivos, el pipeline de los 5 agentes de IA, el modelo relacional SQLAlchemy y sus migraciones DDL automáticas, el mecanismo de aislamiento Multi-Tenant forzado en repositorio, los algoritmos de Scoring y Anti-Prompt Injection, los unit economics detallados ($0.33 USD por 1,000 leads), y una GUÍA PASO A PASO para modificar cualquier parte del sistema: desde cambiar un color, tipografía o título en el frontend (HTML/CSS/JS), hasta añadir nuevos campos a la base de datos o endpoints en el backend."
    )
    r_c2.font.size = Pt(9)
    r_c2.font.color.rgb = RGBColor(51, 65, 85)
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    tech_chapters = [
        ("SECCIÓN 1: MAPA DE LA ESTRUCTURA DEL PROYECTO", [
            ("1.1 Árbol de Directorios y Responsabilidades",
             "El proyecto sigue una estructura limpia y desacoplada ubicada en 'RevOpsAI/':\n\n"
             "• RevOpsAI/src/api/: Contiene el servidor FastAPI (main.py), los endpoints REST (routes.py), webhooks de mensajería (webhooks.py) y el limitador de tasa anti-fuerza bruta (rate_limiter.py).\n"
             "• RevOpsAI/src/agents/: Los 5 agentes de inteligencia artificial y scraping:\n"
             "  - audit_agent.py / ingestion_agent: Ingesta web defensiva y extracción semántica de contenido.\n"
             "  - research_agent.py: Detección técnica de brechas digitales (WhatsApp, agenda, catálogo de servicios).\n"
             "  - scoring_agent.py: Motor de puntuación algorítmica de 0 a 100 con umbral de calificación.\n"
             "  - copywriter_agent.py: Redactor de propuestas personalizadas con cláusula legal de Habeas Data.\n"
             "  - autonomous_scout.py: Bot de descubrimiento territorial que busca empresas por ciudad y orquesta el pipeline.\n"
             "• RevOpsAI/src/core/: Modelos de dominio Pydantic (models.py), orquestador (pipeline.py) y cargador de configuración sectorial YAML (config_loader.py).\n"
             "• RevOpsAI/src/db/: Modelos de persistencia ORM (models.py), repositorio transaccional con aislamiento tenant (repository.py), motor de conexión y auto-migrador DDL (session.py).\n"
             "• RevOpsAI/src/security/: Sanitizador anti-prompt injection (sanitizer.py) y limpiador de datos personales PII (pii_scrubber.py).\n"
             "• RevOpsAI/src/web/: Plantillas HTML semánticas (templates/dashboard.html, login.html) y assets estáticos sin dependencias externas (static/dashboard.css, dashboard.js, tokens.css).\n"
             "• RevOpsAI/config/sectors/: Configuraciones YAML por industria (clinicas.yaml, abogados.yaml, inmobiliarias.yaml).\n"
             "• RevOpsAI/tests/: Suite integral de 131 pruebas unitarias y de integración (test_routes.py, test_isolation.py, test_compliance.py).")
        ]),
        ("SECCIÓN 2: ARQUITECTURA DEL BACKEND Y FLUJO DE DATOS", [
            ("2.1 Ciclo de Vida de una Petición",
             "1. El cliente envía una petición HTTP al backend FastAPI.\n"
             "2. El middleware de autenticación valida la cookie 'revops_session' desencriptando el token de sesión.\n"
             "3. El repositorio 'TenantScopedRepository' se instancia inyectando obligatoriamente el 'tenant_id' activo.\n"
             "4. Toda consulta a la base de datos aplica 'filter_by(tenant_id=self.tenant_id)' garantizando que ningún dato ajeno sea accesible.\n"
             "5. Las respuestas se serializan mediante esquemas Pydantic v2 de alta velocidad."),
            ("2.2 Algoritmo del Motor de Puntuación (Scoring)",
             "El archivo 'src/agents/scoring_agent.py' evalúa el prospecto según la fórmula matemática:\n"
             "Score = Base (50 puntos)\n"
             "+ Catálogo de Especialidades detectadas (hasta +20 puntos)\n"
             "- Ausencia de canal directo WhatsApp (-15 puntos de penalización comercial)\n"
             "- Ausencia de sistema de agendamiento online (-15 puntos de penalización comercial)\n\n"
             "Si el Score es ≥ 70 puntos, el prospecto pasa a estado PENDING_APPROVAL y se genera el borrador de propuesta. Si es menor, se clasifica en DISCARDED.")
        ]),
        ("SECCIÓN 3: MODELO DE BASE DE DATOS Y AUTO-MIGRACIONES DDL", [
            ("3.1 Estructura de la Tabla 'prospects'",
             "• id (VARCHAR PRIMARY KEY): Identificador único (ej. lead_monteria_01).\n"
             "• tenant_id (VARCHAR NOT NULL): Clave de particionamiento multi-tenant.\n"
             "• name, url (VARCHAR): Razón social y dirección web de la empresa.\n"
             "• state (VARCHAR): Ingested, Pending_Approval, Sent, Interested, Discarded, Opt_Out.\n"
             "• score (INTEGER): Puntuación calculada de 0 a 100.\n"
             "• research_summary, draft_message (TEXT): Diagnóstico y propuesta comercial.\n"
             "• contact_name, contact_phone (VARCHAR): Decisor comercial y WhatsApp con prefijo.\n"
             "• internal_notes (TEXT): Bitácora interna de llamadas y recepción.\n"
             "• city (VARCHAR): Territorio o ciudad sede (Montería, Medellín, Bogotá, etc.).\n"
             "• followup_day (INTEGER): Fase activa de cadencia (1, 3 o 7).\n"
             "• is_blacklisted (BOOLEAN): Bandera de exclusión legal por Habeas Data."),
            ("3.2 Mecanismo de Auto-Migración (session.py)",
             "Para evitar caídas del sistema cuando se agregan nuevas columnas en despliegues existentes, la función 'init_db()' en 'src/db/session.py' inspecciona la base de datos (mediante PRAGMA table_info en SQLite) y ejecuta automáticamente 'ALTER TABLE prospects ADD COLUMN...' para cualquier campo faltante, garantizando compatibilidad retroactiva sin perder datos previos.")
        ]),
        ("SECCIÓN 4: SEGURIDAD ENTERPRISE Y DEFENSAS ACTIVAS", [
            ("4.1 Aislamiento Multi-Tenant en Repositorio",
             "A diferencia de soluciones frágiles basadas en filtros opcionales, en RevOps AI es matemáticamente imposible olvidar el filtro de inquilino: la clase 'TenantScopedRepository' exige 'tenant_id' en su constructor y todas sus operaciones (get, list, save, delete, stats) están vinculadas a esa variable."),
            ("4.2 Protección contra Inyección de Prompts",
             "El archivo 'src/security/sanitizer.py' examina el contenido HTML crudo y neutraliza expresiones como 'Ignore previous instructions', comentarios ocultos o atributos CSS con texto camuflado, protegiendo al agente de lenguaje natural de ser manipulado por páginas maliciosas."),
            ("4.3 Trazabilidad Inmutable (Audit Logs)",
             "Toda acción humana o automatizada se escribe en la tabla 'audit_logs' registrando: timestamp ISO 8601, tenant_id, lead_id, actor (ej. 'human_operator' o 'autonomous_bot'), acción ('APPROVE', 'MARK_INTERESTED', 'DISCARD') y motivo justificado.")
        ]),
        ("SECCIÓN 5: GUÍA PASO A PASO PARA MODIFICACIONES MANUALES", [
            ("5.1 ¿Cómo cambiar un título, texto o color en el Frontend?",
             "• Cambiar Colores o Tokens Visuales:\n"
             "  Abra 'RevOpsAI/src/web/static/dashboard.css'. En la regla ':root' encontrará las variables centrales:\n"
             "  - '--bg-app: #09090b;' (Fondo principal ultra-oscuro).\n"
             "  - '--accent: #10b981;' (Color esmeralda de botones y métricas).\n"
             "  - '--border-subtle: #27272a;' (Líneas divisorias finas).\n"
             "  Modifique los códigos hexadecimales para alterar la identidad de marca al instante.\n\n"
             "• Cambiar Títulos o Textos en la Pantalla:\n"
             "  Abra 'RevOpsAI/src/web/templates/dashboard.html'. Busque la etiqueta correspondiente:\n"
             "  - Para el nombre del encabezado, modifique '<span class=\"app-name\">RevOps AI</span>'.\n"
             "  - Para los títulos de las columnas del Kanban, modifique las etiquetas '<h2 class=\"column-title\">...</h2>'.\n"
             "  Guarde el archivo y recargue la página en el navegador (Ctrl + F5)."),
            ("5.2 ¿Cómo agregar un nuevo botón o comportamiento interactivo en JavaScript?",
             "1. En 'dashboard.html', añada el elemento con un ID único (ej. '<button id=\"btn-mi-accion\" class=\"btn btn-line\">Mi Acción</button>').\n"
             "2. En 'dashboard.js', en el objeto 'el' (línea ~25), agregue la referencia:\n"
             "   'btnMiAccion: document.getElementById(\"btn-mi-accion\"),'\n"
             "3. En la función 'bindEvents()' (~línea 1450), añada el escucha de eventos:\n"
             "   'if (el.btnMiAccion) el.btnMiAccion.addEventListener(\"click\", miFuncionHandler);'\n"
             "4. Defina 'async function miFuncionHandler() { ... }' realizando llamadas fetch a la API si se requiere."),
            ("5.3 ¿Cómo agregar un nuevo campo al Lead en la Base de Datos y Backend?",
             "Supongamos que desea añadir el campo 'instagram_url':\n"
             "1. En 'RevOpsAI/src/core/models.py': Añada 'instagram_url: str = \"\"' a la clase 'Prospect'.\n"
             "2. En 'RevOpsAI/src/db/models.py': Añada 'instagram_url = Column(String(255), default=\"\")' en 'ProspectORM'.\n"
             "3. En 'RevOpsAI/src/db/session.py': En 'init_db()', agregue 'instagram_url' a la lista de columnas que se auto-migran.\n"
             "4. En 'RevOpsAI/src/db/repository.py': Mapee el campo en 'save_prospect', 'get_prospect' y 'list_prospects'.\n"
             "5. En 'RevOpsAI/src/api/routes.py': En 'ProspectUpdateRequest', añada 'instagram_url: str | None = None'.\n"
             "6. En 'dashboard.html' y 'dashboard.js': Añada el input y enlázelo en la llamada PATCH."),
            ("5.4 ¿Cómo cambiar las Credenciales de Acceso o la Llave de IA?",
             "Abra el archivo 'RevOpsAI/.env' en la raíz:\n"
             "• GEMINI_API_KEY=AIzaSy... (Su clave de Google AI Studio)\n"
             "• DASHBOARD_USERNAME=admin@hzsaas.com (Usuario maestro)\n"
             "• DASHBOARD_PASSWORD=SuClaveSegura2026! (Contraseña de acceso)\n"
             "• ENVIRONMENT=production (Activa cookies seguras HTTPS)")
        ]),
        ("SECCIÓN 6: MODELO FINANCIERO Y UNIT ECONOMICS", [
            ("6.1 Estructura de Costos Reales por cada 1,000 Prospectos",
             "• Costo de Inferencia LLM (Gemini 2.0 Flash): $0.23 USD (~$950 COP).\n"
             "• Costo de Servidor VPS (Hetzner 2 vCPU / 4GB RAM prorrateado): $0.10 USD (~$410 COP).\n"
             "• Costo de Scraping y Conexión HTTP: $0.00 USD (Nativo).\n"
             "• Costo de Despacho de WhatsApp: $0.00 USD (Enlace nativo wa.me asistido por operador).\n"
             "• COSTO TOTAL OPERATIVO: $0.33 USD (~$1,360 COP) por cada 1,000 empresas auditadas.\n\n"
             "Rentabilidad: En servicios B2B o planes de automatización con tickets promedio de $2,000,000 COP, cerrar 2 clientes a partir de 1,000 prospecciones genera $4,000,000 COP frente a un costo de $1,360 COP. Margen Bruto: > 99.8%.")
        ])
    ]
    
    for sec_title, items in tech_chapters:
        h1 = doc.add_heading(sec_title, level=1)
        h1.paragraph_format.space_before = Pt(16)
        h1.paragraph_format.space_after = Pt(6)
        for i_title, i_content in items:
            h2 = doc.add_heading(i_title, level=2)
            h2.paragraph_format.space_before = Pt(10)
            h2.paragraph_format.space_after = Pt(3)
            p = doc.add_paragraph(i_content)
            p.paragraph_format.space_after = Pt(6)
            p.style.font.size = Pt(9.5)
            
    doc.save(filepath)
    print(f"Manual técnico guardado en: {filepath}")

# ==============================================================================
# 3. GENERADOR DE PDFS COMPLETOS (REPORTLAB)
# ==============================================================================
def generate_user_manual_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a")
    c_accent = colors.HexColor("#059669")
    c_sub = colors.HexColor("#64748b")
    c_card_bg = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#cbd5e1")
    
    s_pre = ParagraphStyle('PreH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=c_accent, textTransform='uppercase')
    s_title = ParagraphStyle('MainT', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=c_primary, alignment=0, spaceAfter=4)
    s_meta = ParagraphStyle('MetaSub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=c_sub, spaceAfter=12)
    s_h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=c_primary, spaceBefore=12, spaceAfter=4, keepWithNext=True)
    s_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor("#1e293b"), spaceBefore=8, spaceAfter=2, keepWithNext=True)
    s_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#334155"), spaceAfter=4)
    s_bullet = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor("#334155"), leftIndent=10, spaceAfter=2)
    
    elements = []
    elements.append(Paragraph("RevOps AI · Plataforma de Generación y Conversión B2B", s_pre))
    elements.append(Paragraph("MANUAL DE USUARIO Y GUÍA DE OPERACIÓN INTEGRAL", s_title))
    elements.append(Paragraph("Versión 2.4 Oficial · Guía Operativa Paso a Paso para SDRs, Closers y Gerentes Comerciales", s_meta))
    
    callout = [[Paragraph("<b>RESUMEN OPERATIVO:</b> RevOps AI automatiza el ciclo comercial: prospección territorial por ciudad, auditoría técnica de brechas digitales (falta de WhatsApp o agendas), calificación objetiva de leads, redacción personalizada y despacho asistido a WhatsApp (+57) conforme a la Ley 1581 de 2012 (Habeas Data Colombia).", s_body)]]
    t_c = Table(callout, colWidths=[530])
    t_c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINEBEFORE', (0,0), (0,0), 3.5, c_accent),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_c)
    elements.append(Spacer(1, 8))
    
    flow_steps = [
        ("01. Prospección Autónoma", "El bot recorre empresas por ciudad y las precalifica automáticamente en el tablero."),
        ("02. Ingesta Masiva (Batch)", "Permite pegar un listado de URLs para auditar hasta 20 sitios de forma concurrente."),
        ("03. Inspección & Scoring", "Auditoría del DOM: califica de 0 a 100 y genera una propuesta comercial personalizada."),
        ("04. Revisión Humana (HITL)", "El operador asigna nombre del decisor, WhatsApp verificado y notas de llamada."),
        ("05. Despacho Asistido (WA)", "Apertura en 1 clic de WhatsApp Web con número +57 y mensaje precargado."),
        ("06. Cadencia & Conversión", "Control de bumps en Día 1, 3 y 7, con botón 'Marcar Interesado' directo.")
    ]
    t_data = [[Paragraph("<b>ETAPA OPERATIVA</b>", s_bullet), Paragraph("<b>DESCRIPCIÓN Y ACCIÓN REQUERIDA</b>", s_bullet)]]
    for st, sd in flow_steps:
        t_data.append([Paragraph(f"<b>{st}</b>", s_body), Paragraph(sd, s_body)])
    t_table = Table(t_data, colWidths=[150, 380])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(Paragraph("1. FLUJO GENERAL DE OPERACIÓN", s_h1))
    elements.append(t_table)
    elements.append(Spacer(1, 8))
    
    sections = [
        ("2. GESTIÓN DE ACCESO Y UNIDADES DE NEGOCIO", [
            "Acceso: Ingrese con su correo autorizado (ej. admin@hzsaas.com) y contraseña corporativa.",
            "Seguridad: Bloqueo de 5 minutos al registrarse 5 intentos fallidos consecutivos.",
            "Selector Multi-Tenant: Alterne entre 'Clínicas Privadas Madrid' y 'SaaS B2B Colombia'. Los datos se aíslan estrictamente sin cruce de información."
        ]),
        ("3. MÓDULOS DE PROSPECCIÓN Y AUDITORÍA", [
            "Bot Autónomo: Haga clic en 'Bot Prospección Autónoma', elija Ciudad (Montería, Medellín, Bogotá, etc.), sector y límite. El bot las audita y coloca en revisión.",
            "Auditoría Masiva (Batch): Pegue múltiples URLs y procéselas en lote sin demoras.",
            "Auditoría Unitaria: Ingrese una URL puntual para diagnóstico inmediato en 3 segundos."
        ]),
        ("4. FILTROS RÁPIDOS Y SEGMENTACIÓN TERRITORIAL", [
            "Filtro Territorial: Aísle el tablero con 1 clic por 'Montería', 'Medellín', 'Bogotá' o 'Todas'.",
            "Filtros de Brechas: Visualice empresas 'Score ≥ 80', 'Sin WhatsApp' o 'Sin agenda en línea'.",
            "Buscador Reactivo: Localice empresas por nombre, teléfono o hallazgo médico al instante."
        ]),
        ("5. REVISIÓN HUMANA, WHATSAPP Y CADENCIA (DÍA 1 / 3 / 7)", [
            "Slide-Over Drawer: Haga clic en cualquier tarjeta para abrir el panel de diagnóstico completo.",
            "Datos del Decisor: Asigne nombre y WhatsApp móvil (formato nacional 3001234567 o internacional).",
            "Despacho WhatsApp: Presione 'Abrir WhatsApp con Decisor' para cargar la conversación con prefijo +57 y aviso legal.",
            "Notas Internas: Registre bitácoras de llamadas y disponibilidad de secretarias en 'Notas & Cadencia'.",
            "Cadencia Activa: Marque el estado (Día 1, Día 3 o Día 7). Las tarjetas mostrarán una insignia visual.",
            "Marcar Interesado: Convierta el lead en oportunidad ganada en 1 clic directamente desde la tarjeta."
        ]),
        ("6. EXCEL Y PROTOCOLO DE HABEAS DATA (COLOMBIA)", [
            "Exportar Excel (.xls): Descarga la cartera completa con codificación UTF-8 pura y saltos de línea ordenados.",
            "Desactivar Datos Demo: Limpia los prospectos simulados para operar con datos reales.",
            "Habeas Data (Ley 1581 de 2012): Si un prospecto responde 'BAJA', descártelo con el motivo 'Baja legal' para bloquearlo permanentemente de futuras prospecciones."
        ])
    ]
    for s_t, items in sections:
        elements.append(Paragraph(s_t, s_h1))
        for it in items:
            elements.append(Paragraph(f"• {it}", s_bullet))
        elements.append(Spacer(1, 4))
        
    doc.build(elements)
    print(f"PDF Usuario creado: {filepath}")

def generate_technical_manual_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a")
    c_accent = colors.HexColor("#2563eb")
    c_sub = colors.HexColor("#64748b")
    c_card_bg = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#cbd5e1")
    
    s_pre = ParagraphStyle('PreHT', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=c_accent, textTransform='uppercase')
    s_title = ParagraphStyle('MainTT', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=c_primary, alignment=0, spaceAfter=4)
    s_meta = ParagraphStyle('MetaSubT', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=10, textColor=c_sub, spaceAfter=12)
    s_h1 = ParagraphStyle('H1T', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_primary, spaceBefore=10, spaceAfter=4, keepWithNext=True)
    s_h2 = ParagraphStyle('H2T', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor("#1e293b"), spaceBefore=6, spaceAfter=2, keepWithNext=True)
    s_body = ParagraphStyle('BodyT', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#334155"), spaceAfter=3)
    s_bullet = ParagraphStyle('BulletT', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#334155"), leftIndent=10, spaceAfter=2)
    
    elements = []
    elements.append(Paragraph("Ingeniería de Software · Arquitectura Enterprise · Guía de Modificaciones", s_pre))
    elements.append(Paragraph("MANUAL TÉCNICO INTERNO Y GUÍA DE MODIFICACIÓN DEL SAAS", s_title))
    elements.append(Paragraph("Especificación Técnica Total v2.4 · Audiencia: CTO, Tech Leads, Desarrolladores y DevOps", s_meta))
    
    callout = [[Paragraph("<b>SINOPSIS ARQUITECTÓNICA:</b> RevOps AI es un micro-kernel asíncrono en FastAPI (Python 3.11+) con un pipeline de 5 agentes desacoplados, aislamiento multi-tenant forzado en repositorio SQLAlchemy, sanitización Zero-Trust anti-prompt injection, telemetría CSS nativa Anti-AI Hallmark y suite de 131 tests unitarios y de integración.", s_body)]]
    t_c = Table(callout, colWidths=[530])
    t_c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINEBEFORE', (0,0), (0,0), 3.5, c_accent),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_c)
    elements.append(Spacer(1, 6))
    
    # 1. Stack
    elements.append(Paragraph("1. MATRIZ DEL STACK TECNOLÓGICO Y COMPONENTES", s_h1))
    stack_data = [
        ("Capa Web / API", "FastAPI + Pydantic v2 + Uvicorn", "Rutas REST asíncronas, validación estricta y documentación OpenAPI."),
        ("Persistencia ORM", "SQLAlchemy 2.0 + SQLite / PostgreSQL", "Mapeo relacional, auto-migración DDL y aislamiento estricto por tenant."),
        ("Scraping & AST", "Requests + BeautifulSoup4 + Regex", "Auditoría con timeouts de 8s, rotación de cabeceras y control defensivo."),
        ("Agentes & IA", "Gemini 2.0 Flash / Pro + Fallback Heurístico", "Inferencia de lenguaje natural, clasificación y redacción B2B."),
        ("Seguridad & Auth", "HMAC-SHA256, Bcrypt, Leaky Bucket", "Protección brute-force, tokens HttpOnly y desinfección de prompts."),
        ("Frontend UI", "HTML5 Semántico, CSS Tokens, Vanilla JS", "Diseño Anti-AI Hallmark, gráficos nativos con CSS y cero dependencias.")
    ]
    t_stk = [[Paragraph("<b>COMPONENTE</b>", s_bullet), Paragraph("<b>TECNOLOGÍA</b>", s_bullet), Paragraph("<b>MISIÓN TÉCNICA</b>", s_bullet)]]
    for c_n, c_t, c_m in stack_data:
        t_stk.append([Paragraph(f"<b>{c_n}</b>", s_body), Paragraph(c_t, s_body), Paragraph(c_m, s_body)])
    t_stk_tab = Table(t_stk, colWidths=[90, 150, 290])
    t_stk_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(t_stk_tab)
    elements.append(Spacer(1, 6))
    
    # 2. Pipeline de Agentes
    elements.append(Paragraph("2. PIPELINE DE AGENTES Y FUNCIONAMIENTO DEL CÓDIGO", s_h1))
    pipe = [
        ("IngestionAgent (audit_agent.py)", "Descarga el HTML aplicando un límite de 8 segundos y cabeceras reales. Neutraliza vectores de inyección ocultos."),
        ("ResearchAgent (research_agent.py)", "Inspecciona el DOM estructurado detectando botones wa.me, agendas en línea (Doctoralia/Calendly) y catálogo de servicios."),
        ("ScoringEngine (scoring_agent.py)", "Fórmula: Score = 50 (Base) + Catálogo (+20) - Sin_WhatsApp (-15) - Sin_Agenda (-15). Umbral ≥ 70 puntos clasifica a revisión."),
        ("CopywriterAgent (copywriter_agent.py)", "Redacta la propuesta hiper-personalizada dirigida al decisor con aviso legal de Habeas Data."),
        ("AutonomousScout (autonomous_scout.py)", "Descubre empresas por ciudad y orquesta el pipeline de auditoría concurrente en lote.")
    ]
    for p_n, p_d in pipe:
        elements.append(Paragraph(f"• <b>{p_n}:</b> {p_d}", s_bullet))
    elements.append(Spacer(1, 4))
    
    # 3. Guía de Modificaciones
    elements.append(Paragraph("3. GUÍA DE MODIFICACIONES: FRONTEND Y BACKEND", s_h1))
    mods = [
        ("A. Modificar Colores, Fuentes o Títulos (CSS/HTML)",
         "• Colores y Tokens: Abra 'src/web/static/dashboard.css' y edite la regla ':root': '--bg-app' (fondo), '--accent' (verde esmeralda), '--border-subtle'.\n"
         "• Títulos y Textos: Abra 'src/web/templates/dashboard.html' y modifique los textos directamente en las etiquetas HTML."),
        ("B. Añadir Botones o Interactividad (JavaScript)",
         "1. Agregue el botón con un ID en 'dashboard.html'. 2. Declare la referencia en el objeto 'el' en 'dashboard.js'. 3. Añada el evento en 'bindEvents()'. 4. Cree la función asíncrona que consuma la API."),
        ("C. Agregar un Nuevo Campo en la Base de Datos y API",
         "1. Declare el campo en 'src/core/models.py' (Pydantic). 2. Añada la columna en 'src/db/models.py' (SQLAlchemy). 3. Incluya el nombre en 'init_db()' en 'src/db/session.py' para auto-migración DDL. 4. Mapee en 'repository.py'. 5. Exponga en 'src/api/routes.py' (ProspectUpdateRequest)."),
        ("D. Variables de Entorno y Configuración",
         "En el archivo 'RevOpsAI/.env' defina: GEMINI_API_KEY, DASHBOARD_USERNAME, DASHBOARD_PASSWORD y ENVIRONMENT=production.")
    ]
    for m_t, m_c in mods:
        elements.append(Paragraph(m_t, s_h2))
        elements.append(Paragraph(m_c, s_body))
    elements.append(Spacer(1, 4))
    
    # 4. Unit Economics
    elements.append(Paragraph("4. UNIT ECONOMICS Y RENTABILIDAD (1,000 LEADS)", s_h1))
    fin_data = [
        ("Inferencia IA (Gemini 2.0 Flash)", "$0.23 USD (~$950 COP)", "1.5k tokens entrada + 200 tokens salida por lead."),
        ("Servidor Backend VPS (Prorrateado)", "$0.10 USD (~$410 COP)", "Servidor 2 vCPU / 4GB RAM prorrateado por volumen."),
        ("Scraping & Despacho WhatsApp", "$0.00 USD ($0 COP)", "Canal nativo directo sin costes de intermediarios."),
        ("COSTO TOTAL (1,000 LEADS AUDITADOS)", "$0.33 USD (~$1,360 COP)", "Costo por lead: $1.36 COP (Margen Operativo Bruto: > 99.8%)")
    ]
    t_fin = [[Paragraph("<b>RUBRO DE GASTO</b>", s_bullet), Paragraph("<b>COSTO ESTIMADO</b>", s_bullet), Paragraph("<b>DETALLE OPERATIVO</b>", s_bullet)]]
    for r_g, c_e, d_o in fin_data:
        t_fin.append([Paragraph(f"<b>{r_g}</b>", s_body), Paragraph(c_e, s_body), Paragraph(d_o, s_body)])
    t_fin_tab = Table(t_fin, colWidths=[150, 130, 250])
    t_fin_tab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e2e8f0")),
    ]))
    elements.append(t_fin_tab)
    
    doc.build(elements)
    print(f"PDF Técnico creado: {filepath}")

if __name__ == "__main__":
    target_dir = r"c:\Users\JESUS\Desktop\Antigravity\documentacion completa"
    os.makedirs(target_dir, exist_ok=True)
    
    u_docx = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI.docx")
    t_docx = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI.docx")
    u_pdf = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI.pdf")
    t_pdf = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI.pdf")
    
    generate_user_manual_docx(u_docx)
    generate_technical_manual_docx(t_docx)
    generate_user_manual_pdf(u_pdf)
    generate_technical_manual_pdf(t_pdf)
    print("¡Toda la documentación exhaustiva ha sido generada exitosamente!")
