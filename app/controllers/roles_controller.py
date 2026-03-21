import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.roles_model import Role
from models.courses_model import Courses
from fastapi.encoders import jsonable_encoder

class RoleController:
        
    def create_role(self, role: Role):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO role (role_name) VALUES (%s)", (role.role_name,))
            conn.commit()
            conn.close()
            return {"resultado": "Role created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_role(self, id_role: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM role WHERE role_id = %s", (id_role,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Role not found")

            content = {
                'id_role': int(result[0]),
                'role_name': result[1]
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
       
    def get_roles(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM role")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id_role':int(data[0]),
                    'role_name':data[1]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Role not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    def update_role(self, id_role: int, role: Role):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE role
                SET role_name = %s
                WHERE role_id = %s
            """, (
                role.role_name,
                id_role
            ))
            conn.commit()
            return {"resultado": "Role updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_role(self, id_role: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM role WHERE role_id = %s", (id_role,))
            conn.commit()
            return {"resultado": "Role deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    ## RUTAS PARA ADMINISTRADOR DE CURSOS

    def create_course_from_admin(self, course: Courses):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO curses (codigo_curso,nombre_curso,cupo_maximo,fecha_hora,id_docente,id_aula,id_periodo,id_estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (course.course_code, course.course_name, course.max_capacity, course.schedule, course.teacher_user_id, course.clasroom, course.period_id, course.status))
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
    
    def update_course_from_admin(self, id_course: int, course: Courses):
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

    def delete_course_from_admin(self, id_course: int):
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
       
##role_controller = RoleController()