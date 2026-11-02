"""
Generador Directo de Documentos PDF Oficiales con ReportLab para RevOps AI
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def build_user_manual_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0f172a") # Slate 900
    c_accent = colors.HexColor("#059669")  # Emerald 600
    c_sub = colors.HexColor("#64748b")     # Slate 500
    c_card_bg = colors.HexColor("#f8fafc") # Slate 50
    c_border = colors.HexColor("#cbd5e1")  # Slate 300
    
    style_pre = ParagraphStyle(
        'PreHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_accent,
        spaceAfter=4,
        textTransform='uppercase'
    )
    
    style_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=0,
        spaceAfter=4
    )
    
    style_meta = ParagraphStyle(
        'MetaSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=c_sub,
        spaceAfter=14
    )
    
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )
    
    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=12,
        spaceAfter=3
    )
    
    style_callout = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph("RevOps AI · Plataforma de Crecimiento Comercial B2B", style_pre))
    elements.append(Paragraph("MANUAL DE USUARIO Y GUÍA DE OPERACIONES", style_title))
    elements.append(Paragraph("Versión 2.4.0 (Edición Corporativa) · Audiencia: Directores Comerciales, SDRs y Operadores de Cuentas", style_meta))
    
    # Callout Box
    callout_data = [[
        Paragraph(
            "<b>PROPÓSITO DE LA PLATAFORMA:</b> RevOps AI es una suite de inteligencia de ingresos diseñada para automatizar la prospección, auditoría digital y redacción de propuestas comerciales B2B. Audita la presencia web de empresas objetivo en búsqueda de brechas comerciales (ausencia de WhatsApp, falta de agendas en línea), redacta propuestas a la medida y asiste al equipo comercial en el despacho y cadencia de seguimiento con estricto apego a la Ley 1581 de 2012 (Habeas Data Colombia).",
            style_callout
        )
    ]]
    t_callout = Table(callout_data, colWidths=[520])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINEBEFORE', (0,0), (0,0), 3.5, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(t_callout)
    elements.append(Spacer(1, 10))
    
    # 1. Flujo General
    elements.append(Paragraph("1. FLUJO GENERAL DE OPERACIÓN", style_h1))
    
    flow_steps = [
        ("01. Descubrimiento Autónomo", "El bot recorre empresas por ciudad y las precalifica en la columna de revisión."),
        ("02. Ingesta Masiva (Batch)", "Permite ingresar múltiples URLs para auditar hasta 20 sitios de forma concurrente."),
        ("03. Inspección & Scoring", "Auditoría del DOM: califica de 0 a 100 y genera propuesta comercial a la medida."),
        ("04. Revisión Humana (HITL)", "El operador enriquece el lead con el decisor, WhatsApp y notas de recepción."),
        ("05. Despacho Asistido (WA)", "Apertura en 1 clic de WhatsApp Web con número +57 y propuesta precargada."),
        ("06. Cadencia & Conversión", "Control de bumps en Día 1, 3 y 7, con botón 'Marcar Interesado' directo.")
    ]
    
    t_flow_data = [
        [Paragraph("<b>ETAPA OPERATIVA</b>", style_bullet), Paragraph("<b>DESCRIPCIÓN Y ACCIÓN CLAVE</b>", style_bullet)]
    ]
    for s_title, s_desc in flow_steps:
        t_flow_data.append([
            Paragraph(f"<b>{s_title}</b>", style_body),
            Paragraph(s_desc, style_body)
        ])
    
    t_flow = Table(t_flow_data, colWidths=[150, 370])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(t_flow)
    elements.append(Spacer(1, 10))
    
    # 2. Guía Detallada
    elements.append(Paragraph("2. GUÍA DETALLADA PASO A PASO POR MÓDULOS", style_h1))
    
    modules = [
        ("A. Bot de Prospección Autónoma (Piloto Automático)", [
            "Haga clic en el botón superior 'Bot Prospección Autónoma'.",
            "Seleccione la Ciudad objetivo (Montería, Medellín, Bogotá, etc.) y el sector económico.",
            "Indique el límite de empresas deseadas y presione 'Lanzar Descubrimiento Autónomo'.",
            "El sistema recorrerá las entidades, auditará su infraestructura web y las insertará precalificadas en '01. Pendientes'."
        ]),
        ("B. Auditoría Masiva en Lote (Batch Audit)", [
            "Haga clic en 'Auditoría Masiva (Batch)'.",
            "Pegue un listado de páginas web (una URL por línea, ej: https://clinicaejemplo.co).",
            "Presione 'Procesar Lote' para realizar el rastreo en paralelo sin demoras manuales."
        ]),
        ("C. Barra de Herramientas y Filtro Territorial Rápido", [
            "Filtros de Brechas: Acceda con un clic a 'Score ≥ 80', 'Sin WhatsApp' y 'Sin agenda en línea'.",
            "Filtro Territorial: Aísle el tablero por 'Montería', 'Medellín', 'Bogotá' o 'Todas'.",
            "Buscador Instantáneo: Escriba palabras clave médicas, nombres o dominios para filtrado en tiempo real."
        ]),
        ("D. Despacho Asistido por WhatsApp Directo", [
            "Abra la tarjeta del prospecto en la columna '01. Pendientes de revisión'.",
            "En la pestaña 'Propuesta', ingrese el Nombre del Decisor y su número celular (formato 3001234567 o +57).",
            "Haga clic en 'Abrir WhatsApp con Decisor': Se iniciará la conversación oficial con la propuesta lista.",
            "Presione 'Aprobar' para transferir el prospecto a la columna '02. En seguimiento'."
        ]),
        ("E. Bitácora de Notas Internas y Control de Cadencia", [
            "En el drawer lateral, acceda a la pestaña 'Notas & Cadencia'.",
            "Guarde notas de recepción, acuerdos telefónicos y objeciones comunes.",
            "Ajuste la cadencia: 'Día 1 (Primer contacto)', 'Día 3 (Bump de seguimiento)' o 'Día 7 (Cierre)'.",
            "Al recibir confirmación de interés, presione 'Marcar Interesado' directamente en la tarjeta."
        ]),
        ("F. Exportación a Excel y Limpieza de Datos Demo", [
            "Exportar Excel (.xls): Genera una hoja de cálculo con codificación UTF-8 pura (sin caracteres rotos) y propuesta estructurada.",
            "Desactivar datos demo: Vacía los prospectos simulados en 1 clic para operar en producción limpia."
        ])
    ]
    
    for m_title, m_items in modules:
        elements.append(Paragraph(m_title, style_h2))
        for item in m_items:
            elements.append(Paragraph(f"• {item}", style_bullet))
        elements.append(Spacer(1, 4))
        
    elements.append(Paragraph("3. PROTOCOLO DE CUMPLIMIENTO LEGAL (LEY 1581 DE 2012)", style_h1))
    elements.append(Paragraph(
        "Toda propuesta emitida incluye obligatoriamente la cláusula de exclusión: <i>'Comunicación comercial B2B conforme a la Ley 1581 de 2012 (Habeas Data Colombia). Responda BAJA para excluir su contacto.'</i> Si un prospecto solicita su exclusión, el operador debe descartarlo indicando 'Baja legal' para activar el bloqueo definitivo en la lista negra del tenant.",
        style_body
    ))
    
    doc.build(elements)
    print(f"PDF Usuario creado: {filename}")


def build_tech_manual_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor("#0f172a") # Slate 900
    c_accent = colors.HexColor("#2563eb")  # Blue 600
    c_sub = colors.HexColor("#64748b")     # Slate 500
    c_card_bg = colors.HexColor("#f8fafc") # Slate 50
    c_border = colors.HexColor("#cbd5e1")  # Slate 300
    
    style_pre = ParagraphStyle(
        'PreHeader_Tech',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_accent,
        spaceAfter=4,
        textTransform='uppercase'
    )
    
    style_title = ParagraphStyle(
        'MainTitle_Tech',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=23,
        textColor=c_primary,
        alignment=0,
        spaceAfter=4
    )
    
    style_meta = ParagraphStyle(
        'MetaSubtitle_Tech',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=c_sub,
        spaceAfter=14
    )
    
    style_h1 = ParagraphStyle(
        'Heading1_Tech',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'Heading2_Tech',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'Body_Tech',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5
    )
    
    style_bullet = ParagraphStyle(
        'Bullet_Tech',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=10,
        spaceAfter=3
    )
    
    style_callout = ParagraphStyle(
        'CalloutText_Tech',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    
    elements = []
    
    elements.append(Paragraph("Ingeniería de Software · Especificación de Arquitectura v2.4", style_pre))
    elements.append(Paragraph("MANUAL TÉCNICO INTERNO Y ARQUITECTURA DE REVOPS AI", style_title))
    elements.append(Paragraph("Clasificación: Confidencial · Audiencia: CTO, Arquitectos de Software, Tech Leads y DevSecOps", style_meta))
    
    callout_data = [[
        Paragraph(
            "<b>SINOPSIS DE INGENIERÍA:</b> RevOps AI está construido como un micro-kernel modular de alto rendimiento implementado en Python 3.11+ y FastAPI. Integra un extractor AST para análisis digital de sitios web en paralelo, un pipeline multi-agente con evaluación heurística y LLM (Gemini 2.0), aislamiento forzado por inquilino en la capa ORM, y una interfaz reactiva Anti-AI Hallmark (cero dependencias externas pesadas, cero parpadeos de diseño y alta densidad visual).",
            style_callout
        )
    ]]
    t_callout = Table(callout_data, colWidths=[520])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_card_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINEBEFORE', (0,0), (0,0), 3.5, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(t_callout)
    elements.append(Spacer(1, 10))
    
    # 1. Stack Tecnológico
    elements.append(Paragraph("1. STACK TECNOLÓGICO Y MATRIZ DE COMPONENTES", style_h1))
    
    stack_data = [
        ("Capa Web / API", "FastAPI + Starlette + Pydantic v2", "Validación estricta de esquemas, serialización nativa y concurrencia asíncrona."),
        ("Persistencia ORM", "SQLAlchemy 2.0 + SQLite / PostgreSQL", "Aislamiento por tenant_id forzado en repositorio y auto-migración DDL."),
        ("Scraping & AST", "Requests + BeautifulSoup4 + Regex", "Auditoría web con timeouts defensivos (8s) y filtrado de prompts ocultos."),
        ("Agentes & IA", "Gemini 2.0 Flash / Pro + Fallback Determinista", "Categorización semántica y redacción B2B con degradación offline."),
        ("Seguridad & Auth", "HMAC-SHA256, Bcrypt, Leaky Bucket Limiter", "Protección anti-fuerza bruta, cookies HttpOnly y sanitización Zero-Trust."),
        ("Frontend UI", "HTML5 Semántico, CSS Tokens, Vanilla JS", "Arquitectura Anti-AI Hallmark, gráficos en tiempo real con CSS nativo.")
    ]
    
    t_stk_data = [
        [Paragraph("<b>COMPONENTE</b>", style_bullet), Paragraph("<b>TECNOLOGÍA</b>", style_bullet), Paragraph("<b>MISIÓN ARQUITECTÓNICA</b>", style_bullet)]
    ]
    for c_name, c_tech, c_desc in stack_data:
        t_stk_data.append([
            Paragraph(f"<b>{c_name}</b>", style_body),
            Paragraph(c_tech, style_body),
            Paragraph(c_desc, style_body)
        ])
        
    t_stk = Table(t_stk_data, colWidths=[110, 150, 260])
    t_stk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(t_stk)
    elements.append(Spacer(1, 10))
    
    # 2. Pipeline de Agentes
    elements.append(Paragraph("2. PIPELINE DE AGENTES Y FUNCIONAMIENTO DEL CÓDIGO", style_h1))
    pipe_steps = [
        ("IngestionAgent (src/agents/ingestion.py)", "Ejecuta GET HTTP defensivo con timeout de 8 segundos. Neutraliza vectores de prompt injection camuflados en comentarios o nodos ocultos."),
        ("ResearchAgent (src/agents/research.py)", "Inspecciona el DOM estructurado identificando canales de mensajería (wa.me), botones de agendamiento (Doctoralia/Calendly) y catálogo de servicios."),
        ("ScoringEngine (src/agents/scoring.py)", "Aplica el algoritmo: Score = 50 (Base) + Especialidades (máx +20) - Sin_WhatsApp (-15) - Sin_Agenda (-15). Umbral: score ≥ 70 precalifica a revisión humana."),
        ("CopywriterAgent (src/agents/copywriter.py)", "Genera la propuesta B2B hiper-personalizada dirigida a resolver las brechas encontradas y añade el aviso legal de exclusión."),
        ("AutonomousProspectingAgent (src/agents/autonomous_scout.py)", "Descubre empresas corporativas por territorio y sector, orquestando el pipeline en lote.")
    ]
    for p_name, p_desc in pipe_steps:
        elements.append(Paragraph(f"• <b>{p_name}:</b> {p_desc}", style_bullet))
        
    elements.append(Spacer(1, 6))
    
    # 3. Rentabilidad y Unit Economics
    elements.append(Paragraph("3. MODELO DE RENTABILIDAD Y UNIT ECONOMICS", style_h1))
    elements.append(Paragraph("Costos operativos unitarios calculados para <b>1,000 prospectos auditados y despachados</b>:", style_body))
    
    cost_data = [
        ("Inferencia IA (Gemini 2.0 Flash)", "$0.23 USD (~$950 COP)", "1.5k tokens entrada + 200 salida por lead."),
        ("Cómputo Backend & VPS", "$0.10 USD (~$410 COP)", "Instancia de $5 USD/mes prorrateada por volumen."),
        ("Scraping & Red Directa", "$0.00 USD ($0 COP)", "Ejecución directa sin intermediarios de API de pago."),
        ("Despacho WhatsApp Asistido", "$0.00 USD ($0 COP)", "Protocolo directo wa.me con operador humano."),
        ("COSTO TOTAL (1,000 EMPRESAS)", "$0.33 USD (~$1,360 COP)", "Costo por lead auditado: $1.36 COP (Margen > 99.8%)")
    ]
    
    t_c_data = [
        [Paragraph("<b>CONCEPTO</b>", style_bullet), Paragraph("<b>COSTO ESTIMADO</b>", style_bullet), Paragraph("<b>DETALLE TÉCNICO</b>", style_bullet)]
    ]
    for c_rubro, c_valor, c_det in cost_data:
        t_c_data.append([
            Paragraph(f"<b>{c_rubro}</b>", style_body),
            Paragraph(c_valor, style_body),
            Paragraph(c_det, style_body)
        ])
        
    t_cost = Table(t_c_data, colWidths=[150, 130, 240])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#e2e8f0")),
    ]))
    elements.append(t_cost)
    elements.append(Spacer(1, 10))
    
    # 4. Ajustes Manuales y API
    elements.append(Paragraph("4. AJUSTE MANUAL DE DATOS Y CONEXIONES INTERNAS", style_h1))
    elements.append(Paragraph(
        "<b>Actualización Directa vía REST API:</b> Envíe peticiones PATCH a <code>/api/v1/prospects/{lead_id}</code> con los campos deseados (contact_name, contact_phone, city, followup_day, internal_notes, draft_message).<br/>"
        "<b>Persistencia y Auto-Migración:</b> El método <code>init_db()</code> en <code>src/db/session.py</code> verifica dinámicamente las columnas SQLite/Postgres y ejecuta <code>ALTER TABLE</code> automáticamente para soportar nuevas versiones sin pérdida de datos.<br/>"
        "<b>Suite de Calidad:</b> 131 tests unitarios y de integración automatizados garantizan el aislamiento multi-tenant y la solidez del motor.",
        style_body
    ))
    
    doc.build(elements)
    print(f"PDF Técnico creado: {filename}")

if __name__ == "__main__":
    build_user_manual_pdf(r"c:\Users\JESUS\Desktop\Antigravity\docs\Manual_de_Usuario_RevOps_AI.pdf")
    build_tech_manual_pdf(r"c:\Users\JESUS\Desktop\Antigravity\docs\Manual_Tecnico_Interno_RevOps_AI.pdf")

