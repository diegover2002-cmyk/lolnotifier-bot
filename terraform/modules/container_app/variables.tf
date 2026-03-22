# terraform/modules/container_app/variables.tf

variable "resource_group_name"          { type = string }
variable "location"                     { type = string }
variable "environment"                  { type = string }
variable "tags"                         { type = map(string) }
variable "keyvault_id"                  { type = string }
variable "telegram_token_secret_id"     { type = string }
variable "riot_api_key_secret_id"       { type = string }
variable "appinsights_connection_string" { type = string }
variable "storage_account_name"         { type = string }
variable "storage_share_name"           { type = string }

variable "container_image" {
  description = "Full container image reference, e.g. ghcr.io/user/lolnotifier-bot:v3.0.0"
  type        = string
  default     = "ghcr.io/diegover2002-cmyk/lolnotifier-bot:v3.0.0"
}
