import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Automations import send_blast_image
from CW_Conversations import ChatwootSenders

template_name = 'copy_relleno_labio_state_25'
buzon = ChatwootSenders.Pacientes  # Instancia de la clase ChatwootSenders
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT        TOP (200) id, phone_number, name
FROM            CW_Contacts
WHERE        (custom_attributes_es_prospecto = 1) AND (custom_attributes_interes_en = 'https://miaclinicasdelamujer.com/aumento-labios/')""" 

#El query lleva, contacto, telefono y parametros
send_blast_image(template_name, bot_name=bot_name, query=query)