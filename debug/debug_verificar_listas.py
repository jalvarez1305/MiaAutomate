"""
Script para verificar si un mensaje está en alguna de las listas conocidas.

Uso: python debug/debug_verificar_listas.py "mensaje a verificar"
"""

import sys
import os

# Añadir rutas al path - ir a la raíz del proyecto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'Bots'))

from Bots.Bots_Config import facebook_messages, google_messages, rosario_messages, revista_messages, audio_gyne

def verificar_mensaje_en_listas(mensaje):
    """
    Verifica si un mensaje está en alguna de las listas conocidas.
    """
    print("=" * 80)
    print(f"🔍 VERIFICANDO MENSAJE EN LISTAS")
    print("=" * 80)
    print(f"\n📝 Mensaje a verificar:")
    print(f"   '{mensaje}'")
    print("\n" + "-" * 80)
    
    # Verificar en cada lista
    esta_en_facebook = mensaje in facebook_messages
    esta_en_google = mensaje in google_messages
    esta_en_rosario = mensaje in rosario_messages
    esta_en_revista = mensaje in revista_messages
    es_audio_gyne = mensaje in audio_gyne
    
    print("\n📋 RESULTADOS:")
    print(f"   facebook_messages: {esta_en_facebook}")
    if esta_en_facebook:
        indice = facebook_messages.index(mensaje)
        print(f"      → Encontrado en índice {indice}")
        print(f"      → Valor exacto: '{facebook_messages[indice]}'")
    
    print(f"\n   google_messages: {esta_en_google}")
    if esta_en_google:
        indice = google_messages.index(mensaje)
        print(f"      → Encontrado en índice {indice}")
        print(f"      → Valor exacto: '{google_messages[indice]}'")
    
    print(f"\n   rosario_messages: {esta_en_rosario}")
    if esta_en_rosario:
        indice = rosario_messages.index(mensaje)
        print(f"      → Encontrado en índice {indice}")
        print(f"      → Valor exacto: '{rosario_messages[indice]}'")
    
    print(f"\n   revista_messages: {esta_en_revista}")
    if esta_en_revista:
        indice = revista_messages.index(mensaje)
        print(f"      → Encontrado en índice {indice}")
        print(f"      → Valor exacto: '{revista_messages[indice]}'")
    
    print(f"\n   audio_gyne: {es_audio_gyne}")
    if es_audio_gyne:
        indice = audio_gyne.index(mensaje)
        print(f"      → Encontrado en índice {indice}")
        print(f"      → Valor exacto: '{audio_gyne[indice]}'")
    
    esta_en_alguna = esta_en_facebook or esta_en_google or esta_en_rosario or esta_en_revista or es_audio_gyne
    
    print("\n" + "=" * 80)
    if esta_en_alguna:
        print("✅ El mensaje ESTÁ en alguna lista conocida")
        print("   → Se enviará audio directamente (bloque if en gyne_general.py)")
    else:
        print("❌ El mensaje NO está en ninguna lista conocida")
        print("   → Solo se enviará audio si:")
        print("     1. Es el primer mensaje del usuario")
        print("     2. No tiene audio_enviado = True")
        print("     3. La IA clasifica como 'Saludo inicial'")
    print("=" * 80)
    
    # Mostrar mensajes similares si no está en ninguna lista
    if not esta_en_alguna:
        print("\n💡 MENSAJES SIMILARES EN LAS LISTAS:")
        mensaje_lower = mensaje.lower().strip()
        
        similares = []
        for lista_nombre, lista in [
            ("facebook_messages", facebook_messages),
            ("google_messages", google_messages),
            ("rosario_messages", rosario_messages),
            ("revista_messages", revista_messages),
            ("audio_gyne", audio_gyne)
        ]:
            for msg in lista:
                if mensaje_lower in msg.lower() or msg.lower() in mensaje_lower:
                    similares.append((lista_nombre, msg))
        
        if similares:
            for lista_nombre, msg in similares[:5]:  # Mostrar solo los primeros 5
                print(f"   - [{lista_nombre}] '{msg}'")
        else:
            print("   No se encontraron mensajes similares")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug/debug_verificar_listas.py \"mensaje a verificar\"")
        sys.exit(1)
    
    mensaje = sys.argv[1]
    verificar_mensaje_en_listas(mensaje)
