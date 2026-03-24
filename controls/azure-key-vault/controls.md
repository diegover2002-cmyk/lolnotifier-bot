# Azure Key Vault — Security Controls

> **MCSB Mapping** | **Severity:** 5 High / 5 Medium / 1 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Checkov Rule |
|---|---|---|---|---|---|---|---|
| KV-001 | NS-2 | NS | Public network access disabled | High | Must | Yes | `CKV_AZURE_109` |
| KV-002 | NS-2 | NS | Private endpoint configured | High | Must | Partial | Custom |
| KV-003 | NS-1 | NS | Network default action deny | High | Must | Yes | `CKV_AZURE_109` |
| KV-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| KV-005 | DP-7 | DP | Soft delete enabled | High | Must | Yes | `CKV_AZURE_42` |
| KV-006 | DP-7 | DP | Purge protection enabled | High | Must | Yes | `CKV_AZURE_110` |
| KV-007 | IM-1 | IM | RBAC authorization model | High | Must | Yes | `CKV2_AZURE_38` |
| KV-008 | DP-6 | DP | Key rotation policy defined | Medium | Should | Partial | Custom |
| KV-009 | DP-6 | DP | Key expiration date set | Medium | Should | Yes | `CKV_AZURE_112` |
| KV-010 | DP-6 | DP | Secret expiration date set | Medium | Should | Yes | `CKV_AZURE_114` |
| KV-011 | PV-1 | PV | Defender for Key Vault enabled | Medium | Should | Partial | `CKV_AZURE_234` |

---

## KV-001 — Public Network Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Key Vault stores secrets, keys, and certificates. Public exposure creates a direct attack surface for credential theft even with authentication controls |
| **Checkov** | `CKV_AZURE_109` |

```hcl
# Insecure
resource "azurerm_key_vault" "bad" {
  public_network_access_enabled = true  # default
}

# Secure
resource "azurerm_key_vault" "good" {
  public_network_access_enabled = false
}
```

---

## KV-002 — Private Endpoint Configured

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — required in production environments |
| **Justification** | Disabling public access without a private endpoint makes the vault unreachable. Private endpoint ensures access only from trusted VNets via private IP |
| **Checkov** | Custom — assert `azurerm_private_endpoint` references Key Vault ID |

```hcl
# Secure
resource "azurerm_private_endpoint" "kv_pe" {
  name                = "pe-keyvault"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.private.id

  private_service_connection {
    name                           = "psc-keyvault"
    private_connection_resource_id = azurerm_key_vault.good.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
}
```

---

## KV-003 — Network Default Action Deny

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Without `default_action = "Deny"`, the vault is reachable from any IP even if public access is nominally restricted |
| **Checkov** | `CKV_AZURE_109` |

```hcl
# Insecure
resource "azurerm_key_vault" "bad" {
  network_acls {
    default_action = "Allow"
    bypass         = ["AzureServices"]
  }
}

# Secure
resource "azurerm_key_vault" "good" {
  network_acls {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.trusted.id]
  }
}
```

---

## KV-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Without audit logs, there is no visibility into who accessed which secret/key and when. Critical for incident response and compliance |
| **Checkov** | Custom — assert `azurerm_monitor_diagnostic_setting` targets Key Vault ID with `AuditEvent` category |

```hcl
# Secure
resource "azurerm_monitor_diagnostic_setting" "kv_diag" {
  name                       = "diag-keyvault"
  target_resource_id         = azurerm_key_vault.good.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log { category = "AuditEvent" }
  enabled_log { category = "AzurePolicyEvaluationDetails" }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
```

---

## KV-005 — Soft Delete Enabled

| Field | Detail |
|---|---|
| **MCSB** | DP-7 — Use a secure key management process |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Without soft delete, accidental or malicious deletion of secrets/keys/certificates is permanent and unrecoverable. Azure now enables this by default but must be explicit in IaC |
| **Checkov** | `CKV_AZURE_42` |

```hcl
# Insecure — omitted or explicitly false
resource "azurerm_key_vault" "bad" {
  soft_delete_retention_days = 0  # not valid but illustrative
}

# Secure
resource "azurerm_key_vault" "good" {
  soft_delete_retention_days = 90  # 7–90 days; 90 recommended
}
```

---

## KV-006 — Purge Protection Enabled

| Field | Detail |
|---|---|
| **MCSB** | DP-7 — Use a secure key management process |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Without purge protection, a soft-deleted vault or object can be permanently purged before the retention period ends. Required to prevent irreversible data loss from insider threats |
| **Checkov** | `CKV_AZURE_110` |

