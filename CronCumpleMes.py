from libs.CW_Automations import send_blast_image
from libs.CW_Conversations import ChatwootSenders


template_name = 'cumple_mes'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT [id]
      ,[phone_number]
      ,[name]
  FROM [Clinica].[dbo].[CW_Contacts]
  WHERE MONTH(custom_attributes_cumple) = MONTH(GETDATE())""" 

#El query lleva, contacto, telefono y parametros
send_blast_image(template_name, bot_name=bot_name, query=query)