import os
import sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from SQL_Helpers import execute_query, ExecuteScalar, ejecutar_update, GetTemplateDetails
from sms_handler import send_sms_with_url


template_id = 'HXe020478ee336694dddbd68cba8c369a8'
query = """
        SELECT 
            Docs.id AS MedicoID, 
            Docs.phone_number, 
            Docs.custom_attributes_nickname AS Medico, 
            COALESCE(Pacs.custom_attributes_nickname, Pacs.name) AS Paciente, 
            CONVERT(VARCHAR(10), Paps.[Fecha Consulta], 23) AS Fecha, 
            Paps.id pap_id
        FROM dbo.Papanicolaous AS Paps
        INNER JOIN dbo.CW_Contacts AS Docs ON Paps.Medico_FK = Docs.id
        INNER JOIN dbo.CW_Contacts AS Pacs ON Paps.Paciente_FK = Pacs.id
        WHERE Paps.Estatus = N'Resultado Recibido' or Paps.Estatus = N'Enviada al Medico'
        """ 


def UpdateEstatus():
    update_query="""
                UPDATE Paps
                SET 
                    [Fecha Medico] = GETDATE(), 
                    Estatus = N'Enviada al Medico'
                FROM dbo.Papanicolaous AS Paps
                WHERE Estatus = N'Resultado Recibido'
                 """
    ejecutar_update(update_query)


def SendPapToDoc():
    """
    Envía SMS con URL del resultado del papanicolaou a los médicos.
    """
    # 1. Obtener los detalles de la plantilla
    template_details = GetTemplateDetails(template_id)
    if template_details is None:
        print(f"No se encontró el body de la plantilla '{template_id}'.")
        return
    
    # 2. Ejecutar el query para obtener el DataFrame
    df = execute_query(query)
    if df is None or df.empty:
        print("No se obtuvieron resultados de la consulta o el resultado no es una tabla.")
        return
    
    # 3. Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        try:
            # Extraer datos de la fila
            contacto_id = int(row['MedicoID'])  # ID del médico
            phone_number = str(row['phone_number'])  # Teléfono del médico
            medico = str(row['Medico'])  # Nombre del médico
            paciente = str(row['Paciente'])  # Nombre del paciente
            fecha = str(row['Fecha'])  # Fecha de consulta
            pap_id = int(row['pap_id'])  # ID del papanicolaou
            
            # 4. Preparar parámetros para el mensaje
            parametros = [medico, paciente, fecha]
            
            # 5. Reemplazar los parámetros en el mensaje de la plantilla
            message = template_details['Body']
            for ii, param in enumerate(parametros, 1):
                message = message.replace(f"{{{{{ii}}}}}", param)
            
            # 6. Construir la URL del resultado
            url = f"https://paps-81av.onrender.com/papanicolaou/{pap_id}"
            
            # 7. Enviar SMS con URL
            if contacto_id and phone_number:
                success = send_sms_with_url(
                    contact_id=contacto_id,
                    phone_number=phone_number,
                    message=message,
                    url=url
                )
                
                if success:
                    print(f"SMS enviado exitosamente al médico {medico} (ID: {contacto_id})")
                else:
                    print(f"Error al enviar SMS al médico {medico} (ID: {contacto_id})")
                
                time.sleep(1)  # Esperar 1 segundo entre envíos
                
        except Exception as e:
            print(f"Error procesando fila {index}: {e}")
            continue
    
    # 8. Actualizar estatus después de enviar todos los mensajes
    UpdateEstatus()
    print("Proceso completado.")


# Ejecutar la función si se llama directamente
if __name__ == "__main__":
    SendPapToDoc()

