# terraform/modules/cosmosdb/outputs.tf

output "account_name" {
  value = azurerm_cosmosdb_account.main.name
}

output "endpoint" {
  description = "CosmosDB account endpoint URL"
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "database_name" {
  value = azurerm_cosmosdb_sql_database.lolnotifier.name
}

output "primary_connection_string" {
  description = "Primary connection string — injected into Function App as app setting via Key Vault reference"
  value       = azurerm_cosmosdb_account.main.primary_sql_connection_string
  sensitive   = true
}

output "primary_key" {
  description = "CosmosDB primary key — sensitive, stored in Key Vault"
  value       = azurerm_cosmosdb_account.main.primary_key
  sensitive   = true
}
