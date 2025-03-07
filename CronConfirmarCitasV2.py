import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Automations import SendBlast
from CW_Conversations import ChatwootSenders


template_name = 'confirmar_v2'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = "ConfirmarCitaBot" # Si no deseas usar un bot, puedes pasar None
query = """SELECT      [Paciente ID],
            Especialidad,
            FORMAT(start_datetime, 'HH:mm') AS Hora,
            UPPER(LEFT(FORMAT(start_datetime, 'dddd', 'es-ES'), 1)) + LOWER(SUBSTRING(FORMAT(start_datetime, 'dddd', 'es-ES'), 2, LEN(FORMAT(start_datetime, 'dddd', 'es-ES')) - 1)) AS Dia,
            FORMAT(start_datetime, 'yyyy-MM-dd') AS Fecha,
			[MedicoNickName],
			case 
				when Especialidad = 'Cita Ginecologia' then 'Ropa ligera como vestido y zapatos facil de retirar como sandalia'
				when Especialidad = 'Cita Nutricion' then ''
				else ''
			END as Recomendaciones
FROM        dbo.vwCalendario
WHERE       (CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1))
and [Status Paciente]=0""" 

SendBlast(template_name, buzon, bot_name, query,force_new=True)