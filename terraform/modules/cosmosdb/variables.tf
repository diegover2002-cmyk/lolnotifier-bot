# terraform/modules/cosmosdb/variables.tf

variable "resource_group_name" { type = string }
variable "location"            { type = string }
variable "environment"         { type = string }
variable "suffix"              { type = string }
variable "tags"                { type = map(string) }
variable "log_analytics_workspace_id" { type = string }
