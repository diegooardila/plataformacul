import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.users_model import User
from fastapi.encoders import jsonable_encoder

class UserController:
        
    def create_user(self, usuario: User):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (identity_document, first_name, middle_name, last_name, second_last_name, email, password_hash, role_id, faculty_id, status_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (usuario.identity_document, usuario.first_name, usuario.middle_name, usuario.last_name, usuario.second_last_name, usuario.email, usuario.password_hash, usuario.role_id, usuario.faculty_id, usuario.status_id))
            conn.commit()
            return {"resultado": "User created"}
        except psycopg2.Error as err:
            print(err)
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))
        finally:
            if conn:
                conn.close()
        
    def get_user(self, user_id: int):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")

            content = {
                'user_id': int(result[0]),
                'identity_document': result[1],
                'first_name': result[2],
                'middle_name': result[3] if result[3] is not None else None,
                'last_name': result[4],
                'second_last_name': result[5] if result[5] is not None else None,
                'email': result[6],
                'password_hash': result[7],
                'role_id': int(result[8]),
                'faculty_id': int(result[9]) if result[9] is not None else None,
                'status_id': int(result[10])
            }

            return jsonable_encoder(content)
                
        except psycopg2.Error as err:
            print(err)
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))
        finally:
            if conn:
                conn.close()
       
    def get_users(self):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
            payload = []
            for data in result:
                content = {
                    'user_id': int(data[0]),
                    'identity_document': data[1],
                    'first_name': data[2],
                    'middle_name': data[3] if data[3] is not None else None,
                    'last_name': data[4],
                    'second_last_name': data[5] if data[5] is not None else None,
                    'email': data[6],
                    'password_hash': data[7],
                    'role_id': int(data[8]),
                    'faculty_id': int(data[9]) if data[9] is not None else None,
                    'status_id': int(data[10])
                }
                payload.append(content)
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="User not found")  
                
        except psycopg2.Error as err:
            print(err)
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))
        finally:
            if conn:
                conn.close()

    def update_user(self, id_user: int, user: User):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET identity_document = %s,
                    first_name = %s,
                    middle_name = %s,
                    last_name = %s,
                    second_last_name = %s,
                    email = %s,
                    password_hash = %s,
                    role_id = %s,
                    faculty_id = %s,
                    status_id = %s
                WHERE user_id = %s
            """, (
                user.identity_document,
                user.first_name,
                user.middle_name,
                user.last_name,
                user.second_last_name,
                user.email,
                user.password_hash,
                user.role_id,
                user.faculty_id,
                user.status_id,
                id_user
            ))
            conn.commit()
            return {"resultado": "User updated"}
        except psycopg2.Error as err:
            print(err)
            if conn:
                conn.rollback()
            raise HTTPException(status_code=500, detail=str(err))
        finally:
            if conn:
                conn.close()

    def delete_user(self, id_user: int):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = %s", (id_user,))
            conn.commit()
            return {"resultado": "User deleted"}
        except psycopg2.Error as err:
            print(err)
            if conn:
                conn.rollback()
            error_msg = str(err).lower()
            if "foreign key constraint" in error_msg:
                raise HTTPException(status_code=400, detail="No se puede eliminar: el usuario tiene registros asociados (inscripciones, notas, etc). Cambie su estado a Inactivo.")
            raise HTTPException(status_code=500, detail="Error interno de la base de datos al eliminar.")
        finally:
            if conn:
                conn.close()
