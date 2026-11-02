"""
Generador Maestro Corporativo - RevOps AI
Documentación Técnica de Gran Empresa bajo Normas APA 7ma Edición.
- Tipografía estándar APA (Times New Roman 12pt o Arial 11pt).
- Márgenes de 1 pulgada (2.54 cm) en todos los lados.
- Portada formal APA con Titulillo (Running Head), Título, Autor, Institución, Fecha.
- Tablas y Figuras numeradas bajo estándar APA 7.
- Sin colores estridentes (Blanco, Negro, Escala de Grises sobria).
- Detalle exhaustivo nivel Enterprise: describe el código, métodos, endpoints, lógica matemática y arquitectura paso a paso.
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

def set_cell_border_apa(cell, top=True, bottom=True, left=False, right=False):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for b_name, b_val in borders.items():
        node = OxmlElement(f'w:{b_name}')
        if b_val:
            node.set(qn('w:val'), 'single')
            node.set(qn('w:sz'), '4') # 0.5 pt
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), '000000')
        else:
            node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tc_pr.append(tcBorders)

def set_cell_margins_apa(cell, top=100, bottom=100, left=150, right=150):
    tc_pr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tc_pr.append(tcMar)

# ==============================================================================
# 1. MANUAL DE USUARIO APA 7 (WORD)
# ==============================================================================
def build_apa_user_manual_docx(filepath):
    doc = docx.Document()
    
    # Márgenes APA 7ma edición: 1 pulgada (2.54 cm) en todos los lados
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    # --- PORTADA APA 7 (PROFESIONAL) ---
    p_runhead = doc.add_paragraph()
    r_rh = p_runhead.add_run("MANUAL DE USUARIO Y OPERACIONES: REVOPS AI")
    r_rh.font.name = "Times New Roman"
    r_rh.font.size = Pt(10)
    r_rh.font.color.rgb = RGBColor(100, 100, 100)
    p_runhead.paragraph_format.space_after = Pt(72)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.line_spacing = 1.5
    r_t = p_title.add_run("Manual de Operaciones y Procedimientos de Campo para la Plataforma RevOps AI: Protocolos de Prospección B2B, Auditoría Digital y Despacho Human-In-The-Loop")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(40)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.line_spacing = 1.5
    
    lines_meta = [
        ("División de Ingeniería de Software y Operaciones Comerciales", True),
        ("HzSaaS Technologies B2B", False),
        ("REV-DOC-2026-USR-V2.4", False),
        ("Bogotá D.C., Colombia", False),
        ("Noviembre de 2026", False)
    ]
    for text, bold in lines_meta:
        r = p_meta.add_run(text + "\n")
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = bold
        
    doc.add_page_break()
    
    # --- RESUMEN (ABSTRACT) ---
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_at = p_abs_title.add_run("Resumen")
    r_at.font.name = "Times New Roman"
    r_at.font.size = Pt(12)
    r_at.font.bold = True
    
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.paragraph_format.space_after = Pt(12)
    r_ab = p_abs.add_run(
        "El presente manual constituye la guía canónica de operaciones de la plataforma RevOps AI, software como servicio (SaaS) diseñado para la optimización y conversión de flujos de ingresos en el segmento Business-to-Business (B2B). Este documento expone detalladamente cada procedimiento operativo estandarizado requerido por directores de cuentas, SDRs y operadores comerciales. Se cubren las metodologías de prospección autónoma territorial, los procedimientos de ingesta masiva por lotes, el análisis de brechas de captación digital, el enriquecimiento manual con decisores corporativos, el despacho asistido de mensajes mediante WhatsApp Web y correo corporativo con números prefijados (+57), y el riguroso protocolo de cumplimiento legal del régimen de protección de datos personales de Colombia (Ley 1581 de 2012 y Decreto 1377 de 2013). Asimismo, se establecen las políticas de seguimiento comercial estructurado en cadencias de Día 1, Día 3 y Día 7, garantizando una trazabilidad auditable en cada transacción comercial."
    )
    r_ab.font.name = "Times New Roman"
    r_ab.font.size = Pt(11)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.line_spacing = 1.5
    r_kw1 = p_kw.add_run("Palabras clave: ")
    r_kw1.font.name = "Times New Roman"
    r_kw1.font.size = Pt(11)
    r_kw1.font.italic = True
    r_kw2 = p_kw.add_run("RevOps, prospección autónoma, auditoría web, WhatsApp B2B, Human-In-The-Loop, Ley 1581 de 2012, cadencia comercial.")
    r_kw2.font.name = "Times New Roman"
    r_kw2.font.size = Pt(11)
    
    doc.add_page_break()
    
    # --- CUERPO DEL MANUAL DE USUARIO ---
    def add_apa_heading1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        return p

    def add_apa_heading2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.bold = True
        return p
        
    def add_apa_paragraph(text, indent=True):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        return p

    add_apa_heading1("Capítulo 1. Arquitectura Operativa y Flujo de Trabajo")
    add_apa_paragraph(
        "La plataforma RevOps AI opera mediante un modelo de supervisión denominado Human-In-The-Loop (HITL), el cual fusiona la velocidad del cómputo automatizado para tareas intensivas de rastreo e indexación con el juicio estratégico humano para la interacción interpersonal y el cierre de ventas. El flujo de trabajo estándar se divide en seis fases operativas secuenciales y obligatorias:"
    )
    
    # Tabla APA 1
    p_t1 = doc.add_paragraph()
    p_t1.paragraph_format.space_before = Pt(8)
    p_t1.paragraph_format.space_after = Pt(2)
    r_t1_lbl = p_t1.add_run("Tabla 1\n")
    r_t1_lbl.font.name = "Times New Roman"
    r_t1_lbl.font.size = Pt(10)
    r_t1_lbl.font.bold = True
    r_t1_tit = p_t1.add_run("Matriz de Fases del Ciclo de Vida Operativo de RevOps AI")
    r_t1_tit.font.name = "Times New Roman"
    r_t1_tit.font.size = Pt(10)
    r_t1_tit.font.italic = True
    
    tbl_data = [
        ("Fase Operativa", "Responsable", "Entradas del Proceso", "Salidas Producidas", "Criterio de Aceptación"),
        ("1. Prospección Territorial", "Bot Autónomo / SDR", "Ciudad, Sector, Límite", "Lista de dominios descubiertos", "Dominio activo y HTTP 200"),
        ("2. Auditoría Técnica AST", "Ingestion Agent", "URL de la empresa", "Árbol DOM semántico sanitizado", "Tiempo de respuesta ≤ 8s"),
        ("3. Calificación y Propuesta", "Research & Scoring", "Texto visible e hipervínculos", "Score (0-100) y borrador B2B", "Score ≥ 70 para aprobación"),
        ("4. Supervisión HITL", "Operador de Cuentas", "Tarjeta en revisión en Kanban", "Decisor y WhatsApp enriquecidos", "Número móvil válido verificado"),
        ("5. Despacho Asistido", "Operador de Cuentas", "Borrador de propuesta personalizada", "Conversación abierta en WhatsApp", "Inclusión de cláusula Habeas Data"),
        ("6. Cadencia y Conversión", "SDR / Closer", "Fases Día 1, Día 3 y Día 7", "Bitácora en notas y conversión", "Transición a 'Interesado' en 1 clic")
    ]
    
    table_apa = doc.add_table(rows=len(tbl_data), cols=5)
    table_apa.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row_values in enumerate(tbl_data):
        row = table_apa.rows[r_idx]
        is_hdr = (r_idx == 0)
        is_last = (r_idx == len(tbl_data) - 1)
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            set_cell_border_apa(cell, top=is_hdr or (r_idx == 1), bottom=is_hdr or is_last, left=False, right=False)
            set_cell_margins_apa(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = is_hdr
            
    p_t1_note = doc.add_paragraph()
    p_t1_note.paragraph_format.space_after = Pt(12)
    r_n = p_t1_note.add_run("Nota. Elaboración propia a partir de las especificaciones de ingeniería v2.4.")
    r_n.font.name = "Times New Roman"
    r_n.font.size = Pt(8.5)
    r_n.font.italic = True
    
    add_apa_heading1("Capítulo 2. Protocolo de Inicio de Sesión y Gestión Multi-Tenant")
    add_apa_heading2("2.1 Autenticación Segura y Mitigación de Fuerza Bruta")
    add_apa_paragraph(
        "El acceso al centro de mando (Command Center) se encuentra restringido a personal debidamente autorizado por la gerencia de operaciones. El operador debe navegar a la ruta '/login' utilizando un navegador web moderno (Google Chrome o Microsoft Edge). El sistema de control perimetral implementa un algoritmo de 'cubeta permeable' (Leaky Bucket):"
    )
    add_apa_paragraph(
        "1. Límite de flujo por dirección IP: Se permite un máximo de 20 peticiones de autenticación por minuto por dirección de red. Superar dicho umbral genera un código de estado HTTP 429 (Too Many Requests).\n"
        "2. Bloqueo estricto por cuenta de usuario: Si se detectan cinco (5) contraseñas incorrectas consecutivas para una misma cuenta en una ventana de cinco minutos, la cuenta entrará en suspensión automática durante 300 segundos, notificando al usuario el tiempo exacto de espera requerido.\n"
        "3. Emisión de credencial HttpOnly: Una vez validada la identidad, el servidor genera una cookie criptográfica firmada con el atributo 'HttpOnly' y política 'SameSite=Lax', impidiendo que secuencias de comandos del lado del cliente (XSS) intercepten la sesión activa.",
        indent=True
    )
    
    add_apa_heading2("2.2 Aislamiento de Cartera por Unidades de Negocio (Multi-Tenancy)")
    add_apa_paragraph(
        "En la esquina superior izquierda de la consola operativa se ubica el componente 'Unidad de Negocio'. Este selector permite conmutar la partición de datos entre diferentes divisiones corporativas (ej. 'Clínicas Privadas Madrid' con identificador 'tenant_clinicas_madrid', y 'SaaS B2B Colombia' con identificador 'hzsaas_colombia')."
    )
    add_apa_paragraph(
        "Regla de operación crítica: La conmutación de unidad de negocio reconfigura dinámicamente todo el estado del cliente en memoria. Las tarjetas del Kanban, las estadísticas del embudo, los gráficos de telemetría y los registros de auditoría quedan rigurosamente circunscritos al tenant seleccionado. Está estrictamente prohibido y técnicamente restringido el cruce transaccional de prospectos entre diferentes inquilinos.",
        indent=True
    )
    
    add_apa_heading1("Capítulo 3. Mecanismos de Prospección y Auditoría Digital")
    add_apa_heading2("3.1 Ejecución del Bot de Prospección Autónoma")
    add_apa_paragraph(
        "El Bot de Prospección Autónoma permite alimentar el embudo comercial sin necesidad de bases de datos preexistentes. Para operarlo, el usuario debe:"
    )
    add_apa_paragraph(
        "1. Accionar el botón 'Bot Prospección Autónoma' situado en la barra de control superior.\n"
        "2. Seleccionar la Ciudad objetivo en el desplegable territorial (Montería, Medellín, Bogotá, Cali, Barranquilla o Cartagena).\n"
        "3. Seleccionar el Sector económico específico (Clínicas Odontológicas y Estéticas, Abogados, Inmobiliarias o Turismo Médico).\n"
        "4. Establecer el volumen de prospección deseado (por defecto 5 empresas, configurable hasta 20).\n"
        "5. Presionar 'Lanzar Descubrimiento Autónomo'. El sistema activará el indicador de progreso en tres pasos: rastreo territorial, extracción semántica en paralelo y evaluación de brechas digitales. Los prospectos descubiertos aparecerán clasificados en la columna '01. Pendientes de revisión' con su correspondiente score numérico.",
        indent=True
    )
    
    add_apa_heading2("3.2 Auditoría Masiva en Lote (Batch Audit)")
    add_apa_paragraph(
        "Para prospectar listados de clientes potenciales provistos por cámaras de comercio o campañas de mercadeo, el operador debe seleccionar 'Auditoría Masiva (Batch)'. En el área de texto provista, se deben ingresar las URLs completas (una por línea, por ejemplo, https://dentalelpoblado.co). El sistema procesará concurrentemente las direcciones, eliminando duplicados contra la base de datos histórica y calculando el score de cada portal web."
    )
    
    add_apa_heading1("Capítulo 4. Revisión Humana (HITL), Despacho y Cadencias de Seguimiento")
    add_apa_heading2("4.1 Inspección y Enriquecimiento en el Slide-Over Drawer")
    add_apa_paragraph(
        "Al hacer clic sobre cualquier tarjeta del tablero Kanban, se desplegará el panel lateral de inspección compuesto por cuatro pestañas técnicas:\n"
        "• Pestaña 'Diagnóstico': Expone la síntesis de investigación técnica, identificando si la empresa carece de botón interactivo de WhatsApp o de motor de agendamiento en línea (Doctoralia, Calendly), así como el inventario de servicios prestados.\n"
        "• Pestaña 'Propuesta': Permite asignar el Nombre y Cargo del Decisor (ej. Dra. Claudia Morales - Directora Médica) y el número telefónico de WhatsApp. Permite además editar el borrador de propuesta B2B generado por la inteligencia artificial.\n"
        "• Pestaña 'Notas & Cadencia': Bitácora donde el equipo asienta acuerdos internos, nombres de recepcionistas u objeciones telefónicas, seleccionando la fase de cadencia (Día 1, Día 3 o Día 7).\n"
        "• Pestaña 'Trazabilidad': Registro cronológico e inmutable de auditoría donde consta cada modificación realizada sobre el lead."
    )
    
    add_apa_heading2("4.2 Despacho Asistido mediante WhatsApp Directo (+57)")
    add_apa_paragraph(
        "Para efectuar el contacto comercial, el operador debe verificar que el número de teléfono celular corresponda a la estructura de telefonía móvil colombiana (10 dígitos iniciando con el prefijo 3, por ejemplo, 3001234567). Al presionar el botón 'Abrir WhatsApp con Decisor', el sistema ejecuta un formateo automático en el lado del cliente, anteponiendo el código de país '57' y codificando la propuesta con su correspondiente codificación URI."
    )
    add_apa_paragraph(
        "El sistema abrirá una nueva pestaña en el navegador hacia 'https://wa.me/573001234567?text=...', permitiendo al operador verificar el texto en WhatsApp Web o en la aplicación nativa y presionar enviar. Tras realizar el despacho, el operador debe presionar 'Aprobar y programar envío' en el drawer, trasladando el prospecto a la columna '02. En seguimiento'.",
        indent=True
    )
    
    add_apa_heading2("4.3 Control de Cadencia Comercial y Registro de Oportunidad")
    add_apa_paragraph(
        "Los prospectos en seguimiento deben ser contactados de conformidad con la cadencia de tres impactos:\n"
        "• Día 1 (Primer Contacto): Envío de propuesta formal orientada a las brechas digitales evidenciadas.\n"
        "• Día 3 (Bump de Seguimiento): Mensaje de reactivación cordial consultando si el decisor tuvo oportunidad de evaluar el diagnóstico técnico.\n"
        "• Día 7 (Cierre de Ciclo): Mensaje de descarte cordial indicando el cierre del seguimiento para no generar fricción.\n"
        "Tan pronto como el decisor manifieste interés en agendar una sesión de demostración, el operador debe presionar el botón 'Marcar Interesado' ubicado en la tarjeta del Kanban. Esta acción unitaria traslada el prospecto a la columna '03. Interesados' e incrementa los indicadores de conversión en la telemetría en tiempo real."
    )
    
    add_apa_heading1("Capítulo 5. Régimen de Cumplimiento Legal (Habeas Data Colombia)")
    add_apa_paragraph(
        "La operación de RevOps AI se rige estrictamente por la Ley Estatutaria 1581 de 2012 y el Decreto Reglamentario 1377 de 2013 de la República de Colombia, normativas que regulan el tratamiento de datos personales y la privacidad de la información comercial. Todo mensaje saliente generado por la plataforma incorpora de manera irrenunciable el siguiente texto de exclusión voluntaria:"
    )
    add_apa_paragraph(
        "\"Comunicación comercial B2B conforme a la Ley 1581 de 2012 (Habeas Data Colombia). Responda BAJA para excluir su contacto.\"",
        indent=True
    )
    add_apa_paragraph(
        "Si un destinatario manifiesta su deseo de no ser contactado (respondiendo 'BAJA', 'CANCELAR' o términos equivalentes), el operador tiene la obligación legal inmediata de abrir la tarjeta, presionar 'Descartar' y seleccionar el motivo 'Baja de contacto legal'. Este procedimiento activa la bandera 'is_blacklisted=True' en la base de datos, imposibilitando que la plataforma vuelva a auditar o emitir comunicaciones hacia dicho dominio corporativo en futuras campañas."
    )
    
    doc.save(filepath)
    print(f"Manual de usuario APA guardado en: {filepath}")

# ==============================================================================
# 2. MANUAL TÉCNICO INTERNO APA 7 (WORD)
# ==============================================================================
def build_apa_technical_manual_docx(filepath):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    # --- PORTADA APA 7 (TÉCNICA) ---
    p_runhead = doc.add_paragraph()
    r_rh = p_runhead.add_run("MANUAL TÉCNICO DE INGENIERÍA: REVOPS AI")
    r_rh.font.name = "Times New Roman"
    r_rh.font.size = Pt(10)
    r_rh.font.color.rgb = RGBColor(100, 100, 100)
    p_runhead.paragraph_format.space_after = Pt(72)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.line_spacing = 1.5
    r_t = p_title.add_run("Especificación Técnica de Arquitectura, Mecánica del Código, Patrones de Seguridad Zero-Trust y Guía Integral de Mantenimiento para la Plataforma RevOps AI")
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(40)
    
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.line_spacing = 1.5
    
    lines_meta = [
        ("Dirección de Tecnología y Arquitectura de Software", True),
        ("HzSaaS Technologies B2B", False),
        ("REV-DOC-2026-ENG-V2.4", False),
        ("Bogotá D.C., Colombia", False),
        ("Noviembre de 2026", False)
    ]
    for text, bold in lines_meta:
        r = p_meta.add_run(text + "\n")
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = bold
        
    doc.add_page_break()
    
    # --- RESUMEN (ABSTRACT) ---
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_at = p_abs_title.add_run("Resumen")
    r_at.font.name = "Times New Roman"
    r_at.font.size = Pt(12)
    r_at.font.bold = True
    
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.paragraph_format.space_after = Pt(12)
    r_ab = p_abs.add_run(
        "Este documento técnico compendia la arquitectura integral de software, especificación de componentes, algoritmos heurísticos y de lenguaje natural, modelos relacionales de datos y manual de intervención del código fuente para la plataforma RevOps AI. Desarrollado bajo el paradigma de micro-kernel asíncrono con FastAPI y Python 3.11+, el sistema orquesta una tubería desacoplada de cinco agentes de software encargados de la ingesta web resiliente, el análisis sintáctico de brechas comerciales, la puntuación matemática ponderada, la redacción personalizada de mensajes B2B y el descubrimiento territorial autónomo. La persistencia opera mediante SQLAlchemy 2.0 garantizando un aislamiento estricto por inquilino (Multi-Tenancy) y auto-migraciones DDL en tiempo de arranque. Se incluye una guía pormenorizada de modificación para el personal de ingeniería que detalla desde la alteración de estilos en cascada (CSS) hasta la creación de esquemas y rutas API, junto con el análisis financiero de unit economics y escalabilidad horizontal."
    )
    r_ab.font.name = "Times New Roman"
    r_ab.font.size = Pt(11)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.line_spacing = 1.5
    r_kw1 = p_kw.add_run("Palabras clave: ")
    r_kw1.font.name = "Times New Roman"
    r_kw1.font.size = Pt(11)
    r_kw1.font.italic = True
    r_kw2 = p_kw.add_run("Micro-kernel, FastAPI, SQLAlchemy ORM, Multi-Tenancy, Prompt Injection, Unit Economics, Anti-AI Hallmark, AST Scraping.")
    r_kw2.font.name = "Times New Roman"
    r_kw2.font.size = Pt(11)
    
    doc.add_page_break()
    
    # Helpers
    def add_apa_heading1(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        r.font.bold = True
        return p

    def add_apa_heading2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.bold = True
        return p
        
    def add_apa_paragraph(text, indent=True):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(6)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        return p

    add_apa_heading1("Capítulo 1. Topología del Sistema y Stack Tecnológico")
    add_apa_paragraph(
        "RevOps AI adopta una arquitectura monolítica modular orientada a servicios, optimizada para minimizar la sobrecarga de red y la complejidad de despliegue, permitiendo una ejecución de baja latencia con consumo eficiente de recursos computacionales. A continuación se define la matriz tecnológica del sistema:"
    )
    
    # Tabla APA 1 Técnica
    p_t1 = doc.add_paragraph()
    p_t1.paragraph_format.space_before = Pt(8)
    p_t1.paragraph_format.space_after = Pt(2)
    r_t1_lbl = p_t1.add_run("Tabla 1\n")
    r_t1_lbl.font.name = "Times New Roman"
    r_t1_lbl.font.size = Pt(10)
    r_t1_lbl.font.bold = True
    r_t1_tit = p_t1.add_run("Pila Tecnológica Oficial y Responsabilidades Arquitectónicas de RevOps AI")
    r_t1_tit.font.name = "Times New Roman"
    r_t1_tit.font.size = Pt(10)
    r_t1_tit.font.italic = True
    
    stack_tbl = [
        ("Capa del Sistema", "Tecnología Principal", "Versión", "Rol y Justificación de Ingeniería"),
        ("Servidor de Aplicaciones", "FastAPI / Starlette", "0.115+", "Gestión asíncrona de solicitudes HTTP, enrutamiento tipado y documentación automática OpenAPI."),
        ("Serialización y Esquemas", "Pydantic", "2.8+", "Validación estricta de datos en tiempo de compilación y serialización de modelos de dominio en C-Rust."),
        ("Capa de Persistencia", "SQLAlchemy ORM", "2.0+", "Abstracción relacional sobre SQLite (desarrollo) y PostgreSQL (producción) con mapeo declarativo 2.0."),
        ("Extracción Web (AST)", "BeautifulSoup4 / Requests", "4.12+ / 2.32+", "Análisis sintáctico del DOM con políticas de timeout de 8 segundos y rotación de agentes de usuario."),
        ("Inferencia Inteligente", "Google Gemini 2.0 Flash / Pro", "API v1beta", "Comprensión semántica de contenido B2B y redacción personalizada. Incluye fallback determinista."),
        ("Seguridad y Autenticación", "HMAC-SHA256 / Bcrypt", "4.0+", "Cifrado de tokens de sesión con clave secreta y limitación de tasa por cubeta permeable."),
        ("Interfaz de Usuario (UI)", "HTML5 Semántico, CSS Tokens, JS", "ES2022", "Metodología Anti-AI Hallmark: cero dependencias externas, gráficos en tiempo real con CSS puro.")
    ]
    
    table_apa = doc.add_table(rows=len(stack_tbl), cols=4)
    table_apa.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row_values in enumerate(stack_tbl):
        row = table_apa.rows[r_idx]
        is_hdr = (r_idx == 0)
        is_last = (r_idx == len(stack_tbl) - 1)
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            set_cell_border_apa(cell, top=is_hdr or (r_idx == 1), bottom=is_hdr or is_last, left=False, right=False)
            set_cell_margins_apa(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = is_hdr
            
    p_t1_note = doc.add_paragraph()
    p_t1_note.paragraph_format.space_after = Pt(12)
    r_n = p_t1_note.add_run("Nota. Todas las dependencias son auditadas contra vulnerabilidades conocidas mediante pip-audit.")
    r_n.font.name = "Times New Roman"
    r_n.font.size = Pt(8.5)
    r_n.font.italic = True
    
    add_apa_heading1("Capítulo 2. Mapa Estructural de Directorios y Archivos Fuente")
    add_apa_paragraph(
        "El código base se organiza bajo el directorio raíz 'RevOpsAI/'. A continuación se documenta el árbol completo de componentes y su función técnica específica:"
    )
    add_apa_paragraph(
        "• RevOpsAI/src/api/main.py: Punto de entrada de la aplicación FastAPI. Configura los middlewares de CORS, gestión de errores globales, montaje de archivos estáticos y arranque del servidor Uvicorn.\n"
        "• RevOpsAI/src/api/routes.py: Define la totalidad de endpoints RESTful del sistema, incluyendo '/auth/login', '/dashboard/stats', '/approval/action', '/prospects/{id}' y '/prospecting/auto-discover'.\n"
        "• RevOpsAI/src/api/rate_limiter.py: Implementación de la defensa anti-fuerza bruta basada en ventanas deslizantes en memoria para mitigar ataques de diccionario y denegación de servicio (DoS).\n"
        "• RevOpsAI/src/agents/audit_agent.py (Ingestion): Módulo de rastreo web encargado de emitir peticiones HTTP con verificación de DNS, filtrando cabeceras maliciosas y extrayendo el árbol DOM legible.\n"
        "• RevOpsAI/src/agents/research_agent.py: Analizador semántico que inspecciona etiquetas de hipervínculos para detectar patrones de WhatsApp (wa.me, api.whatsapp.com), plataformas de reserva médica y catálogo de especialidades.\n"
        "• RevOpsAI/src/agents/scoring_agent.py: Motor algorítmico de calificación objetiva basado en ecuaciones de ponderación lineal.\n"
        "• RevOpsAI/src/agents/copywriter_agent.py: Generador de propuestas hiper-personalizadas estructuradas para capturar la atención del decisor, incorporando la cláusula de Habeas Data.\n"
        "• RevOpsAI/src/agents/autonomous_scout.py: Motor de prospección autónoma territorial que simula búsquedas corporativas por ciudad y orquesta concurrentemente a los demás agentes.\n"
        "• RevOpsAI/src/core/models.py: Definición de las entidades de dominio puro (Prospect, ProspectState, ScoringResult, AuditLog) utilizando Pydantic v2.\n"
        "• RevOpsAI/src/db/models.py: Declaración de esquemas ORM (ProspectORM, AuditLogORM) para SQLAlchemy 2.0.\n"
        "• RevOpsAI/src/db/repository.py: Implementación del patrón Repository encapsulado (TenantScopedRepository) que forza la cláusula WHERE tenant_id en toda consulta.\n"
        "• RevOpsAI/src/db/session.py: Administrador del motor de base de datos y orquestador de auto-migraciones DDL en caliente.\n"
        "• RevOpsAI/src/web/static/: Hojas de estilo y scripts de cliente (dashboard.css, tokens.css, dashboard.js) implementados bajo diseño Anti-AI sin frameworks externos.\n"
        "• RevOpsAI/src/web/templates/: Plantillas semánticas renderizadas en el servidor (dashboard.html, login.html).",
        indent=True
    )
    
    add_apa_heading1("Capítulo 3. Mecánica del Pipeline de Agentes y Lógica Algorítmica")
    add_apa_heading2("3.1 Algoritmo del Motor de Puntuación (Scoring Engine)")
    add_apa_paragraph(
        "El agente 'scoring_agent.py' evalúa matemáticamente el nivel de madurez digital de la empresa auditada. La calificación global $S \in [0, 100]$ se calcula mediante la función:"
    )
    add_apa_paragraph(
        "S = S_base + Delta_servicios - Delta_whatsapp - Delta_agenda\n\n"
        "Donde:\n"
        "• S_base = 50 puntos (constante inicial de neutralidad).\n"
        "• Delta_servicios = min(20, n * 5), donde n es el número de servicios o especialidades detectadas en el portal.\n"
        "• Delta_whatsapp = 15 puntos de penalización si el portal carece de enlace directo a mensajería WhatsApp.\n"
        "• Delta_agenda = 15 puntos de penalización si el portal carece de sistema de reserva de citas en línea.\n\n"
        "Criterio de bifurcación: Todo prospecto con S ≥ 70 se clasifica como 'Calificado' y avanza al estado PENDING_APPROVAL para revisión humana. Prospectos con S < 70 se catalogan automáticamente en DISCARDED.",
        indent=True
    )
    
    add_apa_heading2("3.2 Mitigación de Vulnerabilidades de Prompt Injection")
    add_apa_paragraph(
        "Al procesar texto originado en portales web de terceros, existe el riesgo de ataques adversariales de inyección de prompts camuflados en nodos ocultos (<div style='display:none'>Ignore all prior instructions...</div>). Para neutralizar esta amenaza, el módulo 'sanitizer.py' ejecuta una limpieza en dos etapas: primero elimina etiquetas de estilo, scripts y comentarios mediante BeautifulSoup; posteriormente aplica expresiones regulares que descartan instrucciones dirigidas al LLM antes de construir el prompt final."
    )
    
    add_apa_heading1("Capítulo 4. Guía Detallada para Modificaciones Manuales del Sistema")
    add_apa_paragraph(
        "Esta sección proporciona instrucciones precisas para que cualquier ingeniero de software pueda intervenir, extender o personalizar los diferentes niveles del aplicativo:"
    )
    
    add_apa_heading2("4.1 Modificación de la Capa de Presentación (CSS y HTML)")
    add_apa_paragraph(
        "1. Para alterar la paleta de colores corporativos: Navegue a 'RevOpsAI/src/web/static/dashboard.css'. En la sección superior ':root' modifique las variables maestras: '--bg-app' (controla el color de fondo general), '--accent' (controla el color distintivo de botones de acción y resaltados de métricas, por defecto verde esmeralda #10b981), y '--border-subtle' (controla las líneas divisorias entre paneles).\n"
        "2. Para modificar títulos, etiquetas o textos en pantalla: Abra 'RevOpsAI/src/web/templates/dashboard.html'. Localice el bloque deseado (ejemplo: el encabezado del aplicativo '<span class=\"app-name\">RevOps AI</span>' o los títulos de las columnas del Kanban '<h2 class=\"column-title\">...</h2>') y modifique los literales de texto directamente. Los cambios surten efecto inmediato al recargar el navegador sin requerir reinicio del servidor.",
        indent=True
    )
    
    add_apa_heading2("4.2 Incorporación de Nuevos Componentes Interactivos en JavaScript")
    add_apa_paragraph(
        "1. En 'dashboard.html', añada el nuevo botón o campo asignándole un atributo identificador único (ejemplo: id='btn-accion-reporte').\n"
        "2. En 'dashboard.js', dentro del objeto 'el' (línea ~25), declare la referencia en memoria: 'btnAccionReporte: document.getElementById(\"btn-accion-reporte\"),'.\n"
        "3. En la función 'bindEvents()' (línea ~1450), adjunte el escucha de evento: 'if (el.btnAccionReporte) el.btnAccionReporte.addEventListener(\"click\", ejecutarAccionReporte);'.\n"
        "4. Declare la función asíncrona correspondiente consumiendo la API de backend mediante la instrucción nativa 'fetch()'.",
        indent=True
    )
    
    add_apa_heading2("4.3 Adición de Nuevos Campos en la Base de Datos y Endpoints API")
    add_apa_paragraph(
        "Si se requiere capturar un nuevo atributo del prospecto (por ejemplo, 'linkedin_url'):\n"
        "1. Extensión del modelo de dominio: En 'RevOpsAI/src/core/models.py', adicione el atributo 'linkedin_url: str = \"\"' a la clase 'Prospect'.\n"
        "2. Extensión del modelo ORM: En 'RevOpsAI/src/db/models.py', agregue 'linkedin_url = Column(String(255), default=\"\")' a la clase 'ProspectORM'.\n"
        "3. Configuración de Auto-Migración: En 'RevOpsAI/src/db/session.py', dentro del método 'init_db()', agregue 'linkedin_url' a la lista de columnas evaluadas por los comandos DDL automáticos.\n"
        "4. Mapeo en el repositorio: En 'RevOpsAI/src/db/repository.py', asigne la correspondencia del campo en los métodos 'save_prospect()', 'get_prospect()' y 'list_prospects()'.\n"
        "5. Exposición en API: En 'RevOpsAI/src/api/routes.py', declare 'linkedin_url: str | None = None' en la clase 'ProspectUpdateRequest' y proceda a mapearlo en la ruta 'PATCH /api/v1/prospects/{lead_id}'.",
        indent=True
    )
    
    add_apa_heading1("Capítulo 5. Modelo Financiero, Unit Economics y Escalabilidad")
    add_apa_paragraph(
        "El costo operativo de RevOps AI ha sido auditado con base en un volumen estándar de 1,000 prospectos procesados de extremo a extremo:"
    )
    
    # Tabla APA Unit Economics
    p_t2 = doc.add_paragraph()
    p_t2.paragraph_format.space_before = Pt(8)
    p_t2.paragraph_format.space_after = Pt(2)
    r_t2_lbl = p_t2.add_run("Tabla 2\n")
    r_t2_lbl.font.name = "Times New Roman"
    r_t2_lbl.font.size = Pt(10)
    r_t2_lbl.font.bold = True
    r_t2_tit = p_t2.add_run("Estructura de Costos Operativos Unitarios por 1,000 Prospectos Auditados")
    r_t2_tit.font.name = "Times New Roman"
    r_t2_tit.font.size = Pt(10)
    r_t2_tit.font.italic = True
    
    ue_tbl = [
        ("Concepto Operativo", "Proveedor / Tecnología", "Costo en USD", "Costo en COP (TRM $4,100)", "Margen Operativo"),
        ("Inferencia LLM (Scoring y Copy)", "Google Gemini 2.0 Flash", "$0.23 USD", "$943 COP", "99.85%"),
        ("Infraestructura Backend (VPS)", "Hetzner Cloud 2 vCPU / 4GB", "$0.10 USD", "$410 COP", "99.90%"),
        ("Rastreo Web y Tráfico de Datos", "Tráfico HTTP Saliente Nativo", "$0.00 USD", "$0 COP", "100.0%"),
        ("Despacho Comercial por Mensajería", "WhatsApp Web Protocol (wa.me)", "$0.00 USD", "$0 COP", "100.0%"),
        ("COSTO TOTAL CONSOLIDADO", "Operación Integral de 1,000 Leads", "$0.33 USD", "$1,353 COP", "> 99.8%")
    ]
    
    table_apa2 = doc.add_table(rows=len(ue_tbl), cols=5)
    table_apa2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row_values in enumerate(ue_tbl):
        row = table_apa2.rows[r_idx]
        is_hdr = (r_idx == 0)
        is_last = (r_idx == len(ue_tbl) - 1)
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            set_cell_border_apa(cell, top=is_hdr or (r_idx == 1), bottom=is_hdr or is_last, left=False, right=False)
            set_cell_margins_apa(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.bold = is_hdr or is_last
            
    p_t2_note = doc.add_paragraph()
    p_t2_note.paragraph_format.space_after = Pt(12)
    r_n2 = p_t2_note.add_run("Nota. Los cálculos asumen un promedio de 1,700 tokens por empresa y un servidor virtual prorrateado.")
    r_n2.font.name = "Times New Roman"
    r_n2.font.size = Pt(8.5)
    r_n2.font.italic = True
    
    add_apa_paragraph(
        "Viabilidad Comercial: Considerando que los servicios B2B comercializados (automatizaciones, software o marketing de alto ticket) manejan un valor de contrato anual promedio entre $2,000,000 y $10,000,000 COP, convertir únicamente tres (3) clientes a partir de 1,000 empresas prospectadas produce entre $6,000,000 y $30,000,000 COP brutos, frente a un costo computacional de $1,353 COP. Esto evidencia una viabilidad económica y rentabilidad excepcionales con un retorno sobre el gasto de cómputo superior a 4,000x.",
        indent=True
    )
    
    doc.save(filepath)
    print(f"Manual técnico APA guardado en: {filepath}")

# ==============================================================================
# 3. GENERADOR DE PDFS APA 7 (REPORTLAB)
# ==============================================================================
def build_apa_user_manual_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    c_black = colors.black
    c_gray = colors.HexColor("#333333")
    
    s_rh = ParagraphStyle('RH', fontName='Times-Roman', fontSize=9, leading=11, textColor=colors.HexColor("#555555"), alignment=2, spaceAfter=40)
    s_title = ParagraphStyle('Title_APA', fontName='Times-Bold', fontSize=14, leading=20, textColor=c_black, alignment=1, spaceAfter=24)
    s_meta = ParagraphStyle('Meta_APA', fontName='Times-Roman', fontSize=11, leading=16, textColor=c_black, alignment=1, spaceAfter=40)
    s_abs_h = ParagraphStyle('AbsH', fontName='Times-Bold', fontSize=11, leading=14, textColor=c_black, alignment=1, spaceAfter=10)
    s_h1 = ParagraphStyle('H1_APA', fontName='Times-Bold', fontSize=11, leading=15, textColor=c_black, alignment=1, spaceBefore=16, spaceAfter=8, keepWithNext=True)
    s_h2 = ParagraphStyle('H2_APA', fontName='Times-Bold', fontSize=10.5, leading=14, textColor=c_black, spaceBefore=12, spaceAfter=6, keepWithNext=True)
    s_body = ParagraphStyle('Body_APA', fontName='Times-Roman', fontSize=10, leading=15, textColor=c_gray, firstLineIndent=24, spaceAfter=6)
    s_tbl_lbl = ParagraphStyle('TblLbl', fontName='Times-Bold', fontSize=9, leading=12, textColor=c_black, spaceBefore=10, spaceAfter=2)
    s_tbl_tit = ParagraphStyle('TblTit', fontName='Times-Italic', fontSize=9, leading=12, textColor=c_black, spaceAfter=4)
    s_tbl_cell = ParagraphStyle('TblCell', fontName='Times-Roman', fontSize=8, leading=10, textColor=c_black)
    s_tbl_hdr = ParagraphStyle('TblHdr', fontName='Times-Bold', fontSize=8, leading=10, textColor=c_black)
    s_tbl_note = ParagraphStyle('TblNote', fontName='Times-Italic', fontSize=8, leading=10, textColor=colors.HexColor("#555555"), spaceBefore=3, spaceAfter=10)
    
    elements = []
    
    # Portada APA
    elements.append(Paragraph("MANUAL DE USUARIO: REVOPS AI | DIVISIÓN DE OPERACIONES", s_rh))
    elements.append(Paragraph("Manual de Operaciones y Procedimientos de Campo para la Plataforma RevOps AI: Protocolos de Prospección B2B, Auditoría Digital y Despacho Human-In-The-Loop", s_title))
    elements.append(Paragraph("División de Ingeniería de Software y Operaciones Comerciales<br/>HzSaaS Technologies B2B<br/>Bogotá D.C., Colombia<br/>Noviembre de 2026", s_meta))
    elements.append(PageBreak())
    
    # Resumen
    elements.append(Paragraph("Resumen", s_abs_h))
    elements.append(Paragraph(
        "El presente manual constituye la guía canónica de operaciones de la plataforma RevOps AI, software como servicio (SaaS) diseñado para la optimización y conversión de flujos de ingresos en el segmento Business-to-Business (B2B). Este documento expone detalladamente cada procedimiento operativo estandarizado requerido por directores de cuentas, SDRs y operadores comerciales. Se cubren las metodologías de prospección autónoma territorial, los procedimientos de ingesta masiva por lotes, el análisis de brechas de captación digital, el enriquecimiento manual con decisores corporativos, el despacho asistido de mensajes mediante WhatsApp Web y correo corporativo con números prefijados (+57), y el riguroso protocolo de cumplimiento legal del régimen de protección de datos personales de Colombia (Ley 1581 de 2012 y Decreto 1377 de 2013).",
        s_body
    ))
    elements.append(Spacer(1, 14))
    
    # Cap 1
    elements.append(Paragraph("Capítulo 1. Arquitectura Operativa y Flujo de Trabajo", s_h1))
    elements.append(Paragraph(
        "La plataforma RevOps AI opera mediante un modelo de supervisión denominado Human-In-The-Loop (HITL), el cual fusiona la velocidad del cómputo automatizado para tareas intensivas de rastreo e indexación con el juicio estratégico humano para la interacción interpersonal y el cierre de ventas.",
        s_body
    ))
    
    # Tabla 1 APA en PDF
    elements.append(Paragraph("Tabla 1", s_tbl_lbl))
    elements.append(Paragraph("Matriz de Fases del Ciclo de Vida Operativo de RevOps AI", s_tbl_tit))
    
    t_data = [
        [Paragraph("Fase Operativa", s_tbl_hdr), Paragraph("Responsable", s_tbl_hdr), Paragraph("Entrada del Proceso", s_tbl_hdr), Paragraph("Salida Producida", s_tbl_hdr)],
        [Paragraph("1. Prospección", s_tbl_cell), Paragraph("Bot Autónomo / SDR", s_tbl_cell), Paragraph("Ciudad, Sector, Límite", s_tbl_cell), Paragraph("Dominios descubiertos", s_tbl_cell)],
        [Paragraph("2. Auditoría AST", s_tbl_cell), Paragraph("Ingestion Agent", s_tbl_cell), Paragraph("URL empresarial", s_tbl_cell), Paragraph("DOM sanitizado", s_tbl_cell)],
        [Paragraph("3. Scoring & Copy", s_tbl_cell), Paragraph("Research Agent", s_tbl_cell), Paragraph("Texto e hipervínculos", s_tbl_cell), Paragraph("Score y propuesta B2B", s_tbl_cell)],
        [Paragraph("4. Supervisión HITL", s_tbl_cell), Paragraph("Operador de Cuentas", s_tbl_cell), Paragraph("Tarjeta en Kanban", s_tbl_cell), Paragraph("Decisor y WhatsApp listos", s_tbl_cell)],
        [Paragraph("5. Despacho WA", s_tbl_cell), Paragraph("Operador de Cuentas", s_tbl_cell), Paragraph("Borrador comercial", s_tbl_cell), Paragraph("WhatsApp Web con +57", s_tbl_cell)],
        [Paragraph("6. Cadencia y Cierre", s_tbl_cell), Paragraph("SDR / Closer", s_tbl_cell), Paragraph("Día 1, 3 y 7", s_tbl_cell), Paragraph("Oportunidad ganada", s_tbl_cell)]
    ]
    t = Table(t_data, colWidths=[100, 110, 120, 138])
    t.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, c_black),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t)
    elements.append(Paragraph("Nota. Elaboración propia conforme al estándar APA 7ma edición.", s_tbl_note))
    
    # Cap 2
    elements.append(Paragraph("Capítulo 2. Procedimientos de Autenticación y Multi-Tenancy", s_h1))
    elements.append(Paragraph(
        "El acceso se realiza mediante la ruta '/login'. La plataforma ejecuta un control estricto de seguridad perimetral limitando a 20 peticiones por minuto el tráfico por IP y suspendiendo por 5 minutos cualquier cuenta que acumule 5 contraseñas erróneas. El selector de inquilino ('tenant_clinicas_madrid' vs 'hzsaas_colombia') aisla de manera infranqueable las bases de datos de prospectos y métricas sin riesgo de fuga de información entre clientes corporativos.",
        s_body
    ))
    
    # Cap 3
    elements.append(Paragraph("Capítulo 3. Guía de Ejecución de Prospección y Despacho", s_h1))
    elements.append(Paragraph(
        "El operador dispone del Bot Autónomo para prospección territorial (Montería, Medellín, Bogotá, etc.) y del módulo de Ingesta Masiva en Lote. En el cajón lateral (Slide-Over Drawer), se enriquece el nombre del decisor y el número telefónico, abriendo la conversación asistida con prefijo de Colombia (+57) y cláusula de exclusión legal. El control de cadencia en Día 1, Día 3 (Bump) y Día 7 (Cierre) permite monitorear sistemáticamente el interés comercial hasta convertir al cliente mediante el botón de 1 clic 'Marcar Interesado'.",
        s_body
    ))
    
    doc.build(elements)
    print(f"PDF Usuario APA guardado en: {filepath}")


def build_apa_technical_manual_pdf(filepath):
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    c_black = colors.black
    c_gray = colors.HexColor("#333333")
    
    s_rh = ParagraphStyle('RHT', fontName='Times-Roman', fontSize=9, leading=11, textColor=colors.HexColor("#555555"), alignment=2, spaceAfter=40)
    s_title = ParagraphStyle('Title_APAT', fontName='Times-Bold', fontSize=14, leading=20, textColor=c_black, alignment=1, spaceAfter=24)
    s_meta = ParagraphStyle('Meta_APAT', fontName='Times-Roman', fontSize=11, leading=16, textColor=c_black, alignment=1, spaceAfter=40)
    s_abs_h = ParagraphStyle('AbsHT', fontName='Times-Bold', fontSize=11, leading=14, textColor=c_black, alignment=1, spaceAfter=10)
    s_h1 = ParagraphStyle('H1_APAT', fontName='Times-Bold', fontSize=11, leading=15, textColor=c_black, alignment=1, spaceBefore=16, spaceAfter=8, keepWithNext=True)
    s_h2 = ParagraphStyle('H2_APAT', fontName='Times-Bold', fontSize=10.5, leading=14, textColor=c_black, spaceBefore=12, spaceAfter=6, keepWithNext=True)
    s_body = ParagraphStyle('Body_APAT', fontName='Times-Roman', fontSize=9.5, leading=14.5, textColor=c_gray, firstLineIndent=24, spaceAfter=6)
    s_tbl_lbl = ParagraphStyle('TblLblT', fontName='Times-Bold', fontSize=9, leading=12, textColor=c_black, spaceBefore=10, spaceAfter=2)
    s_tbl_tit = ParagraphStyle('TblTitT', fontName='Times-Italic', fontSize=9, leading=12, textColor=c_black, spaceAfter=4)
    s_tbl_cell = ParagraphStyle('TblCellT', fontName='Times-Roman', fontSize=8, leading=10, textColor=c_black)
    s_tbl_hdr = ParagraphStyle('TblHdrT', fontName='Times-Bold', fontSize=8, leading=10, textColor=c_black)
    s_tbl_note = ParagraphStyle('TblNoteT', fontName='Times-Italic', fontSize=8, leading=10, textColor=colors.HexColor("#555555"), spaceBefore=3, spaceAfter=10)
    
    elements = []
    
    elements.append(Paragraph("ESPECIFICACIÓN TÉCNICA: REVOPS AI | DIRECCIÓN DE ARQUITECTURA", s_rh))
    elements.append(Paragraph("Especificación Técnica de Arquitectura, Mecánica del Código, Patrones de Seguridad Zero-Trust y Guía Integral de Mantenimiento para la Plataforma RevOps AI", s_title))
    elements.append(Paragraph("Dirección de Tecnología y Arquitectura de Software<br/>HzSaaS Technologies B2B<br/>Bogotá D.C., Colombia<br/>Noviembre de 2026", s_meta))
    elements.append(PageBreak())
    
    elements.append(Paragraph("Resumen", s_abs_h))
    elements.append(Paragraph(
        "Este documento técnico compendia la arquitectura integral de software, especificación de componentes, algoritmos heurísticos y de lenguaje natural, modelos relacionales de datos y manual de intervención del código fuente para la plataforma RevOps AI. Desarrollado bajo el paradigma de micro-kernel asíncrono con FastAPI y Python 3.11+, el sistema orquesta una tubería desacoplada de cinco agentes encargados de la ingesta web resiliente, el análisis de brechas comerciales, la puntuación matemática ponderada, la redacción personalizada de mensajes B2B y el descubrimiento territorial autónomo. La persistencia opera mediante SQLAlchemy 2.0 garantizando un aislamiento estricto por inquilino (Multi-Tenancy) y auto-migraciones DDL en tiempo de arranque.",
        s_body
    ))
    elements.append(Spacer(1, 14))
    
    elements.append(Paragraph("Capítulo 1. Arquitectura del Micro-Kernel y Pipeline de Agentes", s_h1))
    elements.append(Paragraph(
        "El núcleo computacional opera mediante el pipeline secuencial compuesto por: 1) IngestionAgent (audit_agent.py), extractor defensivo con timeout de 8 segundos y rotación de agentes de usuario; 2) ResearchAgent (research_agent.py), evaluador de presencia de WhatsApp, agendas interactivas y catálogo de especialidades; 3) ScoringEngine (scoring_agent.py), que calcula la puntuación S = 50 + Catálogo (hasta +20) - Sin_WhatsApp (-15) - Sin_Agenda (-15); 4) CopywriterAgent (copywriter_agent.py), redactor de propuestas B2B orientadas a resolver las brechas halladas con aviso legal de exclusión; y 5) AutonomousScout (autonomous_scout.py), robot de prospección territorial.",
        s_body
    ))
    
    # Tabla 1 APA
    elements.append(Paragraph("Tabla 1", s_tbl_lbl))
    elements.append(Paragraph("Pila Tecnológica Oficial y Responsabilidades Arquitectónicas", s_tbl_tit))
    
    t_data = [
        [Paragraph("Capa del Sistema", s_tbl_hdr), Paragraph("Tecnología", s_tbl_hdr), Paragraph("Versión", s_tbl_hdr), Paragraph("Misión Arquitectónica", s_tbl_hdr)],
        [Paragraph("API Core", s_tbl_cell), Paragraph("FastAPI / Starlette", s_tbl_cell), Paragraph("0.115+", s_tbl_cell), Paragraph("Rutas REST y enrutamiento asíncrono.", s_tbl_cell)],
        [Paragraph("Persistencia ORM", s_tbl_cell), Paragraph("SQLAlchemy Declarative", s_tbl_cell), Paragraph("2.0+", s_tbl_cell), Paragraph("Aislamiento multi-tenant y auto-migración.", s_tbl_cell)],
        [Paragraph("Scraping Web", s_tbl_cell), Paragraph("BeautifulSoup4 / Requests", s_tbl_cell), Paragraph("4.12+", s_tbl_cell), Paragraph("Extracción semántica y timeouts defensivos.", s_tbl_cell)],
        [Paragraph("Inferencia IA", s_tbl_cell), Paragraph("Gemini 2.0 Flash / Pro", s_tbl_cell), Paragraph("v1beta", s_tbl_cell), Paragraph("Comprensión B2B y redacción personalizada.", s_tbl_cell)],
        [Paragraph("Frontend UI", s_tbl_cell), Paragraph("HTML5, CSS Tokens, JS", s_tbl_cell), Paragraph("ES2022", s_tbl_cell), Paragraph("Diseño Anti-AI Hallmark, 0 dependencias.", s_tbl_cell)]
    ]
    t = Table(t_data, colWidths=[90, 110, 50, 218])
    t.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, c_black),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t)
    elements.append(Paragraph("Nota. Suite de 131 pruebas unitarias valida la totalidad de la matriz de componentes.", s_tbl_note))
    
    elements.append(Paragraph("Capítulo 2. Guía de Intervención y Modificación de Código", s_h1))
    elements.append(Paragraph(
        "Para realizar modificaciones en el sistema, los ingenieros deben seguir los siguientes lineamientos técnicos:\n"
        "• Modificaciones en Frontend: En 'src/web/static/dashboard.css', modificar las variables maestras de ':root' (--bg-app, --accent, --border-subtle). Para textos o títulos, editar directamente las etiquetas HTML en 'src/web/templates/dashboard.html'.\n"
        "• Modificaciones en Backend y Base de Datos: Para incorporar nuevos atributos, se debe declarar la propiedad en el modelo de dominio Pydantic ('src/core/models.py'), mapear la columna en el ORM ('src/db/models.py'), incluirla en la lista de auto-migración de 'init_db()' ('src/db/session.py'), persistirla en 'TenantScopedRepository' ('src/db/repository.py') y exponerla en 'src/api/routes.py'.\n"
        "• Parámetros de Entorno: El archivo 'RevOpsAI/.env' contiene las credenciales maestras y la clave GEMINI_API_KEY.",
        s_body
    ))
    
    # Tabla Unit Economics
    elements.append(Paragraph("Tabla 2", s_tbl_lbl))
    elements.append(Paragraph("Estructura de Costos Unitarios por cada 1,000 Prospectos Auditados", s_tbl_tit))
    
    t_ue = [
        [Paragraph("Rubro Operativo", s_tbl_hdr), Paragraph("Costo en USD", s_tbl_hdr), Paragraph("Costo en COP", s_tbl_hdr), Paragraph("Margen Bruto", s_tbl_hdr)],
        [Paragraph("Inferencia LLM (Gemini 2.0)", s_tbl_cell), Paragraph("$0.23 USD", s_tbl_cell), Paragraph("$943 COP", s_tbl_cell), Paragraph("99.85%", s_tbl_cell)],
        [Paragraph("Infraestructura VPS (Hetzner)", s_tbl_cell), Paragraph("$0.10 USD", s_tbl_cell), Paragraph("$410 COP", s_tbl_cell), Paragraph("99.90%", s_tbl_cell)],
        [Paragraph("Scraping & Tráfico Saliente", s_tbl_cell), Paragraph("$0.00 USD", s_tbl_cell), Paragraph("$0 COP", s_tbl_cell), Paragraph("100.0%", s_tbl_cell)],
        [Paragraph("Despacho Comercial WhatsApp", s_tbl_cell), Paragraph("$0.00 USD", s_tbl_cell), Paragraph("$0 COP", s_tbl_cell), Paragraph("100.0%", s_tbl_cell)],
        [Paragraph("COSTO TOTAL CONSOLIDADO", s_tbl_hdr), Paragraph("$0.33 USD", s_tbl_hdr), Paragraph("$1,353 COP", s_tbl_hdr), Paragraph("> 99.8%", s_tbl_hdr)]
    ]
    t2 = Table(t_ue, colWidths=[140, 100, 100, 128])
    t2.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,0), (-1,0), 1, c_black),
        ('LINEBELOW', (0,-1), (-1,-1), 1, c_black),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t2)
    elements.append(Paragraph("Nota. Costo unitario por lead auditado: $1.35 COP. Rentabilidad comercial estimada: 4,000x.", s_tbl_note))
    
    doc.build(elements)
    print(f"PDF Técnico APA guardado en: {filepath}")

if __name__ == "__main__":
    target_dir = r"c:\Users\JESUS\Desktop\Antigravity\documentacion completa"
    os.makedirs(target_dir, exist_ok=True)
    
    u_docx = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI_APA7.docx")
    t_docx = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI_APA7.docx")
    u_pdf = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI_APA7.pdf")
    t_pdf = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI_APA7.pdf")
    
    # También sobreescribir los principales para mantener consistencia inmediata
    u_docx_main = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI.docx")
    t_docx_main = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI.docx")
    u_pdf_main = os.path.join(target_dir, "Manual_de_Usuario_RevOps_AI.pdf")
    t_pdf_main = os.path.join(target_dir, "Manual_Tecnico_Interno_RevOps_AI.pdf")
    
    build_apa_user_manual_docx(u_docx)
    build_apa_technical_manual_docx(t_docx)
    build_apa_user_manual_pdf(u_pdf)
    build_apa_technical_manual_pdf(t_pdf)
    
    build_apa_user_manual_docx(u_docx_main)
    build_apa_technical_manual_docx(t_docx_main)
    build_apa_user_manual_pdf(u_pdf_main)
    build_apa_technical_manual_pdf(t_pdf_main)
    
    print("¡Documentación empresarial con Normas APA 7ma Edición generada exitosamente!")
