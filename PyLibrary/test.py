from CW_Conversations import ChatwootSenders, envia_mensaje_plantilla, get_open_conversation, send_conversation_message

"""
Probar get_open_conversation
if __name__ == "__main__":
    contact_id = 181  # El ID del contacto que deseas probar
    conversation_id = get_open_conversation(contact_id)
    print(f"Conversation ID: {conversation_id}")
"""

"""
Probar enviar mensaje

if __name__ == "__main__":
    conversation_id = 537  # Reemplaza con un ID de conversación válido
    message = "Hola, @Pablo este es un mensaje de prueba, privado."  # Mensaje que deseas enviar
    is_private = True  # Puedes cambiarlo a True si el mensaje es privado
    buzon = ChatwootSenders.Pacientes  # O ChatwootSenders.Medicos, según sea necesario

    # Llamar a la función para enviar el mensaje
    send_conversation_message(conversation_id, message, is_private, buzon)
"""


contacto_id = 162  # Reemplaza con el ID del contacto
plantilla = """Hola {{1}}, queremos ser siempre mejores para ti. Nos podrias decir como calificarías la atención brindada por tu medico {{2}}?

por favor"""
parametros = ["Juan", "de parte de la clínica."]
buzon = ChatwootSenders.Pacientes  # O ChatwootSenders.Medicos
bot_name = "Notificacion"

envia_mensaje_plantilla(contacto_id, plantilla, parametros, buzon, bot_name)


