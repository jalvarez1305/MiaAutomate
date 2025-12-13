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
                Clasifica la conversación en una (y solo una) de las siguientes categorías.
                Evalua cada regla considerando que se cumplan las condiciones de el historial y tambien las del ultimo mensaje del usuario 
                Evalúa las reglas en este orden estricto de prioridad:

1. Acepto cita
   # EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Se le pidió su nombre al usuario
   ## EVALUAR ESTAS REGLAS EN EL ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario proporciono su nombre
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Acepto cita" y no consideres otras categorías

2. Acepto horario
   # EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:
   - El usuario NO ha proporcionado su nombre.
   - El agente no ha solicitado su nombre.  
   ## EVALUAR ESTAS REGLAS EN EL ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario lo aceptó explícitamente alguno de los horarios propuestos
   #### EJEMPLOS:
   - La aceptacion puede tener forma de "El de la mañana me parece bien", "El de la tarde me parece bien", "Me parece bien el horario de la mañana", "Me parece bien el horario de la tarde"
   - La aceptacion puede ser repitiendo el horario ofrecido, como "Me parece bien el lunes a las 10:00 am", "Me parece bien el martes a las 4:00 pm"   
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Acepto horario" y no consideres otras categorías

3. Dudas padecimiento
   # EVALUACIÓN: RECENT_ONLY
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Contiene preguntas específicas sobre sus síntomas o malestar
   - NO está preguntando sobre procedimiento
   - NO esta preguntando sobre ubicacion
   - No esta preguntando sobre precios
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Dudas padecimiento" y no consideres otras categorías

4. Rechazo horario
   # EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:
   - Ya se ofreció un horario específico
   - Se ofrecio mas de un horario
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario indica explícitamente que NO puede asistir en ninguno de esos horarios
   - El usuario NO esta proponiendo un nuevo horario
   - El usuario NO esta proponiendo una nueva fecha
   - El usuario NO esta proponiendo una nueva semana
   ## NOTA IMPORTANTE: 
   - Si cumple estas condiciones, clasifica SOLO como "Rechazo horario" y no consideres otras categorías

5. Solicita horario con precio
   # EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario ya ha resuelto todas sus dudas médicas previas
   - Ya preguntó por el precio
   - El usuario ya acepto el precio o lo reconocio
   - NO se ha ofrecido todavía un horario o mas de uno
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Contiene una solicitud general para agendar
   - NO incluye una fecha específica en su solicitud
   #### EJEMPLOS:
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
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - NO se ha proporcionado o discutido el precio aún
   - NO incluye una fecha específica en su solicitud
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Contiene una solicitud general para agendar
   - NO debe mencionar ninguna fecha, día, semana ni rango de fechas.
   #### EJEMPLOS:
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
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario no ha aceptado ya un horario propuesto
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - No debe contener una hora.
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA ESTAS CONDICIONES:
   - El mensaje contiene una solicitud específica para agendar
   - El usuario menciona un día específico (ej: "lunes", "martes", "hoy", "mañana")
   - El usuario menciona una fecha específica (ej: "2023-10-10", "15 de octubre")
   - El usuario menciona un rango de fechas (ej: "del 10 al 15 de octubre")
   - El usuario menciona una semana, como la (ej: "la siguiente semana", "la proxima semana", "la semana que viene")
   - El usuario menciona día, fecha, semana o rango temporal (ej. “lunes”, “mañana”, “la semana que viene”, “15 de octubre”)
   - incluye una fecha específica en su solicitud, o un dia especifico como "hoy", "mañana", "lunes", "martes", etc.  
   #### EJEMPLOS:
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
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - NO se ha proporcionado el precio aún
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Habla específicamente sobre lo que se hará en consulta o lo que incluye   
   #### EJEMPLOS:
   - ¿qué me van a hacer?
   - ¿incluye el papanicolaou?
   - ¿Que incluye?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Dudas procedimiento" y no consideres otras categorías

9. Precio verrugas
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Cuando se hablo de padecimiento, se mencionó específicamente verrugas
   - NO se ha proporcionado precio aún
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario pregunta explícitamente sobre el precio o costo   
   #### EJEMPLOS:
   - Que incluye
   - Que paquetes tienen
   - ¿Cuánto cuesta?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio verrugas" y no consideres otras categorías

10. Precio prenatal
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Cuando se hablo de padecimiento, se mencionó específicamente embarazo o prenatal
   - NO se ha proporcionado precio aún
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - El usuario pregunta explícitamente sobre el precio o costo
   #### EJEMPLOS:
   - Que incluye
   - Que paquetes tienen
   - ¿Cuánto cuesta?
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio prenatal" y no consideres otras categorías

11. Precio menopausia
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - NO se ha proporcionado precio aún
   ### CLASIFICAR EN ESTA CATEGORIA SI AL MENOS UNA DE ESTAS CONDICIONES:
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
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:  
   - El usuario pregunta explícitamente sobre el precio o costo
   #### EJEMPLOS:
   - Que incluye
   - Cuanto cuesta
   - Que precio tiene
   ## NOTA IMPORTANTE:    
    - Si cumple estas condiciones, clasifica SOLO como "Precio menopausia" y no consideres otras categorías

12. Precio consulta
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Aun no se le proporciona un precio
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:  
   - El último mensaje es una pregunta explícita sobre el precio o costo
   #### EJEMPLOS:
   - revisión ginecólogica anual
   - Revision anual
   - Cheque anual
   - Que incluye
   - Que paquetes tienen
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Precio consulta" y no consideres otras categorías

13. Ubicación aceptada con horario ofrecido
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Ya se proporcionó el domicilio completo
   - Ya se ofreció un horario específico previamente
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:  
   - El usuario responde que le queda cerca o que conoce el lugar
   - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
   #### EJEMPLOS:
   - El usuario dice que le queda cerca
   - El usuario dice que conoce el lugar
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada con horario ofrecido" y no consideres otras categorías

