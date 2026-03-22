#!/usr/bin/env bash
# =============================================================================
# terraform/scripts/bootstrap-backend.sh
#
# Creates the Azure Storage Account used for Terraform remote state.
# Run this ONCE before the first `terraform init`.
#
# Prerequisites:
#   - Azure CLI installed and logged in: az login
#   - Correct subscription selected: az account set --subscription "<id>"
#
# Usage:
#   bash terraform/scripts/bootstrap-backend.sh [dev|prod]
# =============================================================================

set -euo pipefail

ENVIRONMENT="${1:-dev}"
LOCATION="westeurope"
RG_NAME="rg-lolnotifier-tfstate"
SA_NAME="stlolnotifiertfstate"   # Must be globally unique, lowercase, 3-24 chars
CONTAINER_NAME="tfstate"

echo "==> Bootstrapping Terraform remote state for environment: ${ENVIRONMENT}"
echo "    Resource Group : ${RG_NAME}"
echo "    Storage Account: ${SA_NAME}"
echo "    Container      : ${CONTAINER_NAME}"
echo ""

# ── 1. Create resource group for state storage ────────────────────────────────
echo "==> Creating resource group..."
az group create \
  --name "${RG_NAME}" \
  --location "${LOCATION}" \
  --tags "project=lolnotifier-bot" "managed_by=bootstrap-script" \
  --output none

# ── 2. Create storage account ─────────────────────────────────────────────────
echo "==> Creating storage account..."
az storage account create \
  --name "${SA_NAME}" \
  --resource-group "${RG_NAME}" \
  --location "${LOCATION}" \
  --sku "Standard_LRS" \
  --kind "StorageV2" \
  --min-tls-version "TLS1_2" \
  --https-only true \
  --allow-blob-public-access false \
  --output none

# ── 3. Enable versioning (protects state from accidental overwrites) ───────────
echo "==> Enabling blob versioning..."
az storage account blob-service-properties update \
  --account-name "${SA_NAME}" \
  --resource-group "${RG_NAME}" \
  --enable-versioning true \
  --output none

# ── 4. Create blob container ──────────────────────────────────────────────────
echo "==> Creating blob container..."
az storage container create \
  --name "${CONTAINER_NAME}" \
  --account-name "${SA_NAME}" \
  --auth-mode login \
  --output none

# ── 5. Print backend config ───────────────────────────────────────────────────
echo ""
echo "==> Bootstrap complete. Add this to terraform/main.tf backend block:"
echo ""
echo '  backend "azurerm" {'
echo "    resource_group_name  = \"${RG_NAME}\""
echo "    storage_account_name = \"${SA_NAME}\""
echo "    container_name       = \"${CONTAINER_NAME}\""
echo "    key                  = \"lolnotifier-${ENVIRONMENT}.tfstate\""
echo '  }'
echo ""
echo "==> Then run: terraform init"
