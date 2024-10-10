import requests
import os
from dotenv import load_dotenv
import json

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la BASE_URL y CW_TOKEN desde el .env
cw_token = os.getenv('CW_TOKEN')
base_url = os.getenv('BASE_URL')

# Enumeración en Python para los buzones
class ChatwootSenders:
    Medicos = 2  
    Pacientes = 4  

def envia_mensaje_plantilla(contacto_id, plantilla, parametros=None, buzon=ChatwootSenders.Pacientes, bot_name=None):
    """
    Envía un mensaje usando una plantilla en Chatwoot.
    
    :param contacto_id: ID del contacto al que se le enviará el mensaje.
    :param plantilla: Plantilla de mensaje con marcadores de posición ({{1}}, {{2}}, ...).
    :param parametros: Lista de parámetros para reemplazar en la plantilla.
    :param buzon: El buzón desde el que se enviará el mensaje (Pacientes o Medicos).
    :param bot_name: Nombre del bot si es un mensaje automatizado.
    """
    if parametros is None:
        parametros = []

    print(f"Cantidad de parámetros: {len(parametros)} Texto: {plantilla} al contacto: {contacto_id} desde: {buzon}")

    # Reemplazar los parámetros en la plantilla
    text_to_send = plantilla
    for ii, param in enumerate(parametros, 1):
        text_to_send = text_to_send.replace(f"{{{{{ii}}}}}", param)

    print(f"El mensaje a enviar es: {text_to_send}")

    # Obtener la conversación abierta del contacto
    open_conv = get_open_conversation(contacto_id)

    # Verificar si se encontró una conversación abierta
    if open_conv:
        print(f"Se enlaza a la conversación: {open_conv}")
        send_conversation_message(open_conv, text_to_send, buzon=buzon)
    else:
        print(f"No se encontró conversación para el contacto ID: {contacto_id}")

        # Crear una nueva conversación si no hay una abierta
        url = f"{base_url}/conversations"
        headers = {
            "Content-Type": "application/json",
            "api_access_token": cw_token
        }

        if bot_name is None:
            # Crear conversación sin bot
            conversation_body = {
                "contact_id": contacto_id,
                "inbox_id": buzon,
                "message": {
                    "content": text_to_send
                }
            }
        else:
            # Crear conversación con bot
            conversation_body = {
                "contact_id": contacto_id,
                "inbox_id": buzon,
                "message": {
                    "content": text_to_send
                },
                "custom_attributes": {
                    "bot": bot_name
                }
            }

        response = requests.post(url, json=conversation_body, headers=headers)
        print(f"La respuesta al enviar la plantilla fue: {response.json()}")

        if response.status_code == 200:
            conversation_response = response.json()
            if conversation_response and conversation_response.get("status") == "resolved":
                reabrir_conversacion(conversation_response["id"])
            print("Mensaje enviado con éxito.")
        else:
            print(f"Error al enviar mensaje: {response.text}")

def reabrir_conversacion(conv_id):
    """
    Reabre una conversación en Chatwoot cambiando su estado a 'open'.
    
    :param conv_id: ID de la conversación a reabrir.
    """
    print(f"Reabriendo la conversación con ID: {conv_id}")
    
    url = f"{base_url}/conversations/{conv_id}/toggle_status"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    body = {
        "status": "open"
    }

    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        print("Estatus cambiado con éxito.")
    else:
        print(f"Error al cambiar el estatus: {response.text}")

def send_conversation_message(conversation_id, message, is_private=False, buzon=ChatwootSenders.Pacientes):
    """
    Envía un mensaje a una conversación en Chatwoot.
    
    :param conversation_id: ID de la conversación.
    :param message: Mensaje a enviar.
    :param is_private: Si es un mensaje privado o público.
    :param buzon: ID del buzón de Chatwoot.
    """
    print(f"Enviando: {conversation_id} Msg: {message}")
    
    url = f"{base_url}/conversations/{conversation_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    message_body = {
        "content": message,
        "private": is_private
    }

    response = requests.post(url, json=message_body, headers=headers)
    
    if response.status_code == 200:
        print(f"Mensaje enviado con éxito: {response.content.decode()}")
    else:
        print(f"Error al enviar mensaje: {response.text}")

def get_open_conversation(contact_id):
    conv_id = None  # Inicia con None por si no se encuentra ninguna conversación
    url = f"{base_url}/conversations?status=open"
    headers = {
        "api_access_token": cw_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("Mensajes extraidos con éxito.")
            conv_id = get_conv_from_contact(response.json(), contact_id)
        else:
            print(f"Error al enviar mensaje: {response.text}")
    
    except Exception as ex:
        print(f"Excepción: {str(ex)}")
    
    return conv_id

def get_conv_from_contact(response_data, contact_id):
    # Deserializar el contenido de la respuesta y buscar la conversación correspondiente
    try:
        conversations = response_data.get('data', {}).get('payload', [])  # Ajusta la estructura del JSON según la respuesta

        for item in conversations:
            # Verifica si el 'sender.id' coincide con el contact_id
            if item.get('meta', {}).get('sender', {}).get('id') == contact_id:
                return item.get('id')  # Devuelve el ID de la conversación
        
        print(f"No se encontró conversación para el contacto ID: {contact_id}")
    
    except Exception as ex:
        print(f"Error al procesar la respuesta: {str(ex)}")
    
    return None
