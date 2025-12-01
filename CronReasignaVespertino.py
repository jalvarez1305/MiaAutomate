import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'libs')))
from CW_Conversations import reasigna_conversaciones


for page in range(11):  # 0 a 10 inclusive
    #Mayra 32 y Dayana 33
    reasigna_conversaciones(33,32,page)
