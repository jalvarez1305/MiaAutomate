import json
import sys
import os
import logging
import time


# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI')))



from CW_Conversations import send_conversation_message
from CW_Contactos import actualizar_etiqueta,asignar_a_agente


# Configurar logging
logging.basicConfig(level=logging.INFO)

def BotCommands(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')

        #Aqui se evaluan todos los comandos internos a un bot
        if last_message_content == "cita":
            AsignaConversacion(conversation_id,contact_id)
    except Exception as e:
        logging.error(f"Error en bot_commands: {str(e)}")  # Manejo de errores con logging

def AsignaConversacion(conversation_id,paciente_id):
    actualizar_etiqueta(conversation_id,"agendar_cita")
    asignar_a_agente(conversation_id)
    send_conversation_message(conversation_id,f"Paciente numero: {paciente_id}",True)
    send_conversation_message(conversation_id,f"Muchas gracias hermosa 😊, nos vemos en la consulta. Que tengas un lindo día 😉",False)