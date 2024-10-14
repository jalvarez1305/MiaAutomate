import sys
import os

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import get_conversation_messages

def parse_conversation_payload(payload):
    """
    Procesa el payload de una conversación y extrae la información relevante.
    
    :param payload: Diccionario que contiene la información de la conversación.
    :return: Objeto con la información estructurada de la conversación.
    """
    # Extraer información principal de la conversación
    conversation = payload.get("conversation", {})
    meta = conversation.get("meta", {})
    sender_info = meta.get("sender", {})

    # Crear un diccionario para almacenar la información de la conversación
    conversation_info = {
        "conversation_id": conversation.get("id"),
        "contact_id": sender_info.get("id"),
        "contact_name": sender_info.get("name"),
        "bot_attribute": conversation.get("custom_attributes", {}).get("bot")
    }

    # Extraer mensajes de la conversación
    messages = get_conversation_messages(conversation_info['conversation_id'])  # Obtener mensajes
    conversation_info['messages'] = messages

    # Asegurarse de que hay mensajes antes de intentar acceder al último
    if messages:  # Comprobar que la lista de mensajes no esté vacía
        conversation_info["last_message"] = messages[-1]  # Guardar el último mensaje
    else:
        conversation_info["last_message"] = None  # Si no hay mensajes, establecer como None

    return conversation_info
