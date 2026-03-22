# terraform/modules/storage/variables.tf

variable "resource_group_name" { type = string }
variable "location"            { type = string }
variable "environment"         { type = string }
variable "suffix"              { type = string }
variable "tags"                { type = map(string) }
variable "allowed_ip_rules" {
  type    = list(string)
  default = []
}
