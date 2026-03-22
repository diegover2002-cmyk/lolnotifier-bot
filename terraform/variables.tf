# =============================================================================
# terraform/variables.tf
# All input variables for the lolnotifier-bot deployment.
#
# SECRETS: telegram_token, riot_api_key, telegram_chat_id are marked sensitive.
# Pass them via environment variables — NEVER put real values in tfvars files:
#   export TF_VAR_telegram_token="<token>"
#   export TF_VAR_riot_api_key="<key>"
#   export TF_VAR_telegram_chat_id="<id>"
# =============================================================================

# ── Environment ───────────────────────────────────────────────────────────────

variable "environment" {
  description = "Deployment environment. Controls resource naming and sizing."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be 'dev' or 'prod'."
  }
}

variable "location" {
  description = "Azure region for all resources. Use 'westeurope' for lowest latency to EUW Riot API cluster."
  type        = string
  default     = "westeurope"
}

# ── Secrets (sensitive — pass via TF_VAR_* env vars) ─────────────────────────

variable "telegram_token" {
  description = <<-EOT
    Telegram Bot API token from BotFather.
    Stored in Azure Key Vault after first apply — never in state or tfvars.
    Rotate via: az keyvault secret set --vault-name kv-lolnotifier-<env> --name telegram-token --value <new>
  EOT
  type      = string
  sensitive = true
}

variable "riot_api_key" {
  description = <<-EOT
    Riot Games Developer API key from developer.riotgames.com.
    Dev Key expires every 24h — rotate in Key Vault without re-applying Terraform.
    Only account/v1 and match/v5 endpoints are available on Dev Key.
    Blocked endpoints (summoner/v4, league/v4, spectator/v5) return 403 — handled gracefully in code.
  EOT
  type      = string
  sensitive = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID for the bot owner. Used for admin notifications and functional tests."
  type        = string
  sensitive   = true
}

# ── Function App ──────────────────────────────────────────────────────────────

variable "poll_interval_seconds" {
  description = "Seconds between match polling cycles. Default 300 (5 min) stays within Dev Key rate limits."
  type        = number
  default     = 300

  validation {
    condition     = var.poll_interval_seconds >= 60
    error_message = "poll_interval_seconds must be >= 60 to respect Riot Dev Key rate limits."
  }
}

variable "rate_limit_delay" {
  description = "Per-request delay in seconds between Riot API calls. Default 0.06 ≈ 16 req/s (under 20 req/s Dev Key limit)."
  type        = number
  default     = 0.06
}

variable "function_app_sku" {
  description = "App Service Plan SKU for the Function App. Y1 = Consumption (pay-per-use), EP1 = Premium."
  type        = string
  default     = "Y1"

  validation {
    condition     = contains(["Y1", "EP1", "EP2"], var.function_app_sku)
    error_message = "function_app_sku must be Y1 (Consumption), EP1, or EP2 (Premium)."
  }
}

# ── CosmosDB ──────────────────────────────────────────────────────────────────

variable "cosmosdb_throughput" {
  description = "CosmosDB manual throughput in RU/s. 400 is the minimum and sufficient for this bot."
  type        = number
  default     = 400

  validation {
    condition     = var.cosmosdb_throughput >= 400 && var.cosmosdb_throughput <= 10000
    error_message = "cosmosdb_throughput must be between 400 and 10000 RU/s."
  }
}