14. Ubicación aceptada sin horario ofrecido
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Ya se proporcionó el domicilio completo
   - NO se ha ofrecido ningún horario específico aún
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:  
   - El usuario responde que le queda cerca o que conoce el lugar
   - El usuario expresa esta confirmación de conocimiento/aceptación de ubicación
   #### EJEMPLOS:
   - El usuario dice que le queda cerca
   - El usuario dice que conoce el lugar
   ## NOTA IMPORTANTE: 
    - Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada sin horario ofrecido" y no consideres otras categorías

15. Ubicación
   #EVALUACIÓN: INCLUDE_HISTORY
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - No se ha proporcionado la ubicacion aún
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:  
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
   ## EVALUAR ESTAS REGLAS EN EL HISTORIAL:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:
   - Ya se resolvieron todas las dudas del usuario o ya se confirmó completamente la cita
   ## EVALUAR ESTAS REGLAS EN ULTIMO MENSAJE DEL USUARIO:
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE TODAS ESTAS CONDICIONES:  
   - El usuario esta agradeciendoo despidiendose
   #### EJEMPLOS:
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
   ### CLASIFICAR EN ESTA CATEGORIA SI CUMPLE AL MENOS UNA DE ESTAS CONDICIONES:
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
                "content": f"""Este es el hisotrial de la conversacion para su analisis:\n\n{conversacion_formateada}"""
            },
            {
                "role": "user",
                "content": f"""Este es el ultimo mensaje del usuario:\n\n{bloque_reciente_usuario}"""
            },
            {
                "role": "user",
                "content": f"""Internaliza primero el historial de la conversacion para que tengas contexto, 
                                luego entiende el ultimo mensaje del usuario para que entiendas que esta preguntando en este momento 
                                y por ultimo evalua las reglas"""
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

def clasificar_conversacion(ConvMessages):
    """
    Clasifica una conversación en una de tres categorías: Ventas, Citas, o Soporte.
    
    :param ConvMessages: Lista de mensajes de la conversación
    :return: String con la clasificación: "Ventas", "Citas", o "Soporte"
    """
    if not ConvMessages:
        return "Soporte"
    
    # Construir el contexto de la conversación
    conversacion_texto = "\n".join([
        f"{'Agente' if msg['role'] == 'assistant' else 'Paciente'}: {msg.get('content', '')}"
        for msg in ConvMessages
    ])
    
    prompt = f"""Analiza la siguiente conversación y clasifícala en UNA de estas tres categorías:
- Ventas: Si la conversación se trata de vender un servicio, procedimiento, o producto
- Citas: Si la conversación trata sobre horarios, logística de citas, confirmación de citas, o disponibilidad
- Soporte: Si es un paciente buscando indicaciones, información médica general, o cualquier otra consulta que no sea venta ni citas

Conversación:
{conversacion_texto}

Responde SOLO con una palabra: Ventas, Citas, o Soporte"""

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": "Eres un clasificador de conversaciones. Responde solo con una palabra: Ventas, Citas, o Soporte."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=10
        )
        
        clasificacion = response.choices[0].message.content.strip()
        
        # Validar que la respuesta sea una de las categorías esperadas
        if clasificacion not in ["Ventas", "Citas", "Soporte"]:
            # Si no es válida, intentar extraer la palabra correcta
            clasificacion_lower = clasificacion.lower()
            if "venta" in clasificacion_lower:
                return "Ventas"
            elif "cita" in clasificacion_lower:
                return "Citas"
            else:
                return "Soporte"
        
        return clasificacion
    except Exception as e:
        print(f"Error en clasificación: {e}")
        return "Soporte"

def analizar_sentimiento(ConvMessages):
    """
    Analiza el sentimiento del paciente en la conversación y retorna un score del 1 al 10.
    
    :param ConvMessages: Lista de mensajes de la conversación
    :return: Float entre 1 y 10, donde 10 es muy feliz/satisfecho
    """
    if not ConvMessages:
        return 5.0
    
    # Filtrar solo mensajes del paciente
    mensajes_paciente = [
        msg.get('content', '') 
        for msg in ConvMessages 
        if msg.get('role') == 'user'  # En get_AI_conversation_messages, 'user' es el paciente
    ]
    
    if not mensajes_paciente:
        return 5.0
    
    conversacion_paciente = "\n".join(mensajes_paciente)
    
    prompt = f"""Analiza el sentimiento y nivel de satisfacción del paciente en esta conversación.
Evalúa qué tan feliz, satisfecho o contento está el paciente basándote en su tono, palabras, y expresiones.

Mensajes del paciente:
{conversacion_paciente}

Califica del 1 al 10, donde:
- 1-3: Muy insatisfecho, molesto, frustrado
- 4-5: Neutral, indiferente
- 6-7: Satisfecho, contento
- 8-10: Muy feliz, muy satisfecho, entusiasta

Responde SOLO con un número del 1 al 10 (puede ser decimal como 7.5)."""

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": "Eres un analista de sentimientos. Responde solo con un número del 1 al 10."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=5
        )
        
        score_text = response.choices[0].message.content.strip()
        
        # Extraer el número
        try:
            score = float(score_text)
            # Asegurar que esté en el rango 1-10
            score = max(1.0, min(10.0, score))
            return score
        except ValueError:
            # Si no se puede convertir, buscar un número en el texto
            import re
            numbers = re.findall(r'\d+\.?\d*', score_text)
            if numbers:
                score = float(numbers[0])
                return max(1.0, min(10.0, score))
            return 5.0
    except Exception as e:
        print(f"Error en análisis de sentimiento: {e}")
        return 5.0