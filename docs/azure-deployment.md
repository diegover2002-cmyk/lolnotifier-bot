# Azure Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Azure Resource Group                             │
│                  rg-lolnotifier-dev                                 │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐   │
│  │   Key Vault      │    │   Azure Function App (Python 3.11)   │   │
│  │  kv-lolnotifier  │◄───│   func-lolnotifier-dev-h4dx          │   │
│  │  -dev-h4dx       │    │                                      │   │
│  │  telegram-token  │    │   System-Assigned Managed Identity   │   │
│  │  riot-api-key    │    │   reads secrets via KV references    │   │
│  │  telegram-chat-id│    └──────────────┬───────────────────────┘   │
│  │  cosmosdb-conn   │                   │                           │
│  └──────────────────┘    ┌──────────────▼───────────────────────┐   │
│                          │   Logic App Scheduler                │   │
│  ┌──────────────────┐    │   logic-lolnotifier-scheduler-dev    │   │
│  │  Storage Account │    │   Triggers /api/poll every 5 min     │   │
│  │  stlolnotifier   │    │   System-Assigned Managed Identity   │   │
│  │  devh4dx         │    └──────────────────────────────────────┘   │
│  │  File Share      │                                               │
│  └──────────────────┘    ┌──────────────────────────────────────┐   │
│                          │   CosmosDB (NoSQL / Serverless)      │   │
│  ┌──────────────────┐    │   cosmos-lolnotifier-dev-h4dx        │   │
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
│   ├── keyvault/                    # Azure Key Vault + secrets + diagnostic settings
│   ├── cosmosdb/                    # CosmosDB account + database + 3 containers
│   ├── storage/                     # Storage Account + File Share
│   ├── function_app/                # Function App + Service Plan + KV role assignment
│   ├── monitoring/                  # Log Analytics Workspace + App Insights + alerts
│   └── scheduler/                   # Logic App + recurrence trigger + HTTP action
└── scripts/
    └── bootstrap-backend.ps1        # One-time tfstate storage creation
```

---

## Prerequisites

1. Azure CLI installed: `az login`
2. Terraform >= 1.6
3. GitHub repository with secrets configured (see below)
4. Bootstrap script run once: `.\terraform\scripts\bootstrap-backend.ps1`

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

After initial deploy, secrets live in Key Vault. The Function App reads them via
`@Microsoft.KeyVault(SecretUri=...)` references — GitHub secrets are only needed
for Terraform to write them to Key Vault on first apply.

---

## Deployment (Automated via GitHub Actions)

Every push to `main` triggers `.github/workflows/terraform.yml`:

1. Checkov IaC scan (soft fail — warnings only)
2. `terraform init` with remote backend config
3. `terraform apply -auto-approve`

No manual steps needed after initial bootstrap.

---

## Manual Deployment (Local)

```bash
cd terraform

# Set credentials
export ARM_CLIENT_ID="<sp_client_id>"
export ARM_CLIENT_SECRET="<sp_client_secret>"
export ARM_TENANT_ID="<tenant_id>"
export ARM_SUBSCRIPTION_ID="<subscription_id>"

# Set secret values (initial deploy only)
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

Secrets use `lifecycle { ignore_changes = [value] }` — Terraform won't overwrite
them after initial creation. To rotate the Riot Dev Key (expires every 24h):

```bash
az keyvault secret set \
  --vault-name kv-lolnotifier-dev-h4dx \
  --name riot-api-key \
  --value "<new_key>"
```

The Function App picks up the new value automatically on next execution
(Key Vault references are resolved at runtime).

---

## MCSB Security Posture

| Control | Status | Notes |
|---|---|---|
| Key Vault soft delete | ✅ | 7 days (immutable after creation) |
| Key Vault purge protection | ✅ | Enabled |
| Key Vault RBAC | ✅ | `enableRbacAuthorization: true` |
| Key Vault network ACLs | ✅ | `defaultAction: Deny` |
| Key Vault audit logs | ✅ | Diagnostic settings → Log Analytics |
| Secret expiration dates | ✅ | Set on all secrets |
| Storage HTTPS only | ✅ | |
| Storage TLS 1.2 | ✅ | |
| Storage network rules | ✅ | `defaultAction: Deny` + `bypass: AzureServices` |
| Function App HTTPS | ✅ | |
| Function App Managed Identity | ✅ | System Assigned |
| Function App secrets via KV refs | ✅ | No plaintext secrets in app settings |
| CosmosDB encryption at rest | ✅ | Default AES-256 |
| CosmosDB metadata write protection | ✅ | `access_key_metadata_writes_enabled: false` |
| CosmosDB diagnostic logs | ✅ | DataPlaneRequests + QueryRuntimeStatistics |
| Logic App Managed Identity | ✅ | System Assigned |
| Logic App diagnostic logs | ✅ | WorkflowRuntime |
| Log Analytics retention | ✅ | 90 days |
| App Insights retention | ✅ | 90 days |
| SP least privilege | ✅ | `User Access Administrator` scoped to RG only |
| tfstate TLS 1.2 | ✅ | |

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
