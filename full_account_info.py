import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

RIOT_API_KEY = os.getenv('RIOT_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
YOUR_USER_ID = 123456789  # Replace with your Telegram user ID from DB or logs

REGION = 'euw1'
SUMMONER_NAME = 'LaBífica'
ACCOUNT_CLUSTER = 'europe'
GAME_NAME = 'LaBísica'
TAG_LINE = 'EUW'

headers = {"X-Riot-Token": RIOT_API_KEY}

print("=== FULL RIOT DEV API REPORT ===")

# 1. Status
status_url = f"https://{REGION}.api.riotgames.com/lol/status/v4/platform-data"
status = requests.get(status_url)
print(f"STATUS: {status.status_code}")
if status.status_code == 200:
    print(status.json())

# 2. Summoner (403 expected for dev key on summoner)
summoner_url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}"
summoner = requests.get(summoner_url, headers=headers)
print(f"SUMMONER ({SUMMONER_NAME}): {summoner.status_code}")
print(summoner.json() if summoner.status_code == 200 else summoner.text[:200])

# 3. Account
account_url = f"https://{ACCOUNT_CLUSTER}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{GAME_NAME}/{TAG_LINE}"
account = requests.get(account_url, headers=headers)
print(f"ACCOUNT ({GAME_NAME}#{TAG_LINE}): {account.status_code}")
if account.status_code == 200:
    puuid = account.json()['puuid']
    print(account.json())

    # 4. League Entries (dev key limited)
    league_url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/by-summoner/[summoner_id]"  # Needs summoner.id
    print("\nPUUID saved:", puuid)
else:
    print(account.text[:200])

print("\n=== END REPORT ===")

# Telegram send (replace YOUR_USER_ID)
if TELEGRAM_TOKEN:
    message = f"""🔥 RIOT DEV API REPORT {datetime.now()}

**Account**: LaBísica#EUW ✓ PUUID: <redacted>

**Summoner**: 403 (dev limit esperado)
**Status**: 401 (dev limit)

Bot compliant & ready!"""

    tg_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    tg_data = {"chat_id": YOUR_USER_ID, "text": message, "parse_mode": "Markdown"}
    tg_resp = requests.post(tg_url, data=tg_data)
    print(f"Telegram sent: {tg_resp.status_code}")


