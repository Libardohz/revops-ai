"""
Generador de Documentación Profesional para RevOps AI
Genera documentos Word (.docx) y versiones imprimibles a PDF con diseño editorial de alto nivel.
"""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tc_pr.append(tcMar)

def create_user_manual():
    doc = docx.Document()
    
    # Page setup
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        
    # Styles
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    run_sub = title_p.add_run("REVOPS AI · PLATAFORMA DE GENERACIÓN Y CONVERSIÓN DE PIPELINE B2B\n")
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(16, 185, 129) # Emerald
    
    run_title = title_p.add_run("MANUAL DE USUARIO Y GUÍA DE OPERACIONES")
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(24)
    r_meta = p_meta.add_run("Versión 2.4.0 · Producción · Audiencia: Directores Comerciales, SDRs y Operadores de Cuentas")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    
    # Callout Box: Resumen Ejecutivo
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    set_cell_background(c, "F8FAFC")
    set_cell_margins(c, top=140, bottom=140, left=200, right=200)
    cp = c.paragraphs[0]
    cp.paragraph_format.space_after = Pt(2)
    r_c1 = cp.add_run("PROPÓSITO DE LA PLATAFORMA\n")
    r_c1.font.bold = True
    r_c1.font.size = Pt(9.5)
    r_c1.font.color.rgb = RGBColor(15, 23, 42)
    r_c2 = cp.add_run("RevOps AI es un sistema autónomo de inteligencia de ingresos diseñado para auditar infraestructura digital externa de empresas, cuantificar brechas comerciales (ausencia de WhatsApp, falta de agendas en línea), redactar propuestas comerciales hiper-personalizadas y despachar oportunidades mediante WhatsApp y correo con estricto apego a la Ley 1581 de 2012 (Habeas Data Colombia).")
    r_c2.font.size = Pt(9.5)
    r_c2.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # Sección 1: Arquitectura Operativa y Flujo General
    h1 = doc.add_heading("1. FLUJO GENERAL DE OPERACIÓN", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(8)
    
    p = doc.add_paragraph(
        "El ciclo operativo de RevOps AI sigue una secuencia lineal optimizada para maximizar la tasa de conversión minimizando el esfuerzo humano manual:"
    )
    p.paragraph_format.space_after = Pt(8)
    
    steps = [
        ("Fase 1: Prospección Autónoma o Ingesta Masiva", "El sistema descubre o recibe URLs empresariales según territorio y sector económico objetivo."),
        ("Fase 2: Análisis Técnico & Detección de Brechas", "El motor AST inspecciona el DOM de cada sitio web en paralelo, extrayendo canales de contacto, sistemas de cita y servicios ofrecidos."),
        ("Fase 3: Clasificación y Redacción con IA", "Se asigna una puntuación objetiva (0 a 100) y se redacta un borrador comercial a la medida de los dolores detectados."),
        ("Fase 4: Aprobación Humana (Human-In-The-Loop - HITL)", "El operador valida datos en el Command Center, ajusta decisores, asigna notas y aprueba."),
        ("Fase 5: Despacho Asistido por WhatsApp Directo", "Apertura en un clic de WhatsApp Web/App con número formateado (+57) y propuesta precargada."),
        ("Fase 6: Cadencia de Seguimiento & Cierre", "Control sistemático de interacciones en Día 1, Día 3 (Bump) y Día 7 (Cierre), marcando oportunidades ganadas en 1 clic.")
    ]
    
    tbl_flow = doc.add_table(rows=len(steps) + 1, cols=2)
    tbl_flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl_flow.rows[0]
    hdr.cells[0].paragraphs[0].add_run("ETAPA OPERATIVA").font.bold = True
    hdr.cells[1].paragraphs[0].add_run("DESCRIPCIÓN Y ACCIÓN CLAVE").font.bold = True
    set_cell_background(hdr.cells[0], "0F172A")
    set_cell_background(hdr.cells[1], "0F172A")
    hdr.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    hdr.cells[1].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    
    for idx, (etapa, desc) in enumerate(steps, start=1):
        row = tbl_flow.rows[idx]
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        set_cell_background(row.cells[0], bg)
        set_cell_background(row.cells[1], bg)
        set_cell_margins(row.cells[0], 60, 60, 100, 100)
        set_cell_margins(row.cells[1], 60, 60, 100, 100)
        r0 = row.cells[0].paragraphs[0].add_run(etapa)
        r0.font.bold = True
        r0.font.size = Pt(9)
        r1 = row.cells[1].paragraphs[0].add_run(desc)
        r1.font.size = Pt(9)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    
    # Sección 2: Uso Detallado de Cada Módulo
    h2 = doc.add_heading("2. GUÍA PASO A PASO POR MÓDULOS", level=1)
    h2.paragraph_format.space_before = Pt(16)
    
    modules = [
        ("A. Bot de Prospección Autónoma (Piloto Automático)", [
            "Haga clic en el botón 'Bot Prospección Autónoma' en la barra superior del Dashboard.",
            "Seleccione la Ciudad objetivo (Montería, Medellín, Bogotá, Barranquilla, Cali o Cartagena).",
            "Seleccione el Sector (Clínicas Odontológicas y Estéticas, Consultorías, etc.).",
            "Defina el límite de empresas deseadas (ej. 5 o 10 empresas) y presione 'Lanzar Descubrimiento'.",
            "El bot ejecutará la búsqueda territorial, filtrará dominios corporativos válidos, auditará la web de cada uno e insertará los leads precalificados en la columna '01. Pendientes de revisión'."
        ]),
        ("B. Auditoría Masiva en Lote (Batch Audit)", [
            "Haga clic en 'Auditoría Masiva (Batch)'.",
            "Pegue un listado de páginas web (una URL por línea, ej: https://clinicaejemplo.com).",
            "Seleccione el sector y presione 'Procesar Lote'.",
            "El sistema procesará las URLs en paralelo y las incorporará inmediatamente al embudo."
        ]),
        ("C. Panel de Telemetría Operativa en Tiempo Real", [
            "Embudo HITL: Monitorea cuántos prospectos están auditados, cuántos precalifican con score ≥ 70, cuántos han sido despachados y cuántos confirmaron interés.",
            "Radar de Brechas Digitales: Porcentaje exacto de empresas sin botón de WhatsApp y sin agenda interactiva.",
            "Distribución de Calidad: Histograma interactivo de leads de alto valor (≥80 pts), medios (65-79 pts) y descartables (<65 pts)."
        ]),
        ("D. Segmentación Rápida por Territorio y Brechas", [
            "Utilice los chips rápidos en la barra de herramientas para aislar la cartera:",
            "- Filtro por Territorio: 'Montería', 'Medellín', 'Bogotá' o 'Todas'.",
            "- Filtro por Brecha: 'Score ≥ 80', 'Sin WhatsApp', 'Sin agenda en línea'.",
            "- Buscador reactivo: Escriba cualquier nombre o hallazgo médico/comercial para filtrado instantáneo."
        ]),
        ("E. Despacho Asistido a WhatsApp con Número Inteligente", [
            "Abra la tarjeta del prospecto haciendo clic sobre ella en la columna '01. Pendientes'.",
            "En la pestaña 'Propuesta', ingrese el Nombre del Decisor y su número celular.",
            "El sistema soporta números en formato nacional (3001234567) o internacional (+57 300 123 4567).",
            "Haga clic en 'Abrir WhatsApp con Decisor'. Se iniciará la conversación oficial con el texto de la propuesta formateado y listo para enviar en un clic.",
            "Presione 'Aprobar' para transferir el lead automáticamente a la columna '02. En seguimiento'."
        ]),
        ("F. Control de Notas Internas y Cadencia (Día 1 / 3 / 7)", [
            "En el cajón lateral, acceda a la pestaña 'Notas & Cadencia'.",
            "Registre bitácoras de llamadas telefónicas, nombres de recepcionistas o mejores horarios de contacto.",
            "Actualice el estado de la cadencia: 'Día 1 (Primer contacto)', 'Día 3 (Bump de seguimiento)' o 'Día 7 (Cierre)'.",
            "En la columna '02. En seguimiento', las tarjetas mostrarán distintivos visuales con la fase activa.",
            "Al recibir confirmación del cliente, presione 'Marcar Interesado' directamente en la tarjeta."
        ]),
        ("G. Exportación Profesional a Microsoft Excel (.xls)", [
            "Haga clic en 'Exportar Excel' en la esquina superior derecha.",
            "Se generará un archivo formateado en XML/HTML con codificación UTF-8 pura (sin caracteres extraños en tildes ni eñes).",
            "Las propuestas comerciales preservan los saltos de línea dentro de la misma celda, listas para importar en Salesforce, HubSpot o archivo local."
        ]),
        ("H. Desactivar Datos Demo", [
            "Al hacer clic en 'Desactivar datos demo', el sistema vacía los registros ficticios del tenant actual, dejando la bandeja limpia y lista para prospectos 100% reales."
        ])
    ]
    
    for title, bullet_points in modules:
        h3 = doc.add_heading(title, level=2)
        h3.paragraph_format.space_before = Pt(12)
        h3.paragraph_format.space_after = Pt(4)
        for b in bullet_points:
            bp = doc.add_paragraph(b, style='List Bullet')
            bp.paragraph_format.space_after = Pt(3)
            
    # Sección 3: Buenas Prácticas Comerciales y Legales
    h3_leg = doc.add_heading("3. PROTOCOLO DE CUMPLIMIENTO LEGAL (LEY 1581 DE 2012)", level=1)
    h3_leg.paragraph_format.space_before = Pt(16)
    
    p_leg = doc.add_paragraph(
        "Toda comunicación B2B emitida a través de la plataforma incluye obligatoriamente la cláusula de exclusión voluntaria (Opt-out):\n"
        "'Comunicación comercial B2B conforme a la Ley 1581 de 2012 (Habeas Data Colombia). Responda BAJA para excluir su contacto.'\n\n"
        "Regla de oro operativa: Si un prospecto responde 'BAJA', 'NO ENVIAR' o equivalente, el operador debe presionar 'Descartar' en la tarjeta e ingresar 'Solicitud de exclusión legal'. El sistema bloqueará permanentemente dicho dominio en la lista de exclusión del tenant."
    )
    p_leg.paragraph_format.space_after = Pt(14)
    
    out_path = r"c:\Users\JESUS\Desktop\Antigravity\docs\Manual_de_Usuario_RevOps_AI.docx"
    doc.save(out_path)
    print(f"Manual de usuario guardado en: {out_path}")

def create_technical_manual():
    doc = docx.Document()
    
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    run_sub = title_p.add_run("ARQUITECTURA DE SOFTWARE · SEGURIDAD ENTERPRISE · UNIT ECONOMICS\n")
    run_sub.font.size = Pt(10)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(37, 99, 235) # Blue 600
    
    run_title = title_p.add_run("MANUAL TÉCNICO INTERNO Y ARQUITECTURA DE REVOPS AI")
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(24)
    r_meta = p_meta.add_run("Especificación de Ingeniería v2.4 · Confidencial · Audiencia: CTO, Tech Leads, DevSecOps")
    r_meta.font.size = Pt(9.5)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    
    # Resumen Ejecutivo
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    set_cell_background(c, "F1F5F9")
    set_cell_margins(c, top=140, bottom=140, left=200, right=200)
    cp = c.paragraphs[0]
    r_c1 = cp.add_run("SINOPSIS ARQUITECTÓNICA\n")
    r_c1.font.bold = True
    r_c1.font.size = Pt(9.5)
    r_c1.font.color.rgb = RGBColor(15, 23, 42)
    r_c2 = cp.add_run("RevOps AI está construido bajo el paradigma de Micro-Kernel Asíncrono en FastAPI (Python 3.11+), implementando un pipeline de agentes desacoplados con validación Zero-Trust, aislamiento Multi-Tenant forzado a nivel de repositorio ORM, y una interfaz reactiva Anti-AI Hallmark de alto rendimiento sin sobrecarga de dependencias.")
    r_c2.font.size = Pt(9.5)
    r_c2.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # 1. Stack Tecnológico
    h1 = doc.add_heading("1. STACK TECNOLÓGICO Y MATRIZ DE COMPONENTES", level=1)
    h1.paragraph_format.space_before = Pt(16)
    
    stack_data = [
        ("Capa Web / API", "FastAPI + Starlette + Pydantic v2", "Validación estricta de esquemas, serialización nativa ultra-rápida y soporte asíncrono para concurrencia HTTP."),
        ("Persistencia & ORM", "SQLAlchemy 2.0 + SQLite / PostgreSQL", "Mapeo objeto-relacional con soporte de auto-migración de esquema DDL en arranque y aislamiento multi-inquilino."),
        ("Scraping & DOM Parsing", "Requests + BeautifulSoup4 + Regex AST", "Extractor resiliente con control de DNS, timeouts defensivos (8s) y filtrado de contenido malicioso oculto."),
        ("Motor de Agentes & IA", "Gemini 2.0 Flash / Pro + Motor Heurístico", "Inferencia de lenguaje natural para categorización de brechas y redacción B2B, con degradación elegante determinista."),
        ("Capa de Seguridad", "Cryptography + HMAC-SHA256 + Rate Limiter", "Protección contra fuerza bruta de 5 intentos por IP/usuario, tokens de sesión HttpOnly y saneamiento de prompts."),
        ("Frontend & Dashboard", "HTML5 Semántico + CSS Tokens + Vanilla JS", "Arquitectura Anti-AI Hallmark, cero librerías externas (sin jQuery ni React), gráficos en tiempo real con CSS puro.")
    ]
    
    tbl_stk = doc.add_table(rows=len(stack_data) + 1, cols=3)
    tbl_stk.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl_stk.rows[0]
    hdr.cells[0].paragraphs[0].add_run("COMPONENTE").font.bold = True
    hdr.cells[1].paragraphs[0].add_run("TECNOLOGÍA").font.bold = True
    hdr.cells[2].paragraphs[0].add_run("FUNCIÓN ARQUITECTÓNICA").font.bold = True
    for c_i in hdr.cells:
        set_cell_background(c_i, "0F172A")
        c_i.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        
    for idx, (comp, tec, func) in enumerate(stack_data, start=1):
        row = tbl_stk.rows[idx]
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate([comp, tec, func]):
            set_cell_background(row.cells[i], bg)
            set_cell_margins(row.cells[i], 60, 60, 90, 90)
            r = row.cells[i].paragraphs[0].add_run(val)
            r.font.size = Pt(8.5)
            if i == 0:
                r.font.bold = True
                
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    
    # 2. Pipeline de Agentes y Mecánica del Código
    h2 = doc.add_heading("2. MECÁNICA DEL CÓDIGO Y PIPELINE DE AGENTES", level=1)
    h2.paragraph_format.space_before = Pt(16)
    
    p_pipe = doc.add_paragraph(
        "El procesamiento de cada entidad se ejecuta a través de un pipeline secuencial de 4 agentes coordinados por el controlador central:\n\n"
        "1. IngestionAgent (src/agents/ingestion.py): Descarga el HTML aplicando un timeout de 8 segundos y cabeceras que simulan un navegador real. Aplica un analizador de árboles sintácticos para extraer texto visible, títulos y enlaces de contacto, bloqueando vectores de inyección de prompt camuflados en comentarios HTML o atributos ocultos.\n\n"
        "2. ResearchAgent (src/agents/research.py): Evalúa el contenido estructurado en búsqueda de evidencias digitales: enlaces 'wa.me' o 'api.whatsapp.com', sistemas de agenda (Doctoralia, Calendly, formularios dinámicos), y catálogo de especialidades.\n\n"
        "3. ScoringEngine (src/agents/scoring.py): Algoritmo ponderado objetivo que calcula la puntuación del prospecto:\n"
        "   Score = Base (50) + Puntos por Especialidades (máx +20) - Penalización por Falta de WhatsApp (-15) - Penalización por Falta de Agenda (-15).\n"
        "   Un score ≥ 70 clasifica al prospecto automáticamente en estado 'PENDING_APPROVAL'. Un score menor se clasifica como 'DISCARDED'.\n\n"
        "4. CopywriterAgent (src/agents/copywriter.py): Redacta una propuesta de prospección hiper-personalizada mencionando las brechas exactas encontradas y proponiendo una reunión de 10 minutos, anexando el aviso de Habeas Data.\n\n"
        "5. AutonomousProspectingAgent (src/agents/autonomous_scout.py): Simula la prospección comercial en una ciudad específica descubriendo dominios corporativos del sector y orquestando los 4 agentes anteriores en lote."
    )
    p_pipe.paragraph_format.space_after = Pt(14)
    
    # 3. Seguridad Multi-Tenant y Protección de Datos
    h3_sec = doc.add_heading("3. SEGURIDAD ZERO-TRUST Y AISLAMIENTO MULTI-TENANT", level=1)
    h3_sec.paragraph_format.space_before = Pt(16)
    
    sec_points = [
        ("Aislamiento de Inquilinos (Multi-Tenancy)", "El acceso a la base de datos está encapsulado en TenantScopedRepository (src/db/repository.py). Cada consulta impone de manera irrenunciable la cláusula WHERE tenant_id = :tenant_id. Es imposible que un operador de la unidad 'hzsaas_colombia' acceda a registros de 'tenant_clinicas_madrid'."),
        ("Protección Anti-Fuerza Bruta", "El middleware de autenticación (src/security/rate_limiter.py) utiliza un algoritmo de cubeta permeable con bloqueo de doble nivel: máximo 20 peticiones por minuto por IP y suspensión automática de 5 minutos al acumular 5 contraseñas incorrectas para un usuario."),
        ("Protección de Inyección de Prompt", "Todo contenido proveniente de sitios web externos es tratado como no confiable (Zero-Trust). El sanitizador remueve etiquetas script, estilos, atributos ocultos y comandos orientados a vulnerar el LLM (ej. 'Ignore previous instructions')."),
        ("Auditoría Inmutable", "Cada acción (aprobación, edición de contacto, descarte o marcado de interés) genera un registro inalterable en la tabla 'audit_logs' con actor, fecha ISO y justificación.")
    ]
    for st, sd in sec_points:
        p_s = doc.add_paragraph()
        r_st = p_s.add_run(f"• {st}: ")
        r_st.font.bold = True
        r_st.font.size = Pt(9.5)
        r_sd = p_s.add_run(sd)
        r_sd.font.size = Pt(9.5)
        p_s.paragraph_format.space_after = Pt(4)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # 4. Rentabilidad, Unit Economics y Viabilidad
    h4_fin = doc.add_heading("4. MODELO DE RENTABILIDAD Y UNIT ECONOMICS", level=1)
    h4_fin.paragraph_format.space_before = Pt(16)
    
    fin_p = doc.add_paragraph(
        "A continuación se desglosan los costos operativos unitarios por cada 1,000 prospectos procesados a través de la infraestructura:"
    )
    
    cost_data = [
        ("Costos de Inferencia IA (Gemini 2.0 Flash)", "$0.23 USD (~$950 COP)", "1.5k tokens entrada + 200 tokens salida por lead."),
        ("Hosting & Cómputo Backend (VPS)", "$0.10 USD (~$410 COP)", "Servidor 2 vCPU / 4GB RAM prorrateado por volumen."),
        ("Scraping & Conectividad HTTP", "$0.00 USD ($0 COP)", "Ejecución directa sin intermediarios de API de pago."),
        ("Despacho de WhatsApp Asistido", "$0.00 USD ($0 COP)", "Canal nativo directo mediante protocolo wa.me."),
        ("COSTO TOTAL POR 1,000 LEADS AUDITADOS", "$0.33 USD (~$1,360 COP)", "Costo unitario por empresa: $1.36 COP.")
    ]
    
    tbl_c = doc.add_table(rows=len(cost_data) + 1, cols=3)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = tbl_c.rows[0]
    hdr.cells[0].paragraphs[0].add_run("RUBRO DE GASTO").font.bold = True
    hdr.cells[1].paragraphs[0].add_run("COSTO (1,000 PROSPECTOS)").font.bold = True
    hdr.cells[2].paragraphs[0].add_run("DETALLE TÉCNICO").font.bold = True
    for c_i in hdr.cells:
        set_cell_background(c_i, "1E293B")
        c_i.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        
    for idx, (rub, cst, dtl) in enumerate(cost_data, start=1):
        row = tbl_c.rows[idx]
        bg = "F1F5F9" if idx % 2 == 1 else "FFFFFF"
        if idx == len(cost_data):
            bg = "E2E8F0"
        for i, val in enumerate([rub, cst, dtl]):
            set_cell_background(row.cells[i], bg)
            set_cell_margins(row.cells[i], 60, 60, 90, 90)
            r = row.cells[i].paragraphs[0].add_run(val)
            r.font.size = Pt(8.5)
            if idx == len(cost_data) or i == 0:
                r.font.bold = True
                
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    
    # 5. Conexiones Internas y Ajustes Manuales
    h5_man = doc.add_heading("5. GUÍA DE MANTENIMIENTO, CONEXIONES Y AJUSTES MANUALES", level=1)
    h5_man.paragraph_format.space_before = Pt(16)
    
    p_man = doc.add_paragraph(
        "Modificación Manual de Datos y Ajuste de Pipelines:\n\n"
        "A. Actualización de Prospectos vía REST API:\n"
        "Se puede modificar cualquier atributo de un lead enviando un PATCH a '/api/v1/prospects/{lead_id}':\n"
        "Payload JSON:\n"
        "{\n"
        "  \"tenant_id\": \"hzsaas_colombia\",\n"
        "  \"contact_name\": \"Dr. Jorge Arango\",\n"
        "  \"contact_phone\": \"3009876543\",\n"
        "  \"city\": \"Montería\",\n"
        "  \"followup_day\": 3,\n"
        "  \"internal_notes\": \"Llamar el viernes antes de mediodía\",\n"
        "  \"draft_message\": \"Propuesta modificada...\"\n"
        "}\n\n"
        "B. Modificación de Esquema en Base de Datos:\n"
        "El archivo 'src/db/session.py' contiene la función 'init_db()' encargada de auditar la estructura física de SQLite y ejecutar los ALTER TABLE correspondientes automáticamente al encender el servicio. Si se migra a PostgreSQL, se recomienda activar Alembic manteniendo las mismas definiciones ORM de 'src/db/models.py'.\n\n"
        "C. Cambio de Parámetros de Inferencia IA:\n"
        "Las variables de entorno en 'RevOpsAI/.env' controlan el proveedor:\n"
        "- GEMINI_API_KEY: Llave de Google AI Studio.\n"
        "- DASHBOARD_USERNAME y DASHBOARD_PASSWORD: Credenciales de acceso administrativo maestro.\n"
        "- ENVIRONMENT: Fijar en 'production' para habilitar cookies seguras HTTPS."
    )
    p_man.paragraph_format.space_after = Pt(14)
    
    out_path = r"c:\Users\JESUS\Desktop\Antigravity\docs\Manual_Tecnico_Interno_RevOps_AI.docx"
    doc.save(out_path)
    print(f"Manual técnico guardado en: {out_path}")

if __name__ == "__main__":
    create_user_manual()
    create_technical_manual()

