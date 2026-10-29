# Design Spec: Integración de REA (Reverse Engineer Anything) en Antigravity

**Fecha:** 2026-10-29  
**Estado:** Aprobado / Listo para Plan de Implementación  
**Autor:** Antigravity & User  

---

## 1. Resumen Ejecutivo

Este documento especifica la integración de **REA (Reverse Engineer Anything)** (`morluto/rea`) en el entorno de desarrollo y asistencia de Antigravity en Windows.
La integración proporciona capacidades avanzadas de ingeniería inversa para binarios nativos (PE, ELF, Mach-O), aplicaciones JavaScript/Electron (ASAR, bundles), .NET, Android (APK), firmware y endpoints web directamente a través del protocolo MCP (Model Context Protocol) y una Skill contextualizada en el workspace.

---

## 2. Arquitectura de Integración

```
+-------------------------------------------------------------+
|                     Antigravity Agent                       |
|   - Detecta skills en .agents/skills/                       |
|   - Conecta a servidores MCP vía stdio                     |
+--------------+------------------------------+---------------+
               |                              |
               v                              v
+-------------------------------+  +--------------------------+
| Skill Workspace               |  | Global MCP Config        |
| .agents/skills/               |  | ~/.gemini/config/        |
| reverse-engineer-anything/    |  | mcp_config.json          |
|  - SKILL.md                   |  +------------+-------------+
|  - references/*.md            |               |
+-------------------------------+               | spawns stdio
                                                v
                                   +--------------------------+
                                   | REA MCP Server           |
                                   | cmd.exe /c npx.cmd -y    |
                                   | rea-agents@latest --mcp  |
                                   +--------------------------+
```

### Componentes:
1. **Configuración Global MCP (`C:\Users\JESUS\.gemini\config\mcp_config.json`)**:
   - Define el servidor `rea` bajo la clave `mcpServers`.
   - Utiliza transporte Stdio estándar de Node.js encapsulado en `cmd.exe` para asegurar resolución adecuada de rutas y bypass de directivas de ejecución restringidas de PowerShell en Windows.
   - Configura perfiles compactos de esquemas de entrada y salida (`compact`) para proteger la ventana de contexto de los modelos LLM.

2. **Skill de Agente (`c:\Users\JESUS\Desktop\Antigravity\.agents\skills\reverse-engineer-anything`)**:
   - Despliegue de la skill oficial de REA (`SKILL.md`) y sus guías de referencia especializadas (`references/`).
   - Permite al agente enrutar heurísticamente los tipos de artefactos (`analyze_javascript_application` para Electron/Node, `open_binary` para nativo, `inspect_artifact` para bundles empaquetados).

3. **Herramientas y Runtime de REA**:
   - Runtime Node.js (`v24.x`) con soporte para análisis estático y dinámico local.
   - Ejecución verificada con `rea@6.7.0` a través de npm / npx.

---

## 3. Especificación Técnica de Configuración

### 3.1 Servidor MCP (`mcp_config.json`)
El archivo `C:\Users\JESUS\.gemini\config\mcp_config.json` contendrá la siguiente entrada:

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
        "REA_MCP_OUTPUT_SCHEMA_PROFILE": "compact"
      }
    }
  }
}
```

### 3.2 Despliegue de la Skill
- Directorio de destino: `c:\Users\JESUS\Desktop\Antigravity\.agents\skills\reverse-engineer-anything/`
- Copia de los archivos fuente desde el clon local `rea/.agents/skills/reverse-engineer-anything/`:
  - `SKILL.md`
  - `references/android-applications.md`
  - `references/connection-and-recovery.md`
  - `references/environments.md`
  - `references/evidence-workflows.md`
  - `references/javascript-applications.md`
  - `references/native-and-artifacts.md`
  - `references/runtime-observation.md`

---

## 4. Estrategia de Verificación y Criterios de Éxito

### 4.1 Criterios de Éxito
1. `C:\Users\JESUS\.gemini\config\mcp_config.json` es un JSON válido y contiene la definición de `rea`.
2. `.agents/skills/reverse-engineer-anything/SKILL.md` y su carpeta `references/` existen y son legibles en el workspace.
3. El comando de inicialización de REA responde correctamente ejecutando `npx.cmd -y rea-agents doctor --json` sin errores fatales de entorno.
4. El handshake MCP inicial responde correctamente al listar herramientas o iniciar en modo `--mcp`.

---

## 5. Consideraciones de Seguridad y Resiliencia
- **Aislamiento de comandos**: Todo análisis de binarios u observaciones dinámicas se ejecutan localmente en el host.
- **Tolerancia a fallos**: Si alguna dependencia externa (como Ghidra o IDA) no está presente, REA opera en modo estático para JavaScript, Electron, .NET, strings y PE headers sin abortar.
