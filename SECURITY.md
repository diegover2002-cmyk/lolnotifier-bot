# Security Policy

## Secrets Management

### What must never be committed

| Secret | Where it lives | How it's excluded |
|---|---|---|
| `TELEGRAM_TOKEN` | `.env` | `.gitignore` |
| `RIOT_API_KEY` | `.env` | `.gitignore` |
| `TELEGRAM_CHAT_ID` | `.env` | `.gitignore` |
| SQLite database (`*.db`) | local filesystem | `.gitignore` |
| Log files (`logs/`) | local filesystem | `.gitignore` |

### How secrets are loaded

All secrets are loaded at startup via `python-dotenv` in `config.py`:

```python
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
```

The `.env.example` file contains only placeholder values and is safe to commit:

```env
TELEGRAM_TOKEN=<your_botfather_token>
RIOT_API_KEY=<your_riot_dev_key>
TELEGRAM_CHAT_ID=<your_telegram_user_id>
```

### If a secret is accidentally committed

1. Rotate the secret immediately (regenerate the token/key)
2. Remove it from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" HEAD
   git push origin --force
   ```
3. Verify the secret no longer appears in any commit with `git log -p | grep <secret>`

---

## Logging Policy

### What is logged

| Level | Examples |
|---|---|
| `INFO` | Poll cycle completed, bot started, match detected |
| `WARNING` | Rate limit hit (429), failed Telegram send, PUUID not resolved |
| `DEBUG` | Cache hits, 403/404 responses from Riot API, per-request details |
| `ERROR` / `EXCEPTION` | Unexpected exceptions in poll loops |

### What is never logged

- Full PUUIDs (only first 8 characters: `puuid[:8]`)
- Telegram tokens or Riot API keys
- User IDs in combination with account names (no PII correlation)
- Full match payloads at INFO level

### Log file location

`logs/bot.log` — rotating, max 10 MB, 7 backups, UTF-8 encoded.
Excluded from git via `.gitignore`.

### Noisy third-party loggers

`httpx`, `telegram`, and `aiohttp` loggers are silenced to `WARNING` in `logging_setup.py` to prevent credential-adjacent data from appearing in logs.

---

## Riot Dev Key Usage

### Safe practices

- The Dev Key is sent only via the `X-Riot-Token` HTTP header — never in URLs or query strings
- The key is never logged, even at DEBUG level
- Rate limits are enforced proactively (semaphore + delay) to avoid 429s that could expose retry patterns

### Endpoint restrictions

The following endpoints return 403 on a Dev Key and are handled gracefully:

| Endpoint | Behavior on 403 |
|---|---|
| `summoner/v4` | Returns `None`, logs at DEBUG |
| `league/v4` | Returns `None`, logs at DEBUG |
| `spectator/v5` | Returns `None`, logs at DEBUG |
| `champion-mastery/v4` | Returns `None`, logs at DEBUG |

No retries are attempted on 401/403 — these are permanent failures on Dev Key, not transient errors.

---

## Dependency Security

- All dependencies are pinned in `requirements.txt`
- `python-telegram-bot` is installed separately due to its large dependency tree
- Before upgrading any dependency, check the changelog for security advisories
- Do not add dependencies that require native compilation unless strictly necessary

---

## Reporting a Vulnerability

This is a personal/educational project. If you find a security issue, open a GitHub issue with the label `security` or contact the maintainer directly. Do not include live credentials in issue reports.
