mensaje = """Hola 😃 aquí el resultado de tu Papanicolaou: En el , No hay datos de infección de virus del papiloma humano (VPH) 🤗 así que estamos tranquilas , te puede aparecer una moderada inflamación (cervicitis ) que es posible sea por el cepillado , por el día del ciclo o por baja hormonal , lo cual es normal y no es nada de que preocuparnos !! Ya solo tu control anual 🌺



📎 Ver resultado: https://is.gd/pmXzrV



"""

print(f"Total de caracteres: {len(mensaje)}")
print(f"Caracteres sin espacios: {len(mensaje.replace(' ', ''))}")
print(f"Caracteres sin espacios ni saltos de línea: {len(mensaje.replace(' ', '').replace(chr(10), '').replace(chr(13), ''))}")

