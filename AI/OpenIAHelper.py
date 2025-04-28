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
                Clasifica la conversación en una (y solo una) de las siguientes categorías. Evalúa las reglas en este orden estricto de prioridad:

IMPORTANTE: Antes de clasificar, verifica si alguna de estas categorías ya apareció previamente en la conversación: "Acepto cita", "Acepto horario", "Solicita horario con precio", "Precio consulta", "Ubicación aceptada con horario ofrecido", "Solicita horario sin precio", "Ubicación aceptada sin horario ofrecido", "Ubicación". Si la categoría que estás por asignar ya apareció antes, debes elegir la categoría "Otro" en su lugar.

1. Acepto cita
   - Ya se ofreció un horario específico
   - El usuario lo aceptó explícitamente
   - Se le pidió su nombre y lo proporcionó
   - El último mensaje es su nombre o una confirmación final
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Acepto cita" y no consideres otras categorías

2. Acepto horario
   - Ya se ofreció un horario específico
   - El usuario lo aceptó explícitamente
   - Aún NO ha proporcionado su nombre (o no se le ha pedido)
   - El último mensaje muestra aceptación del horario propuesto
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Acepto horario" y no consideres otras categorías

3. Rechazo horario
   - Ya se ofreció un horario específico
   - El usuario indica explícitamente que NO puede asistir en ese horario
   - El último mensaje contiene un rechazo claro del horario propuesto
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Rechazo horario" y no consideres otras categorías

4. Solicita horario con precio
   - El usuario ya ha resuelto todas sus dudas médicas previas
   - Ya preguntó por el precio Y lo aceptó o reconoció explícitamente
   - NO se ha ofrecido todavía un horario específico
   - El último mensaje contiene una solicitud general para agendar (ej: "¿Qué días atienden?", "¿Cuál es su disponibilidad?")
   - NO incluye una fecha específica en su solicitud
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Solicita horario con precio" y no consideres otras categorías

5. Solicita horario sin precio
   - NO se ha proporcionado o discutido el precio aún
   - El último mensaje contiene una solicitud general para agendar (ej: "¿Qué días atienden?", "¿Cuál es su disponibilidad?")
   - NO incluye una fecha específica en su solicitud
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Solicita horario sin precio" y no consideres otras categorías

6. Dudas padecimiento
   - El último mensaje del usuario contiene preguntas específicas sobre sus síntomas o malestar
   - NO está preguntando sobre procedimiento, ubicación ni precios
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Dudas padecimiento" y no consideres otras categorías

7. Dudas procedimiento
   - El último mensaje del usuario es específicamente sobre lo que se hará en consulta o lo que incluye
   - NO se ha proporcionado el precio aún
   - Ejemplos: "¿qué me van a hacer?", "¿incluye el papanicolaou?"
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Dudas procedimiento" y no consideres otras categorías

8. Precio consulta
   - El último mensaje es una pregunta explícita sobre el precio de: consulta general, papanicolaou o trastornos menstruales
   - NO se ha proporcionado ese precio específico antes
   - NO está preguntando por precios de verrugas o consulta prenatal
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio consulta" y no consideres otras categorías

9. Precio verrugas
   - El último mensaje es específicamente sobre el precio para tratamiento de verrugas
   - NO se ha proporcionado ese precio específico antes
   - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio verrugas" y no consideres otras categorías

10. Precio prenatal
    - El último mensaje es específicamente sobre el precio de consulta prenatal o seguimiento de embarazo
    - NO se ha proporcionado ese precio específico antes
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Precio prenatal" y no consideres otras categorías

11. Ubicación aceptada con horario ofrecido
    - Ya se proporcionó el domicilio completo
    - El usuario responde que le queda cerca o que conoce el lugar
    - Ya se ofreció un horario específico previamente
    - El último mensaje expresa esta confirmación de conocimiento/aceptación de ubicación
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada con horario ofrecido" y no consideres las categorías "Ubicación" ni "Ubicación aceptada sin horario ofrecido"

12. Ubicación aceptada sin horario ofrecido
    - Ya se proporcionó el domicilio completo
    - El usuario responde que le queda cerca o que conoce el lugar
    - NO se ha ofrecido ningún horario específico aún
    - El último mensaje expresa esta confirmación de conocimiento/aceptación de ubicación
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación aceptada sin horario ofrecido" y no consideres la categoría "Ubicación"

13. Ubicación
    - El último mensaje contiene una pregunta explícita sobre la ubicación física de la clínica
    - Ejemplos: "¿Dónde están ubicados?", "¿En qué calle es?", "¿Cuál es la dirección?"
    - NO se ha proporcionado el domicilio completo previamente
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ubicación" y no consideres otras categorías

14. Agradecimiento
    - Ya se resolvieron todas las dudas del usuario o ya se confirmó completamente la cita
    - El último mensaje contiene exclusivamente un agradecimiento o despedida
    - Ejemplos: "Gracias", "Perfecto, gracias", "Nos vemos", "Gracias, igualmente"
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Agradecimiento" y no consideres otras categorías

15. Ghosted 1
    - Ya respondimos a todas las dudas del usuario
    - El usuario ha dejado de responder por un tiempo significativo
    - NO se ha enviado el mensaje: "Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"
    - IMPORTANTE: Si cumple estas condiciones, clasifica SOLO como "Ghosted 1" y no consideres otras categorías

16. Otro
    - La conversación NO encaja en ninguna de las categorías anteriores, incluyendo:
    - Pregunta por una fecha específica (aunque quiera horario)
    - Ya se proporcionó el precio y el usuario lo vuelve a solicitar
    - El mensaje es ambiguo, irrelevante o trata temas no considerados (ej. trámites, quejas, otros servicios)
    - Se intenta clasificar en una categoría que ya apareció previamente en la conversación (de la lista mencionada al principio)
    - IMPORTANTE: Utiliza esta categoría SOLO si ninguna de las anteriores aplica o si la categoría adecuada ya fue utilizada antes

Solo responde con el nombre exacto de la categoría.
Toma en cuenta la hora de llegada de los mensajes para determinar el orden cronológico de la conversación.
Revisa el historial completo de la conversación para verificar si alguna categoría ya fue asignada previamente, especialmente: "Acepto cita", "Acepto horario", "Solicita horario con precio", "Precio consulta", "Ubicación aceptada con horario ofrecido", "Solicita horario sin precio", "Ubicación aceptada sin horario ofrecido", "Ubicación".
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