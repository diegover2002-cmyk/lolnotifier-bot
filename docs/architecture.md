# Architecture

## Module Map

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│  - Initializes DB, wires command handlers, starts pollers   │
│  - Owns the aiohttp.ClientSession lifecycle                 │
│  - Runs until KeyboardInterrupt via asyncio.Event().wait()  │
└────────────┬────────────────────────┬───────────────────────┘
             │                        │
     ┌───────▼──────┐        ┌────────▼────────┐
     │  handlers.py │        │   poller.py     │
     │  (commands)  │        │  (background)   │
     └───────┬──────┘        └────────┬────────┘
             │                        │
     ┌───────▼────────────────────────▼────────┐
     │              riot_api.py                │
     │   get_match_history_ids()               │
     │   get_match_info()                      │
     │   parse_match_for_puuid()               │
     │   get_summoner_by_puuid() [prod only]   │
     └───────┬─────────────────────────────────┘
             │
     ┌───────▼──────────┐
     │  riot_account.py │
     │  get_account_by_riot_id()  (account/v1) │
     └──────────────────┘

     ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
     │  database.py │    │   stats.py   │    │ formatter.py │
     │  (SQLite /   │    │  (pure math) │    │ (pure text)  │
     │  CosmosDB)   │    │              │    │              │
     └──────────────┘    └──────────────┘    └──────────────┘
```

---

## Async Lifecycle

```
asyncio.run(main())
  │
  ├── await init_db()                    # create tables, run migrations
  │
  ├── Application.builder().build()      # python-telegram-bot
  │
  ├── async with aiohttp.ClientSession() # single session for all HTTP
  │     │
  │     ├── await app.start()
  │     ├── await app.updater.start_polling()
  │     │
  │     ├── asyncio.create_task(poll_users(...))   # background loop
  │     ├── asyncio.create_task(poll_pros(...))    # background loop
  │     │
  │     └── await asyncio.Event().wait()           # block until Ctrl+C
  │           │
  │           └── finally:
  │                 user_task.cancel()
  │                 pro_task.cancel()
  │                 await app.updater.stop()
  │                 await app.stop()
```

The single `aiohttp.ClientSession` is created in `main()` and passed down to both pollers and handlers. This avoids the overhead of creating a new session per request.

---

## Data Flow — Match Notification

```
poll_users() / poll_pros()
  │
  ├── _last_poll_age(record) < 60s?  → skip
  │
  ├── _resolve_puuid(session, record)
  │     ├── record["puuid"] exists?  → return cached
  │     └── call get_account_by_riot_id()  → store + return
  │
  ├── get_match_history_ids(session, region, puuid, count=1)
  │     └── match/v5/by-puuid/{puuid}/ids
  │
  ├── latest_id == stored last_match_id?  → skip
  │
  ├── get_match_info(session, region, latest_id)
  │     └── match/v5/matches/{id}
  │
  ├── parse_match_for_puuid(match_info, puuid)
  │     └── extract champion, KDA, win, queue, duration
  │
  ├── format_match_summary_with_stats(player_label, parsed, full_participant)
  │     └── pure formatting, no I/O
  │
  └── bot.send_message(chat_id, message)
        └── Telegram Bot API
```

---

## Data Flow — `/stats` Command

```
player_stats(update, context)
  │
  ├── get_user(DB_PATH, user_id)          # fetch PUUID from DB
  │
  ├── get_match_history_ids(..., count=5) # last 5 match IDs
  │
  ├── for each match_id:
  │     get_match_info(...)               # full match payload
  │     extract_match_stats(info, puuid)  # flat stats dict
  │
  ├── aggregate_stats(per_match_list)     # winrate, avg KDA, perf score
  │
  └── format_aggregated_stats(label, agg) → reply_text()
```

---

## Concurrency Model

- **One event loop** — `asyncio.run(main())`
- **Two background tasks** — `poll_users` and `poll_pros` run as `asyncio.Task` objects
- **Rate limiting** — `asyncio.Semaphore(20)` in `riot_api.py` caps concurrent Riot API requests
- **Per-request delay** — `await asyncio.sleep(RATE_LIMIT_DELAY)` after each request
- **Per-player cooldown** — `_MIN_POLL_GAP = 60s` prevents hammering the same player

---

## Module Responsibilities

| Module | I/O | Pure | Responsibility |
|---|---|---|---|
| `main.py` | ✅ | ❌ | Entry point, lifecycle |
| `handlers.py` | ✅ | ❌ | Telegram command dispatch |
| `poller.py` | ✅ | ❌ | Background polling loop |
| `riot_api.py` | ✅ | ❌ | HTTP client for Riot API |
| `riot_account.py` | ✅ | ❌ | account/v1 resolution |
| `database.py` | ✅ | ❌ | SQLite (local) / CosmosDB (Azure) read/write |
| `stats.py` | ❌ | ✅ | Math over match data |
| `formatter.py` | ❌ | ✅ | String formatting |
| `pro_players.py` | ❌ | ✅ | Static dataset |
| `config.py` | ✅ | ❌ | Env var loading |
| `logging_setup.py` | ✅ | ❌ | Logger configuration |
