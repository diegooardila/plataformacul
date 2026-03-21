import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.enrollments_model import Enrollment
from fastapi.encoders import jsonable_encoder

class EnrollmentController:
        
    def create_enrollment(self, enrollment: Enrollment):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO enrollments (student_user_id,course_id,registration_date,status_id) VALUES (%s, %s, %s, %s)", (enrollment.student_user_id, enrollment.course_id, enrollment.registration_date, enrollment.status_id))
            conn.commit()
            conn.close()
            return {"resultado": "Enrollment created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_enrollment(self, enrollment_id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Enrollment not found")

            content = {
                'enrollment_id': int(result[0]),
                'student_user_id': int(result[1]),
                'course_id': int(result[2]),
                'registration_date': result[3],
                'status_id': int(result[4])
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
       
    def get_enrollments(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM enrollments")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'enrollment_id':int(data[0]),
                    'student_user_id':int(data[1]),
                    'course_id':int(data[2]),
                    'registration_date':data[3],
                    'status_id':int(data[4])
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Enrollment not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def update_enrollment(self, enrollment_id: int, enrollment: Enrollment):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE enrollments
                SET student_user_id = %s,
                    course_id = %s,
                    registration_date = %s,
                    status_id = %s
                WHERE enrollment_id = %s
            """, (
                enrollment.student_user_id,
                enrollment.course_id,
                enrollment.registration_date,
                enrollment.status_id,
                enrollment_id
            ))
            conn.commit()
            return {"resultado": "Enrollment updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_enrollment(self, enrollment_id: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
            conn.commit()
            return {"resultado": "Enrollment deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

##enrollment_controller = EnrollmentController()