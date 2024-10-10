from PyLibrary.SQL_Helpers import get_template_body, execute_query
from PyLibrary.CW_Conversations import envia_mensaje_plantilla, ChatwootSenders

def SendBlast(template_name, buzon: ChatwootSenders, bot_name=None, query=None):
    """
    Envía un mensaje en blast a los contactos obtenidos desde el resultado de la consulta,
    usando la plantilla y parámetros proporcionados.

    :param template_name: Nombre de la plantilla a utilizar.
    :param buzon: Instancia de la clase ChatwootSenders que indica el buzón (Medicos = 2, Pacientes = 4).
    :param bot_name: Nombre del bot (puede ser None).
    :param query: Consulta SQL que debe retornar un DataFrame con los contactos y sus parámetros.
    """
    # 1. Ejecutar get_template_body para obtener el body de la plantilla
    body = get_template_body(template_name)
    if body is None:
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
        envia_mensaje_plantilla(contacto_id, body, parametros, buzon, bot_name)