```hcl
# Insecure
resource "azurerm_key_vault" "bad" {
  purge_protection_enabled = false  # default
}

# Secure
resource "azurerm_key_vault" "good" {
  purge_protection_enabled = true
}
```

---

## KV-007 — RBAC Authorization Model

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authentication system |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Key Vaults |
| **Justification** | Access policies (legacy model) are vault-scoped and harder to audit. RBAC model integrates with Azure AD, supports Conditional Access, PIM, and provides per-object granularity |
| **Checkov** | `CKV2_AZURE_38` |

```hcl
# Insecure — legacy access policy model
resource "azurerm_key_vault" "bad" {
  enable_rbac_authorization = false  # default
}

# Secure
resource "azurerm_key_vault" "good" {
  enable_rbac_authorization = true
}
```

---

## KV-008 — Key Rotation Policy Defined

| Field | Detail |
|---|---|
| **MCSB** | DP-6 — Use a secure key management process |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — Key Vaults storing cryptographic keys |
| **Justification** | Without automatic rotation, keys remain valid indefinitely, increasing the blast radius of a key compromise |
| **Checkov** | Custom — assert `azurerm_key_vault_key` has `rotation_policy` block defined |

```hcl
# Insecure — no rotation policy
resource "azurerm_key_vault_key" "bad" {
  name         = "key-example"
  key_vault_id = azurerm_key_vault.good.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt", "encrypt"]
}

# Secure
resource "azurerm_key_vault_key" "good" {
  name         = "key-example"
  key_vault_id = azurerm_key_vault.good.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt", "encrypt"]

  rotation_policy {
    automatic {
      time_before_expiry = "P30D"
    }
    expire_after         = "P1Y"
    notify_before_expiry = "P29D"
  }
}
```

---

## KV-009 — Key Expiration Date Set

| Field | Detail |
|---|---|
| **MCSB** | DP-6 — Use a secure key management process |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all cryptographic keys |
| **Justification** | Keys without expiration remain valid indefinitely. Expiration enforces periodic rotation and limits the window of exposure if a key is compromised |
| **Checkov** | `CKV_AZURE_112` |

```hcl
# Insecure — no expiration
resource "azurerm_key_vault_key" "bad" {
  name         = "key-example"
  key_vault_id = azurerm_key_vault.good.id
  key_type     = "RSA"
  key_size     = 2048
  key_opts     = ["decrypt", "encrypt"]
}

# Secure
resource "azurerm_key_vault_key" "good" {
  name            = "key-example"
  key_vault_id    = azurerm_key_vault.good.id
  key_type        = "RSA"
  key_size        = 2048
  key_opts        = ["decrypt", "encrypt"]
  expiration_date = "2026-01-01T00:00:00Z"
}
```

---

## KV-010 — Secret Expiration Date Set

| Field | Detail |
|---|---|
| **MCSB** | DP-6 — Use a secure key management process |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all secrets stored in Key Vault |
| **Justification** | Secrets without expiration (API keys, passwords, connection strings) remain valid indefinitely, increasing risk from credential leakage |
| **Checkov** | `CKV_AZURE_114` |

```hcl
# Insecure
resource "azurerm_key_vault_secret" "bad" {
  name         = "db-password"
  value        = var.db_password
  key_vault_id = azurerm_key_vault.good.id
}

# Secure
resource "azurerm_key_vault_secret" "good" {
  name            = "db-password"
  value           = var.db_password
  key_vault_id    = azurerm_key_vault.good.id
  expiration_date = "2026-01-01T00:00:00Z"
}
```

---

## KV-011 — Defender for Key Vault Enabled

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Run vulnerability assessments |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all Key Vaults in production |
| **Justification** | Defender for Key Vault detects anomalous access patterns (unusual geolocation, high-volume operations, suspicious enumeration) that indicate credential theft or insider threat |
| **Checkov** | `CKV_AZURE_234` |

```hcl
# Secure
resource "azurerm_security_center_subscription_pricing" "defender_kv" {
  tier          = "Standard"
  resource_type = "KeyVaults"
}
```

---

## Secure Key Vault — Full Reference

```hcl
resource "azurerm_key_vault" "compliant" {
  name                = "kv-example-compliant"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  # KV-005
  soft_delete_retention_days = 90
  # KV-006
  purge_protection_enabled = true
  # KV-007
  enable_rbac_authorization = true
  # KV-001
  public_network_access_enabled = false

  # KV-003
  network_acls {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.trusted.id]
  }
}
```
