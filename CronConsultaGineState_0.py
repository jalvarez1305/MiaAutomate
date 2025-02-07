import os
import sys



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Automations import send_blast_image
from CW_Conversations import ChatwootSenders
from SQL_Helpers import ejecutar_update
from CW_Contactos import actualizar_funel_states

template_name = 'gine_state_0'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        id, phone_number, name,GETDATE() as fecha,funel_state,'gine_state_0' as blast
            FROM            CW_Contacts
            WHERE        (custom_attributes_es_prospecto = 1) 
                    AND (custom_attributes_interes_en = 'https://miaclinicasdelamujer.com/gynecologia/')
                    AND funel_state =0
                    AND datediff(hh,DATEADD(ss, [last_activity_at], '1970-01-01 00:00:00'),getdate())  > 60
                    AND id not in (SELECT [Paciente ID]
                                FROM [Clinica].[dbo].[vw_CalendarEventsExtracted]
                                where DATEADD(hh, - 6, [start_datetime])>getdate() 
                                and not [Paciente ID] is null)
                    """ 

#El query lleva, contacto, telefono y parametros
send_blast_image(template_name, bot_name=bot_name, query=query)
#Insertarlo en el historico de blast
update_query ="""INSERT INTO [dbo].[FunnelHistory]
                        ([id],[phone_number],[name],[fecha],[funel_state],[blast])
                SELECT        id, phone_number, name,GETDATE() as fecha,funel_state,'gine_state_0' as blast
                FROM            CW_Contacts
                WHERE        (custom_attributes_es_prospecto = 1) 
                        AND (custom_attributes_interes_en = 'https://miaclinicasdelamujer.com/gynecologia/')
                        AND funel_state =0
                        AND datediff(hh,DATEADD(ss, [last_activity_at], '1970-01-01 00:00:00'),getdate())  > 60
                        AND id not in (SELECT [Paciente ID]
                                    FROM [Clinica].[dbo].[vw_CalendarEventsExtracted]
                                    where DATEADD(hh, - 6, [start_datetime])>getdate() 
                                    and not [Paciente ID] is null)
                        """
ejecutar_update(update_query)
# Iterar por cada contacto para acutlizar el funnel state a 1
actualizar_funel_states(query,1)