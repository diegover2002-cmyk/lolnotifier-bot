# Azure App Service — Security Controls

> **MCSB Mapping** | **Severity:** 5 High / 6 Medium / 1 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Checkov Rule |
|---|---|---|---|---|---|---|---|
| AS-001 | DP-3 | DP | HTTPS only enabled | High | Must | Yes | `CKV_AZURE_14` |
| AS-002 | DP-3 | DP | Minimum TLS 1.2 | High | Must | Yes | `CKV_AZURE_154` |
| AS-003 | NS-2 | NS | Public network access restricted | High | Must | Yes | `CKV_AZURE_222` |
| AS-004 | NS-2 | NS | VNet integration configured | High | Should | Partial | Custom |
| AS-005 | IM-1 | IM | Managed identity enabled | High | Must | Yes | `CKV_AZURE_16` |
| AS-006 | IM-3 | IM | No credentials in app settings | High | Must | Partial | Custom |
| AS-007 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | `CKV_AZURE_13` |
| AS-008 | LT-3 | LT | HTTP logging enabled | Medium | Must | Yes | `CKV_AZURE_13` |
| AS-009 | PV-5 | PV | Latest runtime version | Medium | Should | Yes | Custom |
| AS-010 | DP-4 | DP | Data encryption at rest | Medium | Must | No | Platform-managed |
| AS-011 | NS-1 | NS | IP restrictions configured | Medium | Should | Yes | `CKV_AZURE_17` |
| AS-012 | PV-1 | PV | Defender for App Service enabled | Low | Should | Partial | `CKV_AZURE_65` |

---

## AS-001 — HTTPS Only Enabled

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | Without HTTPS-only, the app accepts unencrypted HTTP requests, exposing session tokens, credentials, and data to interception |
| **Checkov** | `CKV_AZURE_14` |

```hcl
# Insecure
resource "azurerm_app_service" "bad" {
  https_only = false  # default
}

# Secure
resource "azurerm_app_service" "good" {
  https_only = true
}
```

---

## AS-002 — Minimum TLS Version 1.2

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | TLS 1.0/1.1 are deprecated and vulnerable. App Service must enforce TLS 1.2 as the minimum accepted version |
| **Checkov** | `CKV_AZURE_154` |

```hcl
# Insecure
resource "azurerm_app_service" "bad" {
  site_config {
    min_tls_version = "1.0"
  }
}

# Secure
resource "azurerm_app_service" "good" {
  site_config {
    min_tls_version = "1.2"
  }
}
```

---

## AS-003 — Public Network Access Restricted

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — required unless the app is intentionally public-facing |
| **Justification** | Internal APIs and admin apps must not be reachable from the public internet. Access should be restricted via IP rules or private endpoints |
| **Checkov** | `CKV_AZURE_222` |

```hcl
# Insecure — no access restrictions
resource "azurerm_app_service" "bad" {
  site_config {}
}

# Secure — restrict to internal network
resource "azurerm_app_service" "good" {
  site_config {
    ip_restriction {
      virtual_network_subnet_id = azurerm_subnet.trusted.id
      priority                  = 100
      name                      = "allow-internal"
      action                    = "Allow"
    }
    scm_use_main_ip_restriction = true
  }
}
```

---

## AS-004 — VNet Integration Configured

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Should |
| **Applies** | Conditional — required when app accesses private resources (databases, storage, Key Vault) |
| **Justification** | Without VNet integration, outbound traffic from App Service goes over the public internet. VNet integration routes outbound traffic through the VNet, enabling access to private endpoints |
| **Checkov** | Custom — assert `azurerm_app_service_virtual_network_swift_connection` exists for the app |

```hcl
# Insecure — no VNet integration, outbound over public internet
resource "azurerm_app_service" "bad" {
  # no VNet integration
}

# Secure
resource "azurerm_app_service_virtual_network_swift_connection" "vnet_int" {
  app_service_id = azurerm_app_service.good.id
  subnet_id      = azurerm_subnet.app_delegation.id
}
```

---

## AS-005 — Managed Identity Enabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authentication system |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | Without managed identity, apps must use stored credentials (connection strings, API keys) to access Azure resources. Managed identity eliminates credential management and enables Azure AD-based access |
| **Checkov** | `CKV_AZURE_16` |

```hcl
# Insecure — no identity, must use stored credentials
resource "azurerm_app_service" "bad" {
  # no identity block
}

# Secure
resource "azurerm_app_service" "good" {
  identity {
    type = "SystemAssigned"
  }
}
```

---

## AS-006 — No Credentials in App Settings

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Manage application identities securely |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | Hardcoded credentials in `app_settings` are stored in Terraform state (plaintext), visible in Azure Portal, and logged in CI/CD pipelines. All secrets must reference Key Vault |
| **Checkov** | Custom — Checkov secrets detection + assert no `app_settings` values match patterns for passwords/keys/tokens |

