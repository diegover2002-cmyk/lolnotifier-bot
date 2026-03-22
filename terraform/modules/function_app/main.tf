# =============================================================================
# terraform/modules/function_app/main.tf
#
# Azure Function App (Python 3.11, Linux Consumption plan) hosting the bot.
#
# Functions deployed:
#   - poll_trigger   : Timer trigger — runs every POLL_INTERVAL seconds
#   - telegram_webhook (optional): HTTP trigger for webhook mode
#
# Security model:
#   - System-assigned managed identity reads secrets from Key Vault
#   - No secrets in app settings — all sensitive values use @Microsoft.KeyVault() references
#   - CosmosDB connection string also stored in Key Vault and referenced
#
# Dev Key compliance:
#   - POLL_INTERVAL defaults to 300s (5 min) — well within 100 req/2min Dev Key limit
#   - RATE_LIMIT_DELAY = 0.06s enforced in application code (riot_api.py)
#   - Blocked endpoints (summoner/v4, league/v4, spectator/v5) handled in code — no infra changes needed
# =============================================================================

# ── App Service Plan (Consumption = Y1, pay-per-execution) ───────────────────

resource "azurerm_service_plan" "main" {
  name                = "asp-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  sku_name            = var.sku_name  # Y1 = Consumption, EP1 = Premium

  tags = var.tags
}

# ── Function App ──────────────────────────────────────────────────────────────

resource "azurerm_linux_function_app" "main" {
  name                       = "func-lolnotifier-${var.environment}-${var.suffix}"
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = azurerm_service_plan.main.id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_account_access_key
  https_only                 = true

  # System-assigned managed identity — used to read Key Vault secrets
  identity {
    type = "SystemAssigned"
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }

    # Prevent cold starts on Consumption plan (best-effort)
    application_insights_connection_string = var.appinsights_connection_string
    application_insights_key               = var.appinsights_instrumentation_key
  }

  app_settings = {
    # ── Runtime ──────────────────────────────────────────────────────────────
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "AzureWebJobsFeatureFlags"  = "EnableWorkerIndexing"

    # ── Secrets via Key Vault references ─────────────────────────────────────
    # Format: @Microsoft.KeyVault(SecretUri=<secret_id>)
    # The managed identity must have Key Vault Secrets User role (granted below)
    "TELEGRAM_TOKEN" = "@Microsoft.KeyVault(SecretUri=${var.telegram_token_secret_id})"
    "RIOT_API_KEY"   = "@Microsoft.KeyVault(SecretUri=${var.riot_api_key_secret_id})"

    # ── CosmosDB ──────────────────────────────────────────────────────────────
    # Connection string stored in Key Vault — referenced here, never hardcoded
    "COSMOSDB_CONNECTION_STRING" = "@Microsoft.KeyVault(SecretUri=${var.cosmosdb_kv_secret_id})"

    # ── Bot configuration ─────────────────────────────────────────────────────
    "POLL_INTERVAL"    = tostring(var.poll_interval_seconds)
    "RATE_LIMIT_DELAY" = tostring(var.rate_limit_delay)
    "DB_BACKEND"       = "cosmosdb"  # Tells the bot to use CosmosDB instead of SQLite

    # ── Observability ─────────────────────────────────────────────────────────
    "APPLICATIONINSIGHTS_CONNECTION_STRING" = var.appinsights_connection_string
  }

  tags = var.tags
}

# ── Grant managed identity access to Key Vault ────────────────────────────────

resource "azurerm_role_assignment" "func_kv_reader" {
  scope                = var.keyvault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_function_app.main.identity[0].principal_id

  # Identity is created during apply — depends_on ensures ordering
  depends_on = [azurerm_linux_function_app.main]
}
