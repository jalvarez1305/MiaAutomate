import os
import sys
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Obtener las variables de Chatwoot desde el .env
cw_token = os.getenv('CW_TOKEN')
base_url = os.getenv('BASE_URL')

# Inbox ID para SMS (bandeja 26)
SMS_INBOX_ID = 26


def get_or_create_conversation(contact_id, inbox_id):
    """
    Obtiene una conversación abierta del contacto o crea una nueva en el inbox especificado.
    
    :param contact_id: ID del contacto en Chatwoot.
    :param inbox_id: ID del inbox (bandeja) en Chatwoot.
    :return: ID de la conversación o None si hay error.
    """
    # Primero intentar obtener conversación abierta
    url = f"{base_url}/conversations?status=open"
    headers = {
        "api_access_token": cw_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            response_data = response.json()
            conversations = response_data.get('data', {}).get('payload', [])
            
            # Buscar conversación del contacto en el inbox especificado
            for conv in conversations:
                meta = conv.get('meta', {})
                sender = meta.get('sender', {})
                inbox = conv.get('inbox_id')
                
                if (sender.get('id') == contact_id and 
                    inbox == inbox_id and 
                    conv.get('status') == 'open'):
                    return conv.get('id')
        
        # Si no se encontró, crear una nueva conversación
        url_create = f"{base_url}/conversations"
        headers_create = {
            "Content-Type": "application/json",
            "api_access_token": cw_token
        }
        
        conversation_body = {
            "contact_id": contact_id,
            "inbox_id": inbox_id,
            "message": {
                "content": "",
                "private": True
            }
        }
        
        response_create = requests.post(url_create, json=conversation_body, headers=headers_create)
        
        if response_create.status_code == 200:
            conversation_response = response_create.json()
            # La respuesta puede tener diferentes estructuras, intentar obtener el ID
            if isinstance(conversation_response, dict):
                return conversation_response.get("id") or conversation_response.get("conversation", {}).get("id")
            return None
        else:
            print(f"Error al crear conversación: {response_create.status_code} - {response_create.text}")
            return None
            
    except Exception as e:
        print(f"Error al obtener/crear conversación: {e}")
        return None


def send_sms_with_url(contact_id, phone_number, message, url):
    """
    Envía un mensaje SMS usando Chatwoot en la bandeja 26 con el mensaje y la URL.
    
    :param contact_id: ID del contacto en Chatwoot.
    :param phone_number: Número de teléfono del contacto (no se usa directamente, pero se mantiene por compatibilidad).
    :param message: Mensaje de texto para el SMS.
    :param url: URL a incluir en el mensaje.
    :return: True si se envió correctamente, False en caso contrario.
    """
    try:
        # Paso 1: Obtener o crear conversación en Chatwoot con inbox_id = 26
        conversation_id = get_or_create_conversation(contact_id, SMS_INBOX_ID)
        
        if conversation_id is None:
            print("Error: No se pudo obtener/crear la conversación")
            return False
        
        # Paso 2: Construir el mensaje completo con la URL
        full_message = f"{message}\n\n{url}"
        
        # Paso 3: Enviar mensaje usando Chatwoot en la bandeja 26
        send_result = send_sms_message(conversation_id, full_message)
        
        return send_result
        
    except Exception as e:
        print(f"Error en send_sms_with_url: {e}")
        return False


def send_sms_message(conversation_id, message):
    """
    Envía un mensaje SMS usando Chatwoot en la bandeja 26.
    
    :param conversation_id: ID de la conversación.
    :param message: Mensaje a enviar.
    :return: True si se envió correctamente, False en caso contrario.
    """
    try:
        url = f"{base_url}/conversations/{conversation_id}/messages"
        headers = {
            "Content-Type": "application/json",
            "api_access_token": cw_token
        }
        
        message_body = {
            "content": message,
            "private": False  # Mensaje público (SMS)
        }
        
        response = requests.post(url, json=message_body, headers=headers)
        
        if response.status_code == 200:
            print(f"SMS enviado con éxito a la conversación {conversation_id} en la bandeja 26")
            return True
        else:
            print(f"Error al enviar SMS: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error en send_sms_message: {e}")
        return False

