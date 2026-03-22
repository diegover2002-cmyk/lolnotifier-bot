# terraform/modules/function_app/outputs.tf

output "function_app_id" {
  value = azurerm_linux_function_app.main.id
}

output "default_hostname" {
  description = "Function App hostname — base URL for all HTTP-triggered functions"
  value       = azurerm_linux_function_app.main.default_hostname
}

output "managed_identity_principal_id" {
  description = "Object ID of the system-assigned managed identity — used for RBAC assignments"
  value       = azurerm_linux_function_app.main.identity[0].principal_id
}

output "outbound_ip_addresses" {
  description = "Outbound IPs — add to Riot API allowlist if IP filtering is needed"
  value       = azurerm_linux_function_app.main.outbound_ip_addresses
}
