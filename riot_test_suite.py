#!/usr/bin/env python3
"""
Riot API Complete Test Suite - DEV KEY SAFE
Run: python riot_test_suite.py
"""

import asyncio
import aiohttp
from datetime import datetime
from riot_account import get_puuid_by_game_name
from dotenv import load_dotenv
load_dotenv()
from riot_api import get_summoner_by_puuid, get_active_game, get_match_info, get_static_champions
from config import RIOT_API_KEY, REGIONS, ACCOUNT_CLUSTERS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TEST CONFIG - CHANGE THIS
TEST_GAME_NAME = "LaBísica"
TEST_TAG_LINE = "EUW"
TEST_REGION = "euw1"

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Optional - set to send report
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"     # Optional

class RiotTestSuite:
    def __init__(self):
        self.results = []
        self.test_user = f"{TEST_GAME_NAME}#{TEST_TAG_LINE}"
        self.puuid = None
        self.summoner_id = None
        self.latest_match_id = None

    async def test_account_lookup(self, session):
        """STEP 1"""
        cluster = ACCOUNT_CLUSTERS[TEST_REGION]
        start = datetime.now()

        puuid = await get_puuid_by_game_name(session, cluster, TEST_GAME_NAME, TEST_TAG_LINE)
        duration = (datetime.now() - start).total_seconds()

        if puuid:
            self.puuid = puuid
            self.results.append({
                "endpoint": "account/by-riot-id",
                "status": "✅ PASS",
                "duration": duration,
                "data": f"PUUID: {puuid[:8]}..."
            })
            logger.info("✅ STEP 1 PASS")
            return True
        else:
            self.results.append({
                "endpoint": "account/by-riot-id",
                "status": "❌ FAIL",
                "duration": duration,
                "error": "No PUUID found"
            })
            logger.error("❌ STEP 1 FAIL")
            return False

    async def test_summoner_data(self, session):
        """STEP 2"""
        if not self.puuid:
            return False

        start = datetime.now()
        summoner = await get_summoner_by_puuid(session, TEST_REGION, self.puuid)
        duration = (datetime.now() - start).total_seconds()

        if summoner and summoner.get('id') and summoner.get('summonerLevel', 0) > 0:
            self.summoner_id = summoner['id']
            self.results.append({
                "endpoint": "summoner/by-puuid",
                "status": "✅ PASS",
                "duration": duration,
                "data": f"Level: {summoner['summonerLevel']}"
            })
            logger.info("✅ STEP 2 PASS")
            return True
        else:
            self.results.append({
                "endpoint": "summoner/by-puuid",
                "status": "❌ FAIL",
                "duration": duration,
                "error": "No summonerId or level=0"
            })
            logger.error("❌ STEP 2 FAIL")
            return False

    async def test_match_history(self, session):
        """STEP 3"""
        if not self.puuid:
            return False

        # Add match history endpoint here
        # For now skip or implement get_match_history
        url = f"https://{REGIONS[TEST_REGION]}/lol/match/v5/matches/by-puuid/{self.puuid}/ids?count=5"
        headers = {'X-Riot-Token': RIOT_API_KEY}

        start = datetime.now()
        async with session.get(url, headers=headers) as resp:
            duration = (datetime.now() - start).total_seconds()

            if resp.status == 200:
                matches = await resp.json()
                if matches and len(matches) > 0:
                    self.latest_match_id = matches[0]
                    self.results.append({
                        "endpoint": "match/by-puuid/ids",
                        "status": "✅ PASS",
                        "duration": duration,
                        "data": f"{len(matches)} matches, latest: {self.latest_match_id[:8]}..."
                    })
                    logger.info("✅ STEP 3 PASS")
                    return True
            self.results.append({
                "endpoint": "match/by-puuid/ids",
                "status": "❌ FAIL" if resp.status != 200 else "⚠️ NO MATCHES",
                "duration": duration,
                "error": f"Status: {resp.status}"
            })
            logger.warning(f"⚠️ STEP 3: {resp.status}")
            return resp.status == 200  # No matches OK

    async def test_match_details(self, session):
        """STEP 4"""
        if not self.latest_match_id:
            return False

        start = datetime.now()
        match_info = await get_match_info(session, TEST_REGION, self.latest_match_id)
        duration = (datetime.now() - start).total_seconds()

        if match_info and match_info.get('info', {}).get('participants'):
            participants = match_info['info']['participants']
            player = next((p for p in participants if p['puuid'] == self.puuid), None)
            if player:
                kda = f"{player['kills']}/{player['deaths']}/{player['assists']}"
                win_status = "WIN" if player['win'] else "LOSS"
                champ = player['championName']
                self.results.append({
                    "endpoint": "match/details",
                    "status": "✅ PASS",
                    "duration": duration,
                    "data": f"{champ} {kda} {win_status}"
                })
                logger.info("✅ STEP 4 PASS")
                return True
        self.results.append({
            "endpoint": "match/details",
            "status": "❌ FAIL",
            "duration": duration,
            "error": "No match info or player not found"
        })
        logger.error("❌ STEP 4 FAIL")
        return False

    async def test_ranked_data(self, session):
        """STEP 5"""
        if not self.summoner_id:
            return False

        url = f"https://{REGIONS[TEST_REGION]}/lol/league/v4/entries/by-summoner/{self.summoner_id}"
        headers = {'X-Riot-Token': RIOT_API_KEY}

        start = datetime.now()
        async with session.get(url, headers=headers) as resp:
            duration = (datetime.now() - start).total_seconds()

            if resp.status == 200:
                leagues = await resp.json()
                rank_info = f"{len(leagues)} queue(s)"
                self.results.append({
                    "endpoint": "league/by-summoner",
                    "status": "✅ PASS",
                    "duration": duration,
                    "data": rank_info
                })
                logger.info("✅ STEP 5 PASS")
                return True
            self.results.append({
                "endpoint": "league/by-summoner",
                "status": "❌ FAIL",
                "duration": duration,
                "error": f"Status: {resp.status}"
            })
            return False

    async def test_live_game(self, session):
        """STEP 6"""
        if not self.summoner_id:
            return False

        start = datetime.now()
        game = await get_active_game(session, TEST_REGION, self.summoner_id)
        duration = (datetime.now() - start).total_seconds()

        status = "⚠️ NOT IN GAME (OK)" if game is None else "🎮 LIVE GAME!"
        self.results.append({
            "endpoint": "spectator/active-game",
            "status": status,
            "duration": duration,
            "data": "No game ID" if game is None else f"Game ID: {game.get('gameId', 'N/A')}"
        })
        logger.info(f"✅ STEP 6: {status}")
        return True

    async def test_champion_mastery(self, session):
        """STEP 7"""
        if not self.puuid:
            return False

        url = f"https://{REGIONS[TEST_REGION]}/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.puuid}?count=3"
        headers = {'X-Riot-Token': RIOT_API_KEY}

        start = datetime.now()
        async with session.get(url, headers=headers) as resp:
            duration = (datetime.now() - start).total_seconds()

            if resp.status == 200:
                mastery = await resp.json()
                data = f"{len(mastery)} champs" if mastery else "0"
                self.results.append({
                    "endpoint": "champion-mastery/by-puuid",
                    "status": "✅ PASS",
                    "duration": duration,
                    "data": data
                })
                logger.info("✅ STEP 7 PASS")
                return True
            self.results.append({
                "endpoint": "champion-mastery/by-puuid",
                "status": "❌ FAIL",
                "duration": duration,
                "error": f"Status: {resp.status}"
            })
            return False

    async def test_platform_status(self, session):
        """STEP 8"""
        url = f"https://{REGIONS[TEST_REGION]}/lol/status/v4/platform-data"
        headers = {'X-Riot-Token': RIOT_API_KEY}

        start = datetime.now()
        async with session.get(url, headers=headers) as resp:
            duration = (datetime.now() - start).total_seconds()

            if resp.status == 200:
                status = await resp.json()
                services_ok = len(status.get('services', [])) > 0
                self.results.append({
                    "endpoint": "platform-status",
                    "status": "✅ PASS" if services_ok else "⚠️ EMPTY",
                    "duration": duration,
                    "data": f"{len(status.get('services', []))} services"
                })
                logger.info("✅ STEP 8 PASS")
                return True
            self.results.append({
                "endpoint": "platform-status",
                "status": "❌ FAIL",
                "duration": duration,
                "error": f"Status: {resp.status}"
            })
            return False

    async def send_telegram_report(self):
        """Send structured report to Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.info("No Telegram config - skipping report")
            return

        passed = sum(1 for r in self.results if "PASS" in r["status"])
        total = len(self.results)

        report = f"""🚀 **Riot API Test Report**

