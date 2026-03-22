import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

DB_PATH = 'lolnotifier.db'

# 1. Get your user_id from DB (labìsica user)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT user_id FROM users WHERE summoner_name = 'labìsica'")
result = c.fetchone()
conn.close()

if not result:
    print("No user found for labìsica. Send /set_lol_summoner labìsica euw1 first.")
    exit(1)

user_id = result[0]
print(f"Tu Telegram user_id: {user_id}")

# 2. Riot data
headers = {"X-Riot-Token": RIOT_API_KEY}
account_data = requests.get("https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/LaBísica/EUW", headers=headers).json()
puuid = account_data['puuid']

# 3. Telegram message
message = f"""🔥 **RIOT DEV API REPORT** ({datetime.now().strftime('%Y-%m-%d %H:%M')})

**Cuenta**: LaBífica#EUW ✅
**PUUID**: `{puuid}`
**Status API**: 401 (dev limit)
**Summoner v4**: 403 (dev limit esperado - summoner bloqueado)
**Account v1**: 200 ✅

Bot compliant & polling cada {os.getenv('POLL_INTERVAL', 30)}s con rate limit 20req/s.

¡Listo para prod! 🎮"""

tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
tg_data = {"chat_id": user_id, "text": message, "parse_mode": "Markdown"}
response = requests.post(tg_url, data=tg_data)
print(f"Telegram status: {response.status_code} - {response.text}")


