# terraform/modules/keyvault/variables.tf

variable "resource_group_name" { type = string }
variable "location"            { type = string }
variable "environment"         { type = string }
variable "suffix"              { type = string }
variable "tags"                { type = map(string) }

variable "telegram_token" {
  type      = string
  sensitive = true
}

variable "riot_api_key" {
  type      = string
  sensitive = true
}

variable "telegram_chat_id" {
  type      = string
  sensitive = true
}

variable "cosmosdb_connection_string" {
  description = "CosmosDB primary connection string — stored as a Key Vault secret"
  type        = string
  sensitive   = true
  default     = ""  # Empty until cosmosdb module is applied first
}
