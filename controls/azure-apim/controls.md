# MCSB Controls for Azure API Management

**Category:** Integration / API
**Service:** `Microsoft.ApiManagement/service`

## Checkov Source References

Official Checkov documentation reference: [What is Checkov?](https://www.checkov.io/1.Welcome/What%20is%20Checkov.html)

This section lists the concrete Checkov source files verified during the current APIM review. The documentation site defines the tool scope and policy model; the GitHub repository remains the decisive source for rule IDs, supported Terraform resources, and implemented check logic. Where the historical mapping in this repository differs from the currently verified Checkov rule, the verified rule is shown explicitly. Controls marked as not identified in the current review should stay on custom validation until a deeper Checkov mapping pass proves otherwise.

| Control ID | Repository Mapping | Review Result | Source |
| :--- | :--- | :--- | :--- |
| **AP-001** | `CKV_AZURE_33` | Verified current Terraform rule: `CKV_AZURE_107` | [APIServicesUseVirtualNetwork.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIServicesUseVirtualNetwork.py) |
| **AP-002** | `CKV_AZURE_104` | Verified current Terraform rule: `CKV_AZURE_215` | [APIManagementBackendHTTPS.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementBackendHTTPS.py) |
| **AP-003** | `CKV_AZURE_105` | Verified current Terraform rule: `CKV_AZURE_152` | [APIManagementCertsEnforced.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementCertsEnforced.py) |
| **AP-004** | `CKV_AZURE_106` | No direct APIM managed identity Terraform rule identified in the current review | Keep custom validation against the `identity` block |
| **AP-006** | `CKV_AZURE_65` | No APIM-specific Defender Terraform rule identified in the current review | Validate through subscription pricing plus service scoping review |
| **AP-007** | `CKV_AZURE_103` | No APIM diagnostic logging Terraform rule identified in the current review | Validate through `azurerm_monitor_diagnostic_setting` |
| **AP-008** | `CKV2_AZURE_3` | Verified current Terraform rule: `CKV_AZURE_173` | [APIManagementMinTLS12.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementMinTLS12.py) |
| **AP-009** | `CKV2_AZURE_2` | No APIM-specific Terraform rule with this historical ID identified in the current review | Use `CKV_AZURE_173` plus custom review of insecure ciphers and protocol flags |
| **AP-010** | `CKV2_AZURE_6` | No APIM named value Key Vault Terraform rule identified in the current review | Validate `azurerm_api_management_named_value.value_from_key_vault` with custom logic |

## 1. Control Summary

This document outlines the Microsoft Cloud Security Benchmark (MCSB) controls for Azure API Management (APIM). It focuses on securing the API gateway, protecting backend services, and ensuring secure consumption of APIs.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation (Checkov) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AP-001** | NS-1 | NS | Use virtual network (Internal mode) | **Should** | Yes | `CKV_AZURE_107` |
| **AP-002** | DP-3 | DP | Encrypt communication with backend | **Must** | Yes | `CKV_AZURE_215` |
| **AP-003** | DP-6 | DP | Use certificates from Key Vault | **Must** | Yes | `CKV_AZURE_152` |
| **AP-004** | IM-1 | IM | Use Managed Identity | **Must** | Partial | Custom |
| **AP-005** | IM-1 | IM | Authenticate with Azure AD | **Should** | Partial | Custom |
| **AP-006** | LT-1 | LT | Defender for APIs enabled | **Should** | Partial | Custom |
| **AP-007** | LT-4 | LT | API Management logging enabled | **Must** | Partial | Custom |
| **AP-008** | DP-3 | DP | Enforce minimum TLS 1.2 | **Must** | Yes | `CKV_AZURE_173` |
| **AP-009** | DP-3 | DP | Disable weak ciphers and protocols | **Must** | Partial | `CKV_AZURE_173` + Custom |
| **AP-010** | IM-3 | IM | Use Named Values from Key Vault | **Must** | Partial | Custom |

---

## 2. Control Details

### AP-001: Use virtual network (Internal mode)

- **MCSB:** NS-1 (Network Segmentation)
- **Priority:** **Should**
- **Relevance:** For APIs that are not meant for public consumption, deploying APIM in a VNet (Internal mode) provides network-level isolation, making it accessible only from within the private network.
- **Implementation:** Set the `virtual_network_type` to `Internal`.
- **Validation:** `CKV_AZURE_107: "Ensure that API management services use virtual networks"` via [APIServicesUseVirtualNetwork.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIServicesUseVirtualNetwork.py).

### AP-002: Encrypt communication with backend

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** APIM must use HTTPS to communicate with backend services to protect data in transit between the gateway and the API implementation.
- **Implementation:** Ensure backend URLs use the `https` scheme.
- **Validation:** `CKV_AZURE_215: "Ensure API management backend uses https"` via [APIManagementBackendHTTPS.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementBackendHTTPS.py).

### AP-003: Use certificates from Key Vault

- **MCSB:** DP-6 (Data Protection / Key Management)
- **Priority:** **Must**
- **Relevance:** Client certificates and custom domain TLS certificates should be stored and managed securely in Azure Key Vault, not embedded in code or APIM configuration.
- **Implementation:** Certificates should be sourced from `azurerm_key_vault_certificate`.
- **Validation:** `CKV_AZURE_152: "Ensure Client Certificates are enforced for API management"` via [APIManagementCertsEnforced.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementCertsEnforced.py). This is the closest direct Terraform APIM certificate-related rule identified in the current review.

### AP-004: Use Managed Identity

- **MCSB:** IM-1 (Identity Management)
- **Priority:** **Must**
- **Relevance:** The APIM instance should use a Managed Identity (System or User-assigned) to authenticate to other Azure services (like Key Vault or backend APIs) without needing to store credentials.
- **Implementation:** The `identity` block on the `azurerm_api_management` resource must be configured.
- **Validation:** No direct APIM managed identity Terraform rule was identified in the current review. Keep this as custom validation against the `identity` block on `azurerm_api_management`.

### AP-005: Authenticate with Azure AD

- **MCSB:** IM-1 (Identity Management)
- **Priority:** **Should**
- **Relevance:** Protect APIs by using Azure AD for authentication and authorization, leveraging OAuth 2.0 and OpenID Connect policies. This centralizes access control.
- **Implementation:** Configure `validate-jwt` policies within the APIM service.
- **Validation:** Custom policy check required; not easily detectable via static IaC analysis.

### AP-006: Defender for APIs enabled

- **MCSB:** LT-1 (Logging and Threat Detection)
- **Priority:** **Should**
- **Relevance:** Defender for APIs provides security recommendations, anomaly detection, and threat intelligence for your API inventory.
- **Implementation:** The `azurerm_security_center_subscription_pricing` resource should be configured for `Api`.
- **Validation:** No APIM-specific Defender Terraform rule was identified in the current review. Validate through `azurerm_security_center_subscription_pricing` plus review that the `Api` plan scope matches the intended service coverage.

### AP-007: API Management logging enabled

- **MCSB:** LT-4 (Logging and Threat Detection)
- **Priority:** **Must**
- **Relevance:** Diagnostic logs are essential for monitoring API usage, troubleshooting, and investigating security incidents.
- **Implementation:** An `azurerm_monitor_diagnostic_setting` must be configured to send `GatewayLogs` and other relevant categories to a Log Analytics workspace.
- **Validation:** No APIM-specific diagnostic logging Terraform rule was identified in the current review. Validate through custom checks on `azurerm_monitor_diagnostic_setting` and expected APIM log categories.

### AP-008: Enforce minimum TLS 1.2

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Disables older, insecure TLS versions (1.0, 1.1) for client-to-gateway communication, protecting against known vulnerabilities.
- **Implementation:** Configure the `min_api_version` and custom domain settings to enforce TLS 1.2.
- **Validation:** `CKV_AZURE_173: "Ensure API management uses at least TLS 1.2"` via [APIManagementMinTLS12.py](https://github.com/bridgecrewio/checkov/blob/main/checkov/terraform/checks/resource/azure/APIManagementMinTLS12.py).

### AP-009: Disable weak ciphers and protocols

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Reduces the attack surface by explicitly disabling weak cryptographic ciphers (like 3DES) and protocols (like TLS 1.0/1.1).
- **Implementation:** The `security` block should be used to disable insecure protocols and ciphers.
- **Validation:** Partially covered by `CKV_AZURE_173` for TLS posture. Additional custom review is still needed for insecure cipher and protocol flags beyond the direct Terraform rule confirmed in the current review.

### AP-010: Use Named Values from Key Vault

- **MCSB:** IM-3 (Identity Management)
- **Priority:** **Must**
- **Relevance:** Secrets (like backend keys or tokens) should never be stored directly in APIM policies or as plain text named values. They must be sourced from Key Vault.
- **Implementation:** The `azurerm_api_management_named_value` resource should have its `value_from_key_vault` property set.
- **Validation:** No APIM named value Key Vault Terraform rule was identified in the current review. Validate `azurerm_api_management_named_value.value_from_key_vault` with custom logic.
