import sys
import os
import logging
import time

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders,send_audio_mp3_via_twilio, envia_mensaje_plantilla, remove_bot_attribute
from CW_Contactos import actualizar_interes_en,actualizar_etiqueta
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update
from CW_Automations import send_content
from Bots_Config import saludo_facebook,audio_gyne
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
respuesta_ubicacion="""La ubicación es en tonala
Av. Tonaltecas 180, Tonalá, Centro

https://goo.su/qyWUmj"""

def GyneGeneralBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
        contact_phone = Detalles.get('contact_phone')
       
        respuesta_horario = """Qué tal lindo día ! Platícame un poco más , tienes algún tema en particular que te gustaría revisar , o es porque ya te toca tu chequeo preventivo ?"""
        remate="Sigo a tus órdenes si tienes alguna otra duda o deseas agendar tu cita ☺️"

        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content == saludo_facebook or last_message_content == audio_gyne:
            MandarMensajeSaludo(conversation_id,contact_phone,contact_id)
        elif last_message_content == 'Domicilio':
            send_conversation_message(conversation_id, respuesta_ubicacion, is_private=False, buzon=ChatwootSenders.Pacientes)
        else:
            send_conversation_message(conversation_id, 'Hola soy Robot, me ayudan con esto?', is_private=True, buzon=ChatwootSenders.Pacientes)
    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging

def MandarMensajeSaludo(conversation_id,contact_phone,contact_id):
    
    # Actualiza el interes del contacto para que entre al funel
    send_conversation_message(conversation_id,"Esperare 30 segundos antes de enviar el audio de bien venida",True)
    actualizar_interes_en(contact_id, "https://miaclinicasdelamujer.com/gynecologia")
    actualizar_etiqueta(conversation_id,"citagyne")

    current_time = datetime.now()

    # Revisar si estamos entre las 10 PM y las 8 AM
    if current_time.hour >= 22 or current_time.hour < 8:
        send_conversation_message(conversation_id,"Hola Gracias por comunicarte a Mia clinicas de la mujer, nuestro horario de atencion es de 9:00 a 20:00, en breve nos comunicaremos contigo",False)
        send_conversation_message(conversation_id,"A las 8am se enviara el audio pidiendo detalles",True)
        print("a")

        # Calcular el tiempo restante hasta las 8 AM
        if current_time.hour >= 22:
            # Si es después de las 10 PM, calcular el tiempo hasta las 8 AM del día siguiente
            target_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            # Si es antes de las 8 AM, calcular el tiempo hasta las 8 AM del mismo día
            target_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)

        # Calcular el tiempo de espera
        time_to_wait = (target_time - current_time).total_seconds()

        # Hacer el delay
        print(f"Esperando hasta las 8 AM... {time_to_wait} segundos restantes.")
        time.sleep(time_to_wait)
    else:
        #Mandar el mensaje apropiado para simular que el humano acaba de despertar
        time.sleep(30)
    #despues de esperar lo necesario se manda el audio
    send_audio_mp3_via_twilio(contact_phone,"https://ik.imagekit.io/etqfkh9q2/AudioBienvenidaMp3.mp3")   
    send_conversation_message(conversation_id,"Se envio el audio preguntando por detalles",True)