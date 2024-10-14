from flask import Flask, request, jsonify
import logging

from helper import parse_conversation_payload

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

@app.route('/webhook/chatwoot', methods=['POST'])
def chatwoot_webhook():
    # Obtener el cuerpo de la solicitud
    data = request.get_json()

    if not data:
        logging.error("No se recibió un cuerpo JSON válido.")
        return jsonify({"error": "Invalid JSON payload"}), 400

    split_data = parse_conversation_payload(data)
    
    # Verificar que split_data tiene las claves necesarias
    if not isinstance(split_data, dict):
        logging.error("El payload no tiene el formato esperado.")
        return jsonify({"error": "Unexpected payload format"}), 400

    # Evalúa los bots
    last_message = split_data.get("last_message", {})

    # Verificar la existencia de claves antes de acceder
    if 'bot_attribute' in split_data and 'Sender' in last_message:
        if split_data['bot_attribute'] != "" and last_message.get('Sender') == "contact":  # Asegúrate de que "Contact" sea la cadena correcta
            logging.info("El atributo del bot está presente y el último mensaje es de contacto.")            
            # Usar match-case para evaluar el atributo del bot
            match split_data["bot_attribute"]:
                case "AgendaMedico":
                    logging.info(f"Se ejecuta BOT {split_data['bot_attribute']}")
                    # Aquí puedes agregar más lógica para la ejecución del bot
                case _:
                    logging.warning("Bot no reconocido.")
        else:
            logging.info("No debe ser atendido por un bot.")
    else:
        logging.error("Faltan datos necesarios en el payload.")

    return jsonify({"message": "Webhook received!"}), 200

if __name__ == '__main__':
    app.run(port=5000)  # Cambia el puerto según sea necesario
