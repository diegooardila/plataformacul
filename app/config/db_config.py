import psycopg2

def get_db_connection():
    return psycopg2.connect(
        "postgresql://postgres.rfvzywmfpysnjinykmdr:prycursos2026@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
    )
