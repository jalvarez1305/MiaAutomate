import json
import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ConversationAnswer_tmp(ConvMessages):
  # Obtener el contexto adicional de Pinecone (o cualquier otra fuente que uses)
  texto = json.dumps(ConvMessages)
  context = get_context(texto)
  all_mesg=[
            {"role": "system", "content": f"Contexto adicional: {context}"},
            {"role": "system", "content": """Eres un medico vendedor de servicios de ginecología"""},

            {"role": "system", "content": """El flujo debe ser el siguiente:
                                            El usuario contacta.
                                            Le preguntamos si es una revisión general o si tiene un padecimiento específico.
                                            Nos proporciona el padecimiento.
                                            Buscamos en el contexto de conversaciones anteriores cómo se puede atender el padecimiento.
                                            Le respondemos del padecimiento.
                                            Si tiene más dudas del padecimiento o procesos, le respondemos con el contexto.
                                            Si pide precio, lo obtenemos del contexto.
                                            No ofrezcas la cita a menos que estes seguro que el usuario ya resolvio todas sus dudas
                                            Si puedes proporcionar posibles causas, pero no puedes ofrecer tratamientos
                                            No le pidas agendar la cita a menos que el usuario lo solicite y ya haya resuelto las dudas de su padecimiento
                                            No finalices preguntando dudas, espera que el usuario presente las dudas
                                            No digas consulta a tu medico, habla siempre en primera primersona
                                            Se amable, le hablas a mujeres e incluye 1 o dos emojis
                                            Estas hablando por whatsapp, se brebre y usa el formato apropiado"""}
        ]+ConvMessages
  response = client.responses.create(
      model="gpt-4o-mini",
      input=all_mesg,
      temperature=0.1  # Ajustar la temperatura a 0.1
  )
  return response.output_text

def ghosted_clasification(ConvMessages):
    """
    :param conversacion: Lista de mensajes en orden cronológico. 
                         Cada mensaje es un dict: {'rol': 'usuario'|'agente', 'contenido': str}
    :return: Una string con la categoría
    """
    saludo="""Cuéntame un poquito más ✨ ¿Tienes algún tema en especial que te gustaría revisar en la consulta 🩺💖 o ya te toca tu revisión ginecológica anual? 📅🌸"""
    remate ="""Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"""
    reglas = f"""
              Clasifica la conversación en una (y solo una) de las siguientes categorías. Evalúa en este orden estricto:

              Ghosted A

              El último mensaje es nuestro (del agente).

              Los mensajes que comienzan con 'Categoría:' deben ignorarse.

              Después de enviar el mensaje '{saludo}', el usuario no respondió absolutamente nada (ni monosilábicos).

              El '{saludo}' se ha enviado una sola vez.

              Ghosted B

              El último mensaje es nuestro (del agente).

              Los mensajes que comienzan con 'Categoría:' deben ignorarse.

              Se envió el mensaje '{saludo}'.

              El usuario respondió al menos dos mensajes.

              Después de esas respuestas, el agente hizo una pregunta directa (ej: "¿Te queda bien?", "¿Deseas agendar?") o un ofrecimiento significativo (ej: mandó precios, ofreció horarios, describió un servicio).

              Si después de este ofrecimiento o pregunta, el usuario no contestó, se considera que nos dejó en visto.

              Otro

              Cualquier conversación que no encaje en las anteriores.

              Notas:

              "Ofrecimiento significativo" incluye mandar precios, horarios, descripción de consulta, o cualquier propuesta directa relacionada con la cita.

              No es necesario que el ofrecimiento sea una pregunta explícita.

              Responde únicamente con el nombre de la categoría.

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
