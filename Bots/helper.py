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
    labels = conversation.get("labels", [None])
    label = labels[0] if labels else None

    # Crear un diccionario para almacenar la información de la conversación
    conversation_info = {
        "conversation_id": conversation.get("id"),
        "contact_id": sender_info.get("id"),
        "contact_phone": sender_info.get("phone_number"),
        "contact_name": sender_info.get("name"),
        "bot_attribute": label or conversation.get("custom_attributes", {}).get("bot")
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

def es_primer_mensaje_usuario(conversation_id, contact_id):
    """
    Verifica si es el primer mensaje del usuario en la conversación.
    
    :param conversation_id: ID de la conversación
    :param contact_id: ID del contacto/usuario
    :return: True si es el primer mensaje del usuario, False en caso contrario
    """
    try:
        messages = get_conversation_messages(conversation_id)
        if not messages:
            return True
        
        # Filtrar solo mensajes del usuario (contact)
        user_messages = [m for m in messages if m.get('Sender') == 'contact']
        
        # Si hay exactamente 1 mensaje del usuario, es el primero
        return len(user_messages) == 1
    except Exception as e:
        print(f"Error al verificar primer mensaje: {str(e)}")
        return False
