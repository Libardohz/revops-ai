import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

# Load environment
env_path = Path("RevOpsAI/.env")
load_dotenv(env_path)

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("[ERROR] DATABASE_URL no encontrada en RevOpsAI/.env")
    exit(1)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(db_url)

old_tables = [
    "courses",
    "repository_files",
    "tasks",
    "activity_logs",
    "finances",
    "repository_shares",
    "market_sellers",
    "market_chats",
    "market_messages",
    "market_items",
    "market_ratings",
    "profiles",
]

print("==================================================================")
print("     REVOPS AI - LIMPIEZA DE TABLAS LEGACY DEL GESTOR             ")
print("==================================================================")
print("1. Eliminando tablas antiguas del Gestor con CASCADE...")

with engine.begin() as conn:
    for tbl in old_tables:
        conn.execute(text(f'DROP TABLE IF EXISTS "{tbl}" CASCADE;'))
        print(f"   [ELIMINADA] Tabla: {tbl}")

print("\n2. Verificando estado final del schema 'public' en Supabase...")
inspector = inspect(engine)
remaining = inspector.get_table_names(schema="public")

print("\nTablas activas y exclusivas de RevOps AI:")
for t in remaining:
    print(f"  [OK] {t}")

print("==================================================================")
print("      BASE DE DATOS SUPABASE 100% LIMPIA PARA REVOPS AI           ")
print("==================================================================")

