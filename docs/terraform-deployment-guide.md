# Terraform Deployment Guide

## Architecture Deployed

```
Azure Subscription
└── rg-lolnotifier-{env}
    ├── Key Vault          (kv-lolnotifier-{env}-{suffix})
    │   ├── secret: telegram-token
    │   ├── secret: riot-api-key
    │   ├── secret: telegram-chat-id
    │   └── secret: cosmosdb-connection
    │
    ├── Cosmos DB          (cosmos-lolnotifier-{env}-{suffix})
    │   └── database: lolnotifier
    │       ├── container: users          (partition: /user_id)
    │       ├── container: pro_players    (partition: /region)
    │       └── container: match_history  (partition: /puuid, TTL: 90d)
    │
    ├── Storage Account    (stlolnotifier{env}{suffix})
    │   └── file share: lolnotifier-data  (Function App runtime)
    │
    ├── Function App       (func-lolnotifier-{env}-{suffix})
    │   ├── System-assigned managed identity → Key Vault Secrets User
    │   ├── App settings: KV references (no raw secrets)
    │   └── Python 3.11, Linux, Consumption plan
    │
    ├── Logic App          (logic-lolnotifier-scheduler-{env})
    │   └── Recurrence trigger → POST /api/poll every 5 min
    │
    └── Application Insights (appi-lolnotifier-{env})
        └── Alert: exception spike > 10 in 5 min

rg-lolnotifier-tfstate  (separate, created by bootstrap script)
└── Storage Account      (stlolnotifiertfstate)
    └── container: tfstate → lolnotifier-{env}.tfstate
```

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Terraform | >= 1.6 | https://developer.hashicorp.com/terraform/install |
| Azure CLI | >= 2.50 | https://learn.microsoft.com/en-us/cli/azure/install-azure-cli |
| Python | >= 3.11 | For local bot testing |
| Checkov | >= 3.0 | `pip install checkov` |

---

## Step 1 — Azure Authentication

### Option A: Interactive (local development)

```bash
az login
az account list --output table
az account set --subscription "<your_subscription_id>"

# Verify
az account show --query "{name:name, id:id, state:state}"
```

### Option B: Service Principal (CI/CD or automated)

```bash
# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "sp-lolnotifier-terraform" \
  --role "Contributor" \
  --scopes "/subscriptions/<subscription_id>" \
  --output json

# Set environment variables from the output
# Windows (PowerShell):
$env:ARM_CLIENT_ID       = "<appId>"
$env:ARM_CLIENT_SECRET   = "<password>"
$env:ARM_TENANT_ID       = "<tenant>"
$env:ARM_SUBSCRIPTION_ID = "<subscription_id>"

# Linux / macOS:
export ARM_CLIENT_ID="<appId>"
export ARM_CLIENT_SECRET="<password>"
export ARM_TENANT_ID="<tenant>"
export ARM_SUBSCRIPTION_ID="<subscription_id>"
```

---

## Step 2 — Set Secret Variables

Secrets are passed via environment variables — never written to files.

```bash
# Windows (PowerShell):
$env:TF_VAR_telegram_token   = "<your_telegram_token>"
$env:TF_VAR_riot_api_key     = "<your_riot_dev_key>"
$env:TF_VAR_telegram_chat_id = "<your_telegram_chat_id>"

# Linux / macOS:
export TF_VAR_telegram_token="<your_telegram_token>"
export TF_VAR_riot_api_key="<your_riot_dev_key>"
export TF_VAR_telegram_chat_id="<your_telegram_chat_id>"
```

---

## Step 3 — Bootstrap Remote State (first time only)

```bash
bash terraform/scripts/bootstrap-backend.sh dev
```

This creates `rg-lolnotifier-tfstate` and `stlolnotifiertfstate` storage account. Run once per environment.

---

## Step 4 — Configure tfvars

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — only non-secret values (environment, location, SKUs)
# terraform.tfvars is excluded by .gitignore
```

---

## Step 5 — Security Scan (Checkov)

Run before every apply:

```bash
pip install checkov

# Scan all Terraform files
checkov -d terraform/ --framework terraform --output cli

