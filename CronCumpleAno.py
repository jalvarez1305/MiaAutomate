from Blast.BlastHelper import SendBlast

template_id = 'HX5911d6b0e0c33f027b5473b447d6c84f'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT Cont.[id],
		Cont.phone_number,
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

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)