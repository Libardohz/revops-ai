"""Supabase PostgreSQL automated provisioning and migration script for RevOps AI."""

import os
import sys
from pathlib import Path
from sqlalchemy import text
from RevOpsAI.src.db.session import get_engine, init_db, get_session_factory
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.core.models import Prospect, ProspectState


def setup_supabase(db_url: str | None = None, apply_rls: bool = True) -> None:
    """Connect to Supabase PostgreSQL, create tables, apply RLS, and seed tenants."""
    target_url = db_url or os.getenv("DATABASE_URL")
    if not target_url:
        print("[ERROR] DATABASE_URL no configurada. Exporta la variable o pásala como argumento.")
        print("Ejemplo: postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres")
        sys.exit(1)

    print("==================================================================")
    print("        REVOPS AI - INICIALIZADOR DE SUPABASE POSTGRESQL          ")
    print("==================================================================")
    print(f"1. Conectando con Supabase PostgreSQL...")

    try:
        engine = get_engine(target_url)
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print(f"   [OK] Conexión establecida con éxito:")
            print(f"   {version[:60]}...")
    except Exception as exc:
        print(f"   [ERROR] Falló la conexión con Supabase: {exc}")
        sys.exit(1)

    print("\n2. Creando tablas relacionales (prospects, audit_logs)...")
    try:
        init_db(engine)
        print("   [OK] Esquema de tablas creado/actualizado correctamente.")
    except Exception as exc:
        print(f"   [ERROR] Falló la creación de tablas: {exc}")
        sys.exit(1)

    if apply_rls:
        rls_file = Path(__file__).resolve().parent.parent / "src" / "db" / "schema_rls.sql"
        if rls_file.is_file():
            print(f"\n3. Aplicando políticas de seguridad Row-Level Security ({rls_file.name})...")
            try:
                sql_content = rls_file.read_text(encoding="utf-8")
                # Split statements by semicolon
                statements = [s.strip() for s in sql_content.split(";") if s.strip()]
                with engine.begin() as conn:
                    for stmt in statements:
                        conn.execute(text(stmt))
                print("   [OK] Row-Level Security y aislamiento multi-tenant activado.")
            except Exception as exc:
                print(f"   [ADVERTENCIA] No se pudo aplicar RLS completo (¿permisos limitados?): {exc}")
        else:
            print("\n3. [OMITIDO] Archivo schema_rls.sql no encontrado.")

    print("\n4. Sembrando datos iniciales de verificación multi-tenant...")
    session_factory = get_session_factory(engine)
    with session_factory() as session:
        repo_madrid = TenantScopedRepository(session, "tenant_clinicas_madrid")
        p1 = Prospect(
            id="lead_init_madrid",
            tenant_id="tenant_clinicas_madrid",
            name="Clínica Dental Chamberí Demo",
            url="https://dentalchamberi.madrid",
            state=ProspectState.PENDING_APPROVAL,
            score=88,
            research_summary="Clínica con 8 servicios clave detectados. Sin canal WhatsApp detectado.",
            draft_message="Estimado equipo directivo, optimización disponible para agendamiento.",
        )
        repo_madrid.save_prospect(p1)

        repo_bcn = TenantScopedRepository(session, "tenant_dental_bcn")
        p2 = Prospect(
            id="lead_init_bcn",
            tenant_id="tenant_dental_bcn",
            name="Institut Dental Eixample Demo",
            url="https://dentaleixample.bcn",
            state=ProspectState.PENDING_APPROVAL,
            score=82,
            research_summary="Clínica con 6 servicios clave detectados. Carece de sistema de cita online.",
            draft_message="Apreciado equipo de Institut Dental Eixample, optimización disponible.",
        )
        repo_bcn.save_prospect(p2)

    print("   [OK] Tenants sembrados: tenant_clinicas_madrid y tenant_dental_bcn.")
    print("\n==================================================================")
    print("       BASE DE DATOS SUPABASE LISTA AL 100% PARA PRODUCCIÓN       ")
    print("==================================================================")


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 else None
    setup_supabase(url_arg)

