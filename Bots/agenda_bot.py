import sys
import os
import logging

# Añadir la ruta a libs al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../libs')))
from CW_Conversations import send_conversation_message, ChatwootSenders, envia_mensaje_plantilla, remove_bot_attribute
from SQL_Helpers import GetParametersFromQuery,ExecuteScalar
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)

def AgendaBot(Detalles):
    try:
        # Verifica que las claves existan en Detalles        
        last_message = Detalles.get("last_message", {})
        last_message_content = last_message.get('Content')
        conversation_id = Detalles.get('conversation_id')
        contact_id = Detalles.get('contact_id')
        # Obtener la hora actual
        current_hour = datetime.now().hour
        dia = "Hoy" if current_hour < 16 else "Mañana"
        dia_condition = "CONVERT(date, start_datetime) = CONVERT(date, GETDATE())" if current_hour < 16 else "CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1)"
        
        plantilla_body = """Hola {{1}}, este es un resumen de tus citas de {{2}}:
{{3}}
Saludos!"""

        query = f"""
                SELECT 
                    STRING_AGG(Citas,'\n') as Agenda
                FROM 
                    (
                        SELECT top 100
                            [MedicoNickName],
                            CONCAT(
                                FORMAT(start_datetime, 'HH:mm'), 
                                ' - ', -- Añadido un separador para mejor legibilidad
                                [Paciente], 
                                ' - ', -- Añadido un separador para mejor legibilidad
                                CASE 
                                    WHEN [Status Paciente] = 0 THEN 'Agendada' 
                                    ELSE 'Confirmada' 
                                END,
								' - ',
								Notas
                            ) AS Citas
                        FROM 
                            [dbo].[vwCalendario]
                        WHERE 
                            MedicoId = {contact_id} 
                            AND {dia_condition} 
                        ORDER BY start_datetime
                    ) as concatedCitas
                GROUP BY 
                    [MedicoNickName]
                """
        agenda=ExecuteScalar(query)

        # Validar que las claves necesarias estén presentes
        if conversation_id is None:
            logging.error("conversation_id no está presente en Detalles.")
            return
        
        else:
            logging.info(f"Enviando respuesta afirmativa para la conversación {conversation_id}.")
            send_conversation_message(conversation_id, agenda, is_private=False, buzon=ChatwootSenders.Medicos)
            remove_bot_attribute(conversation_id)

    except Exception as e:
        logging.error(f"Error en AgendaBot: {str(e)}")  # Manejo de errores con logging
