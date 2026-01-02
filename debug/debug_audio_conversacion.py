"""
Script de debug para analizar por qué una conversación no recibió el audio.

Uso: python debug/debug_audio_conversacion.py <CONVERSATION_ID>
"""

import sys
import os
from dotenv import load_dotenv

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Cargar variables de entorno
load_dotenv()

# Añadir rutas al path - ir a la raíz del proyecto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'libs'))
sys.path.insert(0, os.path.join(root_dir, 'Bots'))
sys.path.insert(0, os.path.join(root_dir, 'AI'))

from libs.CW_Conversations import get_conversation_by_id, get_conversation_messages, get_conversation_custom_attributes, get_AI_conversation_messages
from libs.CW_Contactos import obtener_atributos_contacto
from Bots.helper import es_primer_mensaje_usuario
from Bots.Bots_Config import facebook_messages, google_messages, rosario_messages, revista_messages, audio_gyne
from AI.OpenIAHelper import conv_clasification

def debug_conversacion(conversation_id):
    """
    Analiza una conversación para determinar por qué no se envió el audio.
    """
    print("=" * 80)
    print(f"🔍 DEBUG: Analizando conversación {conversation_id}")
    print("=" * 80)
    print("\n💡 TIP: Si el script se traba, presiona Ctrl+C para interrumpir.")
    print("   El script mostrará la información obtenida hasta ese punto.\n")
    
    # 1. Obtener información de la conversación
    print("\n1️⃣ OBTENIENDO INFORMACIÓN DE LA CONVERSACIÓN...")
    try:
        conv_data = get_conversation_by_id(conversation_id)
        if not conv_data:
            print(f"❌ ERROR: No se pudo obtener la conversación {conversation_id}")
            return
        print("   ✓ Conversación obtenida exitosamente")
    except Exception as e:
        print(f"   ❌ ERROR al obtener conversación: {str(e)}")
        return
    
    labels = conv_data.get('labels', [])
    print(f"   📋 Etiquetas: {labels}")
    
    # Obtener atributos de la conversación
    print("   Obteniendo atributos de conversación...")
    try:
        conv_attributes = get_conversation_custom_attributes(conversation_id)
        print(f"   🔧 Atributos de conversación: {conv_attributes}")
    except Exception as e:
        print(f"   ❌ ERROR al obtener atributos: {str(e)}")
        conv_attributes = {}
    
    audio_enviado = conv_attributes.get('audio_enviado', False)
    primer_mensaje_procesado = conv_attributes.get('primer_mensaje_procesado', False)
    
    print(f"   ✅ audio_enviado: {audio_enviado}")
    print(f"   ✅ primer_mensaje_procesado: {primer_mensaje_procesado}")
    
    # 2. Obtener información del contacto
    print("\n2️⃣ OBTENIENDO INFORMACIÓN DEL CONTACTO...")
    contact_id = None
    contact_name = 'N/A'
    contact_phone = 'N/A'
    
    # Intentar obtener contact_id de múltiples formas (igual que en main_bot.py)
    # Forma 1: Desde conversation_data.contact
    contact_info = conv_data.get('contact', {})
    if contact_info:
        contact_id = contact_info.get('id')
        contact_name = contact_info.get('name', 'N/A')
        contact_phone = contact_info.get('phone_number', 'N/A')
    
    # Forma 2: Desde meta.sender (estructura más común en Chatwoot)
    if not contact_id:
        meta = conv_data.get('meta', {})
        sender = meta.get('sender', {})
        if sender:
            contact_id = sender.get('id')
            contact_name = sender.get('name', 'N/A')
            contact_phone = sender.get('phone_number', 'N/A')
            print("   ✓ Contact ID obtenido desde meta.sender")
    
    if not contact_id:
        print("   ❌ ERROR: No se pudo obtener contact_id")
        print("   Intentando continuar sin contact_id...")
        contact_id = None
    else:
        print(f"   👤 Contact ID: {contact_id}")
        print(f"   👤 Contact Name: {contact_name}")
        print(f"   📞 Phone: {contact_phone}")
    
    # Obtener atributos del contacto
    servicios_recibidos = ''
    if contact_id:
        print("   Obteniendo atributos del contacto...")
        try:
            contact_attrs = obtener_atributos_contacto(contact_id)
            servicios_recibidos = contact_attrs.get('servicios_recibidos', '')
            print(f"   🏥 servicios_recibidos: '{servicios_recibidos}' (vacío: {not servicios_recibidos or servicios_recibidos.strip() == ''})")
        except Exception as e:
            print(f"   ❌ ERROR al obtener atributos del contacto: {str(e)}")
            servicios_recibidos = ''
    else:
        print("   ⚠️ No se puede obtener servicios_recibidos sin contact_id")
    
    # 3. Obtener mensajes
    print("\n3️⃣ ANALIZANDO MENSAJES...")
    try:
        print("   Obteniendo mensajes de la conversación...")
        messages = get_conversation_messages(conversation_id)
        
        if not messages:
            print("   ❌ ERROR: No se encontraron mensajes")
            return
        print(f"   ✓ {len(messages)} mensajes obtenidos")
    except Exception as e:
        print(f"   ❌ ERROR al obtener mensajes: {str(e)}")
        return
    
    # Filtrar mensajes del usuario
    user_messages = [m for m in messages if m.get('Sender') == 'contact']
    print(f"   📨 Total de mensajes: {len(messages)}")
    print(f"   👤 Mensajes del usuario: {len(user_messages)}")
    
    # Verificar si es primer mensaje
    print("   Verificando si es primer mensaje del usuario...")
    es_primer = False
    if contact_id:
        try:
            es_primer = es_primer_mensaje_usuario(conversation_id, contact_id)
            print(f"   🎯 Es primer mensaje del usuario: {es_primer}")
        except Exception as e:
            print(f"   ❌ ERROR al verificar primer mensaje: {str(e)}")
            es_primer = False
    else:
        # Intentar determinar si es primer mensaje basándose en los mensajes obtenidos
        if len(user_messages) == 1:
            es_primer = True
            print(f"   🎯 Es primer mensaje del usuario (inferido de que solo hay 1 mensaje): {es_primer}")
        else:
            print("   ⚠️ No se puede verificar si es primer mensaje sin contact_id")
    
    # Inicializar variables para el diagnóstico
    esta_en_listas = False
    respuesta_ia = None
    es_saludo_inicial = False
    
    # Obtener el primer mensaje del usuario
    if user_messages:
        primer_mensaje = user_messages[0]
        primer_mensaje_content = primer_mensaje.get('Content', '')
        print(f"\n   📝 Primer mensaje del usuario:")
        print(f"      '{primer_mensaje_content}'")
        
        # 4. Verificar si está en listas conocidas
        print("\n4️⃣ VERIFICANDO LISTAS CONOCIDAS...")
        esta_en_facebook = primer_mensaje_content in facebook_messages
        esta_en_google = primer_mensaje_content in google_messages
        esta_en_rosario = primer_mensaje_content in rosario_messages
        esta_en_revista = primer_mensaje_content in revista_messages
        es_audio_gyne = primer_mensaje_content in audio_gyne
        
        print(f"   📌 En facebook_messages: {esta_en_facebook}")
        print(f"   📌 En google_messages: {esta_en_google}")
        print(f"   📌 En rosario_messages: {esta_en_rosario}")
        print(f"   📌 En revista_messages: {esta_en_revista}")
        print(f"   📌 Es audio_gyne: {es_audio_gyne}")
        
        esta_en_listas = esta_en_facebook or esta_en_google or esta_en_rosario or esta_en_revista or es_audio_gyne
        print(f"\n   ✅ Está en alguna lista conocida: {esta_en_listas}")
        
        # 5. Clasificación por IA
        print("\n5️⃣ CLASIFICACIÓN POR IA...")
        print("   Obteniendo mensajes para IA (esto puede tardar)...")
        respuesta_ia = None
        es_saludo_inicial = False
        try:
            msg_arr = get_AI_conversation_messages(conversation_id)
            if msg_arr:
                print(f"   ✓ {len(msg_arr)} mensajes obtenidos para IA")
                print("   Clasificando con IA (esto puede tardar 10-30 segundos)...")
                respuesta_ia = conv_clasification(msg_arr)
                print(f"   🤖 Clasificación IA: '{respuesta_ia}'")
                es_saludo_inicial = respuesta_ia == "Saludo inicial"
                print(f"   ✅ Es 'Saludo inicial': {es_saludo_inicial}")
            else:
                print("   ⚠️ No se pudieron obtener mensajes para IA")
        except KeyboardInterrupt:
            print("\n   ⚠️ Interrumpido por el usuario (Ctrl+C)")
            print("   Continuando sin clasificación IA...")
            respuesta_ia = None
            es_saludo_inicial = False
        except Exception as e:
            print(f"   ❌ Error al clasificar con IA: {str(e)}")
            print(f"   Tipo de error: {type(e).__name__}")
            respuesta_ia = None
            es_saludo_inicial = False
    
    # 6. Análisis de condiciones
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE CONDICIONES")
    print("=" * 80)
    
    tiene_citagyne = "citagyne" in labels
    servicios_vacio = not servicios_recibidos or servicios_recibidos.strip() == ''
    
    print(f"\n✅ Tiene etiqueta citagyne: {tiene_citagyne}")
    print(f"✅ Es primer mensaje: {es_primer}")
    print(f"✅ servicios_recibidos está vacío: {servicios_vacio}")
    print(f"✅ audio_enviado: {audio_enviado}")
    print(f"✅ Está en listas conocidas: {esta_en_listas if user_messages else 'N/A'}")
    print(f"✅ IA clasificó como 'Saludo inicial': {es_saludo_inicial if user_messages else 'N/A'}")
    
    # 7. Diagnóstico
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO")
    print("=" * 80)
    
    if esta_en_listas and user_messages:
        print("\n✅ RAZÓN ESPERADA: El mensaje está en listas conocidas")
        print("   → Debería enviarse audio directamente")
        if not audio_enviado:
            print("   ⚠️ PROBLEMA: audio_enviado = False, pero debería estar en True")
            print("   Posibles causas:")
            print("   - Error en MandarMensajeSaludo()")
            print("   - El mensaje no entró al bloque if de facebook_messages")
    elif es_primer and not audio_enviado:
        if es_saludo_inicial:
            print("\n✅ RAZÓN ESPERADA: Es primer mensaje y IA detectó 'Saludo inicial'")
            print("   → Debería enviarse audio")
            print("   ⚠️ PROBLEMA: No se envió el audio")
            print("   Posibles causas:")
            print("   - Error en la clasificación de IA")
            print("   - No se ejecutó el bloque else en GyneGeneralBot")
            print("   - Error al llamar MandarMensajeSaludo()")
        else:
            print("\n❌ RAZÓN DEL PROBLEMA: Es primer mensaje pero IA NO clasificó como 'Saludo inicial'")
            print(f"   → Clasificación actual: '{respuesta_ia if user_messages else 'N/A'}'")
            print("   Soluciones posibles:")
            print("   1. Agregar el mensaje a las listas conocidas")
            print("   2. Mejorar la categoría 'Saludo inicial' en OpenIAHelper.py")
            print("   3. Verificar si el mensaje realmente es un saludo inicial")
    elif audio_enviado:
        print("\n✅ RAZÓN: audio_enviado ya está en True")
        print("   → El audio ya fue enviado (o marcado como enviado)")
    else:
        print("\n❓ RAZÓN DESCONOCIDA: No se cumplen las condiciones esperadas")
        print("   Revisar lógica en gyne_general.py")
    
    # 8. Verificar condiciones para citagyne
    print("\n" + "=" * 80)
    print("🔖 VERIFICACIÓN ETIQUETA citagyne")
    print("=" * 80)
    
    if tiene_citagyne:
        print("✅ La conversación ya tiene la etiqueta citagyne")
    else:
        print("❌ La conversación NO tiene la etiqueta citagyne")
        if es_primer and servicios_vacio and not primer_mensaje_procesado:
            print("   → Debería asignarse (cumple condiciones)")
            print("   ⚠️ PROBLEMA: No se asignó la etiqueta")
        elif primer_mensaje_procesado:
            print("   ℹ️ Ya se procesó el primer mensaje, no se asignará automáticamente")
        elif not servicios_vacio:
            print(f"   ℹ️ El contacto tiene servicios_recibidos: '{servicios_recibidos}'")
    
    print("\n" + "=" * 80)
    print("✅ DEBUG COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug/debug_audio_conversacion.py <CONVERSATION_ID>")
        sys.exit(1)
    
    conversation_id = int(sys.argv[1])
    debug_conversacion(conversation_id)
