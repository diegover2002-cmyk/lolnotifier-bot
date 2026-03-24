# MCSB Controls for Azure Functions

**Category:** Compute / Serverless
**Service:** `Microsoft.Web/sites` (where `kind` is `functionapp`)

## 1. Control Summary

This document outlines the Microsoft Cloud Security Benchmark (MCSB) controls for Azure Functions. The controls are focused on securing the application runtime, managing identity, protecting data in transit, and ensuring proper logging. Many controls for Azure Functions are shared with Azure App Service.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation (Checkov) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FN-001** | DP-3 | DP | HTTPS Only enabled | **Must** | Yes | `CKV_AZURE_14` |
| **FN-002** | IM-1 | IM | Managed Identity enabled | **Must** | Yes | `CKV_AZURE_16` |
| **FN-003** | IM-3 | IM | Secrets in App Settings avoided | **Must** | Yes | `CKV_SECRET_2` |
| **FN-004** | DP-3 | DP | Minimum TLS version 1.2 | **Must** | Yes | `CKV_AZURE_154` |
| **FN-005** | LT-3 | LT | Diagnostic logging enabled | **Must** | Yes | `CKV_AZURE_13` |
| **FN-006** | NS-2 | NS | VNet integration for private access | **Should** | Yes | `CKV2_AZURE_28` |
| **FN-007** | NS-1 | NS | Inbound access restricted (IP filter)| **Should** | Yes | `CKV_AZURE_17` |
| **FN-008** | PV-5 | PV | Use latest runtime version | **Should** | Yes | `CKV2_AZURE_11` |
| **FN-009** | LT-1 | LT | Defender for App Service enabled | **Should** | Yes | `CKV_AZURE_65` |

---

## 2. Control Details

### FN-001: HTTPS Only enabled

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Enforces that all incoming requests to the function app use HTTPS, preventing clear-text communication over the network.
- **Implementation:** The `https_only` property in the `azurerm_function_app` resource must be set to `true`.
- **Validation:** `CKV_AZURE_14: "Ensure web app is using https only"`

### FN-002: Managed Identity enabled

- **MCSB:** IM-1 (Identity Management)
- **Priority:** **Must**
- **Relevance:** Enables the function app to authenticate to other Azure services (Key Vault, Storage, etc.) using an identity managed by Azure AD, eliminating the need for storing credentials in app settings.
- **Implementation:** The `identity` block on the function app resource must be configured.
- **Validation:** `CKV_AZURE_16: "Ensure that Managed Identity is enabled for App Service"`

### FN-003: Secrets in App Settings avoided

- **MCSB:** IM-3 (Identity Management)
- **Priority:** **Must**
- **Relevance:** Application settings are often visible in logs, deployment pipelines, and the Azure portal. Storing secrets here increases the risk of exposure. Secrets should be stored in Key Vault and accessed via Key Vault references.
- **Implementation:** Use Key Vault references in the format `@Microsoft.KeyVault(SecretUri=...)`.
- **Validation:** `CKV_SECRET_2: "Application settings includes a secret"` (This is a secret-scanning check, not a resource check).

### FN-004: Minimum TLS version 1.2

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Protects data in transit by disabling older, vulnerable TLS protocols (1.0, 1.1).
- **Implementation:** The `min_tls_version` site config property must be set to `1.2`.
- **Validation:** `CKV_AZURE_154: "Ensure App Service's minimum TLS version is 1.2"`

### FN-005: Diagnostic logging enabled

- **MCSB:** LT-3 (Logging and Threat Detection)
- **Priority:** **Must**
- **Relevance:** Provides essential data for monitoring, troubleshooting, and security incident investigation.
- **Implementation:** An `azurerm_monitor_diagnostic_setting` should be configured to send function app logs and metrics to a Log Analytics workspace.
- **Validation:** `CKV_AZURE_13: "Ensure diagnostic logging is enabled for App Service"`

### FN-006: VNet integration for private access

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Should**
- **Relevance:** When a function needs to access resources within a VNet (like a private database or a service endpoint), VNet integration allows it to communicate securely without exposing traffic to the public internet.
- **Implementation:** Configure the `virtual_network_subnet_id` property.
- **Validation:** `CKV2_AZURE_28: "Ensure App Service uses VNet injection"`

### FN-007: Inbound access restricted (IP filter)

- **MCSB:** NS-1 (Network Security)
- **Priority:** **Should**
- **Relevance:** For functions that should not be globally accessible, IP access restrictions should be used to limit inbound traffic to a known set of IP addresses.
- **Implementation:** Configure the `ip_restriction` block within the function app's site config.
- **Validation:** `CKV_AZURE_17: "Ensure App Service access is restricted to authorized sources"`

### FN-008: Use latest runtime version

- **MCSB:** PV-5 (Posture & Vulnerability Management)
- **Priority:** **Should**
- **Relevance:** Using the latest supported runtime versions for languages (~dotnet, ~node, ~python, etc.) ensures you receive security patches and avoids running on end-of-life frameworks.
- **Implementation:** Set the `FUNCTIONS_EXTENSION_VERSION` app setting to the latest major version (e.g., `~4`).
- **Validation:** `CKV2_AZURE_11: "Ensure App Service uses the latest version of .NET"` (Example, similar checks for other languages).

### FN-009: Defender for App Service enabled

- **MCSB:** LT-1 (Logging and Threat Detection)
- **Priority:** **Should**
- **Relevance:** Defender for App Service also covers Azure Functions, providing runtime threat detection and security posture recommendations.
- **Implementation:** The `azurerm_security_center_subscription_pricing` resource should be configured for `AppServices`.
- **Validation:** `CKV_AZURE_65: "Ensure that Advanced Threat Protection is enabled for App Service Plan"`
