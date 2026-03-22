# terraform/modules/keyvault/variables.tf

variable "resource_group_name" { type = string }
variable "location"            { type = string }
variable "environment"         { type = string }
variable "tags"                { type = map(string) }

variable "telegram_token" {
  type      = string
  sensitive = true
  default   = ""  # Populated by root module from var.telegram_token
}

variable "riot_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "telegram_chat_id" {
  type      = string
  sensitive = true
  default   = ""
}
