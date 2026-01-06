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
from CW_Conversations import send_conversation_message,send_audio_mp3_via_twilio,get_conversation_custom_attributes,update_conversation_custom_attributes_batch,get_conversation_by_id,get_AI_conversation_messages
from CW_Contactos import actualizar_etiqueta,asignar_a_agente,actualizar_lead_source
from SQL_Helpers import GetFreeTime,ejecutar_update
from Bots_Config import llamada_msg
from openai import OpenAI
import os


# Configurar logging
logging.basicConfig(level=logging.INFO)

# Configurar OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gpt_model = "gpt-4o"

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
        elif last_message_content.lower() == "tarea":
            print(f"Creando tarea para conversación {conversation_id}")
            CrearTarea(conversation_id, contact_id)
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

def generar_resumen_necesidades(conversation_id):
    """
    Genera un resumen de lo que la paciente necesita usando OpenAI
    """
    try:
        # Obtener los mensajes de la conversación
        msg_arr = get_AI_conversation_messages(conversation_id)
        
        if not msg_arr or len(msg_arr) == 0:
            return "No se pudo obtener información de la conversación"
        
        # Formatear la conversación para el prompt
        conversacion_formateada = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in msg_arr])
        
        # Crear el prompt para generar el resumen
        prompt = """Analiza esta conversación y genera un resumen breve y conciso (máximo 2-3 oraciones) de lo que la paciente SOLICITÓ y que está PENDIENTE de responder o resolver.
        
        IMPORTANTE: 
        - NO hagas un resumen general de la conversación
        - Identifica específicamente qué pidió o solicitó la paciente
        - Identifica qué está pendiente de respuesta o acción
        - Enfócate solo en lo que falta por resolver, no en lo que ya se respondió
        
        Ejemplos de lo que debes identificar:
        - Si pidió información sobre un procedimiento y aún no se le dio respuesta completa
        - Si solicitó un horario específico y está pendiente
        - Si tiene una duda médica que no se resolvió
        - Si necesita algo específico que aún no se le proporcionó
        
        Responde solo con el resumen de lo pendiente, sin explicaciones adicionales."""
        
        response = client.responses.create(
            model=gpt_model,
            input=[
                {"role": "system", "content": "Eres un asistente que resume conversaciones médicas de forma clara y concisa."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": f"Conversación:\n\n{conversacion_formateada}"}
            ],
            temperature=0.3
        )
        
        resumen = response.output_text.strip()
        return resumen
        
    except Exception as e:
        logging.error(f"Error al generar resumen: {str(e)}")
        return "No se pudo generar resumen de la conversación"

def CrearTarea(conversation_id, contact_id):
    """
    Crea una tarea en la base de datos y etiqueta la conversación con 'tarea'
    """
    try:
        # 1. Etiquetar la conversación con "tarea"
        actualizar_etiqueta(conversation_id, "tarea")
        logging.info(f"Etiqueta 'tarea' asignada a conversación {conversation_id}")
        
        # 2. Obtener el nombre del contacto/paciente
        contact_name = "Sin nombre"
        try:
            conv_data = get_conversation_by_id(conversation_id)
            if conv_data:
                # Intentar obtener el nombre desde contact
                contact_info = conv_data.get('contact', {})
                if contact_info:
                    contact_name = contact_info.get('name', 'Sin nombre')
                
                # Si no se encontró, intentar desde meta.sender
                if contact_name == "Sin nombre":
                    meta = conv_data.get('meta', {})
                    sender = meta.get('sender', {})
                    if sender:
                        contact_name = sender.get('name', 'Sin nombre')
        except Exception as e:
            logging.error(f"Error al obtener nombre del contacto: {str(e)}")
            contact_name = "Sin nombre"
        
        # 3. Generar resumen de lo que la paciente necesita
        resumen = generar_resumen_necesidades(conversation_id)
        logging.info(f"Resumen generado: {resumen}")
        
        # 4. Construir la URL de la conversación
        descripcion_url = f"https://whatsapp.credi-motos.com/app/accounts/1/conversations/{conversation_id}"
        
        # 5. Construir la descripción completa con resumen y link
        descripcion_completa = f"{resumen}\n\nLink: {descripcion_url}"
        
        # 6. Construir el título (solo el nombre del contacto)
        titulo = contact_name
        
        # 7. Construir el query INSERT
        # Escapar comillas simples en el nombre y la descripción
        titulo_escaped = titulo.replace("'", "''")
        descripcion_escaped = descripcion_completa.replace("'", "''")
        
        insert_query = f"""INSERT INTO [dbo].[Tareas] 
                           ([Titulo], [Descripcion], [Comentarios], [Fecha de Creacion], [Fecha de entrega], [is_finish])
                           VALUES 
                           ('{titulo_escaped}', '{descripcion_escaped}', NULL, GETDATE(), DATEADD(HOUR, 1, GETDATE()), 0)"""
        
        # 8. Ejecutar el INSERT
        ejecutar_update(insert_query)
        logging.info(f"Tarea creada exitosamente para conversación {conversation_id}")
        
        # 9. Enviar mensaje de confirmación
        send_conversation_message(conversation_id, f"✅ Tarea creada: {titulo}", True)
        
    except Exception as e:
        logging.error(f"Error al crear tarea: {str(e)}")
        send_conversation_message(conversation_id, f"❌ Error al crear la tarea: {str(e)}", True)