```hcl
# Insecure — credentials in app settings
resource "azurerm_app_service" "bad" {
  app_settings = {
    "DB_PASSWORD"      = "SuperSecret123!"
    "API_KEY"          = "abc123xyz"
    "CONNECTION_STRING" = "Server=...;Password=..."
  }
}

# Secure — reference Key Vault secrets
resource "azurerm_app_service" "good" {
  app_settings = {
    "DB_PASSWORD" = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.db_pass.id})"
    "API_KEY"     = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.api_key.id})"
  }

  identity {
    type = "SystemAssigned"  # required for Key Vault reference
  }
}
```

---

## AS-007 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | Without diagnostic settings, application errors, HTTP requests, and platform events are not captured in Log Analytics. Required for incident response and anomaly detection |
| **Checkov** | `CKV_AZURE_13` |

```hcl
# Secure
resource "azurerm_monitor_diagnostic_setting" "app_diag" {
  name                       = "diag-appservice"
  target_resource_id         = azurerm_app_service.good.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  enabled_log { category = "AppServiceHTTPLogs" }
  enabled_log { category = "AppServiceConsoleLogs" }
  enabled_log { category = "AppServiceAppLogs" }
  enabled_log { category = "AppServiceAuditLogs" }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}
```

---

## AS-008 — HTTP Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | HTTP access logs capture request details (IP, URL, status code, user agent) required for detecting attacks, unauthorized access, and anomalous patterns |
| **Checkov** | `CKV_AZURE_13` |

```hcl
# Insecure
resource "azurerm_app_service" "bad" {
  logs {
    http_logs {
      retention_in_days = 0  # disabled
    }
  }
}

# Secure
resource "azurerm_app_service" "good" {
  logs {
    http_logs {
      retention_in_days = 30
    }
    failed_request_tracing  = true
    detailed_error_messages = true
  }
}
```

---

## AS-009 — Latest Runtime Version

| Field | Detail |
|---|---|
| **MCSB** | PV-5 — Perform vulnerability assessments |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all App Service apps |
| **Justification** | Outdated runtime versions (Python 3.8, Node 14, .NET 5) contain known CVEs. App Service must use supported, patched runtime versions |
| **Checkov** | Custom — assert `dotnet_framework_version`, `node_version`, `python_version` are not EOL values |

```hcl
# Insecure — EOL runtime
resource "azurerm_app_service" "bad" {
  site_config {
    dotnet_framework_version = "v4.0"  # EOL
    python_version           = "2.7"   # EOL
  }
}

# Secure
resource "azurerm_app_service" "good" {
  site_config {
    dotnet_framework_version = "v8.0"
    python_version           = "3.12"
  }
}
```

---

## AS-010 — Data Encryption at Rest

| Field | Detail |
|---|---|
| **MCSB** | DP-4 — Enable data at rest encryption by default |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all App Service apps |
| **Justification** | App Service encrypts data at rest by default using platform-managed keys. No Terraform attribute required, but must be documented as platform-enforced |
| **Checkov** | No — platform-managed, not configurable in IaC |

> Platform-enforced. No Terraform configuration required. Document as inherited control.

---

## AS-011 — IP Restrictions Configured

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — required for internal or admin apps |
| **Justification** | IP restrictions limit which source IPs can reach the app. Without them, the app is reachable from any IP on the internet |
| **Checkov** | `CKV_AZURE_17` |

```hcl
# Insecure — no IP restrictions
resource "azurerm_app_service" "bad" {
  site_config {}
}

# Secure
resource "azurerm_app_service" "good" {
  site_config {
    ip_restriction {
      ip_address = "203.0.113.0/24"
      priority   = 100
      name       = "allow-corporate"
      action     = "Allow"
    }
    ip_restriction {
      ip_address = "0.0.0.0/0"
      priority   = 200
      name       = "deny-all"
      action     = "Deny"
    }
  }
}
```

---

## AS-012 — Defender for App Service Enabled

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Run vulnerability assessments |
| **Severity** | Low |
| **Priority** | Should |
| **Applies** | Yes — all App Service apps in production |
| **Justification** | Defender for App Service detects web application attacks, suspicious activity, and known exploit patterns at the platform level |
| **Checkov** | `CKV_AZURE_65` |

```hcl
# Secure
resource "azurerm_security_center_subscription_pricing" "defender_app" {
  tier          = "Standard"
  resource_type = "AppServices"
}
```

---

## Secure App Service — Full Reference

```hcl
resource "azurerm_app_service" "compliant" {
  name                = "app-example-compliant"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  app_service_plan_id = azurerm_app_service_plan.plan.id

  # AS-001
  https_only = true

  # AS-005
  identity {
    type = "SystemAssigned"
  }

  site_config {
    # AS-002
    min_tls_version = "1.2"

    # AS-003 + AS-011
    ip_restriction {
      virtual_network_subnet_id = azurerm_subnet.trusted.id
      priority                  = 100
      name                      = "allow-internal"
      action                    = "Allow"
    }
    scm_use_main_ip_restriction = true
  }

  # AS-006 — Key Vault references, no plaintext secrets
  app_settings = {
    "DB_PASSWORD" = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.db_pass.id})"
  }

  # AS-008
  logs {
    http_logs {
      retention_in_days = 30
    }
    failed_request_tracing  = true
    detailed_error_messages = true
  }
}
```
