from libs.CW_Automations import SendBlast
from libs.CW_Conversations import ChatwootSenders


template_name = 'confirmacion'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None # Si no deseas usar un bot, puedes pasar None
query = """SELECT      [Paciente ID],
            Especialidad,
            FORMAT(start_datetime, 'HH:mm') AS Hora,
            UPPER(LEFT(FORMAT(start_datetime, 'dddd', 'es-ES'), 1)) + LOWER(SUBSTRING(FORMAT(start_datetime, 'dddd', 'es-ES'), 2, LEN(FORMAT(start_datetime, 'dddd', 'es-ES')) - 1)) AS Dia,
            FORMAT(start_datetime, 'yyyy-MM-dd') AS Fecha
FROM        dbo.vwCalendario
WHERE       (CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1))""" 

SendBlast(template_name, buzon, bot_name, query,force_new=True)