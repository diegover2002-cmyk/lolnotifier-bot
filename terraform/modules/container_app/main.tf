# terraform/modules/container_app/main.tf
# Azure Container App running the lolnotifier-bot Docker image.
# Secrets are injected from Key Vault via managed identity — no env vars with raw tokens.

resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-lolnotifier-${var.environment}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = var.tags
}

# System-assigned managed identity — used to pull secrets from Key Vault
resource "azurerm_user_assigned_identity" "bot" {
  name                = "id-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Grant the managed identity read access to Key Vault secrets
resource "azurerm_role_assignment" "bot_kv_reader" {
  scope                = var.keyvault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.bot.principal_id
}

resource "azurerm_container_app" "bot" {
  name                         = "ca-lolnotifier-${var.environment}"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.bot.id]
  }

  # Secrets pulled from Key Vault via managed identity
  secret {
    name                = "telegram-token"
    key_vault_secret_id = var.telegram_token_secret_id
    identity            = azurerm_user_assigned_identity.bot.id
  }

  secret {
    name                = "riot-api-key"
    key_vault_secret_id = var.riot_api_key_secret_id
    identity            = azurerm_user_assigned_identity.bot.id
  }

  template {
    min_replicas = 1
    max_replicas = 1  # Bot uses long-polling — single instance only

    container {
      name   = "lolnotifier"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"

      # Secrets injected as environment variables inside the container
      env {
        name        = "TELEGRAM_TOKEN"
        secret_name = "telegram-token"
      }
      env {
        name        = "RIOT_API_KEY"
        secret_name = "riot-api-key"
      }
      env {
        name  = "DB_PATH"
        value = "/app/data/lolnotifier.db"
      }
      env {
        name  = "POLL_INTERVAL"
        value = "300"
      }
      env {
        name  = "RATE_LIMIT_DELAY"
        value = "0.06"
      }
      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.appinsights_connection_string
      }

      # Mount Azure File Share for SQLite persistence
      volume_mounts {
        name = "sqlite-data"
        path = "/app/data"
      }

      liveness_probe {
        transport = "TCP"
        port      = 8080
      }
    }

    volume {
      name         = "sqlite-data"
      storage_type = "AzureFile"
      storage_name = var.storage_share_name
    }
  }

  depends_on = [azurerm_role_assignment.bot_kv_reader]
}
