# Portafolio Profesional de Libardo Hernández - Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir el portafolio profesional de Libardo Hernández en React + Vite con diseño técnico sobrio (Anti-AI slop), soporte bilingüe (ES/PT), inspección técnica interactiva de proyectos y canales de contacto directo para reclutadores de CompuTrabajo.

**Architecture:** Aplicación React (SPA) modular alojada en `portafolio/`. El estado de idioma (ES/PT) se administra de forma reactiva con persistencia local (`localStorage`). Los proyectos cuentan con un modal de inspección técnica que expone arquitectura, diagramas de flujo y fragmentos de código. El diseño utiliza CSS semántico con tokens de alta fidelidad, bordes hairline de 1px e iconografía vectorial precisa vía `lucide-react`.

**Tech Stack:** React 18/19, Vite, Lucide React, CSS Moderno con variables CSS semánticas, JSON de contenido bilingüe.

**Spec:** `docs/superpowers/specs/2026-10-11-portafolio-libardo-hernandez-design.md`

## Global Constraints
- Estricto cumplimiento de principios Anti-AI: sin gradientes morados/rosas (`#6366f1` / `#a855f7`), sin emojis decorativos infantiles, sin destellos.
- Paleta sobria de ingeniería: fondo `#09090b`, superficie `#121215`, bordes hairline `rgba(255, 255, 255, 0.08)`.
- Tipografía técnica: `Inter` y `JetBrains Mono`.
- Cero enlaces muertos: proyectos con inspección técnica completa en modal interactivo.
- Cero advertencias ni errores en `npm run build`.

---

### Task 1: Scaffolding & Configuración del Proyecto

**Files:**
- Create: `portafolio/package.json`
- Create: `portafolio/vite.config.js`
- Create: `portafolio/index.html`
- Create: `portafolio/src/main.jsx`
- Create: `portafolio/src/App.jsx`

**Interfaces:**
- Produces: Servidor de desarrollo Vite funcional en el directorio `portafolio/` con React y `lucide-react`.

- [ ] **Step 1: Crear la estructura base y package.json en `portafolio/`**
- [ ] **Step 2: Configurar `vite.config.js` e `index.html` con fuentes Google Fonts (Inter + JetBrains Mono)**
- [ ] **Step 3: Instalar dependencias necesarias (`npm install` con react, react-dom, lucide-react)**
- [ ] **Step 4: Verificar arranque y compilación básica (`npm run build`)**

---

### Task 2: Sistema de Diseño & Tokens CSS Semánticos (Anti-AI)

**Files:**
- Create: `portafolio/src/index.css`

**Interfaces:**
- Produces: Clases utilitarias y variables CSS globales (`--bg`, `--surface`, `--surface-hover`, `--border-hairline`, `--text-primary`, `--text-secondary`, `--accent-emerald`, `--accent-cyan`).

- [ ] **Step 1: Definir variables CSS de tokens, reset moderno y tipografías**
- [ ] **Step 2: Implementar estilos de bordes hairline con relieve direccional de iluminación superior**
- [ ] **Step 3: Diseñar botones de acción interactivos con estados: default, hover, active, focus-visible**
- [ ] **Step 4: Verificar renderizado de variables y contraste de color accesible (WCAG AA)**

---

### Task 3: Arquitectura de Contenidos Bilingüe (ES / PT)

**Files:**
- Create: `portafolio/src/content/data-es.json`
- Create: `portafolio/src/content/data-pt.json`

**Interfaces:**
- Produces: Contenido estructurado de Libardo Hernández en Español y Portugués (perfil, proyectos, formación SENA + Ingeniería, habilidades y contacto).

- [ ] **Step 1: Crear `data-es.json` con información técnica detallada de los 4 proyectos (Gestor PWA, OfertasTracker, Registro Vehicular, Tienda POO), educación e información de contacto**
- [ ] **Step 2: Crear `data-pt.json` con traducción técnica natural y fluida al portugués de todo el contenido**
- [ ] **Step 3: Validar que ambos JSON compartan exactamente la misma estructura de claves y tipos**

---

### Task 4: Navbar & Estado Global de Idioma

**Files:**
- Create: `portafolio/src/context/LanguageContext.jsx`
- Create: `portafolio/src/components/Navbar.jsx`

**Interfaces:**
- Consumes: `data-es.json`, `data-pt.json`
- Produces: Hook `useLanguage()` y componente `<Navbar />` con switch instantáneo ES/PT y badge de disponibilidad laboral.

- [ ] **Step 1: Implementar `LanguageContext.jsx` con persistencia en `localStorage`**
- [ ] **Step 2: Implementar `Navbar.jsx` con monograma "LH", badge de estatus ("Disponible para vinculación") y selector ES/PT**
- [ ] **Step 3: Probar el cambio de idioma dinámico sin recargar la página**

