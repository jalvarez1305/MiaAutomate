from BlastHelper import SendBlast



template_id = 'HX6ae7cdf4452ea019ac2f80d300ed653a'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        id, phone_number
FROM            dbo.CW_Contacts
WHERE        (funel_state = 1) AND (custom_attributes_es_prospecto = 1)""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)