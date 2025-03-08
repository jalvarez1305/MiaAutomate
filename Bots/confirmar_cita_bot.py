import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

def ConfirmarCitaBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
       
        respuesta = """Muchas gracias hermosa 😊, tu cita queda confirmada. 
                      Que tengas lindo día!"""


        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content =="Si,confirmar":
            cmd=f"SELECT top 1 [ID] FROM [dbo].[vw_CalendarEventsExtracted] where [Paciente ID] = {contact_id} order by start_datetime desc"
            ultima_cita=ExecuteScalar(cmd)
            print(f"Ultima cita: {ultima_cita}")
            cmd=f"UPDATE [cal].[CalendarEvents] SET LocalUpdate=1,[summary]= REPLACE([summary], 'Agendada', 'Confirmada') WHERE ID='{ultima_cita}'"
            ejecutar_update(cmd)
            print(f"update query: {cmd}")
            send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
            RevisaFormularios(conversation_id,contact_id)
        else:
            send_conversation_message(conversation_id, 'Hola soy Robot, me ayudan con esto?', is_private=True, buzon=ChatwootSenders.Pacientes)
    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging

def RevisaFormularios(conversation_id,contact_id):
    cmd=f"SELECT [MedicoID] FROM [dbo].[vwCalendario] where [Paciente ID] = {contact_id} order by start_datetime desc"
    medico_cita=ExecuteScalar(cmd)
    match medico_cita:
        case 190:  # El ID de chatwoot de la paciente  
            respuesta="""https://forms.gle/vmk42hc1ZM58uqP99

Hola 👋🏻

📌Este cuestionario es parte fundamental de su análisis en la próxima consulta nutricional.

🍉Por favor asegúrese de llenarlo el día que le es enviado o al menos un día previo a la fecha de su consulta 🍇

🫐Tiempo estimado qué le tomara llenarlo: 5 minutos.

¡Gracias!"""
            send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
        case _:
            logging.warning("Bot no reconocido.")