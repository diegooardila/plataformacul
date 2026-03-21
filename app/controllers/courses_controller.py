import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.courses_model import Courses
from fastapi.encoders import jsonable_encoder

class CoursesController:
        
    def create_course(self, course: Courses):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO curso (codigo_curso,nombre_curso,cupo_maximo,fecha_hora,id_docente,id_aula,id_periodo,id_estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (course.course_code, course.course_name, course.max_capacity, course.schedule, course.teacher_user_id, course.clasroom, course.period_id, course.status))
            conn.commit()
            conn.close()
            return {"resultado": "Course created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_course(self, id_course: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE id_curso = %s", (id_course,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Course not found")

            content = {
                'course_id': int(result[0]),
                'course_code': result[1],
                'course_name': result[2],
                'max_capacity': int(result[3]),
                'schedule': result[4],
                'teacher_user_id': int(result[5]),
                'clasroom': result[6],
                'period_id': int(result[7]),
                'status': int(result[8])
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
       
    def get_courses(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'course_id':int(data[0]),
                    'course_code':data[1],
                    'course_name':data[2],
                    'max_capacity':int(data[3]),
                    'schedule':data[4],
                    'teacher_user_id':int(data[5]),
                    'clasroom':int(data[6]),
                    'period_id':int(data[7]),
                    'status':int(data[8])
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Course not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def update_course(self, id_course: int, course: Courses):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE courses
                SET course_code = %s,
                    course_name = %s,
                    max_capacity = %s,
                    schedule = %s,
                    teacher_user_id = %s,
                    clasroom = %s,
                    period_id = %s,
                    status = %s
                WHERE course_id = %s
            """, (
                course.course_code,
                course.course_name,
                course.max_capacity,
                course.schedule,
                course.teacher_user_id,
                course.clasroom,
                course.period_id,
                course.status,
                id_course
            ))
            conn.commit()
            return {"resultado": "Course updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_course(self, id_course: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM courses WHERE course_id = %s", (id_course,))
            conn.commit()
            return {"resultado": "Course deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

##coursecontroller = CoursesController()
