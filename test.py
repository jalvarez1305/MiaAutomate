"""
Probar get_open_conversation
if __name__ == "__main__":
    contact_id = 181  # El ID del contacto que deseas probar
    conversation_id = get_open_conversation(contact_id)
    print(f"Conversation ID: {conversation_id}")
"""

"""
Probar enviar mensaje

if __name__ == "__main__":
    conversation_id = 537  # Reemplaza con un ID de conversación válido
    message = "Hola, @Pablo este es un mensaje de prueba, privado."  # Mensaje que deseas enviar
    is_private = True  # Puedes cambiarlo a True si el mensaje es privado
    buzon = ChatwootSenders.Pacientes  # O ChatwootSenders.Medicos, según sea necesario

    # Llamar a la función para enviar el mensaje
    send_conversation_message(conversation_id, message, is_private, buzon)
"""

'''
contacto_id = 162  # Reemplaza con el ID del contacto
plantilla = """Hola {{1}}, queremos ser siempre mejores para ti. Nos podrias decir como calificarías la atención brindada por tu medico {{2}}?

por favor"""
parametros = ["Juan", "de parte de la clínica."]
buzon = ChatwootSenders.Pacientes  # O ChatwootSenders.Medicos
bot_name = "Notificacion"

envia_mensaje_plantilla(contacto_id, plantilla, parametros, buzon, bot_name)
'''
'''
query = """
SELECT TOP (1000) [ID],
      [Descripcion],
      [Comision]
  FROM [Clinica].[dbo].[MetodosPago]
"""

# Ejecutar la consulta y obtener el resultado como DataFrame
result = execute_query(query)

if result is not None:
    print(result)
else:
    print("No se obtuvieron resultados o el resultado no es una tabla.")
'''
'''
template_name = 'agenda_manana'
body = get_template_body(template_name)
if body:
    print(f"El Body de la plantilla '{template_name}' es: {body}")
else:
    print(f"No se encontró el Body de la plantilla '{template_name}'.")
'''




from libs.CW_Automations import SendBlast
from libs.CW_Conversations import ChatwootSenders


template_name = 'agenda_sumary2'
buzon = ChatwootSenders.Medicos  # Instancia de la clase ChatwootSenders
bot_name = 'AgendaMedico'  # Si no deseas usar un bot, puedes pasar None
query = """SELECT 162 as ContactID,'Pablo' Nombre,'Mañana' Dia,'13:20' Inicio,'14:19' Fin"""

SendBlast(template_name, buzon, bot_name, query)



#send_content_builder("+523331830952", "HXf242a71276efc4d46ac93f6d9e9f2055", "https://res.cloudinary.com/dkh1fgvnb/image/upload/v1728746286/cm_iavwfa.jpg", "Cuidate del cancer, por favor")


# Ejemplo de uso:
# send_blast_image("HX4780f22a4a93827a4f37e9e003bbf76d", "NombreBot", "SELECT contacto_id, telefono, param1, param2, param3 FROM tu_tabla")



