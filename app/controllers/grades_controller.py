import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.grades_model import Grade
from fastapi.encoders import jsonable_encoder

class GradeController:
        
    def create_grade(self, grade: Grade):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO grades (enrollment_id, final_grade, observations) VALUES (%s, %s, %s)", (grade.enrollment_id, grade.final_grade, grade.observations))
            conn.commit()
            conn.close()
            return {"resultado": "Grade created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_grade(self, id_grade: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM grades WHERE grade_id = %s", (id_grade,))
            result = cursor.fetchone()
            payload = []
            content = {} 

            if result is None:
                raise HTTPException(status_code=404, detail="Grade not found")

            content = {
                'grade_id': int(result[0]),
                'enrollment_id': int(result[1]),
                'final_grade': float(result[2]),
                'observations': result[3] if result[3] is not None else None
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
       
    def get_grades(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM grades")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'grade_id':int(data[0]),
                    'enrollment_id':int(data[1]),
                    'final_grade':float(data[2]),
                    'observations':data[3] if data[3] is not None else None
                }
                payload.append(content)
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Grade not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def update_grade(self, id_grade: int, grade: Grade):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE grades
                SET enrollment_id = %s,
                    final_grade = %s,
                    observations = %s
                WHERE grade_id = %s
            """, (
                grade.enrollment_id,
                grade.final_grade,
                grade.observations,
                id_grade
            ))
            conn.commit()
            return {"resultado": "Grade updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_grade(self, id_grade: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grades WHERE grade_id = %s", (id_grade,))
            conn.commit()
            return {"resultado": "Grade deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

##grade_controller = GradeController()