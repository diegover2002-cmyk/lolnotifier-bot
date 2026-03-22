# terraform/modules/storage/main.tf
# Azure Storage Account with a File Share for SQLite database persistence.
# The Container App mounts this share at /app/data.
#
# Note: SQLite over Azure File Share (SMB) works for single-instance bots.
# For multi-instance or high-throughput, migrate to Azure SQL or Cosmos DB.

#checkov:skip=CKV_AZURE_59:EXC-002 Storage network rules omitted — Function App Consumption plan (Y1) uses shared Azure infrastructure without VNet injection support. Access key stored in Key Vault. See docs/compliance/exceptions-registry.json.
#checkov:skip=CKV_AZURE_35:EXC-002 Same as CKV_AZURE_59 — network ACL Deny would block Function App runtime on Y1 plan.
resource "azurerm_storage_account" "main" {
  name                     = "stlolnotifier${var.environment}${var.suffix}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  https_traffic_only_enabled      = true
  shared_access_key_enabled       = true  # Required by Function App runtime

  # No network_rules block — storage is protected by HTTPS-only + access key
  # (stored in Key Vault). A Deny firewall blocks Terraform data-plane calls
  # (azurerm_storage_share) from CI runners and is not needed here.

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
