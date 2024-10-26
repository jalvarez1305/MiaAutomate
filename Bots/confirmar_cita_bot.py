import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import execute_query,ExecuteScalar
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
       
        respuesta = """Muchas gracias, tu cita queda confirmada"""


        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content =="Si,confirmar":
            cmd=f"SELECT top 1 [ID] FROM [dbo].[vw_CalendarEventsExtracted] where [Paciente ID] = {contact_id} order by start_datetime desc"
            ultima_cita=ExecuteScalar(cmd)
            cmd=f"UPDATE [cal].[CalendarEvents] SET [summary ]= REPLACE([summary], 'Agendada', 'Confirmada') WHERE ID='{ultima_cita}'"
            ExecuteScalar(cmd)
            send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
        else:
            send_conversation_message(conversation_id, 'Hola soy Robot, me ayudan con esto?', is_private=True, buzon=ChatwootSenders.Pacientes)
    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging
