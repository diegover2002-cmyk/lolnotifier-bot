# CI/CD Workflow

Three GitHub Actions workflows are active in `.github/workflows/`.

---

## Branching Strategy

```
main          ← stable, tagged releases only
  └── develop ← integration branch, all features merge here first
        ├── feature/<name>   ← new functionality
        ├── fix/<name>       ← bug fixes
        └── docs/<name>      ← documentation only
```

| Branch | Protected | Requires PR | Tests required |
|---|---|---|---|
| `main` | Yes | Yes | All pass |
| `develop` | Yes | Yes | Unit tests pass |
| `feature/*` | No | No | Local |

---

## Workflow 1 — CI (`ci.yml`)

Triggers: PR targeting `main` or `develop`, push to `develop`.

| Job | Tool | Notes |
|---|---|---|
| `lint` | ruff | PEP8 + formatting check |
| `unit-tests` | pytest + pytest-cov | 78 tests, no API calls, coverage gate ≥ 55% |
| `security` | bandit + checkov | Python SAST + Terraform IaC scan (soft-fail) |

Coverage report uploaded as artifact (`coverage-report`).
Security reports uploaded as artifact (`security-reports`).

---

## Workflow 2 — Terraform (`terraform.yml`)

Triggers: push/PR to `main` on `terraform/**` changes, or manual dispatch.

```
checkov (IaC scan, soft-fail)
  └── apply (only on push or workflow_dispatch)
        ├── terraform init  (remote backend: stlolnotifiertfstate)
        └── terraform apply -auto-approve
```

Required GitHub secrets:

| Secret | Used by |
|---|---|
| `ARM_CLIENT_ID` | Terraform auth |
| `ARM_CLIENT_SECRET` | Terraform auth |
| `ARM_TENANT_ID` | Terraform auth |
| `ARM_SUBSCRIPTION_ID` | Terraform auth |
| `TF_VAR_TELEGRAM_TOKEN` | Key Vault secret (initial deploy only) |
| `TF_VAR_RIOT_API_KEY` | Key Vault secret (initial deploy only) |
| `TF_VAR_TELEGRAM_CHAT_ID` | Key Vault secret (initial deploy only) |

After initial deploy, secrets live in Key Vault — GitHub secrets are only needed for Terraform to write them on first apply.

---

## Workflow 3 — Release (`release.yml`)

Triggers: push of a `v*.*.*` tag.

```
build  → Build & push Docker image to ghcr.io
  └── deploy-dev  → Deploy to Function App (dev), environment: dev
        └── deploy-prod  → Deploy to Function App (prod), environment: prod
                           (requires manual approval in GitHub Environments)
```

Deploy step uses `az functionapp deployment source config-zip` or `az functionapp update` targeting `func-lolnotifier-dev-<suffix>`.

---

## Functional Tests (manual only)

Excluded from CI — require live Riot Dev Key and send real Telegram messages.

```bash
python functional_test_suite.py
# Expected: Passed: 10  Failed: 0  Warn: 2
```

Run manually before tagging a release.

---

## Release Tagging Process

```bash
# 1. Ensure unit tests pass
python -m pytest tests/ -v

# 2. Run functional tests manually
python functional_test_suite.py

# 3. Update CHANGELOG.md and pyproject.toml version

git add CHANGELOG.md pyproject.toml
git commit -m "chore: release v3.x.x"
git tag -a v3.x.x -m "Release v3.x.x"
git push origin main --tags
```

---

## Monitoring Alerts (Application Insights)

| Alert | Condition | Severity |
|---|---|---|
| Exception spike | >10 exceptions in 5 min | Warning |
| Function restart | Host restart detected | Critical |
| API 429 rate limit | `traces \| where message contains "429"` | Warning |
| Dev Key expiry | `traces \| where message contains "401"` | Info |

```kql
traces
| where timestamp > ago(1h)
| where message contains "403" or message contains "401"
| summarize count() by bin(timestamp, 5m)
| render timechart
```
