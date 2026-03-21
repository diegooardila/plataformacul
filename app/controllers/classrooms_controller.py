import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.classrooms_model import Classroom
from fastapi.encoders import jsonable_encoder

class ClassroomController:
        
    def create_classroom(self, classroom: Classroom):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO classrooms (classroom_code,max_capacity,status) VALUES (%s, %s, %s)", (classroom.classroom_code, classroom.max_capacity, classroom.status))
            conn.commit()
            conn.close()
            return {"resultado": "Classroom created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_classroom(self, id_classroom: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classrooms WHERE id_classroom = %s", (id_classroom,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Classroom not found")

            content = {
                'id_classroom': int(result[0]),
                'classroom_code': result[1],
                'max_capacity': int(result[2]),
                'status': int(result[3])
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
       
    def get_classrooms(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classrooms")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id_classroom':int(data[0]),
                    'classroom_code':data[1],
                    'max_capacity':int(data[2]),
                    'status':int(data[3])
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Classroom not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    def update_classroom(self, id_classroom: int, classroom: Classroom):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE classrooms
                SET classroom_code = %s,
                    max_capacity = %s,
                    status = %s
                WHERE id_classroom = %s
            """, (
                classroom.classroom_code,
                classroom.max_capacity,
                classroom.status,
                id_classroom
            ))
            conn.commit()
            return {"resultado": "Classroom updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_classroom(self, id_classroom: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classrooms WHERE id_classroom = %s", (id_classroom,))
            conn.commit()
            return {"resultado": "Classroom deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
##classroom_controller = ClassroomController()