import json
import sys
import os
import logging
import time


# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI')))


from GinecologiaAI import ResolverPadecimiento
from OpenIAHelper import conv_clasification,get_requested_date
from CW_Conversations import send_conversation_message, ChatwootSenders,send_audio_mp3_via_twilio, envia_mensaje_plantilla, remove_bot_attribute,get_AI_conversation_messages,segundos_entre_ultimos_mensajes
from CW_Contactos import actualizar_interes_en,actualizar_etiqueta,asignar_a_agente,actualizar_lead_source
from SQL_Helpers import GetFreeTime,GetFreeTimeForDate
from CW_Automations import send_content
from Bots_Config import labioplastia_messages
from datetime import datetime

# Configurar logging

segundos_buffer = 30

def Labioplastia_Bot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
        contact_phone = Detalles.get('contact_phone')
        tiempo = segundos_entre_ultimos_mensajes(conversation_id)
        print(f"Tiempo entre mensajes: {tiempo}")
        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content in labioplastia_messages:
            MandarMensajeSaludo(conversation_id,contact_phone,contact_id)
            actualizar_lead_source(contact_id,"Rosario")
            AsignaConversacion(conversation_id)
        else:
           print(f"Todo")
    except Exception as e:
        logging.error(f"Error en Constelaciones_Bot: {str(e)}")  # Manejo de errores con logging

def AsignaConversacion(conversation_id):
    asignar_a_agente(conversation_id)

def MandarMensajeSaludo(conversation_id,contact_phone,contact_id):
    
    # Actualiza el interes del contacto para que entre al funel
    send_conversation_message(conversation_id,"Esperare 30 segundos antes de enviar el audio de bien venida a labioplastia",True)
    actualizar_interes_en(contact_id, "https://www.miaclinicasdelamujer.com/labioplastia/")
    actualizar_etiqueta(conversation_id,"labioplastia")

    time.sleep(30)
    #despues de esperar lo necesario se manda el audio
    send_audio_mp3_via_twilio(contact_phone,"https://ik.imagekit.io/etqfkh9q2/LabioPlastiaMp3.mp3")   
    send_conversation_message(conversation_id,"""Hola 😊
                                                Cuéntame un poquito más sobre tu inquietud con la labioplastía.

                                                Es un procedimiento ginecológico-estético en el que, aquí en el consultorio, realizamos un corte muy preciso en los labios menores para mejorar la apariencia de la vulva ✨

                                                Platícame:
                                                — ¿Te incomodan por infecciones frecuentes?
                                                — ¿Molestias con la ropa?
                                                — ¿Dificultad o dolor en el acto sexual?
                                                — ¿O simplemente no te gusta cómo lucen y te gustaría mejorar su apariencia?

                                                Estoy aquí para resolver todas tus dudas con confianza y respeto 💖""",True)