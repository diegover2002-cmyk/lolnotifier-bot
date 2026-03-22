# =============================================================================
# terraform/main.tf
# Root orchestrator — wires all modules for lolnotifier-bot on Azure.
#
# AUTHENTICATION (choose one):
#   Option A — Interactive (local dev):
#     az login
#     az account set --subscription "<subscription_id>"
#
#   Option B — Service Principal (CI/CD / automated):
#     export ARM_CLIENT_ID="<sp_client_id>"
#     export ARM_CLIENT_SECRET="<sp_client_secret>"
#     export ARM_TENANT_ID="<tenant_id>"
#     export ARM_SUBSCRIPTION_ID="<subscription_id>"
#
# SECRETS (never in .tf files or tfvars):
#   export TF_VAR_telegram_token="<token>"
#   export TF_VAR_riot_api_key="<key>"
#   export TF_VAR_telegram_chat_id="<chat_id>"
#
# FIRST RUN: bootstrap the remote state storage first:
#   bash terraform/scripts/bootstrap-backend.sh
# =============================================================================

terraform {
  required_version = ">= 1.6"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Remote state — Azure Blob Storage.
  # Storage account is created by bootstrap-backend.sh before first terraform init.
  # Values are read from backend.conf (excluded by .gitignore).
  backend "azurerm" {}
}

# -----------------------------------------------------------------------------
# Provider
# Reads ARM_* env vars automatically when set.
# No credentials are ever written in this file.
# -----------------------------------------------------------------------------
provider "azurerm" {
  subscription_id = var.subscription_id

  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}

provider "azuread" {
  tenant_id = var.tenant_id
}

# -----------------------------------------------------------------------------
# Random suffix — ensures globally unique storage/keyvault names
# -----------------------------------------------------------------------------
resource "random_string" "suffix" {
  length  = 4
  upper   = false
  special = false
}

# -----------------------------------------------------------------------------
# Resource Group
# -----------------------------------------------------------------------------
resource "azurerm_resource_group" "main" {
  name     = "rg-lolnotifier-${var.environment}"
  location = var.location
  tags     = local.common_tags
}

# -----------------------------------------------------------------------------
# Modules
# -----------------------------------------------------------------------------

module "keyvault" {
  source              = "./modules/keyvault"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  suffix              = random_string.suffix.result
  tags                = local.common_tags

  # Sensitive — passed via TF_VAR_* env vars, never in tfvars files
  telegram_token   = var.telegram_token
  riot_api_key     = var.riot_api_key
  telegram_chat_id = var.telegram_chat_id

  # CosmosDB connection string — available after cosmosdb module is applied
  cosmosdb_connection_string = module.cosmosdb.primary_connection_string
}

module "cosmosdb" {
  source              = "./modules/cosmosdb"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  suffix              = random_string.suffix.result
  tags                = local.common_tags
}

module "storage" {
  source              = "./modules/storage"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  suffix              = random_string.suffix.result
  tags                = local.common_tags
}

module "monitoring" {
  source              = "./modules/monitoring"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags
}

module "function_app" {
  source              = "./modules/function_app"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  suffix              = random_string.suffix.result
  tags                = local.common_tags

  keyvault_id              = module.keyvault.keyvault_id
  telegram_token_secret_id = module.keyvault.telegram_token_secret_id
  riot_api_key_secret_id   = module.keyvault.riot_api_key_secret_id
  cosmosdb_kv_secret_id    = module.keyvault.cosmosdb_connection_secret_id

  storage_account_name       = module.storage.account_name
  storage_account_access_key = module.storage.primary_access_key

  appinsights_connection_string    = module.monitoring.connection_string
  appinsights_instrumentation_key  = module.monitoring.instrumentation_key

  poll_interval_seconds = var.poll_interval_seconds
  rate_limit_delay      = var.rate_limit_delay
  sku_name              = var.function_app_sku
}

module "scheduler" {
  source              = "./modules/scheduler"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags

  # The scheduler triggers the Function App polling endpoint
  function_app_id       = module.function_app.function_app_id
  function_app_hostname = module.function_app.default_hostname
}

# -----------------------------------------------------------------------------
# Locals
# -----------------------------------------------------------------------------
locals {
  common_tags = {
    project     = "lolnotifier-bot"
    environment = var.environment
    version     = "3.0.0"
    managed_by  = "terraform"
  }
}
