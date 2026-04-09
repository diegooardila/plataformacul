import os
import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.rfvzywmfpysnjinykmdr:prycursos2026@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)