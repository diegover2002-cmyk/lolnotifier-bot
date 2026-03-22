# Release Plan — v3.0.0

## Pre-Release Checklist

### Code Quality
- [x] 78 unit tests passing (`python -m pytest tests/ -v`)
- [x] No `print()` statements in production code (all use `logging`)
- [x] No hardcoded credentials, tokens, or PUUIDs in any source file
- [x] All public functions have docstrings and type hints
- [x] `from __future__ import annotations` in all modules
- [x] `riot_account.py` uses `logging` instead of `print()`

### Documentation
- [x] `README.md` — full setup guide, command table, example output, architecture
- [x] `CHANGELOG.md` — v3.0.0 entry with all changes
- [x] `CONTRIBUTING.md` — pro player workflow, test guidelines, PR checklist
- [x] `SECURITY.md` — secrets policy, logging policy, incident response
- [x] `docs/architecture.md` — module map, async lifecycle, data flow
- [x] `docs/data-model.md` — SQLite schema v2, field descriptions
- [x] `docs/dev-key-constraints.md` — rate limits, 403 endpoints, upgrade path
- [x] `docs/message-templates.md` — all Telegram message formats
- [x] `docs/test-coverage.md` — test breakdown by file and function
- [x] `docs/future-improvements.md` — roadmap and conceptual CI/CD
- [x] `docs/azure-deployment.md` — Terraform guide, step-by-step deploy
- [x] `docs/cicd-workflow.md` — conceptual pipeline definitions

### Infrastructure
- [x] `Dockerfile` — Python 3.11-slim, non-root user, selective COPY
- [x] `docker-compose.yml` — named volumes, no bind-mount DB
- [x] `.gitignore` — Terraform state files excluded
- [x] `terraform/` — full module structure (keyvault, container_app, storage, monitoring)
- [x] `pyproject.toml` — project metadata, version 3.0.0

### Security
- [x] `.env` excluded by `.gitignore`
- [x] `*.db` excluded by `.gitignore`
- [x] `*.tfstate` and `*.tfvars` excluded by `.gitignore`
- [x] No secrets in `terraform.tfvars.example` (placeholders only)
- [x] Key Vault module has purge protection and RBAC authorization

---

## Release Steps

### Step 1 — Final test run

```bash
cd lolnotifier
python -m pytest tests/ -v
# Expected: 78 passed
```

### Step 2 — Functional test run (requires .env)

```bash
python functional_test_suite.py
# Expected: Passed: 10  Failed: 0  Warn: 2
```

### Step 3 — Update version in pyproject.toml

```toml
[project]
version = "3.0.0"
```

### Step 4 — Commit release

```bash
git add -A
git commit -m "chore: release v3.0.0 - production-ready, Azure-ready"
```

### Step 5 — Tag the release

```bash
git tag -a v3.0.0 -m "Release v3.0.0

- 78 unit tests passing
- Full documentation suite (README, CONTRIBUTING, SECURITY, docs/)
- Terraform modules for Azure deployment (Container App, Key Vault, Storage, Monitoring)
- Dockerfile hardened (Python 3.11, non-root user)
- Dev Key compliant (account/v1 + match/v5 only)
- Conceptual CI/CD pipeline defined"

git push origin main --tags
```

### Step 6 — Create GitHub Release

On GitHub: Releases → Draft a new release → Select tag `v3.0.0`

Release title: `v3.0.0 — Production-Ready Release`

Release body (copy from CHANGELOG.md v3.0.0 section).

---

## Post-Release: Azure Migration Path

### Phase 1 — Local Docker (current)

```bash
docker-compose up -d
```

Bot runs locally with SQLite. Good for development and testing.

### Phase 2 — Azure Container App (manual deploy)

```bash
# Build and push image
docker build -t ghcr.io/<user>/lolnotifier-bot:v3.0.0 .
docker push ghcr.io/<user>/lolnotifier-bot:v3.0.0

# Deploy with Terraform
cd terraform/environments/dev
export TF_VAR_telegram_token="<token>"
export TF_VAR_riot_api_key="<key>"
export TF_VAR_telegram_chat_id="<chat_id>"
terraform init && terraform apply
```

See `docs/azure-deployment.md` for full instructions.

### Phase 3 — Production Key Upgrade

When a production Riot API key is obtained:

1. Update Key Vault secret: `az keyvault secret set --vault-name kv-lolnotifier-prod --name riot-api-key --value "<prod_key>"`
2. Restart Container App revision
3. No code changes needed — all 403-guarded endpoints activate automatically

### Phase 4 — CI/CD Automation

Implement the pipelines defined in `docs/cicd-workflow.md`:
1. Create GitHub Actions workflow files in `.github/workflows/`
2. Configure GitHub Environments (dev, prod) with protection rules
3. Add `AZURE_CREDENTIALS` secret to GitHub repository
4. Enable branch protection on `main` and `develop`

---

## Rollback Plan

If v3.0.0 has a critical issue after deployment:

```bash
# Revert Container App to previous image
az containerapp update \
  --name ca-lolnotifier-prod \
  --resource-group rg-lolnotifier-prod \
  --image ghcr.io/<user>/lolnotifier-bot:v2.1.0

# Or revert git tag and redeploy
git checkout v2.1.0
docker build -t ghcr.io/<user>/lolnotifier-bot:v2.1.0-hotfix .
```

The SQLite database is unaffected by image rollbacks — schema v2 is backward compatible.

---

## Known Limitations at Release

| Limitation | Impact | Mitigation |
|---|---|---|
| Dev Key expires every 24h | Bot returns `None` on 401, no crash | Rotate key in Key Vault |
| SQLite over Azure File Share | Not suitable for >1 replica | Acceptable for single-instance bot |
| No ranked/live game data | Features return `None` | Auto-activates on prod key |
| No CI/CD actions active | Manual deploy required | Defined in `docs/cicd-workflow.md` |
| No database unit tests | DB layer untested in isolation | Covered by functional tests |
