import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Blast')))

from BlastHelper import SendBlast
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import ejecutar_update
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
        query=f"""SELECT [id]
                    ,[phone_number]
                FROM [dbo].[CW_Contacts] with (Nolock)
                where id={contact_id}"""


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
                review_msg="""Que bie que tuviste una buena experiencia. Me seria muyt util si me ayudas a calificarnos en Google                
Te dejo el link, ojal tengas la oportunidad de calificarnos: 

https://g.page/r/CaJxTFA06462EBM/review"""
                send_conversation_message(conversation_id, review_msg, is_private=False, buzon=ChatwootSenders.Pacientes)
                #SendBlast("HXf83b08ae35dae1fef5f5283e0f4e1689", bot_name=None, query=query)
            else:
                send_conversation_message(conversation_id, 'Que lamentable, me puedes comentar un poco de tu experiencia?, por favor', is_private=False, buzon=ChatwootSenders.Pacientes)
                send_conversation_message(conversation_id, '@Pablo soy Robot, revisa esta calificacion', is_private=True, buzon=ChatwootSenders.Pacientes)
            update_query=f"EXEC CalificaConsulta {calificacion}, {contact_id}"
            ejecutar_update(update_query)
        else:
            remove_bot_attribute(conversation_id)

    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging
