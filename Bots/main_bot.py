from flask import Flask, request, jsonify
import logging
import socket
import os
import sys
import json
from datetime import datetime
from Bot_Paps import BotPaps
from bot_commands import BotCommands
from gyne_general import GyneGeneralBot
from Constelaciones_Bot import Constelaciones_Bot
from confirmar_cita_bot import ConfirmarCitaBot
from encuesta_paciente_bot import EncuestaPacienteBot
from agenda_bot import AgendaBot
from helper import parse_conversation_payload
from Bots_Config import paps_messages,facebook_messages,custom_commands,agenda_medico,constelaciones_messages
# Obtener el directorio padre (donde está ubicado 'libs')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from AI.OpenIAHelper import conv_close_sale
from libs.SaveConversations import Conversacion
from libs.CW_Conversations import get_AI_conversation_messages
from libs.CW_Contactos import asignar_a_agente

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
    if new_msg in paps_messages:
        logging.info(f"Se ejecuta BOT Paps")
        BotPaps(split_data)
    elif new_msg in facebook_messages:
        logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'GyneGeneralBot')}")
        GyneGeneralBot(split_data)
    elif new_msg in constelaciones_messages:
        logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'Constelaciones_Bot')}")
        Constelaciones_Bot(split_data)
    elif new_msg == agenda_medico:
        logging.info(f"Se ejecuta BOT Agenda Medico")
        AgendaBot(split_data)
    elif new_msg in custom_commands:
        logging.info(f"Se ejecuta BOT BotCommands: {new_msg}")
        BotCommands(split_data)


    if 'bot_attribute' in split_data and 'Sender' in last_message:
        if split_data['bot_attribute'] != "" and last_message.get('Sender') == "contact":
            match split_data["bot_attribute"]:
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
        split_data = parse_conversation_payload(data)
        msg_arr=get_AI_conversation_messages(conversation_id)
        labels = data.get("labels", [None])   
        print(f"Etiquetas: {labels}")
        vendio= conv_close_sale(msg_arr)
        print(f"Vendio: {vendio}")
        # Solamente aqueyas conversaciones de ventas que terminaron en venta
        if "citagyne" in labels and vendio==True:
            conversacion.almacenar_conv_pinecone(data)
            print("✅ Conversación guardada correctamente")
            return jsonify({"message": "Conversación guardada correctamente"}), 200
    except Exception as e:
        logging.error(f"🚨 Error al guardar la conversación {conversation_id}: {e}")
        print(f"🚨 Error al guardar la conversación {conversation_id}: {e}")
        return jsonify({"error": "Error al guardar la conversación"}), 500

@app.route('/AsignarNuevasConversaciones', methods=['POST'])
def asignar_nuevas_conversaciones():
    """Webhook que asigna automáticamente las conversaciones nuevas según reglas establecidas."""
    import datetime  # Importar el módulo datetime
    
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    conversation_id = data.get('id')

    if not conversation_id:
        print("❌ Falta el ID de la conversación")
        return jsonify({"error": "Missing conversation ID"}), 400

    print(f"🔔 Recibí conversación nueva: {conversation_id}")

    # Obtener el atributo cliente desde la ruta correcta en el payload
    cliente = data.get('meta', {}).get('sender', {}).get('custom_attributes', {}).get('cliente')
    
    # Verificar si el atributo "cliente" está presente
    es_cliente = cliente is not None
    
    # Obtener la hora actual - CORREGIDO
    hora_actual = datetime.datetime.now().hour
    
    # Aplicar reglas de asignación
    try:
        if es_cliente:
            if hora_actual < 15:  # Antes de las 3:00 PM
                print(f"Asigna Orlando - Conversación: {conversation_id}")
                asignado = 29
            else:  # 3:00 PM o posterior
                print(f"Asigna Mayra - Conversación: {conversation_id}")
                asignado = 32
        else:
            print(f"Asigna Yanet - Conversación: {conversation_id}")
            asignado = 15
        
        # Aquí podrías agregar código para hacer la asignación real en Chatwoot
        # Por ejemplo, llamar a la API de Chatwoot para asignar el agente correspondiente
        asignar_a_agente(conversation_id,asignado)
        return jsonify({
            "message": f"Conversación {conversation_id} asignada a {asignado}",
            "assigned_to": asignado
        }), 200
    except Exception as e:
        logging.error(f"🚨 Error al asignar la conversación {conversation_id}: {e}")
        print(f"🚨 Error al asignar la conversación {conversation_id}: {e}")
        return jsonify({"error": "Error al asignar la conversación"}), 500


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
