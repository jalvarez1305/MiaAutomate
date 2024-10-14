from .CW_Conversations import ChatwootSenders, envia_mensaje_plantilla, send_content_builder
from .SQL_Helpers import GetTemplateDetails, execute_query


def SendBlast(template_name, buzon: ChatwootSenders, bot_name=None, query=None,force_new=False):
    """
    Envía un mensaje en blast a los contactos obtenidos desde el resultado de la consulta,
    usando la plantilla y parámetros proporcionados.

    :param template_name: Nombre de la plantilla a utilizar.
    :param buzon: Instancia de la clase ChatwootSenders que indica el buzón (Medicos = 2, Pacientes = 4).
    :param bot_name: Nombre del bot (puede ser None).
    :param query: Consulta SQL que debe retornar un DataFrame con los contactos y sus parámetros.
    """
    # 1. Ejecutar get_template_body para obtener el body de la plantilla
    template_details = GetTemplateDetails(template_name)
    if template_details is None:
        print(f"No se encontró el body de la plantilla '{template_name}'.")
        return

    # 2. Ejecutar el query para obtener el DataFrame
    df = execute_query(query)
    if df is None or df.empty:
        print("No se obtuvieron resultados de la consulta o el resultado no es una tabla.")
        return

    # 3. Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        # 3.1 Crear la lista de parámetros sin incluir la primera columna (contacto_id)
        parametros = [str(param) for param in row[1:]]  # Ignorar la primera columna (contacto_id)

        # 4. Enviar mensaje usando la función envia_mensaje_plantilla
        contacto_id = row[0]  # Primera columna es contacto_id
        body = template_details['Body']
        envia_mensaje_plantilla(contacto_id, body, parametros, buzon, bot_name)

def send_blast_image(template_name, bot_name=None, query=None):
    """
    Envía un mensaje en blast a los contactos obtenidos desde el resultado de la consulta,
    usando la plantilla y parámetros proporcionados.

    :param content_sid: SID de la plantilla de contenido a utilizar.
    :param bot_name: Nombre del bot (puede ser None).
    :param query: Consulta SQL que debe retornar un DataFrame con los contactos y sus parámetros.
    """
    # 1. Ejecutar get_template_body para obtener el body de la plantilla
    template_details = GetTemplateDetails(template_name)  # Cambié el nombre a get_template_body para reflejar el uso correcto.
    if template_details is None:
        print(f"No se encontró el body de la plantilla '{template_name}'.")
        return

    # 2. Ejecutar el query para obtener el DataFrame
    df = execute_query(query)
    if df is None or df.empty:
        print("No se obtuvieron resultados de la consulta o el resultado no es una tabla.")
        return

    # 3. Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        # 3.1 Extraer contacto_id y teléfono
        contacto_id = row[0]  # Primera columna es contacto_id
        telefono = row[1]  # Segunda columna es el teléfono
        parametros = [str(param) for param in row[2:]]  # Restantes columnas son parámetros

        # 4. Preparar el mensaje para enviar
        text_to_send = template_details['Body']  # Inicializar con el body de la plantilla

        # 4.1 Reemplazar los parámetros en el texto
        for ii, param in enumerate(parametros, 1):
            text_to_send = text_to_send.replace(f"{{{{{ii}}}}}", param)
        content_sid=template_details['sid']
        url=template_details['url']
        # 5. Llamar a la función send_content_builder
        send_content_builder(telefono, content_sid, url, text_to_send)

        # 6. Si no hay error, llamar a la función envia_mensaje_plantilla
        envia_mensaje_plantilla(contacto_id, text_to_send, parametros, ChatwootSenders.Pacientes, bot_name,is_private=True)

    print("Mensajes enviados correctamente.")
