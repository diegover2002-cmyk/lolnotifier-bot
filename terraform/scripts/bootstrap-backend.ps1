# =============================================================================
# terraform/scripts/bootstrap-backend.ps1
#
# Creates the Azure Storage Account used for Terraform remote state.
# Run ONCE before the first `terraform init`.
#
# Prerequisites:
#   az login --service-principal -u $env:ARM_CLIENT_ID -p $env:ARM_CLIENT_SECRET --tenant $env:ARM_TENANT_ID
#
# Usage:
#   .\terraform\scripts\bootstrap-backend.ps1 [-Environment dev|prod]
# =============================================================================

param(
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

$LOCATION       = "westeurope"
$RG_NAME        = "rg-lolnotifier-tfstate"
$SA_NAME        = "stlolnotifiertfstate"
$CONTAINER_NAME = "tfstate"

Write-Host "==> Bootstrapping Terraform remote state (env: $Environment)" -ForegroundColor Cyan
Write-Host "    Resource Group : $RG_NAME"
Write-Host "    Storage Account: $SA_NAME"
Write-Host "    Container      : $CONTAINER_NAME"
Write-Host ""

# Verify ARM_* env vars are set (required for non-interactive auth)
foreach ($var in @("ARM_CLIENT_ID","ARM_CLIENT_SECRET","ARM_TENANT_ID","ARM_SUBSCRIPTION_ID")) {
    if (-not (Get-Item "env:$var" -ErrorAction SilentlyContinue)) {
        Write-Error "Missing environment variable: $var. Set all ARM_* vars before running."
    }
}

# 1. Resource group
Write-Host "==> Creating resource group..."
az group create `
    --name $RG_NAME `
    --location $LOCATION `
    --tags "project=lolnotifier-bot" "managed_by=bootstrap-script" `
    --output none

# 2. Storage account
Write-Host "==> Creating storage account..."
az storage account create `
    --name $SA_NAME `
    --resource-group $RG_NAME `
    --location $LOCATION `
    --sku Standard_LRS `
    --kind StorageV2 `
    --min-tls-version TLS1_2 `
    --https-only true `
    --allow-blob-public-access false `
    --default-action Deny `
    --bypass AzureServices `
    --output none

# 3. Enable blob versioning
Write-Host "==> Enabling blob versioning..."
az storage account blob-service-properties update `
    --account-name $SA_NAME `
    --resource-group $RG_NAME `
    --enable-versioning true `
    --output none

# 4. Blob container (auth-mode login uses the SP identity — no key needed)
Write-Host "==> Creating blob container..."
az storage container create `
    --name $CONTAINER_NAME `
    --account-name $SA_NAME `
    --auth-mode login `
    --output none

Write-Host ""
Write-Host "==> Bootstrap complete!" -ForegroundColor Green
Write-Host "    Backend config already set in terraform/main.tf:"
Write-Host "      resource_group_name  = `"$RG_NAME`""
Write-Host "      storage_account_name = `"$SA_NAME`""
Write-Host "      container_name       = `"$CONTAINER_NAME`""
Write-Host "      key                  = `"lolnotifier.tfstate`""
Write-Host ""
Write-Host "==> Next: terraform init (from lolnotifier/terraform/)"
