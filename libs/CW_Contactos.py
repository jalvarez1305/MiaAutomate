import requests
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la BASE_URL y CW_TOKEN desde el .env
cw_token = os.getenv('CW_TOKEN')
base_url = os.getenv('BASE_URL')

def actualizar_interes_en(contact_id, interes_en):
    # Configuración de la URL y encabezados de autenticación
    url = f"{base_url}/contacts/{contact_id}"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    # Datos para actualizar el atributo personalizado
    data = {
        "custom_attributes": {
            "interes_en": interes_en,
            "es_prospecto":"1"
        }
    }
    
    # Envío de la solicitud PATCH para actualizar el contacto
    response = requests.put(url, json=data, headers=headers)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        print("Atributo 'interes_en' actualizado correctamente.")
    else:
        print(f"Error al actualizar el atributo: {response.status_code}")
        print(response.json())

def actualizar_etiqueta(conv_id, label):
    # Configuración de la URL y encabezados de autenticación
    url = f"{base_url}/conversations/{conv_id}/labels"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    # Datos para actualizar el atributo personalizado
    data = {
        "labels": 
        [
            label
        ]
    }
    
    # Envío de la solicitud PATCH para actualizar el contacto
    response = requests.put(url, json=data, headers=headers)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        print("Etiqueta actualizada.")
    else:
        print(f"Error al actualizar el atributo: {response.status_code}")
        print(response.json())