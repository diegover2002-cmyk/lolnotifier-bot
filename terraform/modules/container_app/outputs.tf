# terraform/modules/container_app/outputs.tf

output "fqdn" {
  description = "Container App FQDN (for webhook mode)"
  value       = azurerm_container_app.bot.latest_revision_fqdn
}

output "managed_identity_id" {
  value = azurerm_user_assigned_identity.bot.id
}
