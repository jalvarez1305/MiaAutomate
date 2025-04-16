import requests
import os
from dotenv import load_dotenv
import json
from twilio.rest import Client
from datetime import datetime, timedelta

from CW_Contactos import actualizar_etiqueta, actualizar_interes_en
from SQL_Helpers import GetTemplateDetails

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
    Medicos = 16  
    Pacientes = 16  

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

def send_content_builder(to, content_sid, media_url=None, params=None):
    """
    Envía un mensaje utilizando una plantilla de Twilio Content Builder.
    
    :param to: El número de destino en formato internacional (ej. "+523331830952").
    :param content_sid: El Content Template SID para el mensaje.
    :param media_url: La URL de la imagen que se enviará (opcional).
    :param params: Arreglo de parámetros a pasar (opcional).
    """
    # Inicializar el cliente de Twilio
    client = Client(twilio_account_sid, twilio_auth_token)

    try:
        # Construir los argumentos dinámicamente
        message_args = {
            "to": f"whatsapp:{to}",
            "from_": twilio_from_number,
            "content_sid": content_sid,
        }
        
        if media_url:
            # Reemplazar los parámetros de Twilio en la URL media_url
            if params:
                # Asegurarnos de que los parámetros están en el formato adecuado
                if isinstance(params, list) and len(params) > 0:
                    # Reemplazar las instancias de {{n}} en media_url
                    for i, param in enumerate(params):
                        # Reemplazar el marcador {{i+1}} con el valor correspondiente en params
                        media_url = media_url.replace(f"{{{{{i+1}}}}}", str(param))
            
            # Asignar la URL media_url procesada a los argumentos del mensaje
            message_args["media_url"] = media_url
        
        if params:
            #convertir los parametros
            tw_params = {str(i+1): valor for i, valor in enumerate(params or [])}
            message_args["content_variables"] = json.dumps(tw_params)
        
        # Enviar el mensaje usando la plantilla de Content Builder
        message = client.messages.create(**message_args)
        print(f"Mensaje enviado con SID: {message.sid}")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
def send_audio_mp3_via_twilio(to_phone_number, media_url):
    """
    Envía un archivo MP3 a través de Twilio usando la API de mensajería.

    :param to_phone_number: Número de teléfono del destinatario (con código de país, e.g., '+1234567890').
    :param media_url: URL pública del archivo MP3 a enviar.
    :param from_phone_number: Número de teléfono de Twilio desde el cual enviar el mensaje.
    :param account_sid: SID de cuenta de Twilio.
    :param auth_token: Token de autenticación de Twilio.
    """
    # Crear el cliente de Twilio
    client = Client(twilio_account_sid, twilio_auth_token)

    # Enviar el mensaje de audio
    message = client.messages.create(
        body="Aquí tienes el archivo de audio.",  # Mensaje de texto opcional
        from_=twilio_from_number,  # Número de teléfono de Twilio
        to=f"whatsapp:{to_phone_number}",  # Número de destinatario
        media_url=[media_url]  # Lista con la URL del archivo MP3
    )
    # Imprimir el SID del mensaje para referencia
    print(f"Mensaje enviado con SID: {message.sid}")

def envia_mensaje_plantilla(contacto_id,phone_number, content_sid, parametros=None, buzon=ChatwootSenders.Pacientes, bot_name=None,force_new=False):
    """
    Envía un mensaje usando una plantilla en Chatwoot.
    
    :param contacto_id: ID del contacto al que se le enviará el mensaje.
    :param plantilla: Plantilla de mensaje con marcadores de posición ({{1}}, {{2}}, ...).
    :param parametros: Lista de parámetros para reemplazar en la plantilla.
    :param buzon: El buzón desde el que se enviará el mensaje (Pacientes o Medicos).
    :param bot_name: Nombre del bot si es un mensaje automatizado.
    :param url: Cuando el mensaje requiere una url
    """
    #Paso 1, mandar la plantilla por whataspp
    details=GetTemplateDetails(content_sid)
    send_content_builder(phone_number, content_sid, media_url=details['url'], params=parametros)
    if parametros is None:
        parametros = []

    # Reemplazar los parámetros en la plantilla
    text_to_send = details['Body']
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
        send_conversation_message(open_conv, text_to_send, buzon=buzon,is_private=True)
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
                    "private": True,
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
                    "private": True,  # Corregido: eliminada la comilla extra
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
        "status": "resolved"  # Cambiamos el estado a 'closed'
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


