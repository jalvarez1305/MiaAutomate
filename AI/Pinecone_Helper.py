import openai
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Cargar variables de entorno
load_dotenv()

# Configurar claves
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("EMBEDDED_MODEL")
pinecone_api = os.getenv("PINECONE_API_KEY")
pinecone_index = os.getenv("PINECONE_INDEX")

# Validar que las variables necesarias estén presentes
if not all([openai.api_key, MODEL, pinecone_api, pinecone_index]):
    raise ValueError("Faltan variables de entorno necesarias. Revisa tu archivo .env")

# Inicializar Pinecone (nueva forma)
pc = Pinecone(api_key=pinecone_api)
index = pc.Index(pinecone_index)

# Función para insertar en Pinecone
def store_to_pinecone(id, data, extra_metadata=None):
    response = openai.embeddings.create(input=data, model=MODEL)
    embedding = response.data[0].embedding

    metadata = {"raw": data}
    if extra_metadata:
        metadata.update(extra_metadata)

    index.upsert(vectors=[
        {
            "id": str(id),
            "values": embedding,
            "metadata": metadata
        }
    ])
    print(f"✅ Insertado en Pinecone con ID: {id}")

#store_to_pinecone("1", "Qué pedo Ron", {"categoria": "saludo"})
