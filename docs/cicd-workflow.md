# CI/CD Workflow (Conceptual)

> This document defines the intended CI/CD pipeline. No GitHub Actions are currently active in this repo — pipelines are described here for planning and future implementation.

---

## Branching Strategy

```
main          ← stable, tagged releases only
  └── develop ← integration branch, all features merge here first
        ├── feature/<name>   ← new functionality
        ├── fix/<name>       ← bug fixes
        └── docs/<name>      ← documentation only
```

### Rules

| Branch | Who pushes | Protected | Requires PR | Tests required |
|---|---|---|---|---|
| `main` | CI only (via merge from develop) | Yes | Yes | All pass |
| `develop` | Developers via PR | Yes | Yes | Unit tests pass |
| `feature/*` | Developer | No | No | Local |

---

## Pipeline: Pull Request (feature → develop)

Runs on every PR targeting `develop`. Must pass before merge.

```yaml
# Conceptual — not yet implemented as GitHub Actions

name: PR Checks

on:
  pull_request:
    branches: [develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check .                    # PEP8 + style
      - run: ruff format --check .           # Formatting

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install mypy types-aiofiles
      - run: mypy *.py --ignore-missing-imports

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt pytest pytest-asyncio
      - run: python -m pytest tests/ -v --tb=short
      # Note: functional tests excluded — require real API keys

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install checkov bandit
      - run: checkov -d terraform/ --framework terraform --quiet
      - run: bandit -r *.py -ll              # Python security scan (medium+ severity)
```

---

## Pipeline: Release (develop → main)

Runs when a PR from `develop` to `main` is merged. Tags and deploys.

```yaml
name: Release

on:
  push:
    tags: ["v*.*.*"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
            ghcr.io/${{ github.repository }}:latest

  deploy-dev:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Update Container App image
        run: |
          az containerapp update \
            --name ca-lolnotifier-dev \
            --resource-group rg-lolnotifier-dev \
            --image ghcr.io/${{ github.repository }}:${{ github.ref_name }}

  deploy-prod:
    needs: deploy-dev
    runs-on: ubuntu-latest
    environment: prod          # Requires manual approval in GitHub Environments
    steps:
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      - name: Update Container App image
        run: |
          az containerapp update \
            --name ca-lolnotifier-prod \
            --resource-group rg-lolnotifier-prod \
            --image ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

---

## Secrets in CI/CD

| Secret name | Where stored | Used by |
|---|---|---|
| `AZURE_CREDENTIALS` | GitHub Actions secret | Azure login step |
| `TELEGRAM_TOKEN` | Azure Key Vault | Container App (via managed identity) |
| `RIOT_API_KEY` | Azure Key Vault | Container App (via managed identity) |
| `TF_VAR_telegram_token` | GitHub Actions secret | Terraform apply (initial deploy only) |

**Never** store Telegram tokens or Riot API keys as GitHub Actions secrets after initial Key Vault setup — use managed identity from that point on.

---

## Functional Tests in CI

Functional tests (`functional_test_suite.py`) are **excluded from CI** because:
- They require a live Riot Dev Key (expires every 24h)
- They depend on real match history (changes constantly)
- They send real Telegram messages

Run them manually before tagging a release:

```bash
python functional_test_suite.py
# Expected: Passed: 10  Failed: 0  Warn: 2
```

---

## Release Tagging Process

```bash
# 1. Ensure all unit tests pass
python -m pytest tests/ -v

# 2. Run functional tests manually
python functional_test_suite.py

# 3. Update CHANGELOG.md with new version entry

# 4. Update version in pyproject.toml

# 5. Commit and tag
git add CHANGELOG.md pyproject.toml
git commit -m "chore: release v3.0.0"
git tag -a v3.0.0 -m "Release v3.0.0 — production-ready, Azure-ready"
git push origin main --tags
```

---

## Monitoring and Alerting

After deployment, configure these Application Insights alerts:

| Alert | Condition | Severity |
|---|---|---|
| Exception spike | >10 exceptions in 5 min | Warning |
| Container restart | Revision restart detected | Critical |
| API 429 rate limit | Custom log query: `traces | where message contains "429"` | Warning |
| Dev Key expiry | Custom log query: `traces | where message contains "401"` | Info |

Query example for Application Insights (KQL):

```kql
traces
| where timestamp > ago(1h)
| where message contains "403" or message contains "401"
| summarize count() by bin(timestamp, 5m)
| render timechart
```
