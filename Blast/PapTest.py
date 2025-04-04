from BlastHelper import SendBlast



template_id = 'HX309b980d72c86b557050c96a5fec1735'
bot_name = None  # Si no deseas usar un bot, puedes pasar None
query = """SELECT 162 id ,'+5213331830952'phone_number,'Dr.Pablo' Doc,'Pablin' Paciente,'2025-04-03' fecha,'C-855-25%20FRANCELI%20GUADALUPE%20SOTO%20HUERTA.pdf?X-Amz-Expires=518400&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAWT4ZPKLYDIBIFAO7%2F20250403%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20250403T191739Z&X-Amz-SignedHeaders=host&X-Amz-Signature=c293927ed29d0eafae45a8dceb758a5a7ac1b0bd2edb93e44c9cdd24f9076dbb' url""" 

#El query lleva, contacto, telefono y parametros
SendBlast(template_id, bot_name=bot_name, query=query)