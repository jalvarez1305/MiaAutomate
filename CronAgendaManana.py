from Blast.BlastHelper import SendBlast

template_id = 'HXa82203dc7113b22d92bbb1269ad0aa89'
bot_name = "AgendaMedico"   # Si no deseas usar un bot, puedes pasar None
query = """SELECT        MedicoId,
			medico_phone,
            MedicoNickName,
            'Mañana' as Dia,
            MIN(FORMAT(start_datetime, 'HH:mm'))  AS Inicio,
            MAX(FORMAT(start_datetime, 'HH:mm'))  AS Fin
FROM            dbo.vwCalendario
WHERE        (CONVERT(date, start_datetime) = CONVERT(date, GETDATE() + 1))
GROUP BY MedicoID,medico_phone,MedicoNickName""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)