👤 **User**: `{self.test_user}` ({TEST_REGION})

"""
        for result in self.results:
            status_emoji = "✅" if "PASS" in result["status"] else "❌" if "FAIL" in result["status"] else "⚠️"
            report += f"{status_emoji} **{result['endpoint']}**: {result['status']}"
            if 'data' in result:
                report += f" - {result['data']}"
            report += "\n"

        report += f"\n📊 **Summary**: {passed}/{total} ✅\n"
        if 'error' in [r for r in self.results if 'error' in r]:
            report += "🔴 **Failures detected!** Check logs.\n"

        # Send to Telegram (simple)
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': report,
                'parse_mode': 'Markdown'
            }
            async with session.post(url, json=data) as resp:
                logger.info(f"Telegram report sent: {resp.status}")

    async def run_full_suite(self):
        """Run complete test suite"""
        async with aiohttp.ClientSession() as session:
            # Rate limit safety
            await asyncio.sleep(1)

            # Sequential tests
            await self.test_account_lookup(session)
            await asyncio.sleep(1)  # Rate safety

            await self.test_summoner_data(session)
            await asyncio.sleep(1)

            await self.test_match_history(session)
            await asyncio.sleep(1)

            await self.test_match_details(session)
            await asyncio.sleep(1)

            await self.test_ranked_data(session)
            await asyncio.sleep(1)

            await self.test_live_game(session)
            await asyncio.sleep(1)

            await self.test_champion_mastery(session)
            await asyncio.sleep(1)

            await self.test_platform_status(session)

            # Report
            print("\n" + "="*60)
            await self.send_telegram_report()
            print("="*60)

            passed = sum(1 for r in self.results if "PASS" in r["status"])
            print(f"🎉 TEST COMPLETE: {passed}/{len(self.results)} PASSED")
            return passed == len(self.results)

if __name__ == "__main__":
    suite = RiotTestSuite()
    asyncio.run(suite.run_full_suite())

