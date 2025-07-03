import os
from twilio.rest import Client
from dotenv import load_dotenv

# Carga variables desde .env
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def get_child_call_status(parent_sid: str) -> str:
    """
    Busca la llamada hija usando ParentCallSid y devuelve su status.
    """
    calls = client.calls.list(parent_call_sid=parent_sid)

    if not calls:
        #print(f"No se encontraron child calls para ParentCallSid: {parent_sid}")
        return "not-found"

    child_call = calls[0]
    #print(f"Child Call SID: {child_call.sid}, Status: {child_call.status}")

    return child_call.status