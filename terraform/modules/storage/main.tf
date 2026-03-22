# terraform/modules/storage/main.tf
# Azure Storage Account with a File Share for SQLite database persistence.
# The Container App mounts this share at /app/data.
#
# Note: SQLite over Azure File Share (SMB) works for single-instance bots.
# For multi-instance or high-throughput, migrate to Azure SQL or Cosmos DB.

resource "azurerm_storage_account" "main" {
  name                     = "stlolnotifier${var.environment}${var.suffix}"  # globally unique, lowercase, max 24 chars
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Security hardening
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  https_traffic_only_enabled      = true

  blob_properties {
    delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

resource "azurerm_storage_share" "bot_data" {
  name                 = "lolnotifier-data"
  storage_account_name = azurerm_storage_account.main.name
  quota                = 1  # 1 GB — more than enough for SQLite
}