# Scan with SARIF output (for GitHub Security tab)
checkov -d terraform/ --framework terraform --output sarif --output-file checkov-results.sarif
```

### Expected passing checks

| Check ID | Description |
|---|---|
| CKV_AZURE_42 | Key Vault soft delete enabled |
| CKV_AZURE_109 | Key Vault purge protection enabled |
| CKV_AZURE_110 | Key Vault RBAC authorization enabled |
| CKV_AZURE_33 | Storage account HTTPS only |
| CKV_AZURE_3 | Storage account TLS 1.2 minimum |
| CKV_AZURE_59 | Storage account public access disabled |
| CKV_AZURE_190 | Function App HTTPS only |
| CKV_AZURE_70 | Function App managed identity enabled |

### Known acceptable suppressions

```hcl
# In storage/main.tf — public network access is needed for Function App runtime
# Suppress: CKV_AZURE_35 (storage account network rules)
# Reason: Function App Consumption plan uses shared infrastructure, no VNet injection
```

---

## Step 6 — Initialize Terraform

```bash
cd terraform/
terraform init

# Expected output:
# Initializing the backend...
# Successfully configured the backend "azurerm"!
# Terraform has been successfully initialized!
```

If backend storage doesn't exist yet, run Step 3 first.

---

## Step 7 — Validate Configuration

```bash
terraform validate

# Expected: Success! The configuration is valid.
```

---

## Step 8 — Plan Deployment

```bash
terraform plan -out=tfplan

# Review the plan carefully:
# - Check resource names include the random suffix
# - Verify no secrets appear in the plan output (sensitive = true hides them)
# - Confirm Key Vault secret values show as "(sensitive value)"
```

---

## Step 9 — Apply

```bash
terraform apply tfplan

# Type 'yes' when prompted (or use -auto-approve in CI)
# Typical duration: 8-12 minutes (CosmosDB takes longest)
```

---

## Step 10 — Verify Deployment

```bash
# Show all outputs
terraform output

# Check Function App is running
az functionapp show \
  --name "func-lolnotifier-dev-<suffix>" \
  --resource-group "rg-lolnotifier-dev" \
  --query "{state:state, hostname:defaultHostName}"

# Verify Key Vault secrets exist (not their values)
az keyvault secret list \
  --vault-name "kv-lolnotifier-dev-<suffix>" \
  --query "[].name" \
  --output table

# Tail Function App logs
az webapp log tail \
  --name "func-lolnotifier-dev-<suffix>" \
  --resource-group "rg-lolnotifier-dev"
```

---

## Rotating the Riot Dev Key (every 24h)

```bash
# Get new key from developer.riotgames.com, then:
az keyvault secret set \
  --vault-name "kv-lolnotifier-dev-<suffix>" \
  --name "riot-api-key" \
  --value "<new_dev_key>"

# Restart Function App to pick up new value
az functionapp restart \
  --name "func-lolnotifier-dev-<suffix>" \
  --resource-group "rg-lolnotifier-dev"
```

No Terraform re-apply needed — `lifecycle { ignore_changes = [value] }` keeps Terraform from overwriting the new key.

---

## Destroy (teardown)

```bash
# Destroy all resources in the environment
terraform destroy

# WARNING: This will delete CosmosDB data and Key Vault secrets.
# Key Vault has purge protection — it enters soft-delete for 7 days.
# To permanently delete after destroy:
az keyvault purge --name "kv-lolnotifier-dev-<suffix>" --location westeurope
```

The tfstate storage account (`rg-lolnotifier-tfstate`) is NOT destroyed by `terraform destroy` — it must be deleted manually if needed.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `AuthorizationFailed` | SP lacks Contributor role | Re-run `az ad sp create-for-rbac` with correct scope |
| `KeyVaultNameNotAvailable` | KV name taken globally | Change suffix in `random_string` or use different environment name |
| `StorageAccountAlreadyTaken` | Storage name taken | Change `SA_NAME` in bootstrap script |
| `SecretNotFound` in Function App | KV reference before identity RBAC propagates | Wait 2-3 min and restart Function App |
| `403` from Riot API | Dev Key expired | Rotate key in Key Vault (see above) |
| `429` from Riot API | Rate limit hit | Increase `poll_interval_seconds` in tfvars |
