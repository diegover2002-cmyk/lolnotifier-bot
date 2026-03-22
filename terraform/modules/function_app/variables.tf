# terraform/modules/function_app/variables.tf

variable "resource_group_name"          { type = string }
variable "location"                     { type = string }
variable "environment"                  { type = string }
variable "suffix"                       { type = string }
variable "tags"                         { type = map(string) }

variable "keyvault_id"                  { type = string }
variable "telegram_token_secret_id"     { type = string }
variable "riot_api_key_secret_id"       { type = string }
variable "cosmosdb_kv_secret_id"        { type = string }

variable "storage_account_name"         { type = string }
variable "storage_account_access_key"   { type = string; sensitive = true }

variable "appinsights_connection_string"   { type = string; sensitive = true }
variable "appinsights_instrumentation_key" { type = string; sensitive = true }

variable "poll_interval_seconds" {
  type    = number
  default = 300
}

variable "rate_limit_delay" {
  type    = number
  default = 0.06
}

variable "sku_name" {
  description = "App Service Plan SKU: Y1 (Consumption) or EP1/EP2 (Premium)"
  type        = string
  default     = "Y1"
}
