from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import os
from dotenv import load_dotenv
from pinecone import Pinecone  # usar la clase correcta
from langchain.vectorstores import Pinecone as LangchainPinecone

from OpenIAHelper import get_embedding

# Cargar variables de entorno
load_dotenv()

# Configurar claves
pinecone_api = os.getenv("PINECONE_API_KEY")
pinecone_index = os.getenv("PINECONE_INDEX")
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_model_name = os.getenv("EMBEDDED_MODEL")

# Validaciones opcionales
if not all([pinecone_api, pinecone_index, openai_api_key, embedding_model_name]):
    raise ValueError("Faltan variables de entorno necesarias")

# Crear embeddings usando el modelo y API key especificados
embedding_model = OpenAIEmbeddings(
    model=embedding_model_name,
    openai_api_key=openai_api_key
)

# Inicializar cliente Pinecone (forma nueva)
pc = Pinecone(api_key=pinecone_api)
index = pc.Index(pinecone_index)

# Crear vectorstore desde índice existente
# Pasar directamente el index (ya autenticado) a Langchain
vectorstore = LangchainPinecone(
    index=index,
    embedding=embedding_model,
    text_key="raw"
)

# Función para insertar en Pinecone
def store_to_pinecone(id, data, extra_metadata=None):
    embedding = get_embedding(data)

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

# Función para obtener contexto
def get_context(query):
    context = vectorstore.similarity_search(query, 3)
    return context