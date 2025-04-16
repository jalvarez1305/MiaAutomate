from flask import Flask, request, jsonify
import logging
import socket
import os
import sys
import json
from datetime import datetime
from Bot_Paps import BotPaps
from gyne_general import GyneGeneralBot
from confirmar_cita_bot import ConfirmarCitaBot
from encuesta_paciente_bot import EncuestaPacienteBot
from agenda_bot import AgendaBot
from helper import parse_conversation_payload
from Bots_Config import audio_gyne,paps_messages,facebook_messages
# Obtener el directorio padre (donde está ubicado 'libs')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from libs.SaveConversations import Conversacion

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Objeto
conversacion = Conversacion()

@app.route('/webhook/chatwoot', methods=['POST'])
def chatwoot_webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    split_data = parse_conversation_payload(data)
    
    if not isinstance(split_data, dict):
        return jsonify({"error": "Unexpected payload format"}), 400

    last_message = split_data.get("last_message", {})
    new_msg = last_message.get('Content')
    #evaluemos primero pipelines basados en mensajes
    if last_message.get('Sender') == "contact":
        if new_msg in paps_messages:
            logging.info(f"Se ejecuta BOT Paps")
            BotPaps(split_data)
        elif new_msg in facebook_messages:
            logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'GyneGeneralBot')}")
            GyneGeneralBot(split_data)


    if 'bot_attribute' in split_data and 'Sender' in last_message:
        if split_data['bot_attribute'] != "" and last_message.get('Sender') == "contact":
            match split_data["bot_attribute"]:
                case "AgendaMedico":
                    logging.info(f"Se ejecuta BOT {split_data['bot_attribute']}")
                    AgendaBot(split_data)
                case "EncuestaPacienteBot":
                    logging.info(f"Se ejecuta BOT {split_data['bot_attribute']}")
                    EncuestaPacienteBot(split_data)
                case "ConfirmarCitaBot":
                    logging.info(f"Se ejecuta BOT {split_data['bot_attribute']}")
                    ConfirmarCitaBot(split_data)
                case _:                    
                    logging.warning("Mensaje no reconocido.")
    else:
        logging.error("Faltan datos necesarios en el payload.")    

    #Revisamos despues los bots de ventas
    if last_message.get('Sender') == "contact":
        print(f"Las sender contact")
        labels = data['conversation']['labels']
        print(f"Etiquetas: {labels} ")
        if "citagyne" in labels:
            print("Esta es una conversacion de ventas de ginecologia")
            GyneGeneralBot(split_data)
        

    return jsonify({"message": "Webhook received!"}), 200

@app.route('/SaveConversation', methods=['POST'])
def save_conversation():
    """Webhook que guarda la conversación cuando se cierra en Chatwoot."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    conversation_id = data.get('id')
    status = data.get('status')

    print(f"🔔 Recibí conversación: {conversation_id} con estatus: {status}")

    if not conversation_id:
        print("❌ Falta el ID de la conversación")
        return jsonify({"error": "Missing conversation ID"}), 400

    # Solo continuar si el estatus es 'closed'
    if status != 'resolved':
        print(f"ℹ️ Conversación {conversation_id} ignorada porque su estatus no es 'closed'.")
        return jsonify({"message": "Conversación no cerrada, no se almacena"}), 200

    # Almacenar conversación si está cerrada
    try:
        conversacion.almacenar_conv_pinecone(data)
        print("✅ Conversación guardada correctamente")
        return jsonify({"message": "Conversación guardada correctamente"}), 200
    except Exception as e:
        logging.error(f"🚨 Error al guardar la conversación {conversation_id}: {e}")
        print(f"🚨 Error al guardar la conversación {conversation_id}: {e}")
        return jsonify({"error": "Error al guardar la conversación"}), 500


if __name__ == '__main__':
    host_ip = 'localhost'  # Default to localhost
    try:
        # Intentar enlazar a 74.208.33.184 para ver si está disponible
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('74.208.33.184', 0))  # Usa el puerto 0 para no necesitar uno específico
        test_socket.close()
        host_ip = '74.208.33.184'  # Si funciona, cambia a la IP especificada
        logging.info("Ejecutando en 74.208.33.184")
    except Exception as e:
        logging.warning(f"No se puede enlazar a 74.208.33.184, se usará localhost: {e}")
    
    app.run(host=host_ip, port=5001)
