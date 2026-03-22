# terraform/variables.tf

variable "environment" {
  description = "Deployment environment: dev or prod"
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be 'dev' or 'prod'."
  }
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "westeurope"
}

variable "telegram_token" {
  description = "Telegram Bot API token from BotFather. Stored in Key Vault — never in tfvars."
  type        = string
  sensitive   = true
}

variable "riot_api_key" {
  description = "Riot Games API key. Stored in Key Vault — never in tfvars."
  type        = string
  sensitive   = true
}

variable "telegram_chat_id" {
  description = "Telegram chat ID for the bot owner (used for admin notifications)"
  type        = string
  sensitive   = true
}
