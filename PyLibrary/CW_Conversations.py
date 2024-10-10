import requests
import os
from dotenv import load_dotenv
import json

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la BASE_URL y CW_TOKEN desde el .env
cw_token = os.getenv('CW_TOKEN')
base_url = os.getenv('BASE_URL')

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
