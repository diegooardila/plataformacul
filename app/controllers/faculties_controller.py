import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.faculties_model import Faculty
from fastapi.encoders import jsonable_encoder

class FacultyController:
        
    def create_faculty(self, faculty: Faculty):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO faculties (faculty_name) VALUES (%s)", (faculty.faculty_name,))
            conn.commit()
            conn.close()
            return {"resultado": "Faculty created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_faculty(self, id_faculty: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faculties WHERE faculty_id = %s", (id_faculty,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Faculty not found")

            content = {
                'id_faculty': int(result[0]),
                'faculty_name': result[1]
            }

            json_data = jsonable_encoder(content)
            return json_data
                
        except psycopg2.Error as err:
            print(err)
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            ##Maneja el estado de la transacción en la base de datos.Si un INSERT, UPDATE o DELETE falla dentro de una transacción, rollback() revierte esos cambios.
            conn.rollback()
        finally:
            conn.close()
       
    def get_faculties(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faculties")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id_faculty':int(data[0]),
                    'faculty_name':data[1]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Faculty not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    def update_faculty(self, id_faculty: int, faculty: Faculty):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE faculties
                SET faculty_name = %s
                WHERE faculty_id = %s
            """, (
                faculty.faculty_name,
                id_faculty
            ))
            conn.commit()
            return {"resultado": "Faculty updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_faculty(self, id_faculty: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM faculties WHERE faculty_id = %s", (id_faculty,))
            conn.commit()
            return {"resultado": "Faculty deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
       
##faculty_controller = FacultyController()