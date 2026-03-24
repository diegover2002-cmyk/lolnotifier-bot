# Azure Kubernetes Service (AKS) — Security Controls

> **MCSB Mapping** | **Severity:** 6 High / 6 Medium / 1 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Checkov Rule |
|---|---|---|---|---|---|---|---|
| AK-001 | NS-2 | NS | API server authorized IP ranges | High | Must | Yes | `CKV_AZURE_6` |
| AK-002 | NS-2 | NS | Private cluster enabled | High | Should | Yes | `CKV_AZURE_115` |
| AK-003 | IM-1 | IM | Azure AD integration enabled | High | Must | Yes | `CKV_AZURE_5` |
| AK-004 | IM-1 | IM | Local accounts disabled | High | Must | Yes | `CKV_AZURE_141` |
| AK-005 | PA-7 | PA | RBAC enabled | High | Must | Yes | `CKV_AZURE_5` |
| AK-006 | NS-1 | NS | Network policy enabled (Calico/Azure) | High | Must | Yes | `CKV_AZURE_7` |
| AK-007 | PV-2 | PV | Auto-upgrade channel configured | Medium | Should | Yes | `CKV_AZURE_170` |
| AK-008 | PV-5 | PV | Node OS auto-patching enabled | Medium | Should | Yes | `CKV_AZURE_141` |
| AK-009 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| AK-010 | LT-1 | LT | Defender for Containers enabled | Medium | Must | Yes | `CKV_AZURE_117` |
| AK-011 | DP-4 | DP | Disk encryption at rest | Medium | Must | Yes | `CKV_AZURE_226` |
| AK-012 | NS-2 | NS | Ingress with WAF / App Gateway | Medium | Should | Partial | Custom |
| AK-013 | PV-1 | PV | Azure Policy add-on enabled | Low | Should | Yes | `CKV_AZURE_116` |

---

## AK-001 — API Server Authorized IP Ranges

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all non-private AKS clusters |
| **Justification** | The Kubernetes API server is the control plane entry point. Without IP restrictions, it is reachable from the entire internet, exposing it to credential brute-force and exploit attempts |
| **Checkov** | `CKV_AZURE_6` |

```hcl
# Insecure — API server open to internet
resource "azurerm_kubernetes_cluster" "bad" {
  # api_server_authorized_ip_ranges not set = open to 0.0.0.0/0
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  api_server_access_profile {
    authorized_ip_ranges = [
      "203.0.113.0/24",   # corporate egress
      "10.0.0.0/8"        # internal networks
    ]
  }
}
```

---

## AK-002 — Private Cluster Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Should |
| **Applies** | Conditional — required in production; dev clusters may use IP restrictions instead |
| **Justification** | A private cluster removes the API server from the public internet entirely. The control plane endpoint is only accessible via private IP within the VNet or connected networks |
| **Checkov** | `CKV_AZURE_115` |

```hcl
# Insecure — public API server
resource "azurerm_kubernetes_cluster" "bad" {
  private_cluster_enabled = false  # default
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  private_cluster_enabled             = true
  private_dns_zone_id                 = azurerm_private_dns_zone.aks.id
  private_cluster_public_fqdn_enabled = false
}
```

---

## AK-003 — Azure AD Integration Enabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authentication system |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Without Azure AD integration, cluster authentication relies on local kubeconfig certificates with no MFA, no Conditional Access, and no centralized identity governance |
| **Checkov** | `CKV_AZURE_5` |

```hcl
# Insecure — no Azure AD integration
resource "azurerm_kubernetes_cluster" "bad" {
  # no azure_active_directory_role_based_access_control block
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  azure_active_directory_role_based_access_control {
    managed            = true
    azure_rbac_enabled = true
    admin_group_object_ids = [var.aks_admin_group_id]
  }
}
```

---

