from flask import Flask, request
from .helper import parse_conversation_payload

app = Flask(__name__)

@app.route('/webhook/chatwoot', methods=['POST'])
def chatwoot_webhook():
    # Obtener el cuerpo de la solicitud
    data = request.json
    split_data = parse_conversation_payload(data)
    #evalua los bots
    if split_data["bot_attribute"] and split_data["last_message"]["sender"] == "contacto":
        print("El atributo del bot está presente y el último mensaje es de contacto.")
        match split_data["bot_attribute"]:
            case "AgendaMedico":
                print(f"Se ejecuta BOT {split_data["bot_attribute"]}")
            case _:
                print("Bot no reconocido")
    else:
        print("No debe ser atendido por un bot")
    
    # Imprimir el cuerpo de la solicitud
    print("Received webhook data:")
    print(data)
    
    return "Webhook received!", 200

if __name__ == '__main__':
    app.run(port=5000)  # Cambia el puerto según sea necesario


