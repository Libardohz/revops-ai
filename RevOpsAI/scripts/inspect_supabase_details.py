import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv("RevOpsAI/.env")
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("[ERROR] DATABASE_URL no encontrada en RevOpsAI/.env")
    exit(1)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(db_url)

print("==================================================================")
print("     REVOPS AI - AUDITORÍA DETALLADA DE BASE DE DATOS SUPABASE    ")
print("==================================================================")

with engine.connect() as conn:
    # 1. Custom Functions in schema 'public'
    funcs = conn.execute(text(
        "SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';"
    )).fetchall()
    func_names = [f[0] for f in funcs]
    print(f"\n1. Funciones / Procedimientos en schema 'public' ({len(func_names)}):")
    for fn in func_names:
        print(f"   - {fn}")

    # 2. Custom Views in schema 'public'
    views = conn.execute(text(
        "SELECT table_name FROM information_schema.views WHERE table_schema = 'public';"
    )).fetchall()
    view_names = [v[0] for v in views]
    print(f"\n2. Vistas personalizadas en schema 'public' ({len(view_names)}):")
    for vn in view_names:
        print(f"   - {vn}")

    # 3. Triggers in schema 'public'
    triggers = conn.execute(text(
        "SELECT trigger_name, event_object_table FROM information_schema.triggers WHERE trigger_schema = 'public';"
    )).fetchall()
    print(f"\n3. Disparadores (Triggers) activos ({len(triggers)}):")
    for tr, tbl in triggers:
        print(f"   - Trigger '{tr}' sobre tabla '{tbl}'")

    # 4. Storage Buckets
    try:
        buckets = conn.execute(text("SELECT id, name FROM storage.buckets;")).fetchall()
        print(f"\n4. Buckets de Almacenamiento (Storage) ({len(buckets)}):")
        for bid, bname in buckets:
            print(f"   - Bucket: '{bid}' ({bname})")
    except Exception as exc:
        print(f"\n4. Storage: {exc}")

    # 5. Auth Users
    try:
        user_count = conn.execute(text("SELECT count(*) FROM auth.users;")).scalar()
        print(f"\n5. Usuarios en auth.users: {user_count}")
    except Exception as exc:
        print(f"\n5. Auth Users: {exc}")

print("\n==================================================================")

