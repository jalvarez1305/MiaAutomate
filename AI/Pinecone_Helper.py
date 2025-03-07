import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL= os.getenv('EMEDDED_MODEL')
# Obtener la BASE_URL y CW_TOKEN desde el .env
def StoreToPinecone(data):
    res=openai.embeddings.create(input=data,model=MODEL)
    emb_vector= res["data"][0]["embedding"]




StoreToPinecone("Que pedo ron")