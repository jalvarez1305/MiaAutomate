import requests
import os
from dotenv import load_dotenv
import json
from twilio.rest import Client

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la BASE_URL y CW_TOKEN desde el .env
cw_token = os.getenv('CW_TOKEN')
base_url = os.getenv('BASE_URL')
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')

# Enumeración en Python para los buzones
class ChatwootSenders:
    Medicos = 10  
    Pacientes = 11  

def assign_agent_to_conversation(conversation_id, agent_id):
    """
    Asigna un agente a una conversación en Chatwoot.
    
    :param conversation_id: ID de la conversación a la que se asignará el agente.
    :param agent_id: ID del agente que se asignará a la conversación.
    """
    url = f"{base_url}/conversations/{conversation_id}/assign"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    body = {
        "assignee_id": agent_id  # ID del agente a asignar
    }

    response = requests.post(url, json=body, headers=headers)

    if response.status_code == 200:
        print(f"Agente {agent_id} asignado a la conversación {conversation_id} con éxito.")
    else:
        print(f"Error al asignar agente: {response.status_code} - {response.text}")

def remove_bot_attribute(conversation_id):
    """
    Elimina el atributo personalizado 'bot' de una conversación en Chatwoot.
    
    :param conversation_id: ID de la conversación de la que se eliminará el atributo.
    """
    attribute_key = "bot"  # Clave del atributo que se desea eliminar
    url = f"{base_url}/api/v1/conversations/{conversation_id}/custom_attributes/{attribute_key}"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print(f"Atributo '{attribute_key}' eliminado con éxito de la conversación {conversation_id}.")
    else:
        print(f"Error al eliminar el atributo: {response.status_code} - {response.text}")

def send_content_builder(to, content_sid, media_url, body):
    """
    Envía un mensaje utilizando una plantilla de Twilio Content Builder.
    
    :param to: El número de destino en formato internacional (ej. "+523331830952").
    :param content_sid: El Content Template SID para el mensaje.
    :param media_url: La URL de la imagen que se enviará.
    :param body: El mensaje adicional que se enviará.
    """
    
    # Inicializar el cliente de Twilio
    client = Client(twilio_account_sid, twilio_auth_token)

    try:
        # Enviar el mensaje usando la plantilla de Content Builder
        message = client.messages.create(
            to=f"whatsapp:{to}",  # El número de destino (México)
            from_=twilio_from_number,  # Número de Twilio registrado en tu cuenta
            content_sid=content_sid,  # Content Template SID
            body=body,  # Mensaje adicional
            media_url=media_url,  # URL de la imagen
        )
        print(f"Mensaje enviado con SID: {message.sid}")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

def envia_mensaje_plantilla(contacto_id, plantilla, parametros=None, buzon=ChatwootSenders.Pacientes, bot_name=None,is_private=False,force_new=False):
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

    if open_conv and force_new:
        cerrar_conversacion(open_conv)
        open_conv= None
    # Verificar si se encontró una conversación abierta
    if open_conv:
        print(f"Se enlaza a la conversación: {open_conv}")
        send_conversation_message(open_conv, text_to_send, buzon=buzon,is_private=is_private)
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
                    "content": text_to_send,  # Corregido: eliminada la comilla extra
                    "private": is_private,
                    "template_params": {
                        "name": "sorteo_240430",  # Nombre de la plantilla
                        "category": "UTILITY",    # Categoría de la plantilla
                        "language": "en_US",      # Idioma de la plantilla
                        "processed_params": {     # Parámetros procesados
                            "Orlans": "Orlans"    # Parámetro procesado, ajusta según sea necesario
                        }
                    }
                }
            }
        else:
            # Crear conversación con bot
            conversation_body = {
                "contact_id": contacto_id,
                "inbox_id": buzon,
                "message": {
                    "content": text_to_send,
                    "private": is_private,  # Corregido: eliminada la comilla extra
                    "template_params": {
                        "name": "sorteo_240430",  # Nombre de la plantilla
                        "category": "UTILITY",    # Categoría de la plantilla
                        "language": "en_US",      # Idioma de la plantilla
                        "processed_params": {     # Parámetros procesados
                            "Orlans": "Orlans"    # Parámetro procesado, ajusta según sea necesario
                        }
                    }
                },
                "custom_attributes": {
                    "bot": bot_name  # Atributos personalizados para el bot
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

def cerrar_conversacion(conv_id):
    """
    Cierra una conversación en Chatwoot cambiando su estado a 'closed'.
    
    :param conv_id: ID de la conversación a cerrar.
    """
    print(f"Cerrando la conversación con ID: {conv_id}")
    
    url = f"{base_url}/conversations/{conv_id}/toggle_status"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    body = {
        "status": "closed"  # Cambiamos el estado a 'closed'
    }

    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        print("Estatus cambiado a cerrado con éxito.")
    else:
        print(f"Error al cerrar la conversación: {response.text}")


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

def get_conversation_messages(conversation_id):
    """
    Obtiene los mensajes de una conversación en Chatwoot.

    :param conversation_id: ID de la conversación de la cual se desean obtener los mensajes.
    :return: Un arreglo con los mensajes, cada uno conteniendo el 'Sender' y el 'Content'.
    """
    url = f"{base_url}/conversations/{conversation_id}/messages"
    headers = {
        "api_access_token": cw_token
    }
    messages = []  # Lista para almacenar los mensajes

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            # Acceder a 'payload' para obtener los mensajes
            for message in response_data.get('payload', []):
                try:
                    sender = message.get('sender', {}).get('type')  # 'Agent' o 'Contact'
                    content = message.get('content')  # Contenido del mensaje

                    # Añadir el mensaje a la lista si tanto 'sender' como 'content' están presentes
                    if sender and content:
                        messages.append({
                            'Sender': sender,
                            'Content': content
                        })

                except Exception as inner_ex:
                    print(f"Excepción al procesar mensaje: {str(inner_ex)}")
        
            print("Mensajes extraídos con éxito.")
        else:
            print(f"Error al obtener mensajes: {response.text}")

    except Exception as ex:
        print(f"Excepción al obtener mensajes: {str(ex)}")

    return messages


