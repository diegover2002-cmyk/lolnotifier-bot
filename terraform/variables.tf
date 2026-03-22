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

variable "subscription_id" {
  description = "Azure subscription ID. Passed via ARM_SUBSCRIPTION_ID env var."
  type        = string
  default     = ""
}

variable "tenant_id" {
  description = "Azure tenant ID. Passed via ARM_TENANT_ID env var."
  type        = string
  default     = ""
}

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
  description = "Telegram Bot API token from BotFather."
  type        = string
  sensitive   = true
}

variable "riot_api_key" {
  description = "Riot Games Developer API key. Dev Key expires every 24h."
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID for the bot owner."
  type        = string
  sensitive   = true
}

# ── Function App ──────────────────────────────────────────────────────────────

variable "poll_interval_seconds" {
  description = "Seconds between match polling cycles."
  type        = number
  default     = 300

  validation {
    condition     = var.poll_interval_seconds >= 60
    error_message = "poll_interval_seconds must be >= 60."
  }
}

variable "rate_limit_delay" {
  description = "Per-request delay in seconds between Riot API calls."
  type        = number
  default     = 0.06
}

variable "function_app_sku" {
  description = "App Service Plan SKU: Y1 (Consumption), EP1, or EP2 (Premium)."
  type        = string
  default     = "Y1"

  validation {
    condition     = contains(["Y1", "EP1", "EP2"], var.function_app_sku)
    error_message = "function_app_sku must be Y1, EP1, or EP2."
  }
}

# ── Network ───────────────────────────────────────────────────────────────────

variable "allowed_ip_rules" {
  description = "IP addresses allowed through the storage account firewall (e.g. CI runner IP)."
  type        = list(string)
  default     = []
}

# ── CosmosDB ──────────────────────────────────────────────────────────────────

variable "cosmosdb_throughput" {
  description = "CosmosDB manual throughput in RU/s."
  type        = number
  default     = 400

  validation {
    condition     = var.cosmosdb_throughput >= 400 && var.cosmosdb_throughput <= 10000
    error_message = "cosmosdb_throughput must be between 400 and 10000 RU/s."
  }
}
