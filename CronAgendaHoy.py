from libs.CW_Automations import SendBlast
from libs.CW_Conversations import ChatwootSenders


template_name = 'agenda_sumary2'
buzon = ChatwootSenders.Medicos  # Instancia de la clase ChatwootSenders
bot_name = 'AgendaMedico'  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        MedicoId,
                    MedicoNickName,
                    'Hoy' as Dia,
                    MIN(FORMAT(start_datetime, 'HH:mm'))  AS Inicio,
                    MAX(FORMAT(start_datetime, 'HH:mm'))  AS Fin
        FROM            dbo.vwCalendario
        WHERE        (CONVERT(date, start_datetime) = CONVERT(date, GETDATE()))
        GROUP BY MedicoID,MedicoNickName""" 

SendBlast(template_name, buzon, bot_name, query,force_new=True)