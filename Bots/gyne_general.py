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
from Bots_Config import audio_gyne,facebook_messages,google_messages
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
horario_aceptada="""Listo, ya reserve tu espacio. Me regalas tu nombre completo para ponerlo en la cita por favor"""
respuesta_ubicacion="""Estamos en el Centro de Tonala 

📍 Vista en Google Maps: https://maps.app.goo.gl/H8zN3RD23J3j1Yyk8 

Domicilio: Av. Tonaltecas #180. 

( Entre la Comisaria de policia 👮🏻y la prepa UNE 🎒,  por la banqueta de enfrente ) 

Te queda cerca?"""
detalles="""dame un segundito para pasarte los detalles del proceso y los precios por favor 🙂"""
precio_menopausia ="""En la consulta de transición a la menopausia (premenopausia)  y Menopausia  🌷evaluaremos el estado actual de tu Organismo a través de  :

-Entrevista especializada completa 📋🩺

-ultrasonido de ovarios para determinar su bienestar  y carga folicular

-ultrasonido de utero o matriz para descartar alguna alteración🖥️

-Exploración y palpación de mamas 🔎

-Realzacion de solicitud 📝 de estudios dirigidos a tu caso en particular para estudio de la Menopáusia

-👩🏻‍⚕️Explicación detallada de esta etapa y sus diversos tratamientos *Hormonales (sintéticos , bioidenticos, naturales ) y

No hormonales , que existen actualmente

Todo esto para ayudarte a vivir esta etapa sin síntomas molestos que deterioran tu salud y tus relaciones personales

El precio de la consulta es de 650 pesos. Y puedes pagar en efectivo , tarjeta o transferencia 😃"""
precio_consulta="""La consulta ginecológica 🌺 consiste en:

1-Historial médico completo para conocerte💻

2-Identificar factores de riesgo para cancer de mama y cervicouterino , menstruaciones anormales etc!

3-Especuloscopia y vaginoscopia para identificar infecciones 🔬

4-Revision e interpretación de exámenes de laboratorio que tengas

5-Receta para  tratamiento a las enfermedades diagnosticadas 📝

Y en caso de requerir Haremos un

-Eco digital de ovarios

-Eco digital de matriz

😃 Y no te preocupes lo haremos sin ningún costo extra! 🙌🏻😃Siempre y cuando se realice el mismo día de la consulta!!☺

El Precio de la consulta ginecológica es de $650 pesos !!

Y puedes pagar en efectivo, transferencia o tarjeta*!! 💳

***en caso de requerir Papanicolaou sería un costo adicional de $200 pesos !"""

segundos_buffer = 30

def GyneGeneralBot(Detalles):
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
        if last_message_content in facebook_messages or last_message_content == audio_gyne:
            MandarMensajeSaludo(conversation_id,contact_phone,contact_id)
            if last_message_content in audio_gyne:
                logging.info(f"Actualizando el lead source a Otro")
                actualizar_lead_source(contact_id,"Otro")
            elif last_message_content in google_messages:
                logging.info(f"Actualizando el lead source a Google")
                actualizar_lead_source(contact_id,"Google")
            else:
                logging.info(f"Actualizando el lead source a Facebook")
                actualizar_lead_source(contact_id,"Facebook")

        else:
            if tiempo > segundos_buffer:
                time.sleep(segundos_buffer)            
                msg_arr=get_AI_conversation_messages(conversation_id)
                respuesta=conv_clasification(msg_arr)
                if respuesta =="Precio consulta":
                    send_conversation_message(conversation_id,detalles,False)
                    time.sleep(20)   
                    send_conversation_message(conversation_id,precio_consulta,False)
                if respuesta =="Precio menopausia":
                    send_conversation_message(conversation_id,detalles,False)
                    time.sleep(20)   
                    send_conversation_message(conversation_id,precio_menopausia,False)
                elif respuesta =="Ubicación":
                    send_conversation_message(conversation_id,respuesta_ubicacion,False)
                elif respuesta =="Acepto cita":
                    send_conversation_message(conversation_id,"cita",True)
                elif respuesta =="Acepto horario" or respuesta =="Ubicación aceptada con horario ofrecido":
                    send_conversation_message(conversation_id,horario_aceptada,False)
                elif respuesta =="Dudas padecimiento":
                    respuesta_padecimiento=ResolverPadecimiento(msg_arr)                    
                    send_conversation_message(conversation_id,respuesta_padecimiento,False)
                    if respuesta_padecimiento == "Dame un segundito para darte la informacion precisa, por favor":
                        send_conversation_message(conversation_id,"Ayuda",True)
                elif respuesta =="Solicita horario con precio" or respuesta =="Solicita horario sin precio" or respuesta =="Ubicación aceptada sin horario ofrecido":
                    horarios = GetFreeTime(Consultorio=6)
                    if horarios == None:
                        send_conversation_message(conversation_id,"@Yaneth Consultorio 6 esta lleno, favor de ofrecer otro dia u otro consultorio",True)
                    else:
                        send_conversation_message(conversation_id,horarios,False)
                elif respuesta =="Solicita horario especifico" or respuesta =="Solicita horario específico":
                    fecha_solicitada=get_requested_date(msg_arr)
                    send_conversation_message(conversation_id,f"Evaluando: {fecha_solicitada}",True)
                    horarios = GetFreeTimeForDate(fecha_solicitada,Consultorio=6)
                    if horarios == None:
                        send_conversation_message(conversation_id,"@Yaneth Consultorio 6 esta lleno, favor de ofrecer otro dia u otro consultorio",True)
                    else:
                        send_conversation_message(conversation_id,horarios,False)
                else:
                    respuesta=f"Categoría: {respuesta}"
                    send_conversation_message(conversation_id,respuesta,True)
            
                #send_conversation_message(conversation_id,respuesta,True)
    except Exception as e:
        logging.error(f"Error en gyne_general: {str(e)}")  # Manejo de errores con logging

def AsignaConversacion(conversation_id):
    actualizar_etiqueta(conversation_id,"agendar_cita")
    asignar_a_agente(conversation_id)

def MandarMensajeSaludo(conversation_id,contact_phone,contact_id):
    
    # Actualiza el interes del contacto para que entre al funel
    send_conversation_message(conversation_id,"Esperare 30 segundos antes de enviar el audio de bien venida",True)
    actualizar_interes_en(contact_id, "https://miaclinicasdelamujer.com/gynecologia")
    actualizar_etiqueta(conversation_id,"citagyne")

    time.sleep(30)
    #despues de esperar lo necesario se manda el audio
    send_audio_mp3_via_twilio(contact_phone,"https://ik.imagekit.io/etqfkh9q2/AudioBienvenidaMp3.mp3")   
    send_conversation_message(conversation_id,"Cuéntame un poquito más ✨ ¿Tienes algún tema en especial que te gustaría revisar en la consulta 🩺💖 o ya te toca tu revisión ginecológica anual? 📅🌸",True)