def send_conversation_file(conversation_id, file_url, is_private=False):
    """
    Envía un archivo adjunto a una conversación en Chatwoot desde una URL pública.
    
    :param conversation_id: ID de la conversación.
    :param file_url: URL pública del archivo a enviar.
    :param is_private: Si el mensaje es privado o público.
    """
    print(f"Descargando archivo desde {file_url}...")

    # Descargar el archivo desde la URL
    response = requests.get(file_url)
    if response.status_code != 200:
        print(f"Error al descargar el archivo: {response.status_code}, {response.text}")
        return

    # Guardar temporalmente el archivo
    file_name = file_url.split("/")[-1]
    with open(file_name, "wb") as temp_file:
        temp_file.write(response.content)

    # Endpoint de Chatwoot
    url = f"{base_url}/conversations/{conversation_id}/messages"
    headers = {
        "Authorization": f"Bearer {cw_token}",  # Token de autenticación
    }

    # Enviar el archivo como adjunto
    with open(file_name, "rb") as file:
        files = {
            "attachments[]": (file_name, file, "audio/mpeg")  # Asumimos que el archivo es de tipo audio
        }
        data = {
            "private": str(is_private).lower()  # Convertir booleano a string ("true"/"false")
        }

        # Enviar la solicitud
        response = requests.post(url, headers=headers, files=files, data=data)

    # Manejar la respuesta
    if response.status_code == 200:
        print(f"Archivo enviado con éxito: {response.json()}")
    else:
        print(f"Error al enviar archivo: {response.status_code}, {response.text}")


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
def get_conversation_by_id(conv_id):
    url = f"{base_url}/conversations/{conv_id}"
    headers = {
        "api_access_token": cw_token
    }
    
    conversacion = None
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("Conversación extraída con éxito.")
            conversacion = response.json()  # <--- Aquí cambiamos a .json()
        else:
            print(f"Error al extraer conversación: {response.text}")
    
    except Exception as ex:
        print(f"Excepción: {str(ex)}")
    
    return conversacion

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


# Constante para la duración de inactividad permitida
DURACION_INACTIVIDAD = timedelta(hours=23)

def cerrar_conversaciones_inactivas(page=0):
    """
    Cierra todas las conversaciones abiertas que han estado inactivas por más de 16 horas.
    """
    try:
        url = f"{base_url}/conversations?status=open&page={page}"
        headers = {
            "api_access_token": cw_token
        }
        
        response = requests.get(url, headers=headers)
        
        # Comprobar si la respuesta fue exitosa
        if response.status_code == 200:
            try:
                # Intenta deserializar la respuesta JSON
                conversations = response.json().get('data', [])
                now = datetime.utcnow()

                for conversation in conversations['payload']:  # Cambiado a conversations directamente
                    last_activity_at = conversation.get('last_activity_at')
                    
                    if last_activity_at:
                        # Asegúrate de que last_activity_at esté en segundos
                        last_activity_time = datetime.fromtimestamp(last_activity_at)
                        inactivity_duration = now - last_activity_time
                        
                        # Verificar si la conversación está abierta y ha estado inactiva por más de 16 horas
                        if inactivity_duration > DURACION_INACTIVIDAD:
                            try:
                                # Obtener el primer atributo de la lista de etiquetas en 'labels'
                                labels = conversation.get("labels", [None])
                                bot_attribute = labels[0] if labels else None

                                # Verificar que el atributo y el ID del contacto existen antes de proceder
                                if bot_attribute:
                                    contact_meta = conversation.get("meta", {}).get("sender", {})
                                    contact_id = contact_meta.get("id")
                                    
                                    if contact_id:  # Si `contact_id` existe, se actualiza el interés
                                        actualizar_interes_en(contact_id, "https://miaclinicasdelamujer.com/gynecologia/")
                                cerrar_conversacion(conversation.get('id'))
                            except Exception as cerr_error:
                                print(f"Error al cerrar la conversación {conversation.get('id')}: {str(cerr_error)}")
            except ValueError as json_error:
                print(f"Error al procesar el JSON de la respuesta: {str(json_error)}")
                print("Respuesta de la API:", response.text)  # Muestra la respuesta completa para depuración
        else:
            print(f"Error al obtener las conversaciones: {response.status_code} - {response.text}")
    
    except Exception as ex:
        print(f"Error al cerrar conversaciones inactivas: {str(ex)}")