## AK-004 — Local Accounts Disabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authentication system |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters with Azure AD integration |
| **Justification** | Local accounts (`clusterAdmin`, `clusterUser`) bypass Azure AD and provide certificate-based access with no audit trail per identity. Must be disabled to enforce Azure AD-only authentication |
| **Checkov** | `CKV_AZURE_141` |

```hcl
# Insecure — local accounts enabled (default)
resource "azurerm_kubernetes_cluster" "bad" {
  local_account_disabled = false
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  local_account_disabled = true
}
```

---

## AK-005 — RBAC Enabled

| Field | Detail |
|---|---|
| **MCSB** | PA-7 — Follow just enough administration (least privilege) principles |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Without RBAC, all authenticated users have unrestricted access to all Kubernetes resources. RBAC enforces least-privilege access at the namespace and resource level |
| **Checkov** | `CKV_AZURE_5` |

```hcl
# Insecure
resource "azurerm_kubernetes_cluster" "bad" {
  role_based_access_control_enabled = false
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  role_based_access_control_enabled = true

  azure_active_directory_role_based_access_control {
    managed            = true
    azure_rbac_enabled = true  # use Azure RBAC for Kubernetes authorization
  }
}
```

---

## AK-006 — Network Policy Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Without network policy, all pods can communicate with all other pods across all namespaces. Network policy enforces microsegmentation at the pod level, limiting lateral movement |
| **Checkov** | `CKV_AZURE_7` |

```hcl
# Insecure — no network policy
resource "azurerm_kubernetes_cluster" "bad" {
  network_profile {
    network_plugin = "azure"
    # network_policy not set = no pod-level segmentation
  }
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  network_profile {
    network_plugin = "azure"
    network_policy = "calico"  # or "azure"
  }
}
```

---

## AK-007 — Auto-Upgrade Channel Configured

| Field | Detail |
|---|---|
| **MCSB** | PV-2 — Perform regular operations and ensure security of assets |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Without auto-upgrade, clusters run outdated Kubernetes versions with known CVEs. Auto-upgrade ensures timely patching of the control plane |
| **Checkov** | `CKV_AZURE_170` |

```hcl
# Insecure — no auto-upgrade
resource "azurerm_kubernetes_cluster" "bad" {
  automatic_channel_upgrade = "none"  # default
}

# Secure — patch channel for production (only patch version upgrades)
resource "azurerm_kubernetes_cluster" "good" {
  automatic_channel_upgrade = "patch"
}
```

> Recommended channels: `patch` for production (stable), `rapid` for non-prod.

---

## AK-008 — Node OS Auto-Patching Enabled

| Field | Detail |
|---|---|
| **MCSB** | PV-5 — Perform vulnerability assessments |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all AKS node pools |
| **Justification** | Node OS (Ubuntu/Windows) receives OS-level CVE patches independently of Kubernetes version upgrades. Without auto-patching, nodes accumulate OS vulnerabilities |
| **Checkov** | `CKV_AZURE_141` |

```hcl
# Insecure — no OS patching
resource "azurerm_kubernetes_cluster" "bad" {
  node_os_channel_upgrade = "None"
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  node_os_channel_upgrade = "NodeImage"  # applies latest patched node image
}
```

---

## AK-009 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Without diagnostic settings, Kubernetes API audit logs, control plane logs, and node metrics are not captured. Required for detecting unauthorized API calls and incident response |
| **Checkov** | Custom — assert `azurerm_monitor_diagnostic_setting` targets AKS cluster ID with `kube-audit` category |

```hcl
# Secure
resource "azurerm_monitor_diagnostic_setting" "aks_diag" {
  name                       = "diag-aks"
  target_resource_id         = azurerm_kubernetes_cluster.good.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

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
```

---

## AK-010 — Defender for Containers Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-1 — Enable threat detection capabilities |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters in production |
| **Justification** | Defender for Containers provides runtime threat detection (privilege escalation, crypto mining, suspicious process execution), image vulnerability scanning, and Kubernetes audit log analysis |
| **Checkov** | `CKV_AZURE_117` |

