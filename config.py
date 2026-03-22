"""
Configuration — loads all settings from environment variables via .env.
Never import secrets directly; always use the constants defined here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DB_PATH = os.getenv("DB_PATH", "./lolnotifier.db")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "300"))  # 5min para dev keys
MAX_USERS = int(os.getenv("MAX_USERS", "20"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "0.06"))  # ~16 req/s safe
CACHE_TTL_SUMMONER = int(os.getenv("CACHE_TTL_SUMMONER", "300"))
CACHE_TTL_MATCH = int(os.getenv("CACHE_TTL_MATCH", "3600"))
CACHE_TTL_CHAMPION = int(os.getenv("CACHE_TTL_CHAMPION", "86400"))

# Region → Account Cluster mapping
ACCOUNT_CLUSTERS = {
    "br1": "americas",
    "la1": "americas",
    "la2": "americas",
    "na1": "americas",
    "na2": "americas",
    "kr": "asia",
    "jp1": "asia",
    "oce": "americas",
    "euw1": "europe",
    "eun1": "europe",
    "tr1": "europe",
    "ru": "europe",
}

REGIONS = {
    "br1": "americas.api.riotgames.com",
    "la1": "americas.api.riotgames.com",
    "la2": "americas.api.riotgames.com",
    "na1": "americas.api.riotgames.com",
    "kr": "asia.api.riotgames.com",
    "jp1": "asia.api.riotgames.com",
    "oce": "oce.api.riotgames.com",
    "euw1": "europe.api.riotgames.com",
    "eun1": "europe.api.riotgames.com",
    "tr1": "europe.api.riotgames.com",
    "ru": "europe.api.riotgames.com",
}

RIOT_API_BASE = "https://{region}/lol"
