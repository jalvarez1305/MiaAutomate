import os
import openai
from openai import OpenAI
from datetime import date
from datetime import datetime

MODEL = os.getenv("EMBEDDED_MODEL")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gpt_model= "gpt-4o"

def get_embedding(data):
    response = openai.embeddings.create(input=data, model=MODEL)
    embedding = response.data[0].embedding
    return embedding

def conv_clasification(ConvMessages):
    """
    :param conversacion: Lista de mensajes en orden cronológico. 
                         Cada mensaje es un dict: {'rol': 'usuario'|'agente', 'contenido': str}
    :return: Una string con la categoría
    """
    reglas =   """
                Clasifica la conversación en una (y solo una) de las siguientes categorías. Evalúa las reglas en este orden estricto de prioridad:

IMPORTANTE: Antes de clasificar, verifica si alguna de estas categorías ya apareció previamente en la conversación: "Acepto cita", "Acepto horario", "Solicita horario con precio", "Precio consulta", "Ubicación aceptada con horario ofrecido", "Solicita horario sin precio", "Ubicación aceptada sin horario ofrecido", "Ubicación". Si la categoría que estás por asignar ya apareció antes, debes elegir la categoría "Otro" en su lugar.

1. Acepto cita
   - Se le pidio su nombre a el usuario
   - El usuario proporciono su nombre
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Acepto cita" y no consideres otras categorías

2. Acepto horario
   - Ya se ofrecieron horarios especificos
   - El usuario lo aceptó explícitamente alguno de los horarios propuestos
   - Aún NO ha proporcionado su nombre (o no se le ha pedido)
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Acepto horario" y no consideres otras categorías

3. Rechazo horario
   - Ya se ofreció un horario específico o dos
   - El usuario indica explícitamente que NO puede asistir en ninguno de esos horarios
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Rechazo horario" y no consideres otras categorías

4. Solicita horario con precio
   - El usuario ya ha resuelto todas sus dudas médicas previas
   - Ya preguntó por el precio Y lo aceptó o reconoció explícitamente
   - NO se ha ofrecido todavía un horario o dos
   - El último mensaje contiene una solicitud general para agendar (ej: "¿Qué días atienden?", "¿Cuál es su disponibilidad?","cuando tienen citas","Que dia tienen cita","Me parece bien","esta bien","ok","excelente","Es con cita")
   - NO incluye una fecha específica en su solicitud
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Solicita horario con precio" y no consideres otras categorías

5. Solicita horario sin precio
   - NO se ha proporcionado o discutido el precio aún
   - El último mensaje contiene una solicitud general para agendar (ej: "¿Qué días atienden?", "¿Cuál es su disponibilidad?","cuando tienen citas","Que dia tienen cita","Me parece bien","esta bien","ok","excelente","Es con cita")
   - NO incluye una fecha específica en su solicitud
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Solicita horario sin precio" y no consideres otras categorías

6. Solicita horario especifico
    - El mensaje contiene una solicitud específica para agendar (ej: "¿Tienen cita el lunes?", "¿A qué hora tienen cita el martes?", "¿Tienen disponibilidad el viernes?", "¿Tienen citas hoy?","Tienen citas disponibles para el lunes?","¿A qué hora tienen cita el martes?","¿Tienen disponibilidad el viernes?","¿Tienen citas hoy?")
    - El mensaje contiene una solicitud específica para agendar (ej: "Tienen citas disponibles para el miércoles?")
    - El usuario menciona un día específico (ej: "lunes", "martes", "hoy", "mañana")
    - El usuario menciona una fecha específica (ej: "2023-10-10", "15 de octubre")
    - El usuario menciona un rango de fechas (ej: "del 10 al 15 de octubre")
    - El usuario mensiona una semana, como la (ej: "la siguiente semana", "la proxima pasada", "la semana que viene")
    - incluye una fecha específica en su solicitud, o un dia especifico como "hoy", "mañana", "lunes", "martes", etc.
    - El ultimo mensaje es de user y no de assistant
    - Importante: No debe contener una hora, solo la fecha.
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Solicita horario especifico" y no consideres otras categorías

7. Dudas padecimiento
   - El último mensaje del usuario contiene preguntas específicas sobre sus síntomas o malestar
   - NO está preguntando sobre procedimiento, ubicación ni precios
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Dudas padecimiento" y no consideres otras categorías

8. Dudas procedimiento
   - El último mensaje del usuario es específicamente sobre lo que se hará en consulta o lo que incluye
   - NO se ha proporcionado el precio aún
   - Ejemplos: "¿qué me van a hacer?", "¿incluye el papanicolaou?"
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Dudas procedimiento" y no consideres otras categorías

9. Precio verrugas
   - Previamente se hablo sobre verrugas,condilomas
   - El último conjunto de mensajes es una pregunta explícita sobre el precio o costo 
   - NO se ha proporcionado ese precio específico antes
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio verrugas" y no consideres otras categorías

10. Precio prenatal
    - Previamente se hablo sobre embarazo, prenatal
    - El último conjunto de mensajes es una pregunta explícita sobre el precio o costo 
    - NO se ha proporcionado ese precio específico antes
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio prenatal" y no consideres otras categorías

11. Precio menopausia
    - Previamente se hablo sobre menopausia, pre menopausia, climaterio o perimenopausia
    - El último conjunto de mensajes es una pregunta explícita sobre el precio o costo 
    - NO se ha proporcionado ese precio específico antes
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio prenatal" y no consideres otras categorías

12. Precio consulta
   - El último conjunto de mensajes es una pregunta explícita sobre el precio o costo 
   - NO se ha proporcionado ese precio específico antes
   - NO está preguntando por precios de verrugas o consulta prenatal
   - Aun no se le proporciona un precio
   - Puede contener frases como ("revisión ginecólogica anual","Revision anual","Cheque anual","Que incluye","Que paquetes tienen")
   - El ultimo mensaje es de user y no de assistant
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio consulta" y no consideres otras categorías

13. Ubicación aceptada con horario ofrecido
    - Ya se proporcionó el domicilio completo
    - El usuario responde que le queda cerca o que conoce el lugar
    - Ya se ofreció un horario específico previamente
    - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
    - El ultimo mensaje es de user y no de assistant
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada con horario ofrecido" y no consideres las categorías "Ubicación" ni "Ubicación aceptada sin horario ofrecido"

14. Ubicación aceptada sin horario ofrecido
    - Ya se proporcionó el domicilio completo
    - El usuario responde que le queda cerca o que conoce el lugar
    - NO se ha ofrecido ningún horario específico aún
    - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
    - El ultimo mensaje es de user y no de assistant
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada sin horario ofrecido" y no consideres la categoría "Ubicación"

15. Ubicación
    - El último mensaje contiene una pregunta explícita sobre la ubicación física de la clínica
    - Ejemplos: "¿Dónde están ubicados?", "¿En qué calle es?", "¿Cuál es la dirección?"
    - en la conversacion NO le hemos mandado el domicilio, que es en avenida Tonaltecas
    - El ultimo mensaje es de user y no de assistant
    - No debe tener frases como ("Me queda lejos", "Estoy lejos", "Esta lejos")
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación" y no consideres otras categorías

16. Agradecimiento
    - Ya se resolvieron todas las dudas del usuario o ya se confirmó completamente la cita
    - El último mensaje contiene exclusivamente un agradecimiento o despedida
    - Ejemplos: "Gracias", "Perfecto, gracias", "Nos vemos", "Gracias, igualmente"
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Agradecimiento" y no consideres otras categorías

17. Otro
    - La conversación NO encaja en ninguna de las categorías anteriores, incluyendo:
    - Ya se proporcionó el precio y el usuario lo vuelve a solicitar
    - El mensaje es ambiguo, irrelevante o trata temas no considerados (ej. trámites, quejas, otros servicios)
    - Se intenta clasificar en una categoría que ya apareció previamente en la conversación (de la lista mencionada al principio)
    - IMPORTANTE: Utiliza esta categoría SOLO si ninguna de las anteriores aplica o si la categoría adecuada ya fue utilizada antes

Solo responde con el nombre exacto de la categoría.
Toma en cuenta la hora de llegada de los mensajes para determinar el orden cronológico de la conversación.
Revisa el historial completo de la conversación para verificar si alguna categoría ya fue asignada previamente, especialmente: "Acepto cita", "Acepto horario", "Solicita horario con precio", "Precio consulta", "Ubicación aceptada con horario ofrecido", "Solicita horario sin precio", "Ubicación aceptada sin horario ofrecido", "Ubicación".
                """
    

    response = client.responses.create(
        model=gpt_model,
        input=[
            {"role": "system", "content": "Eres un médico que clasifica conversaciones médicas según reglas estrictas."},
            {"role": "user", "content": reglas},
            {"role": "user", "content": f"""Ahora clasifica esta conversacion: {ConvMessages}"""}
        ],
        temperature=0  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text


def conv_close_sale(ConvMessages):
    """
    :param conversacion: Lista de mensajes en orden cronológico. 
                         Cada mensaje es un dict: {'rol': 'usuario'|'agente', 'contenido': str}
    :return: Una Bool que indica si se cerro la venta o no
    """
    reglas =   """
                Clasifica la conversación en True o False dependiendo si se cerro la venta o no
                Para que una venta este cerrada debe cumplir estos criterios
                - Se le ofrecio un horario
                - El usuario acepto el horario
                - Se le pidio su nombre
                - EL usuario nos dio su nombre
                Solo responde True o False.
                """
    

    response = client.responses.create(
        model=gpt_model,
        input=[
            {"role": "system", "content": "Eres un médico que clasifica conversaciones médicas según reglas estrictas."},
            {"role": "user", "content": reglas},
            {"role": "user", "content": f"""Ahora clasifica esta conversacion: {ConvMessages}"""}
        ],
        temperature=0  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text

def get_requested_date(ConvMessages):
    """
    Extrae la fecha solicitada por el usuario desde una lista de mensajes de conversación.

    :param ConvMessages: Lista de mensajes en orden cronológico.
                         Cada mensaje es un dict con las llaves: {'rol': 'usuario'|'agente', 'contenido': str}
    :return: Una fecha exacta en formato 'YYYY-MM-DD' que representa el día solicitado por el usuario.
    """

    mensajes_usuario = obtener_ultimos_mensajes_usuario(ConvMessages)
    user_question = "\n".join([msg["contenido"] for msg in mensajes_usuario])
    hoy = datetime.today().strftime('%Y-%m-%d')

    reglas = f"""
                Eres un asistente que interpreta mensajes en español y extrae la fecha solicitada por el usuario en formato YYYY-MM-DD.

                Fecha actual: {hoy}

                Reglas para identificar la fecha solicitada:

                1. Si el usuario dice palabras como "hoy", "para hoy", "el día de hoy" o similares, devuelve la fecha actual: {hoy}.

                2. Si el usuario menciona "la siguiente semana", "la próxima semana" o expresiones similares, devuelve el **martes** de la próxima semana (no esta), en formato YYYY-MM-DD.

                3. Si el usuario menciona un día de la semana (por ejemplo: "el sábado", "este viernes", "para el domingo"), devuelve la **fecha más cercana en el futuro** que caiga en ese día, en formato YYYY-MM-DD.

                4. Si el usuario escribe una fecha explícita en formato YYYY-MM-DD (por ejemplo: "2023-10-10"), simplemente devuelve esa fecha.

                5. Si el usuario menciona un número de día sin mes (por ejemplo: "el 15", "para el 28", "día 7"), devuelve la **próxima fecha futura** que coincida con ese número, ya sea del mes actual (si aún no ha pasado) o del siguiente mes.

                6. Si no se puede determinar una fecha con claridad, devuelve exactamente: None

                Formato de respuesta:
                Devuelve únicamente la fecha en formato YYYY-MM-DD o None, sin agregar ningún otro texto o explicación.
                """

    response = client.responses.create(
        model=gpt_model,
        input=[
            {"role": "system", "content": "Eres un asistente que interpreta solicitudes de fechas escritas en español y devuelve únicamente una fecha en formato YYYY-MM-DD."},
            {"role": "user", "content": reglas},
            {"role": "user", "content": f"Aquí están los últimos mensajes del usuario solicitando la fecha:\n{user_question}"}
        ],
        temperature=0  # Respuesta más determinística
    )

    return response.output_text

def obtener_ultimos_mensajes_usuario(mensajes):
    """
    Obtiene todos los mensajes del usuario desde la última vez que el asistente escribió.
    
    Args:
        mensajes: Una lista de diccionarios con la estructura especificada
        
    Returns:
        Una lista con los últimos mensajes del usuario
    """
    ultimos_mensajes = []
    
    # Recorremos la lista de mensajes en orden inverso (del más reciente al más antiguo)
    for i in range(len(mensajes) - 1, -1, -1):
        mensaje = mensajes[i]
        
        # Si encontramos un mensaje del asistente, terminamos la búsqueda
        if mensaje["role"] == "assistant":
            break
        
        # Si el mensaje es del usuario, lo agregamos a nuestra lista
        if mensaje["role"] == "user":
            ultimos_mensajes.append(mensaje)
    
    # Invertimos la lista para mantener el orden cronológico original
    return ultimos_mensajes[::-1]