import sys
import os
import logging
import time

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Blast')))
from BlastHelper import SendBlast
from CW_Conversations import send_conversation_message, ChatwootSenders,send_audio_mp3_via_twilio, envia_mensaje_plantilla, remove_bot_attribute
from CW_Contactos import actualizar_interes_en,actualizar_etiqueta
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update
from CW_Automations import send_content
from Bots_Config import saludo_facebook,audio_gyne
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

def BotPaps(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
        contact_phone = Detalles.get('contact_phone')
       

        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content =='2.- PAP Negativo (receta)':
            logging.info("2.- PAP Negativo (receta)")
            NotificarPaciente('HXeb3ba5c4af5c76775adea115755ab53e',contact_id)#Pap negativo con receta
            time.sleep(5)
            send_conversation_message(conversation_id, "Me puede compartir la receta, por favor", is_private=False, buzon=ChatwootSenders.Pacientes)
        """
        if last_message_content == saludo_facebook or last_message_content == audio_gyne:
            MandarMensajeSaludo(conversation_id,contact_phone,contact_id)
        elif last_message_content == 'Domicilio':
            send_conversation_message(conversation_id, respuesta_ubicacion, is_private=False, buzon=ChatwootSenders.Pacientes)
        else:
            send_conversation_message(conversation_id, 'Hola soy Robot, me ayudan con esto?', is_private=True, buzon=ChatwootSenders.Pacientes)
        """
    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging

def NotificarPaciente(template_sid, Medico_FK):
    
    template_id = template_sid
    bot_name = None  # Si no deseas usar un bot, puedes pasar None
    query = f"""SELECT        Cont.id, Cont.phone_number, REPLACE(Paps.[presigned url], 'https://papanicolaous.s3.us-east-2.amazonaws.com/', '') AS url
                FROM            dbo.Papanicolaous AS Paps WITH (NOLOCK) INNER JOIN
                                        dbo.CW_Contacts AS Cont WITH (nolock) ON Paps.Paciente_FK = Cont.id
                WHERE        (Paps.Medico_FK = {Medico_FK}) AND (Paps.Estatus = N'Enviada al Medico')""" 

    #El query lleva, contacto, telefono y parametros
    SendBlast(template_id, bot_name=None, query=query)