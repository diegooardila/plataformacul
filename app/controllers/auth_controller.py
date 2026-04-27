from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.db_config import get_db_connection
from models.auth_model import LoginRequest, RegisterRequest
from services.token_service import (
    COOKIE_SECURE,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)

REFRESH_COOKIE_NAME = "refresh_token"

bearer_scheme = HTTPBearer(auto_error=False)


# ─── internal helpers ────────────────────────────────────────────────────────

def _fetch_user_by_email(cur, email: str) -> Optional[dict]:
    cur.execute(
        """
        SELECT user_id, identity_document, first_name, middle_name, last_name,
               second_last_name, email, password_hash, role_id, faculty_id, status_id
        FROM users WHERE email = %s
        """,
        (email,),
    )
    row = cur.fetchone()
    if not row:
        return None
    keys = [
        "user_id", "identity_document", "first_name", "middle_name", "last_name",
        "second_last_name", "email", "password_hash", "role_id", "faculty_id", "status_id",
    ]
    return dict(zip(keys, row))


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth",
    )


def _store_refresh_token(cur, user_id: int, token_hash: str) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    cur.execute(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES (%s, %s, %s)",
        (user_id, token_hash, expires_at),
    )


def _revoke_refresh_token(cur, token_hash: str) -> None:
    cur.execute(
        "UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s",
        (token_hash,),
    )


def _upgrade_password_if_legacy(cur, user_id: int, plain_password: str, stored_hash: str) -> None:
    """Silently upgrades a plaintext password to bcrypt within the current transaction."""
    if not (stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$")):
        new_hash = hash_password(plain_password)
        cur.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, user_id),
        )


# ─── register ────────────────────────────────────────────────────────────────

def register_user(data: RegisterRequest, response: Response) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="El email ya está registrado")

        cur.execute(
            "SELECT user_id FROM users WHERE identity_document = %s",
            (data.identity_document,),
        )
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="El documento de identidad ya está registrado")

        hashed_pw = hash_password(data.password)

        cur.execute(
            """
            INSERT INTO users (
                identity_document, first_name, middle_name, last_name,
                second_last_name, email, password_hash, role_id, faculty_id, status_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id, identity_document, first_name, middle_name, last_name,
                      second_last_name, email, role_id, faculty_id, status_id
            """,
            (
                data.identity_document, data.first_name, data.middle_name,
                data.last_name, data.second_last_name, data.email,
                hashed_pw, data.role_id, data.faculty_id, data.status_id,
            ),
        )
        row = cur.fetchone()
        keys = [
            "user_id", "identity_document", "first_name", "middle_name", "last_name",
            "second_last_name", "email", "role_id", "faculty_id", "status_id",
        ]
        user = dict(zip(keys, row))

        raw_token, token_hash = generate_refresh_token()
        _store_refresh_token(cur, user["user_id"], token_hash)
        conn.commit()

        access_token = create_access_token(user["user_id"], user["role_id"])
        _set_refresh_cookie(response, raw_token)

        return {"access_token": access_token, "token_type": "bearer", "user": user}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# ─── login ───────────────────────────────────────────────────────────────────

def login_user(login_data: LoginRequest, response: Response) -> dict:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        user = _fetch_user_by_email(cur, login_data.email)
        if not user or not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        _upgrade_password_if_legacy(cur, user["user_id"], login_data.password, user["password_hash"])

        raw_token, token_hash = generate_refresh_token()
        _store_refresh_token(cur, user["user_id"], token_hash)
        conn.commit()

        access_token = create_access_token(user["user_id"], user["role_id"])
        _set_refresh_cookie(response, raw_token)

        del user["password_hash"]
        return {"access_token": access_token, "token_type": "bearer", "user": user}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# ─── refresh ─────────────────────────────────────────────────────────────────

def refresh_tokens(request: Request, response: Response) -> dict:
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Refresh token no encontrado")

    token_hash = hash_refresh_token(raw_token)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT rt.id, rt.user_id, rt.expires_at, rt.revoked, u.role_id
            FROM refresh_tokens rt
            JOIN users u ON u.user_id = rt.user_id
            WHERE rt.token_hash = %s
            """,
            (token_hash,),
        )
        row = cur.fetchone()

        if not row:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        _rt_id, user_id, expires_at, revoked, role_id = row

        if revoked:
            # Token reuse detected — revoke all tokens for this user
            cur.execute(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE user_id = %s",
                (user_id,),
            )
            conn.commit()
            raise HTTPException(status_code=401, detail="Refresh token revocado — inicia sesión de nuevo")

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=401, detail="Refresh token expirado")

        # Rotate: revoke old, issue new
        _revoke_refresh_token(cur, token_hash)
        new_raw, new_hash = generate_refresh_token()
        _store_refresh_token(cur, user_id, new_hash)
        conn.commit()

        access_token = create_access_token(user_id, role_id)
        _set_refresh_cookie(response, new_raw)

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


# ─── logout ──────────────────────────────────────────────────────────────────

def logout_user(request: Request, response: Response) -> dict:
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        token_hash = hash_refresh_token(raw_token)
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            _revoke_refresh_token(cur, token_hash)
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/api/auth")
    return {"detail": "Sesión cerrada correctamente"}


# ─── get_current_user dependency ─────────────────────────────────────────────

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Tipo de token inválido")
        return {"user_id": int(payload["sub"]), "role_id": payload["role_id"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
