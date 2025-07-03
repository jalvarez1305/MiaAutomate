import math
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))

from CW_Conversations import ChatwootSenders, envia_mensaje_plantilla
from SQL_Helpers import GetTemplateDetails, execute_query


def SendBlast(template_id, bot_name, query,etiqueta=None):
    """
    Envía un mensaje en blast a los contactos obtenidos desde el resultado de la consulta,
    usando la plantilla y parámetros proporcionados.

    :param template_id: Nombre de la plantilla a utilizar.
    :param bot_name: Nombre del bot (puede ser None).
    :param query: Consulta SQL que debe retornar un DataFrame con los contactos y sus parámetros, contacto ->0 telefono ->1, parametros.
    """
    # 1. Ejecutar get_template_body para obtener el body de la plantilla
    template_details = GetTemplateDetails(template_id)
    if template_details is None:
        print(f"No se encontró el body de la plantilla '{template_id}'.")
        return

    # 2. Ejecutar el query para obtener el DataFrame
    df = execute_query(query)
    if df is None or df.empty:
        print("No se obtuvieron resultados de la consulta o el resultado no es una tabla.")
        return

    # 3. Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        # 3.1 Crear la lista de parámetros sin incluir la primera columna (contacto_id)
        parametros = [str(param) for param in row[2:]]  # Ignorar la primera columna (contacto_id) y la segunda Telefono

        # 4. Enviar mensaje usando la función envia_mensaje_plantilla
        contacto_id = row[0]  # Primera columna es contacto_id
        phone_number = row[1]  # La segunda columna siempre debe ser el telefono
        if not math.isnan(contacto_id):
            envia_mensaje_plantilla(contacto_id=contacto_id,phone_number=phone_number, content_sid=template_id, parametros=parametros, buzon=ChatwootSenders.Pacientes, bot_name=bot_name,force_new=False,etiqueta=etiqueta)
            time.sleep(1)