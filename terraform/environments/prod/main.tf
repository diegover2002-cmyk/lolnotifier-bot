# terraform/environments/prod/main.tf
# Production environment entry point.
# Remote backend must be configured before first apply.

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-lolnotifier-tfstate"
    storage_account_name = "<your_tfstate_storage_account>"
    container_name       = "tfstate"
    key                  = "lolnotifier-prod.tfstate"
  }
}

module "lolnotifier" {
  source = "../../"

  environment      = "prod"
  location         = "westeurope"
  telegram_token   = var.telegram_token
  riot_api_key     = var.riot_api_key
  telegram_chat_id = var.telegram_chat_id
}

variable "telegram_token"   { type = string; sensitive = true }
variable "riot_api_key"     { type = string; sensitive = true }
variable "telegram_chat_id" { type = string; sensitive = true }

output "keyvault_uri"       { value = module.lolnotifier.keyvault_uri }
output "container_app_fqdn" { value = module.lolnotifier.container_app_fqdn }
