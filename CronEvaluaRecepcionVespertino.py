from Blast.BlastHelper import SendBlast

template_id = 'HX768f5ddd324413bc9adb3f076361c5ed'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        id, phone_number
            FROM            dbo.CW_Contacts
            WHERE        (id = 163)"""

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)