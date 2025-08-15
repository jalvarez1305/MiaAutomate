from flask import Flask, request, jsonify,Response
import logging
import socket
import os
import sys
import json
from datetime import datetime
from bot_commands import BotCommands
from gyne_general import GyneGeneralBot
from Constelaciones_Bot import Constelaciones_Bot
from Labioplastia_Bot import Labioplastia_Bot
from confirmar_cita_bot import ConfirmarCitaBot
from encuesta_paciente_bot import EncuestaPacienteBot
from agenda_bot import AgendaBot
from helper import parse_conversation_payload
from Bots_Config import paps_messages,facebook_messages,custom_commands,agenda_medico,constelaciones_messages,labioplastia_messages
# Obtener el directorio padre (donde está ubicado 'libs')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from AI.OpenIAHelper import conv_close_sale
from libs.SaveConversations import Conversacion
from libs.CW_Conversations import get_AI_conversation_messages
from libs.CW_Contactos import asignar_a_agente,devolver_llamada,get_linphone_name,get_tipo_contacto,crear_contacto
from libs.TwilioHandler import get_child_call_status

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
    if new_msg in facebook_messages:
        logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'GyneGeneralBot')}")
        GyneGeneralBot(split_data)
    elif new_msg in constelaciones_messages:
        logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'Constelaciones_Bot')}")
        Constelaciones_Bot(split_data)
    elif new_msg in labioplastia_messages:
        logging.info(f"Se ejecuta BOT {split_data.get('bot_attribute', 'Labioplastia_Bot')}")
        Labioplastia_Bot(split_data)
    elif new_msg == agenda_medico:
        logging.info(f"Se ejecuta BOT Agenda Medico")
        AgendaBot(split_data)
    elif new_msg in custom_commands:
        logging.info(f"Se ejecuta BOT BotCommands: {new_msg}")
        BotCommands(split_data)


    
    else:
        logging.error("Faltan datos necesarios en el payload.")    

    #Revisamos despues los bots de ventas
    if last_message.get('Sender') == "contact":
        print(f"Las sender contact")
        labels = data['conversation']['labels']
        print(f"Etiquetas: {labels} ")
        if "citagyne" in labels:
            print("Esta es una conversacion de ventas de ginecologia")
            #GyneGeneralBot(split_data)
        

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

@app.route('/twilio/callend', methods=['GET', 'POST'])
def llamada_telefonica_terminada():
    data = request.form.to_dict()
    #print("Payload en formato JSON:")
    #print(data)

    parent_call_sid = data.get('CallSid')  # El CallSid de esta llamada INBOUND es el Parent de la OUTBOUND
    call_direction = data.get('CallDirection')
    from_number = data.get('From')

    if from_number and from_number.startswith('+52'):
        from_number = from_number.replace('+52', '+521', 1)

    if parent_call_sid:
        child_status = get_child_call_status(parent_call_sid)
        print(f"Estado de la llamada hija: {child_status}")

        if child_status in ['no-answer', 'busy']:
            print(f"Llamada NO contestada o ocupada: {child_status}, FROM: {from_number}")
            devolver_llamada(from_number)

    return '<Response></Response>', 200


@app.route('/calltosip', methods=['GET', 'POST'])
def call_to_sip():
    from_number = request.values.get('From', '')
    if from_number and from_number.startswith('+52'):
        from_number = from_number.replace('+52', '+521', 1)
    tipo_contacto = get_tipo_contacto(from_number)
    if tipo_contacto == "prospecto":
        new_contid=crear_contacto(from_number)
        caller_id=f'Prospecto--{new_contid}'
    else:
        caller_id=get_linphone_name(from_number)
    print("Reenviando llamada a SIP, contacto:", caller_id)
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial callerId="{caller_id}">
    <Sip>sip:linphone@mia.sip.twilio.com</Sip>
  </Dial>
</Response>"""
    return Response(twiml, mimetype='text/xml')


@app.route('/outgoingcall', methods=['POST'])
def outgoing_call():
    print("----- Incoming Outgoing Call Request -----")
    for key, value in request.values.items():
        print(f"{key}: {value}")

    to_number = request.values.get('To', '')
    print(f"Destino a marcar: {to_number}")

    # Extraer solo el número en formato E.164 si viene en formato SIP URI
    if 'sip:' in to_number:
        to_number = to_number.split(':')[1].split('@')[0]

    if not to_number.startswith('+'):
        to_number = '+52' + to_number  # ajusta según país si es necesario

    twiml = f"""
    <Response>
      <Dial callerId="+523359800766">
        <Number>{to_number}</Number>
      </Dial>
    </Response>
    """
    print("TwiML generado:")
    print(twiml)
    return Response(twiml, mimetype='text/xml')

if __name__ == '__main__':
    host_ip = '0.0.0.0'  # Default to localhost
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
