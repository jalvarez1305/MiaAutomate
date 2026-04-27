import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import execute_query,ExecuteScalar,ejecutar_update
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

def ConfirmarCitaBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
       
        respuesta = """¡Excelente hermosa! 😊💕 Tu cita queda confirmada.

Te pedimos llegar 10 minutos antes. 

⚠️ IMPORTANTE: Solo tenemos 5 minutos de tolerancia.

¡Gracias por tu comprensión! Que tengas un día maravilloso ��✨"""


        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        if last_message_content =="Si,confirmar":
            cmd=f"SELECT top 1 [ID] FROM [dbo].[vw_CalendarEventsExtracted] where [Paciente ID] = {contact_id} order by start_datetime desc"
            ultima_cita=ExecuteScalar(cmd)
            print(f"Ultima cita: {ultima_cita}")
            cmd=f"UPDATE [cal].[CalendarEvents] SET LocalUpdate=1,[summary]= REPLACE([summary], 'Agendada', 'Confirmada') WHERE ID='{ultima_cita}'"
            ejecutar_update(cmd)
            #print(f"update query: {cmd}")
            cmd=f"SELECT [start_datetime],[end_datetime],[LinkReunion] FROM [cal].[CalendarEvents] WHERE ID='{ultima_cita}'"
            cita_data = execute_query(cmd)
            if cita_data is None:
                registros = []
            elif hasattr(cita_data, "to_dict"):
                registros = cita_data.to_dict("records")
            elif isinstance(cita_data, list):
                registros = cita_data
            else:
                try:
                    registros = list(cita_data)
                except TypeError:
                    registros = []

            if len(registros) == 0:
                send_conversation_message(
                    conversation_id,
                    "No se encontró información de la cita para validar fecha y tipo de confirmación.",
                    is_private=True,
                    buzon=ChatwootSenders.Pacientes
                )
            else:
                start_dt = registros[0].get('start_datetime')
                end_dt = registros[0].get('end_datetime')
                link_reunion = registros[0].get('LinkReunion')
                if not start_dt or not end_dt:
                    send_conversation_message(
                        conversation_id,
                        "Faltan start_datetime/end_datetime en la cita para validar tipo de confirmación.",
                        is_private=True,
                        buzon=ChatwootSenders.Pacientes
                    )
                else:
                    duracion_minutos = (end_dt - start_dt).total_seconds() / 60
                    if duracion_minutos < 6:
                        link_reunion = link_reunion or ""
                        respuesta = f"""¡Excelente hermosa! 😊💕 Tu cita queda confirmada.

Te pedimos conectarte 5 minutos antes. 

{link_reunion}

⚠️ IMPORTANTE: Las citas virtuales no tienen tolerancia.

¡Gracias por tu comprensión! Que tengas un día maravilloso ��✨"""
            send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
            RevisaFormularios(conversation_id,contact_id)
        elif last_message_content =="No, reagendar":
            cmd=f"SELECT top 1 [ID] FROM [dbo].[vw_CalendarEventsExtracted] where [Paciente ID] = {contact_id} order by start_datetime desc"
            ultima_cita=ExecuteScalar(cmd)
            print(f"Ultima cita: {ultima_cita}")
            cmd=f"UPDATE [cal].[CalendarEvents] SET LocalUpdate=1,[summary]= 'Cancelada' WHERE ID='{ultima_cita}'"
            ejecutar_update(cmd)
        else:
            send_conversation_message(conversation_id, 'Hola soy Robot, me ayudan con esto?', is_private=True, buzon=ChatwootSenders.Pacientes)
    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging

def RevisaFormularios(conversation_id,contact_id):
    cmd=f"SELECT [MedicoID] FROM [dbo].[vwCalendario_v2] where [Paciente ID] = {contact_id} order by start_datetime desc"
    medico_cita=ExecuteScalar(cmd)
    match medico_cita:
        case 190:  # El ID de chatwoot de la paciente  
            respuesta="""https://forms.gle/vmk42hc1ZM58uqP99

Hola 👋🏻

📌Este cuestionario es parte fundamental de su análisis en la próxima consulta nutricional.

🍉Por favor asegúrese de llenarlo el día que le es enviado o al menos un día previo a la fecha de su consulta 🍇

🫐Tiempo estimado qué le tomara llenarlo: 5 minutos.

¡Gracias!"""
            send_conversation_message(conversation_id, respuesta, is_private=False, buzon=ChatwootSenders.Pacientes)
        case _:
            logging.warning("Bot no reconocido.")