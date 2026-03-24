# terraform/modules/aks/variables.tf

variable "resource_group_name" { type = string }
variable "location"            { type = string }
variable "environment"         { type = string }
variable "tags"                { type = map(string) }
variable "log_analytics_workspace_id" { type = string }

variable "node_count" {
  type    = number
  default = 3
}

variable "vm_size" {
  type    = string
  default = "Standard_D4s_v3"
}

# AK-001 — restrict API server to known CIDRs
variable "api_server_authorized_ip_ranges" {
  description = "List of CIDRs allowed to reach the Kubernetes API server (AK-001)"
  type        = list(string)
}

# AK-003 / AK-005 — Azure AD group whose members get cluster-admin
variable "aks_admin_group_ids" {
  description = "Azure AD group object IDs granted cluster-admin RBAC role (AK-003)"
  type        = list(string)
}

# AK-011 — CMK disk encryption set
variable "disk_encryption_set_id" {
  description = "Resource ID of the DiskEncryptionSet for CMK node disk encryption (AK-011)"
  type        = string
}
