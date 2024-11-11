from libs.CW_Automations import SendBlast
from libs.CW_Conversations import ChatwootSenders


template_name = 'cumple_ano'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None # Si no deseas usar un bot, puedes pasar None
query = """SELECT Cont.[id],
       Cont.custom_attributes_nickname,
	   coalesce((SELECT top 1 
						Med.custom_attributes_nickname
				FROM [dbo].[Consultas] Con with (nolock) 
					inner join [dbo].[CW_Contacts] Med with (nolock)
				on Con.[Medico_FK] = Med.Id
				WHERE Paciente_FK = Cont.[id]
				order by Con.[Inicio Real] desc),'Rosario') as Medico
FROM [dbo].[CW_Contacts] Cont with (nolock)
WHERE 	
		MONTH(custom_attributes_cumple) = MONTH(GETDATE())
  AND DAY(custom_attributes_cumple) = DAY(GETDATE())""" 

SendBlast(template_name, buzon, bot_name, query,force_new=False)