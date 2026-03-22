# terraform/outputs.tf

output "resource_group_name" {
  description = "Name of the main resource group"
  value       = azurerm_resource_group.main.name
}

output "keyvault_uri" {
  description = "URI of the Key Vault (for manual secret upload)"
  value       = module.keyvault.keyvault_uri
}

output "container_app_fqdn" {
  description = "FQDN of the deployed Container App (if using webhook mode)"
  value       = module.container_app.fqdn
}

output "appinsights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.instrumentation_key
  sensitive   = true
}
