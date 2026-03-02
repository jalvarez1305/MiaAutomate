# Herramientas de Debug - Sistema de Audio y Etiquetado

Esta carpeta contiene herramientas para debuggear problemas relacionados con:
- Envío de audio de bienvenida
- Asignación de etiqueta `citagyne`
- Detección de saludos iniciales
- Procesamiento del primer mensaje
- IDs de agentes para asignación de conversaciones

## Archivos

### `debug_audio_conversacion.py`
Script principal para analizar por qué una conversación específica no recibió el audio.

**Uso:**
```bash
python debug/debug_audio_conversacion.py 31811
```

**Qué verifica:**
1. Si el primer mensaje está en las listas conocidas (`facebook_messages`, `google_messages`, etc.)
2. Si es el primer mensaje del usuario
3. Si tiene el atributo `audio_enviado` marcado
4. Si tiene el atributo `primer_mensaje_procesado` marcado
5. Qué clasificación le dio la IA al mensaje
6. Si tiene la etiqueta `citagyne`
7. Si el contacto tiene `servicios_recibidos`
8. Información del contacto y mensajes

**Salida:**
Muestra un reporte detallado con todas las condiciones y valores que determinan si se debe enviar el audio.

### `debug_verificar_listas.py`
Script para verificar si un mensaje está en alguna de las listas conocidas.

**Uso:**
```bash
python debug/debug_verificar_listas.py "Hola, necesito información"
```

**Qué hace:**
- Compara el mensaje exacto con todas las listas
- Muestra en cuál lista está (si está)
- Útil para agregar nuevos mensajes a las listas

### `debug_listar_agentes.py`
Script para listar agentes de Chatwoot y localizar sus IDs.

**Uso:**
```bash
python debug/debug_listar_agentes.py
```

**Qué hace:**
- Consulta la API de Chatwoot para obtener todos los agentes
- Muestra una tabla con ID, nombre y email de cada agente
- Destaca los IDs de Lina y Yaneth para la asignación de conversaciones
- Útil cuando se modifican las reglas de asignación en `AsignarNuevasConversaciones`

## Flujo de Decisión del Audio

El sistema decide enviar audio en estos casos:

1. **Mensaje en listas conocidas:**
   - Si `last_message_content in facebook_messages` o `last_message_content == audio_gyne`
   - ✅ Envía audio directamente

2. **Mensaje nuevo detectado por IA:**
   - Si NO está en listas conocidas
   - Si NO tiene `audio_enviado = True`
   - Si es el primer mensaje del usuario
   - Si la IA clasifica como "Saludo inicial"
   - ✅ Envía audio

## Condiciones para Etiqueta `citagyne`

La etiqueta se asigna si:
- Es el primer mensaje del usuario (`primer_mensaje_procesado = False`)
- El contacto NO tiene `servicios_recibidos` o está vacío
- NO tiene la etiqueta `citagyne` aún

## Cómo Usar

**⚠️ IMPORTANTE: Siempre activar el entorno virtual antes de ejecutar los scripts**

### Activar el entorno virtual:

**Activar el venv (ubicado en `.venv` en la raíz del proyecto):**
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

**Ruta completa:** `C:\GitRepos\MiaAutomate\.venv`

### Ejecutar scripts:

1. **Para debuggear una conversación específica:**
   ```bash
   python debug/debug_audio_conversacion.py <CONVERSATION_ID>
   ```
   Ejemplo:
   ```bash
   python debug/debug_audio_conversacion.py 31811
   ```

2. **Para verificar un mensaje:**
   ```bash
   python debug/debug_verificar_listas.py "tu mensaje aquí"
   ```

3. **Para listar agentes de Chatwoot:**
   ```bash
   python debug/debug_listar_agentes.py
   ```

4. **Revisar los logs:**
   - Buscar mensajes con `🔖`, `🎵`, `✅` que indican acciones del sistema
   - Buscar errores con `❌` o `ERROR`

## Puntos de Verificación

Cuando una conversación no recibe audio, verificar:

1. ✅ ¿El mensaje está en `facebook_messages` o es `audio_gyne`?
2. ✅ ¿Es el primer mensaje del usuario?
3. ✅ ¿Ya tiene `audio_enviado = True`?
4. ✅ ¿La IA clasificó como "Saludo inicial"?
5. ✅ ¿Tiene la etiqueta `citagyne`?
6. ✅ ¿El contacto tiene `servicios_recibidos`?

## Notas Importantes

- El script `debug_audio_conversacion.py` es seguro de usar, solo lee información (no modifica nada)
- Todos los scripts requieren las variables de entorno configuradas (.env)
- Los scripts muestran información detallada para facilitar el debugging
- **Si el script se traba**: Presiona `Ctrl+C` para interrumpir. El script mostrará la información obtenida hasta ese punto
- La clasificación por IA puede tardar 10-30 segundos, es normal
- Si el script se cuelga en la clasificación IA, puedes interrumpirlo y aún obtendrás toda la información importante
