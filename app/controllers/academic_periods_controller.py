import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.academic_periods_model import AcademicPeriod
from fastapi.encoders import jsonable_encoder

class AcademicPeriodController:
        
    def create_academic_period(self, academic_period: AcademicPeriod):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO academic_periods (period_code, start_date, end_date) VALUES (%s, %s, %s)", (academic_period.period_code, academic_period.start_date, academic_period.end_date))
            conn.commit()
            conn.close()
            return {"resultado": "Academic period created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        

    def get_academic_period(self, id_period: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM academic_periods WHERE period_id = %s", (id_period,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Academic period not found")

            content = {
                'id_period': int(result[0]),
                'period_code': result[1],
                'start_date': result[2],
                'end_date': result[3]
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
       
    def get_academic_periods(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM academic_periods")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id_period':int(data[0]),
                    'period_code':data[1],
                    'start_date':data[2],
                    'end_date':data[3]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Academic period not found")  

        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def update_academic_period(self, id_period: int, academic_period: AcademicPeriod):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE academic_periods
                SET period_code = %s, start_date = %s, end_date = %s
                WHERE period_id = %s
            """, (
                academic_period.period_code,
                academic_period.start_date,
                academic_period.end_date,
                id_period
            ))
            conn.commit()
            return {"resultado": "Academic period updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_academic_period(self, id_period: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM academic_periods WHERE period_id = %s", (id_period,))
            conn.commit()
            return {"resultado": "Academic period deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    
##academic_period_controller = AcademicPeriodController()