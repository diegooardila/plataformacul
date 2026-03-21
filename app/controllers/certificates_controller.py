import psycopg2
from fastapi import HTTPException
from config.db_config import get_db_connection
from models.certificates_model import Certificate
from fastapi.encoders import jsonable_encoder

class CertificateController:
        
    def create_certificate(self, certificate: Certificate):   
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO certificates (enrollment_id, verification_code, issue_date) VALUES (%s, %s, %s)", (certificate.enrollment_id, certificate.verification_code, certificate.issue_date))
            conn.commit()
            conn.close()
            return {"resultado": "certificate created"}
        except psycopg2.Error as err:
            print(err)
            # Si falla el INSERT, los datos no quedan guardados parcialmente en la base de datos
            # Se usa para deshacer los cambios de la transacción activa cuando ocurre un error en el try.
            conn.rollback()
        finally:
            conn.close()
        

    def get_certificate(self, id_certificate: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM certificates WHERE certificate_id = %s", (id_certificate,))
            result = cursor.fetchone()
            payload = []
            content = {} 
            

            if result is None:
                raise HTTPException(status_code=404, detail="Certificate not found")

            content = {
                'certificate_id': int(result[0]),
                'enrollment_id': int(result[1]),
                'verification_code': result[2],
                'issue_date': result[3]
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
       
    def get_certificates(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM certificates")
            result = cursor.fetchall()
            payload = []
            content = {} 
            for data in result:
                content={
                    'certificate_id':int(data[0]),
                    'enrollment_id':int(data[1]),
                    'verification_code':data[2],
                    'issue_date':data[3]
                }
                payload.append(content)
                content = {}
            json_data = jsonable_encoder(payload)        
            if result:
               return {"resultado": json_data}
            else:
                raise HTTPException(status_code=404, detail="Certificate not found")  
                
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
    
    def update_certificate(self, id_certificate: int, certificate: Certificate):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE certificates
                SET enrollment_id = %s, verification_code = %s, issue_date = %s
                WHERE certificate_id = %s
            """, (
                certificate.enrollment_id,
                certificate.verification_code,
                certificate.issue_date,
                id_certificate
            ))
            conn.commit()
            return {"resultado": "Certificate updated"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()

    def delete_certificate(self, id_certificate: int):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM certificates WHERE certificate_id = %s", (id_certificate,))
            conn.commit()
            return {"resultado": "Certificate deleted"}
        except psycopg2.Error as err:
            print(err)
            conn.rollback()
        finally:
            conn.close()
       
##certificate_controller = CertificateController()