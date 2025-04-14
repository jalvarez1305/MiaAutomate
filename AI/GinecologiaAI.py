import json
import os
from openai import OpenAI

from Pinecone_Helper import get_context

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ConversationAnswer(ConvMessages):
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
