# REA MCP & Skill Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar REA (Reverse Engineer Anything) como servidor MCP global de Antigravity y registrar la skill `reverse-engineer-anything` en el workspace para habilitar capacidades de ingeniería inversa de binarios, apps Electron/JS y APIs.

**Architecture:** Registramos el servidor MCP en `C:\Users\JESUS\.gemini\config\mcp_config.json` utilizando `cmd.exe` y `npx.cmd` para máxima compatibilidad con el entorno Windows, y desplegamos la skill oficial con todas sus guías de referencia en `.agents/skills/reverse-engineer-anything/`.

**Tech Stack:** Node.js v24, npm/npx, MCP (Model Context Protocol) sobre Stdio, JSON, Markdown.

**Spec:** [2026-10-29-rea-mcp-integration-design.md](file:///c:/Users/JESUS/Desktop/Antigravity/docs/superpowers/specs/2026-10-29-rea-mcp-integration-design.md)

## Global Constraints
- Ejecutable del servidor MCP debe usar `cmd.exe` con `args: ["/c", "npx.cmd", "-y", "rea-agents@latest", "--mcp"]` para evitar problemas con políticas de PowerShell en Windows.
- Perfiles de esquema configurados en `compact` (`REA_MCP_INPUT_SCHEMA_PROFILE` y `REA_MCP_OUTPUT_SCHEMA_PROFILE`).
- Preservar la integridad de los archivos existentes en `~/.gemini/config/`.

---

### Task 1: Desplegar la Skill `reverse-engineer-anything` y Guías de Referencia

**Files:**
- Create: `.agents/skills/reverse-engineer-anything/SKILL.md`
- Create: `.agents/skills/reverse-engineer-anything/references/android-applications.md`
- Create: `.agents/skills/reverse-engineer-anything/references/connection-and-recovery.md`
- Create: `.agents/skills/reverse-engineer-anything/references/environments.md`
- Create: `.agents/skills/reverse-engineer-anything/references/evidence-workflows.md`
- Create: `.agents/skills/reverse-engineer-anything/references/javascript-applications.md`
- Create: `.agents/skills/reverse-engineer-anything/references/native-and-artifacts.md`
- Create: `.agents/skills/reverse-engineer-anything/references/runtime-observation.md`

**Interfaces:**
- Consumes: Contenido clonado en `c:\Users\JESUS\Desktop\Antigravity\rea\.agents\skills\reverse-engineer-anything/`
- Produces: Skill de Antigravity accesible en el workspace para guiar al modelo en análisis de ingeniería inversa.

- [x] **Step 1: Crear directorio de destino y copiar archivos de la skill**
Copiar el directorio `.agents/skills/reverse-engineer-anything` desde el repositorio clonado `rea` hacia `.agents/skills/reverse-engineer-anything`.

- [x] **Step 2: Verificar la existencia e integridad de los archivos copiados**
Ejecutar verificación de que `SKILL.md` y los 7 archivos de referencia existen y tienen tamaño > 0 bytes.

- [x] **Step 3: Commit de la skill al repositorio**
```bash
git add .agents/skills/reverse-engineer-anything
git commit -m "feat(skills): add reverse-engineer-anything skill and reference guides"
```

---

### Task 2: Configurar el Servidor MCP Global en Antigravity

**Files:**
- Modify: `C:\Users\JESUS\.gemini\config\mcp_config.json`

**Interfaces:**
- Consumes: Configuración del spec
- Produces: Definición del servidor `rea` bajo `mcpServers` en `mcp_config.json`

- [x] **Step 1: Escribir la configuración de `mcpServers.rea` en `mcp_config.json`**
```json
{
  "mcpServers": {
    "rea": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "npx.cmd",
        "-y",
        "rea-agents@latest",
        "--mcp"
      ],
      "env": {
        "REA_MCP_INPUT_SCHEMA_PROFILE": "compact",
        "REA_MCP_OUTPUT_SCHEMA_PROFILE": "off"
      }
    }
  }
}
```

- [x] **Step 2: Validar el formato JSON y la estructura de `mcp_config.json`**
Verificar con PowerShell / Node que el JSON es válido y contiene la clave `mcpServers.rea.command`.

---

### Task 3: Verificación y Smoke Test del Servidor y Herramientas

**Files:**
- Test target: Ejecución del diagnóstico y verificación de herramientas REA

**Interfaces:**
- Consumes: `mcp_config.json` y paquetes instalados
- Produces: Confirmación de operatividad de REA en el sistema

- [x] **Step 1: Ejecutar verificación de diagnóstico `rea doctor --json`**
Ejecutar:
```powershell
cmd.exe /c npx.cmd -y rea-agents@latest doctor --json
```
Verificar que la salida sea un JSON válido con el estado de preparación y herramientas disponibles.

- [x] **Step 2: Comprobar el arranque stdio del servidor MCP**
Verificar que `cmd.exe /c npx.cmd -y rea-agents@latest --mcp` responde adecuadamente sobre stdio sin errores de inicio.

- [x] **Step 3: Actualizar la documentación y estado del repositorio**
Realizar commit de los cambios finales si aplica y resumir la configuración al usuario.

