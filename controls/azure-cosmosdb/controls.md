# MCSB Controls for Azure Cosmos DB

**Category:** Database
**Service:** `Microsoft.DocumentDB/databaseAccounts`

## 1. Control Summary

This document outlines the Microsoft Cloud Security Benchmark (MCSB) controls applicable to Azure Cosmos DB. The focus is on ensuring proper network isolation, identity management, and data protection for NoSQL databases.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation (Checkov) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CO-001** | NS-2 | NS | Public network access disabled | **Must** | Yes | `CKV_AZURE_101` |
| **CO-002** | NS-2 | NS | Private endpoint enabled | **Must** | Partial | `CKV2_AZURE_18` |
| **CO-003** | IM-1 | IM | RBAC for data plane (Core API) | **Must** | Yes | `CKV2_AZURE_68` |
| **CO-004** | IM-3 | IM | Local authentication disabled | **Should** | Yes | `CKV_AZURE_217` |
| **CO-005** | LT-1 | LT | Defender for Cosmos DB enabled | **Should** | Yes | `CKV_AZURE_65` |
| **CO-006** | LT-4 | LT | Diagnostic logging enabled | **Must** | Yes | `CKV_AZURE_102`|
| **CO-007** | DP-5 | DP | Customer-Managed Key (CMK) enabled | **Should** | Yes | `CKV_AZURE_100` |
| **CO-008** | BR-1 | BR | Automatic failover enabled | **Should** | Yes | `CKV_AZURE_99` |
| **CO-009**| NS-1 | NS| IP filter enabled | **Must**| Yes| `CKV_AZURE_101`|

---

## 2. Control Details

### CO-001: Public network access disabled

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** Disabling public network access is the primary method to prevent internet-based threats from reaching the database.
- **Implementation:** The `public_network_access_enabled` property must be set to `false`. When disabled, access is only possible via private endpoints.
- **Validation:** `CKV_AZURE_101: "Ensure that Cosmos DB accounts restrict network access"` (This check validates if IP rules or VNet filters are used. Disabling public access is the strongest form of compliance).

### CO-002: Private endpoint enabled

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** A private endpoint provides a secure entry point from a VNet, effectively making the Cosmos DB account part of your private network.
- **Implementation:** An `azurerm_private_endpoint` should be linked to the Cosmos DB account.
- **Validation:** `CKV2_AZURE_18: "Ensure CosmosDB is using a private endpoint"`

### CO-003: RBAC for data plane (Core API)

- **MCSB:** IM-1 (Centralized Identity) / PA-7 (Privileged Access)
- **Priority:** **Must**
- **Relevance:** Using Azure AD and RBAC for data plane operations (for the Core/SQL API) avoids sharing account keys, enabling fine-grained, identity-based access control.
- **Implementation:** The `is_virtual_network_filter_enabled` property is often used with network controls, but RBAC is a separate identity concern. The key is to use AAD identities for applications instead of connection strings with keys.
- **Validation:** `CKV2_AZURE_68: "Ensure that Azure Cosmos DB disables local authentication"`

### CO-004: Local authentication disabled

- **MCSB:** IM-3 (Identity Management)
- **Priority:** **Should**
- **Relevance:** Disabling local authentication (i.e., account keys) ensures that all access is channeled through Azure AD, enforcing centralized identity governance.
- **Implementation:** The `local_authentication_disabled` property should be set to `true`.
- **Validation:** `CKV_AZURE_217: "Ensure that Cosmos DB accounts have local authentication disabled"`

### CO-005: Defender for Cosmos DB enabled

- **MCSB:** LT-1 (Logging and Threat Detection)
- **Priority:** **Should**
- **Relevance:** Defender provides an intelligent layer of security that detects unusual and potentially harmful attempts to access or exploit Cosmos DB accounts.
- **Implementation:** The `azurerm_security_center_subscription_pricing` resource should be configured for `CosmosDbs`.
- **Validation:** `CKV_AZURE_65: "Ensure that Advanced Threat Protection is enabled for Azure Cosmos DB account"`

### CO-006: Diagnostic logging enabled

- **MCSB:** LT-4 (Logging and Threat Detection)
- **Priority:** **Must**
- **Relevance:** Capturing diagnostic logs is crucial for security analysis, performance monitoring, and incident response.
- **Implementation:** An `azurerm_monitor_diagnostic_setting` should target the Cosmos DB account and route logs like `DataPlaneRequests`, `QueryRuntimeStatistics`, and `Audit` to a Log Analytics workspace.
- **Validation:** `CKV_AZURE_102: "Ensure that diagnostic logging is enabled for Cosmos DB"`

### CO-007: Customer-Managed Key (CMK) enabled

- **MCSB:** DP-5 (Data Protection)
- **Priority:** **Should**
- **Relevance:** For sensitive data requiring a higher level of assurance, using a CMK from Azure Key Vault gives you control over the data encryption key.
- **Implementation:** The `key_vault_key_id` property should be set on the Cosmos DB account.
- **Validation:** `CKV_AZURE_100: "Ensure that Cosmos DB accounts use customer-managed keys"`

### CO-008: Automatic failover enabled

- **MCSB:** BR-1 (Backup and Recovery)
- **Priority:** **Should**
- **Relevance:** Configuring automatic failover is a critical component of a disaster recovery strategy, ensuring high availability by failing over to a secondary region.
- **Implementation:** The `enable_automatic_failover` property should be set to `true` in a multi-region deployment.
- **Validation:** `CKV_AZURE_99: "Ensure that automatic failover is enabled for Cosmos DB account"`

### CO-009: IP filter enabled

- **MCSB:** NS-1 (Network Security)
- **Priority:** **Must**
- **Relevance:** If public access is not completely disabled, an IP filter must be configured to restrict access to a specific set of allowed IP addresses or ranges. This is a minimum baseline for network hardening.
- **Implementation:** The `ip_range_filter` property should not be empty or allow `0.0.0.0/0` if public access is enabled.
- **Validation:** `CKV_AZURE_101: "Ensure that Cosmos DB accounts restrict network access"`
