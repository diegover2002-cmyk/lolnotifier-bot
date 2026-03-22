# terraform/environments/dev/main.tf
# Dev environment entry point.
# Run: terraform init && terraform plan && terraform apply

module "lolnotifier" {
  source = "../../"

  environment      = "dev"
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
