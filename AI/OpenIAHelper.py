import os
import openai
from openai import OpenAI


MODEL = os.getenv("EMBEDDED_MODEL")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
                Clasifica la conversación en una (y solo una) de las siguientes categorías. Evalúa las reglas en este orden:

                1. Acepto cita
                - Ya se ofreció un horario
                - El usuario lo aceptó
                - Se le pidió su nombre y lo proporcionó
                - El último mensaje es su nombre o una confirmación

                2. Acepto horario
                - Ya se ofreció un horario
                - El usuario lo aceptó
                - Aún no proporciona su nombre
                - El último mensaje es aceptación

                3. Rechazo horario
                - Ya se ofreció un horario
                - El usuario no puede tomarlo
                - El último mensaje es un rechazo claro

                4. Solicita horario con precio
                - El usuario ya resolvió dudas médicas
                - Ya preguntó y aceptó el precio
                - Aún no se ha ofrecido un horario
                - El último mensaje es una solicitud general para agendar pronto (ej: “¿Qué días atienden?”, “¿Qué día tienes citas?”, “¿Tienes disponibilidad?”, “¿Qué tienes lo más pronto?”)
                - Si el mensaje incluye una fecha específica (ej. “¿tienes el lunes?”, “¿el 15?”), clasifica como 'Otro'

                5. Solicita horario sin precio
                - Aún no se ha proporcionado precio
                - El último mensaje es una solicitud general para agendar pronto (ej: “¿Qué días atienden?”, “¿Qué día tienes citas?”, “¿Tienes disponibilidad?”, “¿Qué tienes lo más pronto?”)
                - Si el mensaje incluye una fecha específica (ej. “¿tienes el lunes?”, “¿el 15?”), clasifica como 'Otro'

                6. Dudas padecimiento
                - El último mensaje del usuario es una duda sobre sus síntomas o malestar
                - No está preguntando sobre procedimiento, ubicación ni precios

                7. Dudas procedimiento
                - El último mensaje del usuario es sobre lo que se hará en consulta o lo que incluye
                - Aún no se ha dado precio
                - Ejemplos: “¿qué me van a hacer?”, “¿incluye el papanicolaou?”

                8. Precio consulta
                - El último mensaje es una duda sobre el precio de: consulta, papanicolaou o trastornos menstruales
                - Aún no se ha dado ese precio

                9. Precio verrugas
                - El último mensaje es una duda sobre precio para verrugas
                - Aún no se ha dado ese precio

                10. Precio prenatal
                - El último mensaje es una duda sobre precio de consulta prenatal o seguimiento de embarazo
                - Aún no se ha dado ese precio

                11. Ubicación aceptada con horario ofrecido
                - Ya se proporcionó el domicilio
                - El usuario responde que le queda cerca o que conoce el lugar
                - Ya se ofreció un horario previamente
                - El último mensaje es esa validación
                - No clasifiques como “Ubicación” ni “Ubicación aceptada sin horario ofrecido”

                12. Ubicación aceptada sin horario ofrecido
                - Ya se proporcionó el domicilio
                - El usuario responde que le queda cerca o que conoce el lugar
                - Aún no se ha ofrecido ningún horario
                - El último mensaje es esa validación
                - No clasifiques como “Ubicación”

                13. Ubicación
                - El último mensaje es una pregunta sobre la ubicación de la clínica
                - Ej: “¿Dónde están ubicados?”, “¿En qué calle es?”
                - Solo si aún no se ha proporcionado el domicilio

                14. Agradecimiento
                - Ya se resolvieron las dudas o ya se confirmó la cita
                - El último mensaje es solo un agradecimiento o despedida
                - Ej: “Gracias”, “Perfecto, gracias”, “Nos vemos”, “Gracias, igualmente”

                15. Ghosted 1
                - Ya respondimos todas sus dudas
                - El usuario dejó de responder
                - No se ha enviado el mensaje: "Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"

                16. Otro
                - No entra en ninguna de las categorías anteriores
                - Pregunta por una fecha específica (aunque quiera horario)
                - Ya se dio el precio y el usuario lo vuelve a pedir
                - El mensaje es ambiguo, irrelevante o trata temas no considerados (ej. trámites, quejas, otros precios)

                Solo responde con el nombre exacto de la categoría.
                Toma en cuenta la hora de llegada de los mensajes para saber cual llego primero y cual despues
                """
    

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "system", "content": "Eres un médico que clasifica conversaciones médicas según reglas estrictas."},
            {"role": "user", "content": reglas},
            {"role": "user", "content": f"""Ahora clasifica esta conversacion: {ConvMessages}"""}
        ],
        temperature=0  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text