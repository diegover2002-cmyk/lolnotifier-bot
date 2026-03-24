# Azure Storage Account — Security Controls

> **MCSB Mapping** | **Severity:** 6 High / 4 Medium / 2 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Checkov Rule |
|---|---|---|---|---|---|---|---|
| ST-001 | NS-1 | NS | Public blob access disabled | High | Must | Yes | `CKV_AZURE_59` |
| ST-002 | DP-3 | DP | HTTPS only (secure transfer) | High | Must | Yes | `CKV_AZURE_3` |
| ST-003 | DP-3 | DP | Minimum TLS 1.2 | High | Must | Yes | `CKV_AZURE_44` |
| ST-004 | DP-4 | DP | Infrastructure encryption | Medium | Should | Yes | `CKV_AZURE_256` |
| ST-005 | DP-5 | DP | Customer-managed keys (CMK) | Medium | Should | Partial | `CKV_AZURE_206` |
| ST-006 | NS-2 | NS | Network firewall default deny | High | Must | Yes | `CKV_AZURE_35` |
| ST-007 | NS-2 | NS | Public network access disabled | High | Must | Yes | `CKV_AZURE_190` |
| ST-008 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| ST-009 | DP-8 | DP | Soft delete ≥ 7 days | Medium | Should | Yes | `CKV_AZURE_111` |
| ST-010 | DP-8 | DP | Blob versioning enabled | Low | Nice | Yes | `CKV_AZURE_119` |
| ST-011 | IM-1 | IM | Shared key access disabled | High | Must | Yes | `CKV2_AZURE_40` |
| ST-012 | NS-1 | NS | Cross-tenant replication disabled | High | Must | Yes | `CKV_AZURE_92` |

---

## ST-001 — Public Blob Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | `allow_nested_items_to_be_public = true` (default) allows any blob container to be set as public, exposing data to the internet without authentication |
| **Checkov** | `CKV_AZURE_59` |
| **tfsec** | `azure-storage-no-public-access` |

```hcl
# Insecure — default or explicit true
resource "azurerm_storage_account" "bad" {
  allow_nested_items_to_be_public = true
}

# Secure
resource "azurerm_storage_account" "good" {
  allow_nested_items_to_be_public = false
}
```

---

## ST-002 — HTTPS Only (Secure Transfer)

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | Without this flag, clients can connect over unencrypted HTTP, exposing data in transit to interception |
| **Checkov** | `CKV_AZURE_3` |
| **tfsec** | `azure-storage-enforce-https` |

```hcl
# Insecure
resource "azurerm_storage_account" "bad" {
  enable_https_traffic_only = false
}

# Secure — must be explicit even though default is true
resource "azurerm_storage_account" "good" {
  enable_https_traffic_only = true
}
```

---

## ST-003 — Minimum TLS Version 1.2

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | TLS 1.0 and 1.1 are vulnerable to POODLE and BEAST attacks. Azure still allows them unless explicitly restricted |
| **Checkov** | `CKV_AZURE_44` |
| **tfsec** | `azure-storage-use-secure-tls-policy` |

```hcl
# Insecure
resource "azurerm_storage_account" "bad" {
  min_tls_version = "TLS1_0"
}

# Secure
resource "azurerm_storage_account" "good" {
  min_tls_version = "TLS1_2"
}
```

---

## ST-004 — Infrastructure Encryption (Double Encryption)

| Field | Detail |
|---|---|
| **MCSB** | DP-4 — Enable data at rest encryption by default |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — storage accounts handling sensitive or regulated data |
| **Justification** | Adds a second layer of AES-256 encryption at the infrastructure level. Required for defense-in-depth in regulated environments (CNI, ENS) |
| **Checkov** | `CKV_AZURE_256` |

```hcl
# Insecure — omitted defaults to false
resource "azurerm_storage_account" "bad" {
  # infrastructure_encryption_enabled not set
}

# Secure
resource "azurerm_storage_account" "good" {
  infrastructure_encryption_enabled = true
}
```

---

## ST-005 — Customer-Managed Keys (CMK)

| Field | Detail |
|---|---|
| **MCSB** | DP-5 — Use customer-managed key option in data at rest encryption when required |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — required for storage accounts with sensitive/regulated data |
| **Justification** | Microsoft-managed keys reduce customer control over key lifecycle, rotation, and revocation. CMK via Key Vault is required for ENS Alto / CNI compliance |
| **Checkov** | `CKV_AZURE_206` |

```hcl
# Insecure — no CMK configured
resource "azurerm_storage_account" "bad" {
  # only platform-managed encryption
}

# Secure
resource "azurerm_storage_account_customer_managed_key" "good" {
  storage_account_id = azurerm_storage_account.good.id
  key_vault_id       = azurerm_key_vault.kv.id
  key_name           = azurerm_key_vault_key.key.name
}
```

---

## ST-006 — Network Firewall Default Deny

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | Without `default_action = "Deny"`, the storage account is accessible from any public IP. The firewall must explicitly allowlist trusted sources |
| **Checkov** | `CKV_AZURE_35` |
| **tfsec** | `azure-storage-default-action-deny` |

