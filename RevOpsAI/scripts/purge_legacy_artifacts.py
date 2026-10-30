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
print("     REVOPS AI - PURGA DE FUNCIONES Y BUCKETS LEGACY GESTOR       ")
print("==================================================================")

with engine.begin() as conn:
    # 1. Drop Legacy Functions
    legacy_funcs = [
        "import_shared_note",
        "handle_user_profile_sync",
        "delete_own_user",
    ]
    for fn in legacy_funcs:
        conn.execute(text(f"DROP FUNCTION IF EXISTS public.{fn} CASCADE;"))
        print(f"   [DROPPED FUNCTION] public.{fn}")

    # 2. Drop Legacy Storage Buckets
    try:
        conn.execute(text("DELETE FROM storage.objects WHERE bucket_id IN ('repository', 'market_images', 'avatars');"))
        conn.execute(text("DELETE FROM storage.buckets WHERE id IN ('repository', 'market_images', 'avatars');"))
        print("   [DROPPED BUCKETS] repository, market_images, avatars")
    except Exception as exc:
        print(f"   [STORAGE NOTICE] {exc}")

print("\n==================================================================")
print("     PURGA FINALIZADA: CERO FUNCIONES NI BUCKETS DEL GESTOR       ")
print("==================================================================")