def get_all_conversation_messages(conversation_id):
    all_messages = []
    headers = {"api_access_token": cw_token}
    before = None  # Iniciamos sin un ID específico

    first_iteration = True
    while True:
        url = f"{base_url}/conversations/{conversation_id}/messages"
        params = {}  # Sin parámetros en la primera iteración
        if not first_iteration:
            params["before"] = before  # Usar el ID más bajo del lote anterior en iteraciones siguientes

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break  # Si hay error, salimos del bucle

        data = response.json()
        messages = data.get("payload", [])
        if not messages:
            break  # Si no hay más mensajes, terminamos

        all_messages.extend([
            {
                "role": "assistant" if msg["sender"]["type"] == "user" else "user",
                "content": msg.get("content", ""),
                "created_at": msg.get("created_at", 0)
            }
            for msg in messages 
            if not msg.get("private", False) and "type" in msg.get("sender", {})
        ])

        # Obtener el ID más bajo del lote actual para la siguiente petición
        before = min(msg["id"] for msg in messages)
        first_iteration = False  # Desactivar la bandera después de la primera iteración

    # Ordenar los mensajes por created_at antes de retornarlos
    all_messages.sort(key=lambda msg: msg["created_at"])
    
    return all_messages

def get_AI_conversation_messages(conversation_id):
    all_messages_raw = []
    headers = {"api_access_token": cw_token}
    before = None
    first_iteration = True

    while True:
        url = f"{base_url}/conversations/{conversation_id}/messages"
        params = {} if first_iteration else {"before": before}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        messages = data.get("payload", [])
        if not messages:
            break

        # Guardamos mensajes con created_at solo para ordenarlos después
        all_messages_raw.extend([
            {
                "role": "user" if msg["sender"]["type"] == "user" else "assistant",
                "content": msg.get("content", ""),
                "created_at": msg.get("created_at", 0)
            }
            for msg in messages
            if not msg.get("private", False) and "type" in msg.get("sender", {})
        ])

        before = min(msg["id"] for msg in messages)
        first_iteration = False

    # Ordenamos por created_at
    all_messages_raw.sort(key=lambda msg: msg["created_at"])

    # Eliminamos el campo created_at antes de retornar
    all_messages = [{"role": msg["role"], "content": msg["content"]} for msg in all_messages_raw]

    return all_messages

def segundos_entre_ultimos_mensajes(conversation_id):
    mensajes = get_all_conversation_messages(conversation_id)

    # Filtrar solo los mensajes del rol "user"
    mensajes_user = [msg for msg in mensajes if msg["role"] == "user"]

    if len(mensajes_user) < 2:
        return 0  # No hay suficientes mensajes para calcular la diferencia

    ultimo = mensajes_user[-1]["created_at"]
    penultimo = mensajes_user[-2]["created_at"]

    return int(ultimo - penultimo)
