# terraform/main.tf
# Root configuration — wires all modules for the lolnotifier-bot Azure deployment.
# Run from terraform/environments/dev or terraform/environments/prod.

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
  }

  # Remote state — Azure Blob Storage backend.
  # Uncomment and fill in after creating the storage account manually.
  # backend "azurerm" {
  #   resource_group_name  = "rg-lolnotifier-tfstate"
  #   storage_account_name = "<your_tfstate_storage_account>"
  #   container_name       = "tfstate"
  #   key                  = "lolnotifier.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
  }
}

# ── Resource Group ────────────────────────────────────────────────────────────

resource "azurerm_resource_group" "main" {
  name     = "rg-lolnotifier-${var.environment}"
  location = var.location
  tags     = local.common_tags
}

# ── Modules ───────────────────────────────────────────────────────────────────

module "keyvault" {
  source              = "../../modules/keyvault"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags
}

module "storage" {
  source              = "../../modules/storage"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags
}

module "monitoring" {
  source              = "../../modules/monitoring"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags
}

module "container_app" {
  source              = "../../modules/container_app"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  environment         = var.environment
  tags                = local.common_tags

  # Secrets injected from Key Vault — never hardcoded
  keyvault_id                  = module.keyvault.keyvault_id
  telegram_token_secret_id     = module.keyvault.telegram_token_secret_id
  riot_api_key_secret_id       = module.keyvault.riot_api_key_secret_id
  appinsights_connection_string = module.monitoring.connection_string

  # Storage for SQLite persistence
  storage_account_name = module.storage.account_name
  storage_share_name   = module.storage.share_name
}

# ── Locals ────────────────────────────────────────────────────────────────────

locals {
  common_tags = {
    project     = "lolnotifier-bot"
    environment = var.environment
    managed_by  = "terraform"
  }
}