```hcl
# Insecure
resource "azurerm_storage_account" "bad" {
  network_rules {
    default_action = "Allow"
  }
}

# Secure
resource "azurerm_storage_account" "good" {
  network_rules {
    default_action             = "Deny"
    ip_rules                   = ["203.0.113.0/24"]
    virtual_network_subnet_ids = [azurerm_subnet.trusted.id]
    bypass                     = ["AzureServices"]
  }
}
```

---

## ST-007 — Public Network Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — required when storage is accessed only from private networks |
| **Justification** | `public_network_access_enabled = true` (default) exposes the storage endpoint on the public internet. Must be disabled and replaced with a private endpoint for internal workloads |
| **Checkov** | `CKV_AZURE_190` |

```hcl
# Insecure
resource "azurerm_storage_account" "bad" {
  public_network_access_enabled = true
}

# Secure
resource "azurerm_storage_account" "good" {
  public_network_access_enabled = false
}

resource "azurerm_private_endpoint" "storage_pe" {
  name                = "pe-storage"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private.id

  private_service_connection {
    name                           = "psc-storage"
    private_connection_resource_id = azurerm_storage_account.good.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }
}
```

---

## ST-008 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | Without diagnostic settings, there is no audit trail for blob read/write/delete operations. Required for incident response and forensics |
| **Checkov** | Custom — assert `azurerm_monitor_diagnostic_setting` with target `{storage_id}/blobServices/default` |

```hcl
# Insecure — no diagnostic setting defined

# Secure
resource "azurerm_monitor_diagnostic_setting" "storage_diag" {
  name                       = "diag-storage"
  target_resource_id         = "${azurerm_storage_account.good.id}/blobServices/default"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log { category = "StorageRead" }
  enabled_log { category = "StorageWrite" }
  enabled_log { category = "StorageDelete" }
}
```

---

## ST-009 — Soft Delete ≥ 7 Days

| Field | Detail |
|---|---|
| **MCSB** | DP-8 — Ensure recovery of data and keys |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all storage accounts with blob data |
| **Justification** | Without soft delete, accidental or malicious deletion is unrecoverable. Minimum 7 days; 30 days recommended for production |
| **Checkov** | `CKV_AZURE_111` |

```hcl
# Insecure — omitted or too short
resource "azurerm_storage_account" "bad" {
  blob_properties {
    delete_retention_policy {
      days = 1
    }
  }
}

# Secure
resource "azurerm_storage_account" "good" {
  blob_properties {
    delete_retention_policy {
      days = 30
    }
    container_delete_retention_policy {
      days = 30
    }
  }
}
```

---

## ST-010 — Blob Versioning Enabled

| Field | Detail |
|---|---|
| **MCSB** | DP-8 — Ensure recovery of data and keys |
| **Severity** | Low |
| **Priority** | Nice |
| **Applies** | Yes — storage accounts where object history is required |
| **Justification** | Versioning allows recovery of previous states of overwritten objects. Complements soft delete for full data protection |
| **Checkov** | `CKV_AZURE_119` |

```hcl
# Insecure — defaults to false
resource "azurerm_storage_account" "bad" {
  blob_properties {}
}

# Secure
resource "azurerm_storage_account" "good" {
  blob_properties {
    versioning_enabled = true
  }
}
```

---

## ST-011 — Shared Key Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authentication system |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | Shared keys bypass Azure AD entirely — no identity attribution, no MFA, no Conditional Access, no audit per identity. All access must go through Azure AD RBAC |
| **Checkov** | `CKV2_AZURE_40` |

```hcl
# Insecure — default is true
resource "azurerm_storage_account" "bad" {
  shared_access_key_enabled = true
}

# Secure
resource "azurerm_storage_account" "good" {
  shared_access_key_enabled = false
}
```

---

## ST-012 — Cross-Tenant Replication Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all storage accounts |
| **Justification** | When enabled (default), data can be replicated to storage accounts in external Azure tenants outside the organization's control, creating a data exfiltration vector |
| **Checkov** | `CKV_AZURE_92` |

```hcl
# Insecure — default is true
resource "azurerm_storage_account" "bad" {
  cross_tenant_replication_enabled = true
}

# Secure
resource "azurerm_storage_account" "good" {
  cross_tenant_replication_enabled = false
}
```

---

## Secure Storage Account — Full Reference

```hcl
resource "azurerm_storage_account" "compliant" {
  name                = "stexamplecompliant"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  account_tier             = "Standard"
  account_replication_type = "GRS"

  # ST-001
  allow_nested_items_to_be_public = false
  # ST-002
  enable_https_traffic_only = true
  # ST-003
  min_tls_version = "TLS1_2"
  # ST-004
  infrastructure_encryption_enabled = true
  # ST-007
  public_network_access_enabled = false
  # ST-011
  shared_access_key_enabled = false
  # ST-012
  cross_tenant_replication_enabled = false

  # ST-006
  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.trusted.id]
  }

  # ST-009 + ST-010
  blob_properties {
    versioning_enabled = true
    delete_retention_policy {
      days = 30
    }
    container_delete_retention_policy {
      days = 30
    }
  }
}
```
