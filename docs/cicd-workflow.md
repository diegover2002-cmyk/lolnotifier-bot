# CI/CD Workflow

## Branching Strategy

```
main          ← stable, auto-deploys to Azure on push
  └── develop ← integration branch
        ├── feature/<name>
        ├── fix/<name>
        └── docs/<name>
```

---

## Workflow 1 — CI (`ci.yml`)

Triggers: PR to `main` or `develop`, push to `develop`.

| Job | Tool | Notes |
|---|---|---|
| `lint` | ruff | PEP8 + formatting check |
| `unit-tests` | pytest + pytest-cov | 78 tests, no API calls, coverage gate ≥ 55% |
| `security` | bandit + checkov | Python SAST + Terraform IaC scan (soft-fail) |

---

## Workflow 2 — Terraform (`terraform.yml`)

Triggers: push to `main` on `terraform/**` changes, or manual dispatch.

```
checkov (IaC scan, soft-fail)
  └── apply (only on push or workflow_dispatch)
        ├── Get runner public IP (for storage firewall)
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

---

## Workflow 3 — Release (`release.yml`)

Triggers: push of a `v*.*.*` tag.

```
build  → Build & push Docker image to ghcr.io
  └── deploy-dev  → Deploy to Function App (dev)
        └── deploy-prod  → Deploy to Function App (prod)
                           (requires manual approval in GitHub Environments)
```

---

## Functional Tests (manual only)

Excluded from CI — require live Riot Dev Key and send real Telegram messages.

```bash
python functional_test_suite.py
# Expected: Passed: 10  Failed: 0  Warn: 2
```

Run manually before tagging a release.

---

## Release Process

```bash
# 1. Ensure unit tests pass
python -m pytest tests/ -v

# 2. Run functional tests manually
python functional_test_suite.py

# 3. Update CHANGELOG.md and pyproject.toml version

git add CHANGELOG.md pyproject.toml
git commit -m "chore: release vX.X.X"
git tag -a vX.X.X -m "Release vX.X.X"
git push origin main --tags
```
