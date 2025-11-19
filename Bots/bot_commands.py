import json
import sys
import os
import logging
import time


# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Blast')))



from BlastHelper import SendBlast
from CW_Conversations import send_conversation_message,send_audio_mp3_via_twilio,get_conversation_custom_attributes,update_conversation_custom_attributes_batch
from CW_Contactos import actualizar_etiqueta,asignar_a_agente,actualizar_lead_source
from SQL_Helpers import GetFreeTime
from Bots_Config import llamada_msg


# Configurar logging
logging.basicConfig(level=logging.INFO)

def BotCommands(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
        contact_phone = Detalles.get('contact_phone')

        #Aqui se evaluan todos los comandos internos a un bot
        if last_message_content == "Cita" or last_message_content == "cita" :
            print(f"AsignaConversacion")
            AsignaConversacion(conversation_id,contact_id)
        elif last_message_content == "Dame un segundito para platicarte de las opciones que manejamos, por favor 🙌":            
            print(f"MandarAudioMenopausia")
            MandarAudioMenopausia(conversation_id,contact_phone,contact_id)
        elif last_message_content == "Reagendar" or last_message_content == "No, reagendar":            
            time.sleep(20)
            send_conversation_message(conversation_id,"con todo gusto hermosa, cuentame que dia te gustaria para tu cita?",False)
        elif last_message_content == "Hola!":  
            actualizar_lead_source(contact_id,"Rosario")          
            time.sleep(20)
            send_conversation_message(conversation_id,"Hola Hermosa, soy Yaneth la asistente de la CLinica y de Rosario, a tus ordenes",False)
        elif last_message_content == "★" or last_message_content == "★★★":     
            print("Tuvimos una mala experiencia")
            # Se asigna la etiqueta de mala experiencia       
            time.sleep(20)            
            send_conversation_message(conversation_id,"Que mal :( que tu experiencia no haya sido fantastica. Me puedes compartir un poco de como podemos hacerla mejor?",False)
            query=f"""SELECT [id]
                        ,[phone_number]
                        ,'{conversation_id}' ConvId
                    FROM [dbo].[CW_Contacts]
                    where id=165"""
            SendBlast("HX7458e441e3c397750e3f147b9b463904",None,query)
        elif last_message_content == "Horarios"or last_message_content == "Agendar cita":            
            print(f"Mandar horarios")
            horarios = GetFreeTime(Consultorio=6)
            if horarios == None:
                send_conversation_message(conversation_id,"@Yaneth Consultorio 6 esta lleno, favor de ofrecer otro dia u otro consultorio",True)
            else:
                time.sleep(20)
                send_conversation_message(conversation_id,horarios,False)
        elif last_message_content.lower() == "humano" or last_message_content.lower() == "ayuda":
            print(f"Solicitud de atención humana")
            # Obtener atributos actuales de la conversación
            attributes = get_conversation_custom_attributes(conversation_id)
            # Actualizar el atributo humano a True
            attributes['humano'] = True
            update_conversation_custom_attributes_batch(conversation_id, attributes)
            # Asignar la conversación a un agente
            asignar_a_agente(conversation_id)
            # Enviar mensaje privado
            send_conversation_message(conversation_id,"Este paciente desea ser atendido por un humano",True)
        elif last_message_content == llamada_msg:  
            actualizar_etiqueta(conversation_id,"citagyne") 
    except Exception as e:
        logging.error(f"Error en bot_commands: {str(e)}")  # Manejo de errores con logging

def AsignaConversacion(conversation_id,paciente_id):
    actualizar_etiqueta(conversation_id,"agendar_cita")
    asignar_a_agente(conversation_id)
    send_conversation_message(conversation_id,f"Paciente numero: {paciente_id}",True)
    send_conversation_message(conversation_id,f"Muchas gracias hermosa 😊, nos vemos en la consulta. Que tengas un lindo día 😉",False)

def MandarAudioMenopausia(conversation_id,contact_phone,contact_id):
    
    # Actualiza el interes del contacto para que entre al funel
    send_conversation_message(conversation_id,"Esperare 30 segundos antes de enviar el audio de menopausia",True)

    time.sleep(30)
    #despues de esperar lo necesario se manda el audio
    send_audio_mp3_via_twilio(contact_phone,"https://ik.imagekit.io/etqfkh9q2/MenopausiaMP3.mp3")   
    send_conversation_message(conversation_id,"""La transición a la menopausia o premenopausia es una etapa que todas las mujeres vamos a vivir 💫 entre los 40 y 53 años de edad.
                                                Podemos experimentar síntomas como:
                                                🔻 Bajo apetito sexual
                                                🌙 Insomnio
                                                🔥 Sequedad vaginal
                                                ⚖️ Aumento de peso

                                                💡 Para todo esto ya existen nuevos tratamientos que ofrecemos en la clínica:
                                                💊 Terapias hormonales
                                                🌱 Tratamientos no hormonales

                                                Una serie de opciones que pueden ayudarte a tener una mejor calidad de vida 💖.

                                                Para poder ofrecerte el tratamiento adecuado, necesitas acudir a una consulta de valoración 👩‍⚕️ donde tu médico hará un historial médico completo 📝 y te dirá si eres candidata a una terapia de reemplazo hormonal 💉 o si, con ciertos cambios en tu estilo de vida 🥗🚶‍♀️, puedes mejorar la situación que estás viviendo.

                                                Estamos para acompañarte en esta etapa 🤝✨""",True)