# LoLNotifierBot

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Tests](https://img.shields.io/badge/tests-78%20passing-brightgreen)
![Azure](https://img.shields.io/badge/azure-function%20app-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Telegram bot that tracks League of Legends matches for personal accounts and pro players via the Riot Games API. Deployed on Azure Function App (Python 3.11, Consumption plan) with secrets in Key Vault and data in CosmosDB.

---

## Features

| Feature | Status | Notes |
|---|---|---|
| Riot ID → PUUID resolution | ✅ | `account/v1` |
| Match history polling | ✅ | `match/v5` |
| Match notifications (KDA, CS, gold, damage, vision) | ✅ | |
| Aggregated stats (`/stats`) | ✅ | Last 5 matches |
| Performance score | ✅ | Computed locally |
| Pro player tracking (28 players) | ✅ | 4 regions |
| Summoner level / Ranked / Live game | ⚠️ | Dev key 403 — activates on prod key |

---

## Architecture

```
Azure Resource Group: rg-lolnotifier-dev
├── Function App (Python 3.11, Consumption Y1)
│   └── System-assigned Managed Identity → Key Vault Secrets User
├── Key Vault
│   ├── secret: telegram-token
│   ├── secret: riot-api-key
│   ├── secret: telegram-chat-id
│   └── secret: cosmosdb-connection
├── CosmosDB (Serverless, northeurope)
│   └── DB: lolnotifier
│       ├── container: users          (partition: /user_id)
│       ├── container: pro_players    (partition: /region)
│       └── container: match_history  (partition: /puuid, TTL: 90d)
├── Storage Account
│   └── File Share: lolnotifier-data  (Function App runtime)
├── Logic App Scheduler
│   └── POST /api/poll every 5 min → Function App
└── Log Analytics + App Insights (90 day retention)
```

Remote state: `rg-lolnotifier-tfstate / stlolnotifiertfstate`

---

## Local Development

### 1. Clone and create virtual environment

```bash
git clone https://github.com/<user>/lolnotifier-bot.git
cd lolnotifier-bot
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
pip install python-telegram-bot==20.7
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_TOKEN=<your_botfather_token>
RIOT_API_KEY=<your_riot_dev_key>
TELEGRAM_CHAT_ID=<your_telegram_user_id>
RIOT_GAME_NAME=YourGameName
RIOT_TAG_LINE=EUW
RIOT_REGION=euw1
```

### 4. Run locally

```bash
python main.py
```

### 5. Run with Docker

```bash
docker-compose up -d
```

---

## Bot Commands

| Command | Description | Example |
|---|---|---|
| `/set_summoner GameName#TAG region` | Link your LoL account | `/set_summoner LaBísica#EUW euw1` |
| `/status` | Show linked account and last poll | `/status` |
| `/stats` | Aggregated stats from last 5 matches | `/stats` |
| `/toggle` | Enable or pause notifications | `/toggle` |
| `/add_pro GameName#TAG region` | Track a pro player | `/add_pro Caps#EUW euw1` |
| `/list_pros` | List all tracked pros | `/list_pros` |
| `/remove_pro <id>` | Remove a pro by ID | `/remove_pro 3` |
| `/load_pros` | Bulk-load the 28-player dataset | `/load_pros` |

Supported regions: `na1` · `euw1` · `eun1` · `kr` · `la1` · `la2` · `br1` · `jp1` · `tr1`

---

## Azure Deployment

Every push to `main` triggers `.github/workflows/terraform.yml`:

1. Checkov IaC scan
2. `terraform init` (remote backend: `stlolnotifiertfstate`)
3. `terraform apply -auto-approve`

### First deploy (one-time bootstrap)

```bash
bash terraform/scripts/bootstrap-backend.sh dev
```

### Manual deploy

```bash
cd terraform/

export ARM_CLIENT_ID="<sp_client_id>"
export ARM_CLIENT_SECRET="<sp_client_secret>"
export ARM_TENANT_ID="<tenant_id>"
export ARM_SUBSCRIPTION_ID="<subscription_id>"

export TF_VAR_telegram_token="<token>"
export TF_VAR_riot_api_key="<key>"
export TF_VAR_telegram_chat_id="<chat_id>"

terraform init \
  -backend-config="resource_group_name=rg-lolnotifier-tfstate" \
  -backend-config="storage_account_name=stlolnotifiertfstate" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=lolnotifier.tfstate"

terraform apply
```

### Rotating the Riot Dev Key (every 24h)

```bash
az keyvault secret set \
  --vault-name kv-lolnotifier-dev-<suffix> \
  --name riot-api-key \
  --value "<new_key>"
```

No Terraform re-apply needed.

---

## Tests

```bash
# Unit tests (78 tests, no API calls)
python -m pytest tests/ -v

# Functional tests (requires .env with real keys)
python functional_test_suite.py
# Expected: Passed: 10  Failed: 0  Warn: 2
```

---

## Performance Score Formula

```
score = (winrate% × 0.40) + (avg_kda × 2.0) + (avg_cs_per_min × 0.5) + (avg_vision × 0.2)
```

Max theoretical score ≈ 100.

---

## Documentation

| Document | Description |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Module map, async lifecycle, data flow |
| [docs/data-model.md](docs/data-model.md) | CosmosDB + SQLite schema |
| [docs/dev-key-constraints.md](docs/dev-key-constraints.md) | Rate limits, 403 endpoints |
| [docs/azure-deployment.md](docs/azure-deployment.md) | Full Azure architecture and deploy guide |
| [docs/terraform-deployment-guide.md](docs/terraform-deployment-guide.md) | Step-by-step Terraform guide |
| [docs/cicd-workflow.md](docs/cicd-workflow.md) | CI/CD pipeline and branching strategy |
| [docs/message-templates.md](docs/message-templates.md) | All Telegram message formats |
| [docs/test-coverage.md](docs/test-coverage.md) | Test strategy and coverage breakdown |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [SECURITY.md](SECURITY.md) | Secrets handling and logging policy |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## License

MIT
