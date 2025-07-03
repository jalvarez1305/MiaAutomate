from flask import Flask, request, jsonify,Response
import logging

import os
import sys

# Obtener el directorio padre (donde está ubicado 'libs')
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from libs.CW_Contactos import devolver_llamada
from libs.TwilioHandler import get_child_call_status

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

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



if __name__ == '__main__':
    # Host siempre 0.0.0.0 para aceptar tráfico externo
    host_ip = '0.0.0.0'

    # Puerto configurable desde variable de entorno, con fallback a 5000
    port = int(os.environ.get('PORT', 5000))

    logging.info(f"Ejecutando en {host_ip}:{port}")

    app.run(host=host_ip, port=port)
