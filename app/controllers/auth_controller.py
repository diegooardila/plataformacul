from fastapi import HTTPException
from config.db_config import get_db_connection
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "proyecto-cul-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

class LoginRequest(BaseModel):
    email: str
    password: str

def login_user(login_data: LoginRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

    cur = conn.cursor()
    try:
        # Buscamos al usuario por su email
        cur.execute("""
            SELECT user_id, identity_document, first_name, last_name, email, password_hash, role_id, faculty_id, status_id
            FROM users
            WHERE email = %s
        """, (login_data.email,))
        
        user_row = cur.fetchone()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas (usuario no encontrado)")

        user = {
            "user_id": user_row[0],
            "identity_document": user_row[1],
            "first_name": user_row[2],
            "last_name": user_row[3],
            "email": user_row[4],
            "password_hash": user_row[5],
            "role_id": user_row[6],
            "faculty_id": user_row[7],
            "status_id": user_row[8]
        }

        # NOTA: Validar contraseña en texto plano por petición estructural del ambiente legacy.
        if user["password_hash"] != login_data.password:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas (contraseña inválida)")

        # Generar Token JWT
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": str(user["user_id"]),
            "role_id": user["role_id"],
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        # Removed password_hash from returning to the frontend for security
        del user["password_hash"]

        return {
            "resultado": {
                "token": encoded_jwt,
                "user": user
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
