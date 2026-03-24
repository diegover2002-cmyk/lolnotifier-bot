# =============================================================================
# terraform/modules/aks/main.tf
#
# Azure Kubernetes Service — gold-tier security baseline.
#
# MCSB Must controls implemented:
#   AK-001  API server authorized IP ranges      CKV_AZURE_6
#   AK-003  Azure AD integration enabled         CKV_AZURE_5
#   AK-004  Local accounts disabled              CKV_AZURE_141
#   AK-005  RBAC enabled                         CKV_AZURE_5
#   AK-006  Network policy (Calico)              CKV_AZURE_7
#   AK-009  Diagnostic logging (kube-audit)      Custom
#   AK-010  Defender for Containers              CKV_AZURE_117
#   AK-011  Disk encryption (CMK)                CKV_AZURE_226
# =============================================================================

resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-lolnotifier-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "aks-lolnotifier-${var.environment}"

  # AK-004
  local_account_disabled = true

  # AK-005 + AK-003
  role_based_access_control_enabled = true

  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = var.aks_admin_group_ids
  }

  # AK-011
  disk_encryption_set_id = var.disk_encryption_set_id

  # AK-007 (Should — included for defence-in-depth)
  automatic_channel_upgrade = "patch"

  # AK-008 (Should — included for defence-in-depth)
  node_os_channel_upgrade = "NodeImage"

  # AK-013 (Should — Azure Policy OPA enforcement)
  azure_policy_enabled = true

  default_node_pool {
    name       = "system"
    node_count = var.node_count
    vm_size    = var.vm_size

    upgrade_settings {
      max_surge = "33%"
    }
  }

  identity {
    type = "SystemAssigned"
  }

  # AK-006
  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
  }

  # AK-001
  api_server_access_profile {
    authorized_ip_ranges = var.api_server_authorized_ip_ranges
  }

  # AK-010
  microsoft_defender {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  tags = var.tags
}

# AK-009 — Kubernetes control plane audit logs
resource "azurerm_monitor_diagnostic_setting" "aks" {
  name                       = "diag-aks-${var.environment}"
  target_resource_id         = azurerm_kubernetes_cluster.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log { category = "kube-audit" }
  enabled_log { category = "kube-audit-admin" }
  enabled_log { category = "kube-apiserver" }
  enabled_log { category = "kube-controller-manager" }
  enabled_log { category = "kube-scheduler" }
  enabled_log { category = "guard" }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
