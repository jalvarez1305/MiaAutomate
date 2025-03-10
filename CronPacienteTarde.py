from Blast.BlastHelper import SendBlast

template_id = 'HXad2c917455923d73ccebce2f9d915f6f'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT 
                [Paciente ID], 
				phone_number,
                LEFT([Paciente], CHARINDEX(' ', [Paciente] + ' ') - 1) AS PrimerNombre
            FROM 
                [dbo].[vwCalendario]
            WHERE 
                DATEDIFF(MINUTE, [start_datetime], GETDATE()) > 3
                AND DATEDIFF(MINUTE, [start_datetime], GETDATE()) < 15
                AND CONVERT(DATE, [start_datetime]) = CONVERT(DATE, GETDATE())
                AND [EstatusGeneral] = 0
                ANd not [Paciente ID] is null"""

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)