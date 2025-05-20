import os
import requests
import pymssql
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

CHATWOOT_URL = os.getenv("BASE_URL")
CHATWOOT_TOKEN = os.getenv("CW_TOKEN")
HEADERS = {
        "Content-Type": "application/json",
        "api_access_token": CHATWOOT_TOKEN
    }

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DB = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# Conexión a SQL Server
conn = pymssql.connect(server=SQL_SERVER, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DB)
cursor = conn.cursor()

def get_chatwoot_contact(contact_id):
    try:
        url = f"{CHATWOOT_URL}/contacts/{contact_id}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[{contact_id}] No encontrado o error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[{contact_id}] Error al consultar contacto Chatwoot: {e}")
        return None

def get_sql_funnel_state(identifier):
    try:
        cursor.execute("SELECT funel_state FROM [dbo].[CW_Contacts] WHERE id = %s", (identifier,))
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"[{identifier}] Error al consultar SQL: {e}")
        return None

def update_sql_funnel_state(identifier, new_state):
    try:
        cursor.execute(
            "UPDATE [dbo].[CW_Contacts] SET funel_state = %s WHERE id = %s",
            (new_state, identifier)
        )
        conn.commit()
        print(f"[{identifier}] Actualizado funnel_state en SQL a: {new_state}")
    except Exception as e:
        print(f"[{identifier}] Error al actualizar SQL: {e}")

# Iterar sobre contactos
for contact_id in range(2066, 2600):
    contacto = get_chatwoot_contact(contact_id)
    if not contacto:
        continue

    contact_data = contacto.get("payload", {})
    identifier = contact_data.get("id")
    funnel_state_chatwoot = contact_data.get("custom_attributes", {}).get("funel_state")


    if identifier is None or funnel_state_chatwoot is None:
        print(f"[{contact_id}] Sin identifier o funnel_state")
        continue

    funnel_state_sql = get_sql_funnel_state(identifier)

    try:
        funnel_state_chatwoot_int = int(funnel_state_chatwoot)
    except (ValueError, TypeError):
        print(f"[{identifier}] Valor inválido de funnel_state en Chatwoot: {funnel_state_chatwoot}")
        continue

    if funnel_state_sql != funnel_state_chatwoot_int:
        print(f"[{identifier}] Diferencia - SQL: {funnel_state_sql}, Chatwoot: {funnel_state_chatwoot_int}")
        update_sql_funnel_state(identifier, funnel_state_chatwoot_int)

