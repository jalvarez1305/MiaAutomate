import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import execute_query
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

def EncuestaPacienteBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
       
        respuesta = """Muchas gracias por tu respuesta. Me seria de gran ayuda si me ayudas a compartir esa calificacion en Google. Puedes?"""


        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        
        calificacion=0
        if '★' in last_message_content:
            match last_message_content:
                case "★":
                    calificacion=1
                case "★★★":
                    calificacion=3
                case "★★★★★":
                    calificacion=5
                case _:
                    logging.warning("Bot no reconocido.")
            if calificacion == 5:
                send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
            else:
                send_conversation_message(conversation_id, 'Que lamentable, me puedes comentar un poco de tu experiencia?, por favor', is_private=False, buzon=ChatwootSenders.Pacientes)
                send_conversation_message(conversation_id, '@Pablo soy Robot, revisa esta calificacion', is_private=True, buzon=ChatwootSenders.Pacientes)
            update_query=f"EXEC CalificaConsulta ({calificacion}, {contact_id})"
            execute_query(update_query)
        else:
            send_conversation_message(conversation_id, '@Pablo soy Robot, no puedo responder esto', is_private=True, buzon=ChatwootSenders.Pacientes)
            remove_bot_attribute(conversation_id)

    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging
