import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.status_model import Status
from fastapi.encoders import jsonable_encoder

class StatusController:
        
    def create_status(self, status: Status):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO status (status_name) VALUES (%s)", (status.status_name,))
            conn.commit()
            conn.close()
            return {"resultado": "Status created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        
    def get_status(self, id_status: int):

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM status WHERE status_id = %s", (id_status,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Status not found")

            content = {
                'id_status': int(result[0]),
                'status_name': result[1]
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
       
    def get_statuses(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM status")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'id_status':int(data[0]),
                    'status_name':data[1]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Status not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    def update_status(self, id_status: int, status: Status):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE status SET status_name = %s WHERE status_id = %s", (status.status_name, id_status))
            conn.commit()
            conn.close()
            return {"resultado": "Status updated"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el UPDATE, los datos no quedan guardados parcialmente en la base de datos
             # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()

    def delete_status(self, id_status: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM status WHERE status_id = %s", (id_status,))
            conn.commit()
            return {"resultado": "Status deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
       
##status_controller = StatusController()