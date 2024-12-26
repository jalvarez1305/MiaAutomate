import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Conversations import cerrar_conversaciones_inactivas


cerrar_conversaciones_inactivas()