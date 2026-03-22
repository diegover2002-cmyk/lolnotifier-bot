# terraform/modules/scheduler/variables.tf

variable "resource_group_name"        { type = string }
variable "location"                   { type = string }
variable "environment"                { type = string }
variable "tags"                       { type = map(string) }
variable "function_app_id"            { type = string }
variable "function_app_hostname"      { type = string }
variable "log_analytics_workspace_id" { type = string }

variable "poll_interval_minutes" {
  description = "How often to trigger the polling function. Must match POLL_INTERVAL / 60 in the Function App."
  type        = number
  default     = 5

  validation {
    condition     = var.poll_interval_minutes >= 1
    error_message = "poll_interval_minutes must be >= 1."
  }
}
