
from Blast.BlastHelper import SendBlast

template_id = 'HX4675e2d228c6f2bc2e99e06a4e702a70'
bot_name = "ConfirmarCitaBot"   # Si no deseas usar un bot, puedes pasar None
query = """SELECT      [Paciente ID],
			phone_number,
            Especialidad,
            UPPER(LEFT(FORMAT(start_datetime, 'dddd', 'es-ES'), 1)) + LOWER(SUBSTRING(FORMAT(start_datetime, 'dddd', 'es-ES'), 2, LEN(FORMAT(start_datetime, 'dddd', 'es-ES')) - 1)) AS Dia,
            FORMAT(start_datetime, 'yyyy-MM-dd') AS Fecha,
            FORMAT(start_datetime, 'HH:mm') AS Hora,
			[MedicoNickName],
			case 
				when Especialidad = 'Ginecologia' then 'Ropa ligera como vestido y zapatos facil de retirar como sandalia'
				when Especialidad = 'Cita Nutricion' then 'No aplica'
				else 'No aplica'
			END as Recomendaciones
FROM        dbo.vwCalendario
WHERE       (CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1))
		and Not [Paciente ID] is null
		and not phone_number is null
and [Status Paciente]=0""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)