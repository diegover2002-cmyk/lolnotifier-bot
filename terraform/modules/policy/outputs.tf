output "initiative_id" {
  description = "Policy initiative (set definition) ID."
  value       = azurerm_policy_set_definition.mcsb_lolnotifier.id
}

output "assignment_id" {
  description = "Policy assignment ID."
  value       = azurerm_resource_group_policy_assignment.mcsb_lolnotifier.id
}
