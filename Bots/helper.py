def parse_conversation_payload(payload):
    """
    Procesa el payload de una conversación y extrae la información relevante.
    
    :param payload: Diccionario que contiene la información de la conversación.
    :return: Objeto con la información estructurada de la conversación.
    """
    conversation_info = {
        "conversation_id": payload.get("id"),
        "contact_id": payload.get("meta", {}).get("sender", {}).get("id"),
        "bot_attribute": payload.get("custom_attributes", {}).get("bot"),
        "messages": []
    }

    # Extraer mensajes
    messages = payload.get("messages", [])
    last_sender = None
    last_message_text = None

    for message in messages:
        sender_type = "agente" if message.get("sender_type") == "agent" else "contacto"
        message_info = {
            "sender": sender_type,
            "text": message.get("content")
        }
        conversation_info["messages"].append(message_info)

        # Actualizar información del último mensaje
        if message.get("created_at"):  # Si hay una fecha de creación
            if last_sender is None or message.get("created_at") > last_message_text:
                last_sender = sender_type
                last_message_text = message.get("content")

    # Añadir el último mensaje al objeto de conversación
    conversation_info["last_message"] = {
        "sender": last_sender,
        "text": last_message_text
    }

    return conversation_info
