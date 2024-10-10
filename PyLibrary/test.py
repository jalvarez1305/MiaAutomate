from CW_Conversations import get_open_conversation


if __name__ == "__main__":
    contact_id = 181  # El ID del contacto que deseas probar
    conversation_id = get_open_conversation(contact_id)
    print(f"Conversation ID: {conversation_id}")