# =============================================================================
# terraform/outputs.tf
# Key outputs after deployment. Run: terraform output
# =============================================================================

output "resource_group_name" {
  description = "Main resource group — use this to scope az CLI commands"
  value       = azurerm_resource_group.main.name
}

output "keyvault_uri" {
  description = "Key Vault URI — use this to manually rotate secrets"
  value       = module.keyvault.keyvault_uri
}

output "function_app_hostname" {
  description = "Function App default hostname — base URL for all function endpoints"
  value       = module.function_app.default_hostname
}

output "function_app_polling_url" {
  description = "Direct URL to trigger the polling function manually"
  value       = "https://${module.function_app.default_hostname}/api/poll"
}

output "cosmosdb_endpoint" {
  description = "CosmosDB account endpoint"
  value       = module.cosmosdb.endpoint
}

output "appinsights_app_id" {
  description = "Application Insights app ID — use for KQL queries in Azure Portal"
  value       = module.monitoring.app_id
}

# Sensitive outputs — only shown with: terraform output -json
output "appinsights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.instrumentation_key
  sensitive   = true
}

output "cosmosdb_primary_key" {
  description = "CosmosDB primary key — stored in Key Vault, shown here for reference only"
  value       = module.cosmosdb.primary_key
  sensitive   = true
}
