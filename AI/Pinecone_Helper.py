from langchain_community.embeddings import OpenAIEmbeddings
import openai
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore  # Cambiado para usar la clase correcta
from pinecone import Pinecone, ServerlessSpec

from OpenIAHelper import get_embedding

# Cargar variables de entorno
load_dotenv()

# Configurar claves
pinecone_api = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX")
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_model_name = os.getenv("EMBEDDED_MODEL")
# Wrap your function if needed
class EmbeddingWrapper:
    def __init__(self, embedding_function):
        self.embedding_function = get_embedding

    def embed_query(self, query):
        return self.embedding_function(query)
embedding_wrapper = EmbeddingWrapper(get_embedding)

# Validaciones opcionales
if not all([pinecone_api, pinecone_index_name, openai_api_key, embedding_model_name]):
    raise ValueError("Faltan variables de entorno necesarias")

# Crear embeddings usando el modelo y API key especificados
embedding_model = OpenAIEmbeddings(
    model=embedding_model_name,
    openai_api_key=openai_api_key
)

# Inicializar cliente Pinecone (usando la nueva forma recomendada)
pc = Pinecone(
        api_key=pinecone_api
    )
index = pc.Index(pinecone_index_name)  # Usamos la clase Index de Pinecone directamente

# Crear el vectorstore desde el índice de Pinecone
vectorstore = PineconeVectorStore(
    index_name=pinecone_index_name,
    embedding=embedding_wrapper,
    text_key="raw"
)

# Función para insertar en Pinecone
def store_to_pinecone(id, data, extra_metadata=None):
    embedding = get_embedding(data)

    metadata = {"raw": data}
    if extra_metadata:
        metadata.update(extra_metadata)

    index.upsert(vectors=[{
        "id": str(id),
        "values": embedding,
        "metadata": metadata
    }])
    print(f"✅ Insertado en Pinecone con ID: {id}")

# Función para obtener contexto
def get_context(query):    
    context = vectorstore.similarity_search(query, 3)
    return context

