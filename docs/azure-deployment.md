# Azure Deployment Guide

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Azure Resource Group                             │
│                  rg-lolnotifier-dev                                 │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐   │
│  │   Key Vault      │    │   Azure Function App (Python 3.11)   │   │
│  │  kv-lolnotifier  │◄───│   func-lolnotifier-dev-{suffix}      │   │
│  │  -dev-{suffix}   │    │                                      │   │
│  │  telegram-token  │    │   System-Assigned Managed Identity   │   │
│  │  riot-api-key    │    │   reads secrets via KV references    │   │
│  │  telegram-chat-id│    └──────────────┬───────────────────────┘   │
│  │  cosmosdb-conn   │                   │                           │
│  └──────────────────┘    ┌──────────────▼───────────────────────┐   │
│                          │   Logic App Scheduler                │   │
│  ┌──────────────────┐    │   logic-lolnotifier-scheduler-dev    │   │
│  │  Storage Account │    │   POST /api/poll every 5 min         │   │
│  │  stlolnotifier   │    │   System-Assigned Managed Identity   │   │
│  │  dev{suffix}     │    └──────────────────────────────────────┘   │
│  │  File Share      │                                               │
│  └──────────────────┘    ┌──────────────────────────────────────┐   │
│                          │   CosmosDB (NoSQL / Serverless)      │   │
│  ┌──────────────────┐    │   cosmos-lolnotifier-dev-{suffix}    │   │
│  │  App Insights    │    │   northeurope                        │   │
│  │  + Log Analytics │    │   DB: lolnotifier                    │   │
│  │  log-lolnotifier │    │   Containers: users, match_history,  │   │
│  │  -dev            │    │   pro_players                        │   │
│  └──────────────────┘    └──────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

Remote State (separate RG):
  rg-lolnotifier-tfstate / stlolnotifiertfstate / container: tfstate
```

## Terraform Module Structure

```
terraform/
├── main.tf                          # Root: wires all modules
├── variables.tf                     # Input variables
├── outputs.tf                       # Output values
├── modules/
│   ├── keyvault/                    # Key Vault + secrets + diagnostic settings
│   ├── cosmosdb/                    # CosmosDB account + database + 3 containers
│   ├── storage/                     # Storage Account + File Share
│   ├── function_app/                # Function App + Service Plan + KV role assignment
│   ├── monitoring/                  # Log Analytics Workspace + App Insights + alerts
│   └── scheduler/                   # Logic App + recurrence trigger + HTTP action
└── scripts/
    └── bootstrap-backend.sh         # One-time tfstate storage creation
```

---

## GitHub Secrets Required

| Secret | Description |
|---|---|
| `ARM_CLIENT_ID` | Service Principal client ID |
| `ARM_CLIENT_SECRET` | Service Principal client secret |
| `ARM_TENANT_ID` | Azure AD tenant ID |
| `ARM_SUBSCRIPTION_ID` | Azure subscription ID |
| `TF_VAR_TELEGRAM_TOKEN` | Telegram Bot API token (initial deploy only) |
| `TF_VAR_RIOT_API_KEY` | Riot Games Dev API key (initial deploy only) |
| `TF_VAR_TELEGRAM_CHAT_ID` | Telegram chat ID for notifications |

After initial deploy, secrets live in Key Vault. The Function App reads them via `@Microsoft.KeyVault(SecretUri=...)` references — GitHub secrets are only needed for Terraform to write them on first apply.

---

## Deployment (Automated via GitHub Actions)

Every push to `main` triggers `.github/workflows/terraform.yml`:

1. Checkov IaC scan (soft fail)
2. Fetch runner public IP (injected as `TF_VAR_allowed_ip_rules` for storage firewall)
3. `terraform init` with remote backend
4. `terraform apply -auto-approve`

---

## Manual Deployment

```bash
cd terraform

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

---

## Secret Rotation

Secrets use `lifecycle { ignore_changes = [value] }` — Terraform won't overwrite them after initial creation.

To rotate the Riot Dev Key (expires every 24h):

```bash
az keyvault secret set \
  --vault-name kv-lolnotifier-dev-<suffix> \
  --name riot-api-key \
  --value "<new_key>"
```

The Function App picks up the new value automatically on next execution.

---

## MCSB Security Posture

| Control | Status | Notes |
|---|---|---|
| Key Vault soft delete | ✅ | 7 days |
| Key Vault purge protection | ✅ | Enabled |
| Key Vault RBAC | ✅ | `enableRbacAuthorization: true` |
| Key Vault network ACLs | ✅ | `defaultAction: Deny` |
| Key Vault audit logs | ✅ | Diagnostic settings → Log Analytics |
| Secret expiration dates | ✅ | Set on all secrets |
| Storage HTTPS only | ✅ | |
| Storage TLS 1.2 | ✅ | |
| Function App HTTPS | ✅ | |
| Function App Managed Identity | ✅ | System Assigned |
| Function App secrets via KV refs | ✅ | No plaintext secrets in app settings |
| TELEGRAM_CHAT_ID via KV ref | ✅ | Added in v5.2.0 |
| CosmosDB encryption at rest | ✅ | Default AES-256 |
| CosmosDB metadata write protection | ✅ | `access_key_metadata_writes_enabled: false` |
| CosmosDB diagnostic logs | ✅ | DataPlaneRequests + QueryRuntimeStatistics |
| Logic App Managed Identity | ✅ | System Assigned |
| Logic App → Function App auth | ✅ | ManagedServiceIdentity (fixed in v5.2.0) |
| Logic App diagnostic logs | ✅ | WorkflowRuntime |
| Log Analytics retention | ✅ | 90 days |
| App Insights retention | ✅ | 90 days |
| Log Analytics diagnostic logs | ✅ | Audit → Log Analytics (fixed in v5.2.0) |
| SP least privilege | ✅ | Contributor scoped to RG only |

---

## Cost Estimate (Dev environment)

| Resource | SKU | Est. monthly cost |
|---|---|---|
| Function App | Y1 Consumption | ~$0–5 |
| CosmosDB | Serverless | ~$0–2 |
| Key Vault | Standard | ~$0.03/10k ops |
| Storage Account | Standard LRS | ~$0.02 |
| Log Analytics | PerGB2018 | ~$0–3 |
| Logic App | Consumption | ~$0 (free tier) |
| **Total** | | **~$2–10/month** |

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `403` on `azurerm_storage_share` | Storage firewall blocks CI runner | Runner IP injected via `TF_VAR_allowed_ip_rules` automatically |
| `AuthorizationFailed` | SP lacks Contributor role | Re-run `az ad sp create-for-rbac` with correct scope |
| `KeyVaultNameNotAvailable` | KV name taken globally | Change suffix in `random_string` |
| `SecretNotFound` in Function App | KV reference before identity RBAC propagates | Wait 2-3 min and restart Function App |
| `403` from Riot API | Dev Key expired | Rotate key in Key Vault |
| `429` from Riot API | Rate limit hit | Increase `poll_interval_seconds` in tfvars |