---

### Task 5: Hero Section & Barra de Métricas

**Files:**
- Create: `portafolio/src/components/Hero.jsx`
- Create: `portafolio/src/components/StatsBar.jsx`

**Interfaces:**
- Consumes: `useLanguage()`, contenido de `hero` y `stats`
- Produces: Encabezado principal de alto impacto con botones directos (Descargar CV, WhatsApp directo, Copiar correo).

- [ ] **Step 1: Implementar `Hero.jsx` destacando rol (Ingeniería de Sistemas · Automatización & Software)**
- [ ] **Step 2: Incorporar botones de acción para reclutadores (WhatsApp con mensaje parametrizado, copiado de email en un clic con feedback visual, visualización/descarga de CV)**
- [ ] **Step 3: Implementar `StatsBar.jsx` con métricas clave (proyectos productivos, tecnologías backend/frontend, automatizaciones activas)**
- [ ] **Step 4: Verificar adaptabilidad móvil y respuesta táctil de los botones**

---

### Task 6: Showcase de Proyectos & Modal de Inspección Técnica

**Files:**
- Create: `portafolio/src/components/ProjectShowcase.jsx`
- Create: `portafolio/src/components/ProjectModal.jsx`

**Interfaces:**
- Consumes: `useLanguage()`, lista de proyectos
- Produces: Tarjetas técnicas asimétricas y modal interactivo para visualizar arquitectura, diagramas de flujo y fragmentos de código.

- [ ] **Step 1: Implementar `ProjectShowcase.jsx` con layout asimétrico de densidad técnica (badges de stack, categoría, problema resuelto)**
- [ ] **Step 2: Implementar `ProjectModal.jsx` con pestañas de "Arquitectura", "Flujo de Datos" y "Código Destacado"**
- [ ] **Step 3: Configurar navegación accesible (cerrar con tecla ESC, clic fuera del modal, foco visible)**
- [ ] **Step 4: Probar la apertura e inspección de cada uno de los 4 proyectos**

---

### Task 7: Trayectoria Académica (SENA + Universidad) & Matriz de Habilidades

**Files:**
- Create: `portafolio/src/components/FormationTimeline.jsx`
- Create: `portafolio/src/components/SkillsMatrix.jsx`

**Interfaces:**
- Consumes: `useLanguage()`, datos de formación y habilidades
- Produces: Línea de tiempo educativa y matriz categorizada de tecnologías.

- [ ] **Step 1: Implementar `FormationTimeline.jsx` detallando Ingeniería de Sistemas, Tecnólogo ADSO (SENA) y Técnico en Sistemas (SENA)**
- [ ] **Step 2: Implementar `SkillsMatrix.jsx` dividida en: Automatización & Bots, Backend & APIs, Frontend & PWA, Bases de Datos & Herramientas**
- [ ] **Step 3: Añadir badge de dominio de idiomas: Español (Nativo) y Portugués (Intermedio)**

---

### Task 8: Sección de Contacto Directo para Reclutadores (CompuTrabajo Friendly) & Footer

**Files:**
- Create: `portafolio/src/components/ContactSection.jsx`
- Create: `portafolio/src/components/Footer.jsx`

**Interfaces:**
- Consumes: `useLanguage()`, datos de contacto
- Produces: Bloque de llamado a la acción enfocado en contratación directa.

- [ ] **Step 1: Implementar `ContactSection.jsx` con tarjeta de contacto rápido (enlace directo a chat de WhatsApp, correo institucional/personal y descarga de hoja de vida)**
- [ ] **Step 2: Implementar `Footer.jsx` con copyright, créditos técnicos y selector de idioma secundario**
- [ ] **Step 3: Verificar que todos los enlaces externos y de copia rápida funcionen correctamente**

---

### Task 9: Integración Completa, Modal de Hoja de Vida y Verificación Build

**Files:**
- Modify: `portafolio/src/App.jsx`
- Create: `portafolio/src/components/CvModal.jsx`

**Interfaces:**
- Produces: Aplicación completamente ensamblada, lista para producción.

- [ ] **Step 1: Integrar todos los componentes en `App.jsx` dentro del proveedor `LanguageProvider`**
- [ ] **Step 2: Implementar `CvModal.jsx` para visualización interactiva y opción de descarga del CV de Libardo**
- [ ] **Step 3: Probar responsividad completa en resolución móvil (375px), tablet (768px) y escritorio (1280px+)**
- [ ] **Step 4: Ejecutar `npm run build` y certificar 0 errores, 0 advertencias y tiempos de carga instantáneos**
