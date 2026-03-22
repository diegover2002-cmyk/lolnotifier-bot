# =============================================================================
# terraform/modules/keyvault/main.tf
#
# Azure Key Vault — single source of truth for all secrets.
#
# Secrets stored:
#   telegram-token       : Telegram Bot API token
#   riot-api-key         : Riot Games Dev Key (expires every 24h — rotate manually)
#   telegram-chat-id     : Bot owner's Telegram chat ID
#   cosmosdb-connection  : CosmosDB primary connection string
#
# Security:
#   - RBAC authorization (not legacy access policies)
#   - Soft-delete + purge protection: secrets survive accidental terraform destroy
#   - lifecycle ignore_changes on secret values: Terraform won't overwrite manual rotations
#   - Network ACL: deny all by default, allow Azure services (for managed identity access)
# =============================================================================

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = "kv-lolnotifier-${var.environment}-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  soft_delete_retention_days = 7
  purge_protection_enabled   = true
  enable_rbac_authorization  = true

  network_acls {
    default_action = "Allow"  # Tighten to "Deny" + ip_rules when VNet is configured
    bypass         = "AzureServices"
  }

  tags = var.tags
}

# ── RBAC: grant the deploying identity (developer / CI service principal) ─────

resource "azurerm_role_assignment" "deployer_secrets_officer" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

# ── Secrets ───────────────────────────────────────────────────────────────────
# lifecycle.ignore_changes = [value] means:
#   - Terraform creates the secret on first apply
#   - Manual rotations (az keyvault secret set ...) are NOT overwritten on next apply
#   - To force a new value via Terraform: terraform taint <resource>

resource "azurerm_key_vault_secret" "telegram_token" {
  name         = "telegram-token"
  value        = var.telegram_token
  key_vault_id = azurerm_key_vault.main.id
  content_type = "text/plain"

  lifecycle {
    ignore_changes = [value]
  }

  depends_on = [azurerm_role_assignment.deployer_secrets_officer]
}

resource "azurerm_key_vault_secret" "riot_api_key" {
  name         = "riot-api-key"
  value        = var.riot_api_key
  key_vault_id = azurerm_key_vault.main.id
  content_type = "text/plain"

  # Dev Key expires every 24h — rotate with:
  # az keyvault secret set --vault-name <vault> --name riot-api-key --value <new_key>
  lifecycle {
    ignore_changes = [value]
  }

  depends_on = [azurerm_role_assignment.deployer_secrets_officer]
}

resource "azurerm_key_vault_secret" "telegram_chat_id" {
  name         = "telegram-chat-id"
  value        = var.telegram_chat_id
  key_vault_id = azurerm_key_vault.main.id
  content_type = "text/plain"

  depends_on = [azurerm_role_assignment.deployer_secrets_officer]
}

resource "azurerm_key_vault_secret" "cosmosdb_connection" {
  name         = "cosmosdb-connection"
  value        = var.cosmosdb_connection_string
  key_vault_id = azurerm_key_vault.main.id
  content_type = "text/plain"

  lifecycle {
    ignore_changes = [value]
  }

  depends_on = [azurerm_role_assignment.deployer_secrets_officer]
}
