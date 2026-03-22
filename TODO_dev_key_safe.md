# DEV KEY SAFE Migration TODO

**Approved**: Riot ID → PUUID flow only

**Steps**:

1. **database.py**: Add columns `game_name`, `tag_line`, `puuid` to `users`/`pro_players`. Update `set_user_*`, `get_all_*`.

2. **riot_api.py**:
   - Add `get_account_by_riot_id(cluster, game_name, tag_line)`
   - Add `get_summoner_by_puuid(region, puuid)`
   - Add `get_match_history(region, puuid)`
   - Replace by-name with puuid flow
   - Cache puuid/match IDs

3. **handlers.py**:
   - `/set_lol_player GameName#TagLine region` → parse → fetch puuid/summonerId
   - Update `/status` show Riot ID/PUUID/rank

4. **poller.py**:
   - Poll `get_match_history(puuid)` → compare last 5 matches vs stored
   - New match → notify + fetch details

5. **config.py**: Add `ACCOUNT_CLUSTERS = {'euw1': 'europe', 'la2': 'americas'}`

6. **README.md**: Update commands to Riot ID format. Remove summoner name.

7. **test_riot_key.py**: Add puuid flow test

8. **Migrate data**: Run script to convert existing summoner_name → puuid (if possible)

9. **Test**: docker-compose up → /set_lol_player LaBísica#EUW la2

**Progress**: 1/9 (config.py ✅ - ACCOUNT_CLUSTERS + dev-safe rates)
