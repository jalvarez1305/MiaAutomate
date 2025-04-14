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

def is_user_ready(ConvMessages):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": """Eres un analizador de conversaciones que dice si el usuario ya resolvió todas sus dudas y está listo para agendar."""},
            {"role": "system", "content": """Dada la siguiente conversación, regresa True o False en un booleano de Python."""},
            {"role": "user", "content": ConvMessages}  # Asegúrate de que ConvMessages esté correctamente formateado
        ],
        temperature=0.1  # Ajustar la temperatura a 0.1
    )
    
    return response.output_text