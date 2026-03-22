# terraform/modules/keyvault/main.tf
# Provisions Azure Key Vault for storing Telegram token, Riot API key,
# and any other secrets. Soft-delete and purge protection enabled.

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = "kv-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # Security hardening
  soft_delete_retention_days  = 7
  purge_protection_enabled    = true
  enable_rbac_authorization   = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    # Add your deployment IP or VNet here for tighter control
    ip_rules = []
  }

  tags = var.tags
}

# Grant the deploying principal (CI/CD service principal or developer) access
resource "azurerm_role_assignment" "deployer_secrets_officer" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Secrets — values passed in as sensitive variables, never hardcoded
resource "azurerm_key_vault_secret" "telegram_token" {
  name         = "telegram-token"
  value        = var.telegram_token
  key_vault_id = azurerm_key_vault.main.id

  lifecycle {
    ignore_changes = [value]  # Allow manual rotation without Terraform drift
  }
}

resource "azurerm_key_vault_secret" "riot_api_key" {
  name         = "riot-api-key"
  value        = var.riot_api_key
  key_vault_id = azurerm_key_vault.main.id

  lifecycle {
    ignore_changes = [value]  # Allow manual rotation without Terraform drift
  }
}

resource "azurerm_key_vault_secret" "telegram_chat_id" {
  name         = "telegram-chat-id"
  value        = var.telegram_chat_id
  key_vault_id = azurerm_key_vault.main.id
}
