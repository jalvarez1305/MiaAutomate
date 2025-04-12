import json
from CW_Conversations import get_conversation_by_id
from SaveConversations import Conversacion

conv_handles = Conversacion()

# Definir el rango de IDs a revisar (desde 0 hasta 100 por ejemplo)
for conv_id in range(0, 6746):  # Ajusta el rango si es necesario
    print(f"🔍 Obteniendo conversación con ID {conv_id}...")

    # Obtener la conversación
    conv = get_conversation_by_id(conv_id)
    
    if conv is None:
        print(f"❌ Conversación {conv_id} no encontrada o error al obtenerla.")
        continue  # Saltar a la siguiente conversación si no se pudo obtener
    
    # Si la conversación se obtuvo con éxito, almacenarla en Pinecone
    try:
        conv_handles.almacenar_conv_pinecone(conv)
        print(f"✅ Conversación {conv_id} almacenada correctamente en Pinecone.")
    except Exception as e:
        print(f"⚠️ Error al almacenar la conversación {conv_id} en Pinecone: {str(e)}")
