from Blast.BlastHelper import SendBlast

template_id = 'HX10064a7fff83ee65ddc83eb726ba07a0'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        MedicoId,
					medico_phone,
                    MedicoNickName,
                    'Hoy' as Dia,
                    MIN(FORMAT(start_datetime, 'HH:mm'))  AS Inicio,
                    MAX(FORMAT(start_datetime, 'HH:mm'))  AS Fin
        FROM            dbo.vwCalendario
        WHERE        (CONVERT(date, start_datetime) = CONVERT(date, GETDATE()))
        GROUP BY MedicoID,medico_phone,MedicoNickName""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)