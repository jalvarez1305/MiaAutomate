import requests
import os
from dotenv import load_dotenv

from SQL_Helpers import execute_query

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
    response = requests.post(url, json=data, headers=headers)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        print("Etiqueta actualizada.")
    else:
        print(f"Error al actualizar la etiqueta: {response.status_code}")
        print(conv_id)

def asignar_a_agente(conv_id, agente_id=15):
    # Configuración de la URL y encabezados de autenticación
    #15 Yaneth
    url = f"{base_url}/conversations/{conv_id}/assignments"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }

    # Datos para asignar la conversación al agente por ID
    data = {
        "assignee_id": agente_id
    }

    # Envío de la solicitud POST para asignar la conversación
    response = requests.post(url, json=data, headers=headers)

    # Verificación de la respuesta
    if response.status_code == 200:
        print(f"Conversación {conv_id} asignada al agente con ID {agente_id}.")
    else:
        print(f"Error al asignar la conversación: {response.status_code}")
        print(f"ID de la conversación: {conv_id}")


def actualizar_funel_state(contact_id, state):
    # Configuración de la URL y encabezados de autenticación
    url = f"{base_url}/contacts/{contact_id}"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    # Datos para actualizar el atributo personalizado
    data = {
        "custom_attributes": {
            "funel_state": state
        }
    }
    
    # Envío de la solicitud PATCH para actualizar el contacto
    response = requests.put(url, json=data, headers=headers)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        print("Atributo 'funnel_state' actualizado correctamente.")
    else:
        print(f"Error al actualizar el atributo: {response.status_code}")
        print(response.json())

def actualizar_funel_states(query=None,new_state=None):
    """
    Ejecuta la consulta y para cada fila busca el contacto y asi actualiza su state
    """

    # 2. Ejecutar el query para obtener el DataFrame
    df = execute_query(query)
    if df is None or df.empty:
        print("No se obtuvieron resultados de la consulta o el resultado no es una tabla.")
        return

    # 3. Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        # 3.1 Extraer contacto_id y teléfono
        contacto_id = row[0]  # Primera columna es contacto_id
        # 5. Llamar a la función send_content_builder
        actualizar_funel_state(contacto_id, new_state)
    print("Contactos actualizados")