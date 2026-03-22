import os
from dotenv import load_dotenv
import requests

load_dotenv()

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
REGION = 'euw1'  # Cambia por la región adecuada

# 1. Probar el endpoint de status (no requiere autenticación)
status_url = f"https://{REGION}.api.riotgames.com/lol/status/v4/platform-data"
status_response = requests.get(status_url)
print(f"[STATUS API] Status code: {status_response.status_code}")
if status_response.status_code == 200:
	print("[STATUS API] La API de Riot está operativa:")
	print(status_response.json())
else:
	print(f"[STATUS API] Error: {status_response.text}")

# 2. Probar el endpoint de summoner (requiere autenticación)
SUMMONER_NAME = 'LaBísica'  # Tu summoner name
summoner_url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}"
headers = {"X-Riot-Token": RIOT_API_KEY}
summoner_response = requests.get(summoner_url, headers=headers)
print(f"[SUMMONER API] Status code: {summoner_response.status_code}")
if summoner_response.status_code == 200:
	print("[SUMMONER API] Consulta exitosa. Datos de la cuenta:")
	print(summoner_response.json())
elif summoner_response.status_code == 401:
	print("[SUMMONER API] Error 401: API key vacía o inválida.")
elif summoner_response.status_code == 403:
	print("[SUMMONER API] Error 403: La API key es válida pero no tienes permisos para este recurso o endpoint. Verifica que usas un endpoint permitido para claves de desarrollo y que la región/nombre existen.")
elif summoner_response.status_code == 404:
	print("[SUMMONER API] Error 404: No se encontró el invocador. Verifica el nombre y la región.")
else:
	print(f"[SUMMONER API] Error inesperado: {summoner_response.text}")

# 3. Probar el endpoint ACCOUNT-V1 (mejor práctica)
# Usa el cluster adecuado: americas, europe, asia
ACCOUNT_CLUSTER = 'europe'  # Cambia según el Riot ID
GAME_NAME = 'LaBísica'      # Tu gameName real
TAG_LINE = 'EUW'            # Cambia por el tagLine real
account_url = f"https://{ACCOUNT_CLUSTER}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAG_LINE}"
account_response = requests.get(account_url, headers=headers)
print(f"[ACCOUNT-V1 API] Status code: {account_response.status_code}")
if account_response.status_code == 200:
	print("[ACCOUNT-V1 API] Consulta exitosa. Datos de la cuenta:")
	print(account_response.json())
elif account_response.status_code == 401:
	print("[ACCOUNT-V1 API] Error 401: API key vacía o inválida.")
elif account_response.status_code == 403:
	print("[ACCOUNT-V1 API] Error 403: La API key es válida pero no tienes permisos para este recurso o endpoint. Verifica que usas un endpoint permitido para claves de desarrollo y que el Riot ID existe.")
elif account_response.status_code == 404:
	print("[ACCOUNT-V1 API] Error 404: No se encontró la cuenta. Verifica el gameName y tagLine.")
else:
	print(f"[ACCOUNT-V1 API] Error inesperado: {account_response.text}")
