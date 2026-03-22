# terraform/modules/scheduler/outputs.tf

output "logic_app_id" {
  value = azurerm_logic_app_workflow.scheduler.id
}

output "logic_app_callback_url" {
  description = "Logic App trigger callback URL — use to manually fire the scheduler"
  value       = azurerm_logic_app_workflow.scheduler.access_endpoint
}
