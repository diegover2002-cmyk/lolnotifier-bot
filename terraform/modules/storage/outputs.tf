# terraform/modules/storage/outputs.tf

output "account_name" {
  value = azurerm_storage_account.main.name
}

output "share_name" {
  value = azurerm_storage_share.bot_data.name
}

output "primary_access_key" {
  value     = azurerm_storage_account.main.primary_access_key
  sensitive = true
}
