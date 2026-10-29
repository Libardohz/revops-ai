-- RevOpsAI: Esquema PostgreSQL con Row-Level Security (RLS) Mandatorio

CREATE TABLE IF NOT EXISTS prospects (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(512) NOT NULL,
    state VARCHAR(32) NOT NULL DEFAULT 'INGESTED',
    score INT DEFAULT 0,
    research_summary TEXT DEFAULT '',
    draft_message TEXT DEFAULT '',
    is_blacklisted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL,
    lead_id VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    reason TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 1. Habilitar RLS en tablas críticas
ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 2. Crear políticas de aislamiento estricto por sesión
-- El tenant_id debe coincidir exactamente con la variable de sesión inyectada por la conexión
CREATE POLICY tenant_isolation_prospects ON prospects
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_isolation_audit ON audit_logs
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
