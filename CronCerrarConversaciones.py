import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Conversations import cerrar_conversaciones_inactivas


for page in range(50):  # 0 a 10 inclusive
    cerrar_conversaciones_inactivas(page)
