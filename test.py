from libs.CW_Automations import send_blast_image

template_name="med_day_2024"
query="""SELECT [id]
      ,[phone_number]
      ,[custom_attributes_nickname]
  FROM [Clinica].[dbo].[CW_Contacts]
  where [custom_attributes_cliente] ='Medico'"""

send_blast_image(template_name=template_name, bot_name=None, query=query)