import os
import sys
from BlastHelper import SendBlast
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update


template_id = 'HX309b980d72c86b557050c96a5fec1735'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """
        WITH CTE AS (
        SELECT 
            Docs.id AS MedicoID, 
            Docs.phone_number, 
            Docs.custom_attributes_nickname AS Medico, 
            COALESCE(Docs.custom_attributes_nickname, Pacs.name) AS Paciente, 
            CONVERT(VARCHAR(10), Paps.[Fecha Consulta], 23) AS Fecha, 
            REPLACE(Paps.[presigned url], 'https://papanicolaous.s3.us-east-2.amazonaws.com/', '') AS Url,
            ROW_NUMBER() OVER (PARTITION BY Docs.id ORDER BY Paps.[Fecha Consulta] ASC) AS RowNum
        FROM dbo.Papanicolaous AS Paps
        INNER JOIN dbo.CW_Contacts AS Docs ON Paps.Medico_FK = Docs.id
        INNER JOIN dbo.CW_Contacts AS Pacs ON Paps.Paciente_FK = Pacs.id
        WHERE 
            Docs.id NOT IN (
                SELECT DISTINCT Medico_FK 
                FROM dbo.Papanicolaous WITH (NOLOCK) 
                WHERE Estatus = N'Enviada al Medico'
            )
            AND Paps.Estatus = N'Resultado Recibido'
    )
    SELECT MedicoID, 
            phone_number, 
            Medico, 
            Paciente, 
            Fecha, 
            Url
    FROM CTE
    WHERE RowNum = 1
        """ 
def UpdateEstatus():
    update_query="""
                WITH CTE AS (
                    SELECT 
                        Paps.id AS PapanicolaousID, 
                        Docs.id AS MedicoID, 
                        ROW_NUMBER() OVER (PARTITION BY Docs.id ORDER BY Paps.[Fecha Consulta] ASC) AS RowNum
                    FROM dbo.Papanicolaous AS Paps
                    INNER JOIN dbo.CW_Contacts AS Docs ON Paps.Medico_FK = Docs.id
                    WHERE 
                        Docs.id NOT IN (
                            SELECT DISTINCT Medico_FK 
                            FROM dbo.Papanicolaous WITH (NOLOCK) 
                            WHERE Estatus = N'Enviada al Medico'
                        )
                        AND Paps.Estatus = N'Resultado Recibido'
                )
                UPDATE Paps
                SET 
                    Paps.[Fecha Medico] = GETDATE(), 
                    Paps.Estatus = 'Enviada al Medico'
                FROM dbo.Papanicolaous AS Paps
                INNER JOIN CTE ON Paps.id = CTE.PapanicolaousID
                WHERE CTE.RowNum = 1;
                 """
    ejecutar_update(update_query)
#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)
UpdateEstatus()

def SendPapToDoc():
    SendBlast(template_id, bot_name=bot_name, query=query)
    UpdateEstatus()

