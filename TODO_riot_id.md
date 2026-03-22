# Riot ID Best Practice Upgrade TODO

Approved plan steps:

1. **riot_api.py**: Add get_account_by_riot_id(session, game_name, tag_line, region) -> call account/v1/by-riot-id (cluster from region), get puuid, then summoner/v4/summoners/by-puuid

2. **database.py**: ALTER TABLE users/pro_players ADD summoner_id TEXT; update get_user/get_all_* to include; set_user_riot_id(user_id, game_name, tag_line, region, summoner_id)

3. **handlers.py**: /set_lol_summoner parse arg[0] as "game#tag", arg[1] region; call get_account, store summoner_id/game_name/tag_line/region. Similar for add_pro.

4. **poller.py**: Use user['summoner_id'] for get_active_game (skip get_summoner)

5. **README/handlers start**: Update instructions to "gameName#tagLine region" (find in LoL client profile)

6. **main.py**: No change

7. Test: docker-compose up, /set_lol_summoner labisica#EUW la2

Progress: 0/7
