# RevOpsAI — Departamento de Ingresos Digital Multi-Agente

Sistema modular de Revenue Operations (RevOps) multi-agente, diseñado bajo el paradigma **Zero-Trust** y arquitectura desacoplada (70% núcleo reutilizable / 30% configuración por sector).

---

## Estructura del Proyecto

```text
RevOpsAI/
├── config/              # El 30% adaptable (YAMLs de configuración por sector)
│   └── sectors/         # clinicas.yaml, abogados.yaml, etc.
├── src/                 # El 70% inmutable (Código fuente principal)
│   ├── core/            # Orquestador LangGraph, máquina de estados y base de datos
│   ├── agents/          # Los 9 agentes especializados
│   ├── security/        # Sanitizador Anti-Prompt Injection, PII scrubber y Guardrails
│   └── integrations/    # Adaptadores para CRM, WhatsApp, Email y Web
├── docs/                # Especificaciones de diseño, arquitectura y seguridad
│   └── 2026-10-27-design-spec.md
├── tests/               # Pruebas automatizadas (inyección, aislamiento RLS y flujo)
└── data/                # CSVs de prueba y datasets aislados
```

---

## Pilares de Seguridad (Zero-Trust)

1. **Anti-Inyecciones:** Arquitectura Dual-LLM con sanitizador perimetral antes de que el contenido no estructurado toque al motor decisor.
2. **Cero Fugas (Multi-Tenant):** Políticas de Row-Level Security (RLS) en PostgreSQL para aislamiento estricto por cliente.
3. **Privacidad PII:** Enmascaramiento automático de datos sensibles de pacientes y contactos antes de interactuar con modelos.
4. **Control Humano (HITL):** Bandeja de aprobación obligatoria antes de cualquier despacho de comunicación exterior.
5. **Cumplimiento Legal:** Prohibición estricta de diagnósticos clínicos y lista negra automática e inmutable para bajas (`opt-out`).

