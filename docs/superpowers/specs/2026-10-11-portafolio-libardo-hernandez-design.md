# Especificación de Diseño: Portafolio Profesional de Libardo Hernández

- **Fecha:** 2026-10-11
- **Autor / Titular:** Libardo Hernández
- **Perfil:** Ingeniero de Sistemas en formación · Técnico en Sistemas (SENA) · Estudiante de Tecnólogo en Análisis y Desarrollo de Software (ADSO - SENA)
- **Especialidad:** Desarrollo de Software, Arquitectura y Automatización
- **Idiomas:** Español (Nativo) · Portugués (Intermedio)

---

## 1. Objetivo y Filosofía del Proyecto

### 1.1 Propósito
Construir una plataforma web de portafolio profesional de alto impacto para reclutadores técnicos y empresas (con énfasis en contrataciones vía CompuTrabajo y canales directos en Colombia/Latinoamérica). 

### 1.2 Principios de Diseño Anti-AI (Reglas Estrictas)
1. **Cero Clichés de IA:** Prohibidos los gradientes violeta/rosa (`#6366f1` a `#a855f7`), tarjetas infladas con desenfoques excesivos, emojis decorativos infantiles o iconos de chispas/estrellas.
2. **Estética de Ingeniería Sobria:** Paleta monocromática de alto contraste (fondo `#09090b`, superficie `#121215`, bordes de 1px *hairline* `rgba(255, 255, 255, 0.08)` con sutil iluminación direccional).
3. **Tipografía de Alta Legibilidad:** `Inter` para texto editorial y `JetBrains Mono` para datos técnicos, métricas y fragmentos de código.
4. **Validación Técnica Directa (Sin enlaces muertos):** En lugar de enlazar a repositorios vacíos de GitHub, cada proyecto cuenta con un modal de **Inspección Técnica** con flujo arquitectónico, decisiones de diseño, métricas reales y fragmentos de código representativos.

---

## 2. Contenido y Proyectos Reales

### 2.1 Proyectos Principales en Exhibición

1. **Task Manager & Gestor PWA**
   - **Rol:** Creador & Desarrollador Full-Stack
   - **Stack:** React 18, Vite, Supabase (PostgreSQL), Groq AI SDK, Tesseract.js (OCR en cliente), PWA.
   - **Aspectos Técnicos:** Capacidad offline-first, digitalización de documentos vía OCR sin servidor intermedio, generador y exportador de informes en PDF.
   - **Métricas:** 100% funcional en cliente móvil/escritorio, cero latencia para lecturas en caché local.

2. **OfertasTracker (Motor de Scraping & Alertas)**
   - **Rol:** Desarrollador de Automatización
   - **Stack:** Node.js, SQLite, Cheerio, Axios, Telegram Bot API.
   - **Aspectos Técnicos:** Monitoreo periódico desatendido de precios y promociones en retail (Almacenes Éxito), análisis de variación histórica de precios y despacho automatizado de notificaciones push a Telegram.
   - **Métricas:** Detección de ofertas en tiempo real y persistencia ligera en base de datos local SQLite.

3. **Sistema de Gestión y Registro Vehicular**
   - **Rol:** Desarrollador Backend
   - **Stack:** Java 17, Spring Boot 3, Thymeleaf / REST API, JUnit.
   - **Aspectos Técnicos:** Control y auditoría de flujo de accesos vehiculares, validación de reglas de negocio en capas de servicio y controladores RESTful.
   - **Métricas:** Cobertura de pruebas unitarias y arquitectura orientada al dominio.

4. **Tienda de Dispositivos & Patrones POO**
   - **Rol:** Desarrollador Java
   - **Stack:** Java 17, Maven, Patrones Creacionales y Estructurales (Singleton, Factories, Herencia e Interfaces).
   - **Aspectos Técnicos:** Aplicación rigurosa de principios SOLID, desacoplamiento de dependencias y modularidad.

