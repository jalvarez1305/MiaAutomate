import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Blast')))
from BlastHelper import SendBlast
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update
from CW_Contactos import actualizar_funel_states


template_id = 'HX3561b9f5865bd48c71f6b5aa8280b227'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """
        SELECT        top 20 
			id, phone_number, name,GETDATE() as fecha,funel_state,'gine_state_3' as blast
            FROM            CW_Contacts
            WHERE        (custom_attributes_es_prospecto = 1) 
                    AND (custom_attributes_interes_en = 'https://miaclinicasdelamujer.com/gynecologia/')
                    AND funel_state =3
                    AND datediff(dd,DATEADD(ss, [last_activity_at], '1970-01-01 00:00:00'),getdate())  > 30
                    AND id not in (SELECT [Paciente ID]
                                FROM [Clinica].[dbo].[vw_CalendarEventsExtracted]
                                where DATEADD(hh, - 6, [start_datetime])>getdate() 
                                and not [Paciente ID] is null)
			order by created_at
    """ 
def UpdateEstatus():
    update_query="""
                INSERT INTO [dbo].[FunnelHistory]
                        ([id],[phone_number],[name],[fecha],[funel_state],[blast])
                SELECT        top 20 
			id, phone_number, name,GETDATE() as fecha,funel_state,'gine_state_3' as blast
            FROM            CW_Contacts
            WHERE        (custom_attributes_es_prospecto = 1) 
                    AND (custom_attributes_interes_en = 'https://miaclinicasdelamujer.com/gynecologia/')
                    AND funel_state =3
                    AND datediff(dd,DATEADD(ss, [last_activity_at], '1970-01-01 00:00:00'),getdate())  > 30
                    AND id not in (SELECT [Paciente ID]
                                FROM [Clinica].[dbo].[vw_CalendarEventsExtracted]
                                where DATEADD(hh, - 6, [start_datetime])>getdate() 
                                and not [Paciente ID] is null)
			order by created_at
                 """
    ejecutar_update(update_query)
#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)
UpdateEstatus()
# Iterar por cada contacto para acutlizar el funnel state a 2
actualizar_funel_states(query,4)
