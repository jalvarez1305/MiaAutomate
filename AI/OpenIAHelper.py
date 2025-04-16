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
    reglas = """
                Clasifica la conversación en una (y solo una) de las siguientes categorías:

                1. Acepto cita
                - Ya se ofreció un horario
                - El usuario lo aceptó
                - Se le pidió su nombre y lo proporcionó
                - El último mensaje del usuario es el nombre o una confirmación

                2. Acepto horario
                - Ya se ofreció un horario
                - El usuario lo aceptó
                - Aún no proporciona su nombre
                - El último mensaje es aceptación

                3. Rechazo horario
                - Ya se ofreció un horario
                - El usuario no puede tomarlo
                - El último mensaje es un rechazo claro

                4. Solicita horario
                - El usuario ya resolvió dudas médicas
                - Ya preguntó precio y aceptó
                - El último mensaje es una pregunta por disponibilidad
                - No se ha dado un horario aún

                5. Dudas padecimiento
                - El último mensaje es sobre síntomas o malestar
                - No habla de procedimiento ni precios

                6. Dudas procedimiento
                - El último mensaje es sobre lo que se hará en consulta o lo que incluye
                - Aún no se ha dado el precio

                7. Precio consulta
                - El último mensaje es duda sobre precio de: consulta, papanicolaou o trastornos menstruales
                - Aún no se dio ese precio

                8. Precio verrugas
                - El último mensaje es duda sobre precio para verrugas
                - Aún no se dio ese precio

                9. Precio prenatal
                - El último mensaje es duda sobre precio de consulta prenatal
                - Aún no se dio ese precio

                10. Ghosted 1
                    - Ya respondimos todas sus dudas
                    - El usuario dejó de responder
                    - No se envió el mensaje "Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"

                11. Otro
                    - No entra en ninguna de las anteriores
                    - O se repitió el precio ya dado
                    - O el mensaje es ambiguo o irrelevante

                Clasifica exclusivamente en una de estas categorías, basándote en el último mensaje y el contexto anterior.
                Responde únicamente con el nombre de la categoría.
                """
    mensajes_sistema = [
        {"role": "system", "content": "Eres un médico que clasifica conversaciones médicas según reglas estrictas."},
        {"role": "user", "content": reglas}
    ]
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