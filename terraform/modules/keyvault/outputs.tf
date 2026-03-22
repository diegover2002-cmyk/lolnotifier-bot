# terraform/modules/keyvault/outputs.tf

output "keyvault_id" {
  value = azurerm_key_vault.main.id
}

output "keyvault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "telegram_token_secret_id" {
  value = azurerm_key_vault_secret.telegram_token.id
}

output "riot_api_key_secret_id" {
  value = azurerm_key_vault_secret.riot_api_key.id
}

output "cosmosdb_connection_secret_id" {
  description = "Key Vault secret ID for CosmosDB connection string — used in Function App KV reference"
  value       = azurerm_key_vault_secret.cosmosdb_connection.id
}