```hcl
# Secure — enable at subscription level
resource "azurerm_security_center_subscription_pricing" "defender_containers" {
  tier          = "Standard"
  resource_type = "Containers"
}

# Enable Defender profile on the cluster
resource "azurerm_kubernetes_cluster" "good" {
  microsoft_defender {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  }
}
```

---

## AK-011 — Disk Encryption at Rest

| Field | Detail |
|---|---|
| **MCSB** | DP-4 — Enable data at rest encryption by default |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all AKS clusters |
| **Justification** | Node OS disks and data disks must be encrypted. AKS supports encryption with platform-managed keys by default, but customer-managed keys via a DiskEncryptionSet are required for regulated workloads |
| **Checkov** | `CKV_AZURE_226` |

```hcl
# Insecure — no CMK disk encryption
resource "azurerm_kubernetes_cluster" "bad" {
  # disk_encryption_set_id not set = platform-managed keys only
}

# Secure — CMK via DiskEncryptionSet
resource "azurerm_disk_encryption_set" "aks_des" {
  name                = "des-aks"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  key_vault_key_id    = azurerm_key_vault_key.aks_key.id
}

resource "azurerm_kubernetes_cluster" "good" {
  disk_encryption_set_id = azurerm_disk_encryption_set.aks_des.id
}
```

---

## AK-012 — Ingress with WAF / Application Gateway

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — required when AKS exposes public HTTP/HTTPS endpoints |
| **Justification** | Without a WAF in front of ingress, web workloads are exposed to OWASP Top 10 attacks (SQLi, XSS, etc.). AGIC (Application Gateway Ingress Controller) provides WAF capabilities |
| **Checkov** | Custom — assert `azurerm_application_gateway` with WAF tier is associated with the AKS cluster |

```hcl
# Secure — AGIC with WAF_v2
resource "azurerm_application_gateway" "agic" {
  name                = "agw-aks"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
  # ... frontend, backend, listener config
}

resource "azurerm_kubernetes_cluster" "good" {
  ingress_application_gateway {
    gateway_id = azurerm_application_gateway.agic.id
  }
}
```

---

## AK-013 — Azure Policy Add-on Enabled

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Run vulnerability assessments |
| **Severity** | Low |
| **Priority** | Should |
| **Applies** | Yes — all AKS clusters |
| **Justification** | The Azure Policy add-on enforces Gatekeeper policies (OPA) on the cluster, enabling guardrails like no privileged containers, required resource limits, and allowed image registries |
| **Checkov** | `CKV_AZURE_116` |

```hcl
# Insecure — no policy enforcement
resource "azurerm_kubernetes_cluster" "bad" {
  # azure_policy_enabled not set = false
}

# Secure
resource "azurerm_kubernetes_cluster" "good" {
  azure_policy_enabled = true
}
```

---

## Secure AKS Cluster — Full Reference

```hcl
resource "azurerm_kubernetes_cluster" "compliant" {
  name                = "aks-compliant"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "aks-compliant"

  # AK-002
  private_cluster_enabled             = true
  private_cluster_public_fqdn_enabled = false

  # AK-004
  local_account_disabled = true

  # AK-005 + AK-003
  role_based_access_control_enabled = true
  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = [var.aks_admin_group_id]
  }

  # AK-007
  automatic_channel_upgrade = "patch"

  # AK-008
  node_os_channel_upgrade = "NodeImage"

  # AK-013
  azure_policy_enabled = true

  # AK-011
  disk_encryption_set_id = azurerm_disk_encryption_set.aks_des.id

  default_node_pool {
    name       = "system"
    node_count = 3
    vm_size    = "Standard_D4s_v3"
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
    authorized_ip_ranges = [var.corporate_ip_range]
  }

  # AK-010
  microsoft_defender {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
  }
}
```
