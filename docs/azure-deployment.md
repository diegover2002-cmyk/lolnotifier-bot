# Azure Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Resource Group                         │
│                  rg-lolnotifier-{env}                           │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────────────────────┐   │
│  │   Key Vault      │    │     Container App Environment    │   │
│  │  kv-lolnotifier  │◄───│                                  │   │
│  │                  │    │  ┌────────────────────────────┐  │   │
│  │  telegram-token  │    │  │   Container App (bot)      │  │   │
│  │  riot-api-key    │    │  │   ca-lolnotifier-{env}     │  │   │
│  │  telegram-chat-id│    │  │                            │  │   │
│  └──────────────────┘    │  │  Managed Identity ─────────┼──┘   │
│                          │  │  reads secrets from KV     │      │
│  ┌──────────────────┐    │  └────────────┬───────────────┘      │
│  │  Storage Account │    │               │                      │
│  │  File Share      │◄───┼───────────────┘ /app/data mount      │
│  │  /lolnotifier.db │    └──────────────────────────────────┘   │
│  └──────────────────┘                                           │
│                                                                 │
│  ┌──────────────────┐                                           │
│  │ Application      │    Logs, traces, exception alerts         │
│  │ Insights         │◄── from bot via connection string env var  │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Terraform Module Structure

```
terraform/
├── main.tf                          # Root: wires all modules
├── variables.tf                     # Input variables
├── outputs.tf                       # Output values
├── modules/
│   ├── container_app/               # Azure Container App (bot runtime)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── keyvault/                    # Azure Key Vault (secrets)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── storage/                     # Azure Storage (SQLite persistence)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/                  # Application Insights + alerts
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── dev/
    │   ├── main.tf
    │   └── terraform.tfvars.example
    └── prod/
        └── main.tf                  # Has remote backend configured
```

---

## Prerequisites

1. Azure CLI installed and logged in: `az login`
2. Terraform >= 1.6 installed
3. An Azure subscription with Contributor access
4. Docker image built and pushed to a registry (GitHub Container Registry or Azure Container Registry)

---

## Step-by-Step Deployment

### 1. Build and push the Docker image

```bash
# From lolnotifier/ directory
docker build -t ghcr.io/<your-github-user>/lolnotifier-bot:v3.0.0 .
docker push ghcr.io/<your-github-user>/lolnotifier-bot:v3.0.0
```

### 2. Create Terraform state storage (one-time, manual)

```bash
az group create --name rg-lolnotifier-tfstate --location westeurope

az storage account create \
  --name stlolnotifiertfstate \
  --resource-group rg-lolnotifier-tfstate \
  --sku Standard_LRS \
  --min-tls-version TLS1_2

az storage container create \
  --name tfstate \
  --account-name stlolnotifiertfstate
```

### 3. Set secrets as environment variables (never in tfvars)

```bash
export TF_VAR_telegram_token="<your_telegram_token>"
export TF_VAR_riot_api_key="<your_riot_api_key>"
export TF_VAR_telegram_chat_id="<your_chat_id>"
```

### 4. Deploy dev environment

```bash
cd terraform/environments/dev
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### 5. Verify deployment

```bash
# Check Container App is running
az containerapp show \
  --name ca-lolnotifier-dev \
  --resource-group rg-lolnotifier-dev \
  --query "properties.latestRevisionFqdn"

# Tail logs
az containerapp logs show \
  --name ca-lolnotifier-dev \
  --resource-group rg-lolnotifier-dev \
  --follow
```

---

## Secret Rotation

Secrets are stored in Key Vault with `lifecycle { ignore_changes = [value] }` — Terraform will not overwrite them after initial creation. To rotate:

```bash
az keyvault secret set \
  --vault-name kv-lolnotifier-prod \
  --name riot-api-key \
  --value "<new_key>"
```

The Container App picks up the new value on next restart (or trigger a revision):

```bash
az containerapp revision restart \
  --name ca-lolnotifier-prod \
  --resource-group rg-lolnotifier-prod \
  --revision <revision-name>
```

---

## Security Checklist (Checkov)

Run Checkov against the Terraform modules before applying:

```bash
pip install checkov
checkov -d terraform/ --framework terraform
```

Key checks that should pass:
- `CKV_AZURE_42` — Key Vault soft delete enabled ✅
- `CKV_AZURE_109` — Key Vault purge protection enabled ✅
- `CKV_AZURE_33` — Storage account uses HTTPS only ✅
- `CKV_AZURE_3` — Storage account minimum TLS 1.2 ✅
- `CKV_AZURE_190` — Container App uses managed identity ✅

---

## Cost Estimate (Dev Key usage)

| Resource | SKU | Estimated monthly cost |
|---|---|---|
| Container App | 0.25 vCPU / 0.5 GB | ~$5–10 |
| Key Vault | Standard | ~$0.03/10k ops |
| Storage Account | Standard LRS, 1 GB | ~$0.02 |
| Application Insights | Pay-per-use, 30d retention | ~$0–2 |
| **Total** | | **~$7–15/month** |

---

## Dev Key Considerations on Azure

- Dev Key expires every 24 hours — the bot handles 401 gracefully (returns `None`, no crash)
- To renew: update the Key Vault secret `riot-api-key` and restart the Container App revision
- `POLL_INTERVAL=300` (5 min) keeps well within Dev Key rate limits even on Azure
- Single Container App replica (`max_replicas = 1`) prevents duplicate notifications from concurrent instances
