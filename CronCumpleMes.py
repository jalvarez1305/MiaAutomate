from Blast.BlastHelper import SendBlast

template_id = 'HXd881c200c7b75a813bc8509bc7b63e2c'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT [id]
      ,[phone_number]
      ,[name]
  FROM [Clinica].[dbo].[CW_Contacts]
  WHERE MONTH(custom_attributes_cumple) = MONTH(GETDATE())""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)