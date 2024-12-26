import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Automations import SendBlast
from CW_Conversations import ChatwootSenders


template_name = 'paciente_retrasada'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None # Si no deseas usar un bot, puedes pasar None
query = """SELECT 
                [Paciente ID], 
                LEFT([Paciente], CHARINDEX(' ', [Paciente] + ' ') - 1) AS PrimerNombre
            FROM 
                [dbo].[vwCalendario]
            WHERE 
                DATEDIFF(MINUTE, [start_datetime], GETDATE()) > 3
                AND DATEDIFF(MINUTE, [start_datetime], GETDATE()) < 15
                AND CONVERT(DATE, [start_datetime]) = CONVERT(DATE, GETDATE())
                AND [EstatusGeneral] = 0""" 

SendBlast(template_name, buzon, bot_name, query,force_new=True)