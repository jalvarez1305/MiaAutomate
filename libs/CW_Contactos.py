import sys
import requests
import os
from dotenv import load_dotenv
import time

from SQL_Helpers import execute_query,update_sql_funnel_state,ExecuteScalar
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Blast')))


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

def actualizar_lead_source(contact_id, lead_source):
    # Configuración de la URL y encabezados de autenticación
    url = f"{base_url}/contacts/{contact_id}"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }
    
    # Datos para actualizar el atributo personalizado
    data = {
        "custom_attributes": {
            "lead_source": lead_source
        }
    }
    
    # Envío de la solicitud PATCH para actualizar el contacto
    response = requests.put(url, json=data, headers=headers)
    
    # Verificación de la respuesta
    if response.status_code == 200:
        print("Atributo 'lead_source' actualizado correctamente.")
    else:
        print(f"Error al actualizar el atributo lead_source: {response.status_code}")
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

def devolver_llamada(phone_number):
    """
    Cuando se recibe una llamada perdida en el webhoow inicia una conversacion con el contacto si ya existe
    Si no existe se crea y despues se inicia conversacion
    Si ya existe pero aun no es paciente se crea una conversacion diferente
    """
    tipo_contacto=get_tipo_contacto(phone_number)
    if tipo_contacto == "paciente" \
        or tipo_contacto == "citado":
        iniciar_Conv(phone_number,tipo_contacto)
    elif tipo_contacto == "prospecto":
        crear_contacto(phone_number)
        iniciar_Conv(phone_number,tipo_contacto)

def iniciar_Conv(phone_number,tipo_contacto):
    """
    Inicia una conversación en Chatwoot con el contacto dado"""
    time.sleep(10)
    from BlastHelper import SendBlast
    if tipo_contacto == "prospecto":
        template_id = 'HX4e3a35af08905947b55d7be6c840654d'   
    elif tipo_contacto == "citado":
        template_id = 'HX448ce843951d1867f4eb9531a48c3e85'
    elif tipo_contacto == "paciente":
        template_id = 'HX74e4965ec8f33d8b086ad6f2b654ae5d'
    query = f"""
        SELECT  id, phone_number, coalesce(custom_attributes_nickname,'Hermosa') custom_attributes_nickname
        FROM            CW_Contacts
        where phone_number ='{phone_number}'
    """ 
    SendBlast(template_id, bot_name=None, query=query)

def get_tipo_contacto(phone_number):
    cmd = f"SELECT [custom_attributes_es_prospecto] FROM [dbo].[CW_Contacts] where phone_number='{phone_number}'"
    prospecto= ExecuteScalar(cmd)
    if prospecto is None:
        print(f"No se encontró el contacto con el número {phone_number}.")
        return "prospecto"
    elif prospecto == 'True':
        print(f"El contacto con el número {phone_number} es un prospecto que ya tenia conversaciones antes.")
        return "citado"
    elif prospecto == 'False':
        print(f"El contacto con el número {phone_number} es un paciente o citado.")
        return "paciente"
    else:
        print(f"El contacto con el número {phone_number} no es un prospecto, paciente o citado.")
        return "desconocido"
def get_linphone_name(phone_number):
    cmd = f"""SELECT
                COALESCE(
                    (
                    SELECT 
                        -- Campo 1
                        CASE 
                        WHEN custom_attributes_nickname IS NOT NULL THEN custom_attributes_nickname
                        ELSE LEFT(name, CHARINDEX(' ', name + ' ') - 1)
                        END
                        + '--' +
                        -- Campo 2
                        CASE 
                        WHEN custom_attributes_nickname IS NOT NULL THEN 'Paciente'
                        ELSE 'Contacto'
                        END
                        + '--' +
                        -- Campo 3
                        CAST(id AS NVARCHAR)
                    FROM [dbo].[CW_Contacts]
                    WHERE phone_number = '{phone_number}'
                    ),
                    -- Si no existe registro
                    'Desconocida--Prospecto--{phone_number}'
                ) AS Resultado"""
    contact_name= ExecuteScalar(cmd)
    return contact_name
    
def crear_contacto(phone_number):
    """
    Crea un contacto en Chatwoot con el número telefónico dado
    como nombre y lead_source 'llamada'
    """
    url = f"{base_url}/contacts"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }

    data = {
        "name": phone_number,
        "phone_number": phone_number,
        "custom_attributes": {
            "lead_source": "llamada",
            "interes_en": "https://miaclinicasdelamujer.com/gynecologia",
            "es_prospecto": "1"
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        contact_data = response.json()
        contact_id = contact_data["payload"]["contact"]["id"]
        print(f"Contacto creado correctamente con ID {contact_id}.")
        return contact_id
    else:
        print(f"Error al crear el contacto: {response.status_code}")
        print(response.json())
        return None


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
        update_sql_funnel_state(contact_id, state)
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

def obtener_atributos_contacto(contact_id):
    """
    Obtiene los atributos personalizados de un contacto.
    
    :param contact_id: ID del contacto
    :return: Diccionario con los atributos personalizados, o diccionario vacío si hay error
    """
    url = f"{base_url}/contacts/{contact_id}"
    headers = {
        "api_access_token": cw_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            contact_data = response.json()
            return contact_data.get('custom_attributes', {})
        else:
            print(f"Error al obtener atributos del contacto {contact_id}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error al obtener atributos del contacto {contact_id}: {str(e)}")
        return {}