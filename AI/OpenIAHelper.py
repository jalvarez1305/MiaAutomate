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
    if not ConvMessages or ConvMessages[-1]["role"] != "user":
        return "Ultimo Mensaje no es del usuario"
    
    mensajes_usuario = obtener_ultimos_mensajes_usuario(ConvMessages)
    bloque_reciente_usuario = "\n".join([msg["content"] for msg in mensajes_usuario])
    
    reglas =   """
                Clasifica la conversación en una (y solo una) de las siguientes categorías. Evalúa las reglas en este orden estricto de prioridad:

1. Acepto cita
   # EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Se le pidió su nombre al usuario anteriormente
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - El usuario proporciono su nombre
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Acepto cita" y no consideres otras categorías

2. Acepto horario
   # EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### AL MENOS UNA DE ESTAS:
   - El usuario NO ha proporcionado su nombre en ningún mensaje anterior de la conversación.
   - El agente no ha solicitado su nombre en ningún mensaje anterior de la conversación.  
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - El usuario lo aceptó explícitamente alguno de los horarios propuestos
   ### EJEMPLOS:
   - La aceptacion puede tener forma de "El de la mañana me parece bien", "El de la tarde me parece bien", "Me parece bien el horario de la mañana", "Me parece bien el horario de la tarde"
   - La aceptacion puede ser repitiendo el horario ofrecido, como "Me parece bien el lunes a las 10:00 am", "Me parece bien el martes a las 4:00 pm"
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Acepto horario" y no consideres otras categorías

3. Dudas padecimiento
   # EVALUACIÓN: RECENT_ONLY
   ### TODAS ESTAS:
   - El último mensaje del usuario contiene preguntas específicas sobre sus síntomas o malestar
   - NO está preguntando sobre procedimiento
   - NO esta preguntando sobre ubicacion
   - No esta preguntando sobre precios
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Dudas padecimiento" y no consideres otras categorías

4. Rechazo horario
   # EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### AL MENOS UNA DE ESTAS:
   - Ya se ofreció un horario específico
   - Se ofrecio mas de un horario
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### AL MENOS UNA DE ESTAS:
   - El usuario indica explícitamente que NO puede asistir en ninguno de esos horarios
   - El usuario NO esta proponiendo un nuevo horario
   - El usuario NO esta proponiendo una nueva fecha
   - El usuario NO esta proponiendo una nueva semana
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Rechazo horario" y no consideres otras categorías

5. Solicita horario con precio
   # EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - El usuario ya ha resuelto todas sus dudas médicas previas
   - Ya preguntó por el precio
   - El usuario ya acepto el precio o lo reconocio
   - NO se ha ofrecido todavía un horario o mas de uno
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:   
   ### TODAS ESTAS:
   - Contiene una solicitud general para agendar
   - NO incluye una fecha específica en su solicitud
   ### EJEMPLOS:
   - ¿Qué días atienden?
   - ¿Cuál es su disponibilidad?
   - cuando tienen citas
   - Que dia tienen cita
   - Me parece bien
   - esta bien
   - ok
   - excelente
   - Es con cita
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Solicita horario con precio" y no consideres otras categorías

6. Solicita horario sin precio
   # EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - NO se ha proporcionado o discutido el precio aún
   - NO incluye una fecha específica en su solicitud
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - Contiene una solicitud general para agendar
   - NO debe mencionar ninguna fecha, día, semana ni rango de fechas.
   ### EJEMPLOS:
   - ¿Qué días atienden?
   - ¿Cuál es su disponibilidad?
   - cuando tienen citas
   - Que dia tienen cita
   - Me parece bien
   - esta bien
   - ok
   - excelente
   - Es con cita
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Solicita horario sin precio" y no consideres otras categorías

7. Solicita horario especifico
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - El usuario no ha aceptado ya un horario propuesto
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - No debe contener una hora.
   ### AL MENOS UNA DE ESTAS:
   - El mensaje contiene una solicitud específica para agendar
   - El usuario menciona un día específico (ej: "lunes", "martes", "hoy", "mañana")
   - El usuario menciona una fecha específica (ej: "2023-10-10", "15 de octubre")
   - El usuario menciona un rango de fechas (ej: "del 10 al 15 de octubre")
   - El usuario mensiona una semana, como la (ej: "la siguiente semana", "la proxima pasada", "la semana que viene")
   - El usuario menciona día, fecha, semana o rango temporal (ej. “lunes”, “mañana”, “la semana que viene”, “15 de octubre”)
   - incluye una fecha específica en su solicitud, o un dia especifico como "hoy", "mañana", "lunes", "martes", etc.  ### EJEMPLOS:
   - ¿Tienen cita el lunes?
   - ¿A qué hora tienen cita el martes?
   - ¿Tienen disponibilidad el viernes?
   - ¿Tienen citas hoy?
   - Tienen citas disponibles para el lunes?
   - ¿A qué hora tienen cita el martes?
   - ¿Tienen disponibilidad el viernes?
   - ¿Tienen citas hoy?
   - Tienen citas disponibles para el miércoles?
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Solicita horario especifico" y no consideres otras categorías

8. Dudas procedimiento
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - NO se ha proporcionado el precio aún
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - Es específicamente sobre lo que se hará en consulta o lo que incluye   
   ### EJEMPLOS:
   - ¿qué me van a hacer?
   - ¿incluye el papanicolaou?
   - ¿Que incluye?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Dudas procedimiento" y no consideres otras categorías

9. Precio verrugas
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Cuando se hablo de padecimiento, se mencionó específicamente verrugas
   - NO se ha proporcionado precio aún
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:   
   ### TODAS ESTAS:
   - El usuario pregunta explícitamente sobre el precio o costo   
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio verrugas" y no consideres otras categorías

10. Precio prenatal
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Cuando se hablo de padecimiento, se mencionó específicamente embarazo o prenatal
   - NO se ha proporcionado precio aún
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:   
   ### TODAS ESTAS:
   - El usuario pregunta explícitamente sobre el precio o costo
   ### EJEMPLOS:
   - Que incluye
   - Que paquetes tienen
   - ¿Cuánto cuesta?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio prenatal" y no consideres otras categorías

11. Precio menopausia
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - NO se ha proporcionado precio aún
   ### AL MENOS UNA DE ESTAS:
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia
   - Cuando se hablo de padecimiento, se mencionó específicamente climaterio
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia precoz
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia temprana
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia tardía
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia prematura
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia artificial
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia quirúrgica
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia inducida
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia natural
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia fisiológica
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia biológica
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia hormonal
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia sintomática
   - Cuando se hablo de padecimiento, se mencionó específicamente menopausia asintomática
   - Cuando se hablo de padecimiento, se mencionó específicamente perimenopausia
   - Cuando se hablo de padecimiento, se mencionó específicamente premenopausia
   - Incluye el texto exacto "Dame un segundito para platicarte de las opciones que manejamos, por favor 🙌"
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:   
   - El usuario pregunta explícitamente sobre el precio o costo
   ### EJEMPLOS:
   - Que incluye
   - Cuanto cuesta
   ## NOTA IMPORTANTE:    
    - Si cumple estas condiciones, clasifica SOLO como "Precio menopausia" y no consideres otras categorías

12. Precio consulta
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Aun no se le proporciona un precio
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - El último mensaje es una pregunta explícita sobre el precio o costo
   ### EJEMPLOS:
   - revisión ginecólogica anual
   - Revision anual
   - Cheque anual
   - Que incluye
   - Que paquetes tienen
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio consulta" y no consideres otras categorías

13. Ubicación aceptada con horario ofrecido
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Ya se proporcionó el domicilio completo
   - Ya se ofreció un horario específico previamente
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### AL MENOS UNA DE ESTAS:
   - El usuario responde que le queda cerca o que conoce el lugar
   - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada con horario ofrecido" y no consideres otras categorías

14. Ubicación aceptada sin horario ofrecido
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Ya se proporcionó el domicilio completo
   - NO se ha ofrecido ningún horario específico aún
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### AL MENOS UNA DE ESTAS:
   - El usuario responde que le queda cerca o que conoce el lugar
   - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada sin horario ofrecido" y no consideres otras categorías

15. Ubicación
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - No se ha proporcionado la ubicacion aún
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - El usuario hace una pregunta explícita sobre la ubicación física de la clínica
   ### EJEMPLOS:
   - El usuario pregunta por la dirección, calle o ubicación de la clínica
   - ¿Dónde están ubicados?
   - ¿En qué calle es?
   - ¿Cuál es la dirección?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Ubicación" y no consideres otras categorías

16. Agradecimiento
   #EVALUACIÓN: INCLUDE_HISTORY
   ## Condiciones que deben haberse cumplido en el historial:
   ### TODAS ESTAS:
   - Ya se resolvieron todas las dudas del usuario o ya se confirmó completamente la cita
   ## Condiciones que deben cumplirse SOLO en los mensajes recientes del usuario:
   ### TODAS ESTAS:
   - El usuario esta agradeciendoo despidiendose
   ### EJEMPLOS:
   - Gracias
   - Perfecto
   - gracias
   - Nos vemos
   - Gracias
   - igualmente
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Agradecimiento" y no consideres otras categorías

17. Otro
   ## Condiciones para clasificar como "Otro":
   ### AL MENOS UNA DE ESTAS:
   - La conversación NO encaja en ninguna de las categorías anteriores.
   - Ya se proporcionó el precio y el usuario lo vuelve a solicitar.
   - El mensaje es ambiguo, irrelevante o trata temas no considerados (ej. trámites, quejas, otros servicios).
   - Se intenta clasificar en una categoría que ya apareció previamente en la conversación (de la lista mencionada al principio).
   ### IMPORTANTE:
   - Utiliza esta categoría SOLO si ninguna de las anteriores aplica o si la categoría adecuada ya fue utilizada antes.

Solo responde con el nombre exacto de la categoría.
Toma en cuenta la hora de llegada de los mensajes para determinar el orden cronológico de la conversación.
Revisa el historial completo de la conversación para verificar si alguna categoría ya fue asignada previamente, especialmente: "Acepto cita", "Acepto horario", "Solicita horario con precio", "Precio consulta", "Ubicación aceptada con horario ofrecido", "Solicita horario sin precio", "Ubicación aceptada sin horario ofrecido", "Ubicación".
                """
    conversacion_formateada = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in ConvMessages])

    response = client.responses.create(
        model=gpt_model,
        input=[
            {
                "role": "system",
                "content": "Eres un médico ginecólogo que sabe mucho sobre el ciclo menstrual y clasifica conversaciones médicas según reglas estrictas."
            },
            {
                "role": "user",
                "content": f"Estas son las reglas:\n\n{reglas}"
            },
            {
                "role": "user",
                "content": f"""Clasifica esta conversación enfocándote principalmente en los mensajes recientes del usuario desde la última intervención del agente:\n\n{bloque_reciente_usuario}\n\nTambién considera el historial completo de la conversación por si alguna categoría requiere contexto previo:\n\n{conversacion_formateada}"""
            }
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
    user_question = "\n".join([msg["content"] for msg in mensajes_usuario])
    print(f"user_question: {user_question}")
    hoy = datetime.today().strftime('%Y-%m-%d')

    reglas = f"""
                Eres un asistente que interpreta mensajes en español y extrae la fecha solicitada por el usuario en formato YYYY-MM-DD.

                Fecha actual: {hoy}

                Reglas para identificar la fecha solicitada:

                1. Si el usuario dice palabras como "hoy", "para hoy", "el día de hoy" o similares, devuelve la fecha actual: {hoy}.

                2. Si el usuario menciona "la siguiente semana", "la próxima semana" o expresiones similares, devuelve el **martes** de la próxima semana (no esta), en formato YYYY-MM-DD.

                3. Si el usuario menciona un día de la semana (por ejemplo: "sábado", "viernes", "domingo"), devuelve la **fecha más cercana en el futuro** que caiga en ese día, en formato YYYY-MM-DD.

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