### 2.2 Trayectoria y Formación
- **Ingeniería de Sistemas:** En curso (Fundamentos algorítmicos, modelado de sistemas y computación).
- **Tecnólogo en Análisis y Desarrollo de Software (ADSO - SENA):** En curso (Ciclo de vida de software, pruebas, bases de datos y metodologías ágiles).
- **Técnico en Sistemas (SENA):** Certificado (Infraestructura, mantenimiento, soporte y arquitectura de hardware/software).

### 2.3 Idiomas
- **Español:** Nativo.
- **Portugués:** Intermedio (lectura, escritura y comunicación técnica).
- *Selector bilingüe instantáneo (ES / PT) integrado en el Navbar.*

### 2.4 Canales de Contacto para Reclutadores
- **Acceso a Hoja de Vida (CV):** Botón directo para visualización y descarga en PDF.
- **WhatsApp Directo:** Enlace directo con mensaje parametrizado ("Hola Libardo, vi tu portafolio y me gustaría hablar sobre una vacante...").
- **Correo Electrónico:** Visualización limpia con botón de copiado al portapapeles en 1 clic.
- **Indicador de Disponibilidad:** Badge en vivo (*"Disponible para vinculación inmediata / Presencial o Remoto"*).

---

## 3. Arquitectura Técnica de la Aplicación

### 3.1 Stack de Implementación
- **Ubicación:** Subdirectorio `/portafolio` en la raíz del espacio de trabajo.
- **Base:** React con Vite.
- **Estilos:** CSS Vanilla estructurado con variables semánticas (`--bg`, `--surface`, `--surface-hover`, `--border-hairline`, `--text-primary`, `--text-muted`, `--accent-teal`, `--accent-blue`).
- **Iconografía:** `lucide-react` para iconos vectoriales limpios y funcionales.

### 3.2 Componentes Modulares
1. `Navbar.jsx`: Logo / Firma ("LH"), badge de estado laboral, selector de idioma (ES / PT).
2. `Hero.jsx`: Presentación contundente de Libardo Hernández, especialidades, propuesta de valor y botones primarios de acción (CV, WhatsApp, Correo).
3. `StatsBar.jsx`: Indicadores rápidos (Proyectos construidos, Tecnologías dominadas, Horas de desarrollo/automatización, Nivel de idiomas).
4. `ProjectShowcase.jsx`: Cuadrícula asimétrica y limpia de proyectos con ficha de métricas, etiquetas de stack y disparador de inspección técnica.
5. `ProjectModal.jsx`: Modal de detalle técnico que expone arquitectura, flujo de datos, reto técnico y fragmento de código sin salir de la página.
6. `FormationTimeline.jsx`: Cronología académica estructurada (Ingeniería + SENA ADSO + SENA Técnico).
7. `SkillsMatrix.jsx`: Matriz clasificada de capacidades (Automatización, Backend, Frontend, Datos & Herramientas).
8. `ContactSection.jsx`: Llamado a la acción rápido para RRHH y reclutadores de CompuTrabajo.

### 3.3 Datos y Soporte Bilingüe
Los textos y contenidos se estructuran en archivos JSON (`src/content/data-es.json` y `src/content/data-pt.json`), permitiendo que el 100% de la interfaz cambie al instante sin alterar la lógica de renderizado.

---

## 4. Criterios de Aceptación y Calidad

1. **Alineación Visual Anti-Slop:** Cero gradientes rosas/morados, cero destellos, cero emojis en encabezados. Bordes hairline de 1px y alto contraste accesible (cumple WCAG AA).
2. **Rendimiento:** Carga inicial en < 1 segundo, 0 Cumulative Layout Shift (CLS).
3. **Responsividad:** Experiencia impecable tanto en dispositivos móviles (375px+) como en pantallas de escritorio ultrawide.
4. **Verificación:** Ejecución limpia de compilación de producción (`npm run build`) sin advertencias ni errores.
