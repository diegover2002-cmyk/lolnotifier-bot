variable "environment" {
  description = "Deployment environment (dev or prod)."
  type        = string
}

variable "resource_group_id" {
  description = "Resource group ID to scope the policy assignment."
  type        = string
}
