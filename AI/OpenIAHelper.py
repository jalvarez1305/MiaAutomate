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
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": """En una clinica medica tu eres un Medico que se dedica a clasificar conversaciones en una de las siguientes categorias
                                                Dudas padecimiento: Para entrar en esta clasificacion el ultimo texto del usuario debe hacer referencia a dudas sobre su padecimiento medico
                                                Solicita horario: Para entrar en esta clasificacion el usuario ya resolvio sus dudas de padecimiento.
                                                                  Para entrar en esta clasificacion el usuario ya pregunto por el precio y estuvo de acuerdo
                                                                  Especificamente pregunta por un espacio disponible; Pero, ya resolvio dudas medicas
                                                                  Si ya le proporcionamos un horario, no puede tener esta clasificacion
                                                Dudas procedimiento: Para entrar en esta clasificacion el usuario Tiene dudas sobre el precio
                                                                     Tiene dudas sobre lo que se hara en consulta
                                                                     Tiene dudas sobre lo que incluye la consulta
                                                                     No se le ha pasaso precio anteriormente
                                                Acepto Horario: Para entrar en esta clasificacion ya se le ofrecio un horario al paciente y este acepto uno
                                                                La aceptacion debe ser el ultimo mensaje del usuario
                                                Rechazo Horario: Para entrar en esta clasificacion ya se le ofrecio un horario al paciente y no puede tomar el horario ofrecido
                                                                 El rechazo debe ser el ultimo mensaje del usuario
                                                Acepto Cita: Para entrar en esta clasificacion ya se le ofrecio un horario, lo acepto, se le pidio su nombre y lo proporciono
                                                Ghosted 1: Para entrar en esta clasificacion ya hemos respondido todas las preguntas del usuario y este dejo de responder
                                                            no debe tener el mensaje "Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"
                                                Otro: Cuando no entra en ninguna de estas clasificaciones se clasifica como Otro
                                                                  """},
            {"role": "system", "content": """Dada la siguiente conversación, regresa la clasificacion"""}
        ]+ConvMessages,
        temperature=0.1  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text