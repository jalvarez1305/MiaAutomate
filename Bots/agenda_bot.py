import sys
import os
# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message,ChatwootSenders


def AgendaBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles
        last_message_content = Detalles.get('last_message', {}).get('content')
        conversation_id = Detalles.get('conversation_id')

        if last_message_content == 'Si':
            send_conversation_message(conversation_id, 'Prueba de respuesta',buzon=ChatwootSenders.Medicos)  # Mensaje de prueba
        else:
            send_conversation_message(conversation_id, '@Pablo, no puedo responder esto', is_private=True,buzon=ChatwootSenders.Medicos)

    except Exception as e:
        print(f"Error en AgendaBot: {str(e)}")  # Manejo básico de errores
