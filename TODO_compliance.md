# Riot API Production Compliance TODO

Approved plan steps (sequential execution):

1. **Update database.py**: Add `last_poll_time` TIMESTAMP column to `users` and `pro_players` tables. Update `get_all_users()`, `get_all_pros()` to include it. Add `update_last_poll_time(db_path, user_id_or_pro_id, timestamp)` functions.

2. **Update config.py**: Add `RATE_LIMIT_DELAY=0.05` (20 req/s), `CACHE_TTL_SUMMONER=300` (5min), `CACHE_TTL_CHAMPION=86400` (24h). Add compliance warning comment.

3. **Update riot_api.py**:
   - Add `asyncio.Semaphore(20)` for concurrency.
   - Add `await asyncio.sleep(config.RATE_LIMIT_DELAY)` post-req.
   - Implement dict caches for summoner/active_game (check TTL).
   - Add `get_static_champions(session, region)` for real champ names (cache).
   - Enhance retry for 429 (max 60s backoff).

4. **Update poller.py**: In loops, skip if `now - last_poll_time < 60s`. Call `update_last_poll_time` after poll. Use caches. Add call counters/logging.

5. **Update handlers.py**: `/status` show `Last poll: {last_poll_time}`.

6. **Update README.md**: Add 'Riot API Compliance' section with limits/caching info.

7. **Minor**: Update test_riot_key.py with rate sim; clear old TODO.md content.

8. **Test**: docker-compose up; simulate load; check logs.

9. **Complete**: attempt_completion.

Progress: 6/9 ✅ README compliance section added
