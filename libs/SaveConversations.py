import json
import os
import sys


from CW_Conversations import get_all_conversation_messages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI')))
from Pinecone_Helper import store_to_pinecone

class Conversacion:
    def __init__(self):
        self.folder = "CW_Close_Conversations"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def transformar(self, data):
        conv_id=data['id']
        messages_array=get_all_conversation_messages(conv_id)
        return {
            "sender": {
                "id": data.get("meta", {}).get("assignee", {}).get("id"),
                "name": data.get("meta", {}).get("assignee", {}).get("name", "Desconocido")
            },
            "team": {
                "id": data.get("meta", {}).get("team", {}).get("id"),
                "name": data.get("meta", {}).get("team", {}).get("name", "Sin equipo")
            } if data.get("meta", {}).get("team") else None,
            "contact_inbox": {
                "contact_id": data.get("contact_inbox", {}).get("contact_id"),
                "source_id": data.get("contact_inbox", {}).get("source_id"),
                "created_at": data.get("contact_inbox", {}).get("created_at"),
                "updated_at": data.get("contact_inbox", {}).get("updated_at"),
                "custom_attributes": data.get("meta", {}).get("sender", {}).get("custom_attributes", {})
            },
            "id": data.get("id"),
            "inbox_id": data.get("inbox_id"),
            "messages": messages_array,
            "labels": data.get("labels", []),
            "custom_attributes": data.get("custom_attributes", {}),
            "first_reply_created_at": data.get("first_reply_created_at"),
            "agent_last_seen_at": data.get("agent_last_seen_at", 0),
            "contact_last_seen_at": data.get("contact_last_seen_at", 0),
            "last_activity_at": data.get("last_activity_at", 0),
            "timestamp": data.get("timestamp", 0),
            "created_at": data.get("created_at", 0)
        }



    def almacenar(self, data):
        transformed_data = self.transformar(data)
        file_path = os.path.join(self.folder, f"{transformed_data['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(transformed_data, f, ensure_ascii=False, indent=4)
            
    def almacenar_conv_pinecone(self, data):
        #Almacena toda una cnversacion en pinecone
        transformed_data = self.transformar(data)
        # Convertir a string
        json_str = json.dumps(transformed_data)
        store_to_pinecone(transformed_data['id'],json_str)
