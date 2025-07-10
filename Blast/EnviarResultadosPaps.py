import os
import sys
from BlastHelper import SendBlast
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update


template_id = 'HX4c6fc074747b615ccf32d69ab78c75fb'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
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
#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)
UpdateEstatus()

def SendPapToDoc():
    SendBlast(template_id, bot_name=bot_name, query=query)
    UpdateEstatus()

