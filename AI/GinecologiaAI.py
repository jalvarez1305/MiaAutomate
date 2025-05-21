import json
import os
from openai import OpenAI
from OpenIAHelper import obtener_ultimos_mensajes_usuario
from Pinecone_Helper import get_context


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gpt_model= "gpt-4o"

def ResolverPadecimiento(ConvMessages):
  # Obtener el contexto adicional de Pinecone (o cualquier otra fuente que uses)
  mensajes_usuario = obtener_ultimos_mensajes_usuario(ConvMessages)
  user_question = "\n".join([msg["contenido"] for msg in mensajes_usuario])
  texto = json.dumps(user_question)
  context = get_context(texto)
  all_mesg=[
            {"role": "system", "content": f"Contexto adicional: {context}"},
            {"role": "system", "content": """Eres un medico que porporciona una breve atencion a padecimientos medicos, no proporcionas tratamiento
                                            unicamente le haces saber que conoces su padecimiento y por que es importante que le de tratamiento"""},
            {"role": "system", "content": """tus respuestas deben venir exclusivamente del contexto para que tus respuestas se parezcan a como assitant ha respondido a conversaciones anteriores"""},
            {"role": "system", "content": """El flujo debe ser el siguiente:
                                            El usuario contacta.
                                            Le preguntamos si es una revisión general o si tiene un padecimiento específico.
                                            Nos proporciona el padecimiento.
                                            Buscamos en el contexto de conversaciones anteriores cómo se puede atender el padecimiento.
                                            Le respondemos del padecimiento.
                                            Si tiene más dudas del padecimiento, le respondemos con el contexto.                        
                                            Si puedes proporcionar posibles causas, pero no puedes ofrecer tratamientos
                                            No finalices preguntando dudas
                                            No digas consulta a tu medico, habla siempre en primera primersona
                                            Se amable, le hablas a mujeres e incluye 1 o dos emojis
                                            Estas hablando por whatsapp, se brebre y usa el formato apropiado
                                            Se breve
                                            Si la pregunta es sobre 'Menopausia','Premenopausia','Perimenopausia' responde este texto extacto 'Dame un segundito para platicarte de las opciones que manejamos, por favor 🙌'
                                            Si el contexto no tiene la informacion ue necesitas, responde este texto exacto 'Dame un segundito para darte la informacion precisa, por favor'"""}
        ]+ConvMessages
  response = client.responses.create(
      model=gpt_model,
      input=all_mesg,
      temperature=0  # Ajustar la temperatura a 0.1
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

              No se ha enviado el mensaje '{remate}'

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
        model=gpt_model,
        input=[
            {"role": "system", "content": "Eres un médico que clasifica conversaciones médicas según reglas estrictas."},
            {"role": "user", "content": reglas},
            {"role": "user", "content": f"""Ahora clasifica esta conversacion: {ConvMessages}"""}
        ],
        temperature=0  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text

