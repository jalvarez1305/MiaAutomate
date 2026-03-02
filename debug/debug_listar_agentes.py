"""
Script de debug para listar agentes de Chatwoot y localizar IDs.

Uso: python debug/debug_listar_agentes.py
"""

import sys
import os
import requests
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

def listar_agentes():
    """Obtiene y muestra la lista de agentes desde la API de Chatwoot."""
    base_url = os.getenv('BASE_URL')
    cw_token = os.getenv('CW_TOKEN')

    if not base_url or not cw_token:
        print("❌ ERROR: BASE_URL o CW_TOKEN no configurados en .env")
        sys.exit(1)

    # Probar diferentes formatos de URL (Chatwoot API v1)
    # BASE_URL puede ser: .../api/v1/accounts/1, .../api/v1, o raíz
    base = base_url.rstrip('/')
    urls_to_try = []
    if base.endswith("accounts/1"):
        urls_to_try.append(f"{base}/agents")
    urls_to_try.extend([
        f"{base}/accounts/1/agents",
        f"{base}/api/v1/accounts/1/agents",
    ])

    headers = {
        "Content-Type": "application/json",
        "api_access_token": cw_token
    }

    agents = None
    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # La API puede devolver payload o array directo
                agents = data.get('payload', data) if isinstance(data, dict) else data
                if isinstance(agents, list) and len(agents) > 0:
                    break
        except Exception as e:
            continue

    if not agents:
        print("❌ ERROR: No se pudieron obtener agentes.")
        print("   Verifica BASE_URL y CW_TOKEN en .env")
        print("   Endpoints probados:", urls_to_try)
        sys.exit(1)

    print("=" * 80)
    print("📋 AGENTES DE CHATWOOT")
    print("=" * 80)
    print(f"{'ID':<6} {'available_name':<20} {'name':<25} {'email':<35}")
    print("-" * 80)

    lina_id = None
    yaneth_id = None

    for agent in agents:
        aid = agent.get('id', 'N/A')
        available_name = agent.get('available_name', '') or ''
        name = agent.get('name', '') or ''
        email = agent.get('email', '') or ''

        # Buscar Lina y Yaneth (case insensitive)
        if 'lina' in available_name.lower() or 'lina' in name.lower():
            lina_id = aid
            print(f"{aid:<6} {available_name:<20} {name:<25} {email:<35}  ← LINA")
        elif 'yaneth' in available_name.lower() or 'yaneth' in name.lower():
            yaneth_id = aid
            print(f"{aid:<6} {available_name:<20} {name:<25} {email:<35}  ← YANETH")
        else:
            print(f"{aid:<6} {available_name:<20} {name:<25} {email:<35}")

    print("=" * 80)
    print("\n🔍 AGENTES BUSCADOS:")
    print(f"   Lina:   ID = {lina_id if lina_id else 'NO ENCONTRADA'}")
    print(f"   Yaneth: ID = {yaneth_id if yaneth_id else 'NO ENCONTRADA'}")
    print("\n💡 Usa estos IDs en main_bot.py para LINA_ID y YANETH_ID")
    print("=" * 80)

if __name__ == "__main__":
    listar_agentes()
