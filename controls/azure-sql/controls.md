# MCSB Controls for Azure SQL Database

**Category:** Database
**Service:** `Microsoft.Sql/servers`

## 1. Control Summary

This document outlines the Microsoft Cloud Security Benchmark (MCSB) controls applicable to Azure SQL Database. The goal is to ensure that all provisioned instances align with enterprise security standards for data protection, network security, and identity management.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation (Checkov) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SQ-001** | NS-2 | NS | Public network access disabled | **Must** | Yes | `CKV_AZURE_46` |
| **SQ-002** | NS-2 | NS | Private endpoint enabled | **Must** | Partial | `CKV2_AZURE_18` |
| **SQ-003** | IM-1 | IM | Azure AD-only authentication enabled | **Must** | Yes | `CKV_AZURE_192` |
| **SQ-004** | LT-1 | LT | Defender for Cloud for SQL enabled | **Should** | Yes | `CKV_AZURE_47` |
| **SQ-005** | LT-4 | LT | Auditing to Log Analytics enabled | **Must** | Yes | `CKV_AZURE_49`, `CKV_AZURE_21`|
| **SQ-006** | DP-3 | DP | Minimum TLS version 1.2 | **Must** | Yes | `CKV_AZURE_191` |
| **SQ-007** | IM-3 | IM | Managed Identity for CMK | **Should** | Partial | Custom |
| **SQ-008** | DP-5 | DP | Customer-Managed Key (CMK) enabled | **Should** | Yes | `CKV_AZURE_205` |
| **SQ-009** | BR-1 | BR | Geo-redundant backup enabled | **Should** | Yes | `CKV2_AZURE_21` |

---

## 2. Control Details

### SQ-001: Public network access disabled

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** Disabling public access is the most effective way to protect a database from external threats. All access should be routed through private endpoints or service endpoints from trusted VNets.
- **Implementation:** The `public_network_access_enabled` property must be set to `false`.
- **Validation:** `CKV_AZURE_46: "Ensure that 'Public network access' is disabled for Azure SQL Database server"`

### SQ-002: Private endpoint enabled

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** Paired with disabling public access, a private endpoint provides a secure, private IP-based entry point to the database from within an approved VNet, isolating it completely from the public internet.
- **Implementation:** A `azurerm_private_endpoint` resource should be associated with the SQL server.
- **Validation:** `CKV2_AZURE_18: "Ensure SQL server is using a private endpoint"`

### SQ-003: Azure AD-only authentication enabled

- **MCSB:** IM-1 (Centralized Identity)
- **Priority:** **Must**
- **Relevance:** Enforcing Azure AD-only authentication disables SQL local authentication, centralizes identity management, and allows for modern security features like Conditional Access and MFA.
- **Implementation:** The `azuread_authentication_only` property must be set to `true`.
- **Validation:** `CKV_AZURE_192: "Ensure that Azure Active Directory only authentication is enabled for Azure SQL server"`

### SQ-004: Defender for Cloud for SQL enabled

- **MCSB:** LT-1 (Logging and Threat Detection)
- **Priority:** **Should**
- **Relevance:** Defender for SQL provides Advanced Threat Protection and vulnerability assessment, detecting anomalies, and suggesting security hardening.
- **Implementation:** The `azurerm_security_center_subscription_pricing` resource should be configured for `SqlServers`.
- **Validation:** `CKV_AZURE_47: "Ensure that Advanced data security is enabled on Azure SQL Server"`

### SQ-005: Auditing to Log Analytics enabled

- **MCSB:** LT-4 (Logging and Threat Detection)
- **Priority:** **Must**
- **Relevance:** Detailed audit logs are essential for incident investigation, compliance, and monitoring database activity. Sending these logs to a central Log Analytics workspace is critical for SecOps.
- **Implementation:** An `azurerm_mssql_server_extended_auditing_policy` should be defined and linked to a Log Analytics workspace.
- **Validation:** `CKV_AZURE_49` and `CKV_AZURE_21`.

### SQ-006: Minimum TLS version 1.2

- **MCSB:** DP-3 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Enforces strong encryption for data in transit, protecting against downgrade attacks and vulnerabilities in older TLS versions.
- **Implementation:** The `minimum_tls_version` property must be set to `1.2`.
- **Validation:** `CKV_AZURE_191: "Ensure that the minimum TLS version is 1.2 for Azure SQL Database server"`

### SQ-007: Managed Identity for CMK

- **MCSB:** IM-3 (Identity Management)
- **Priority:** **Should**
- **Relevance:** When using a Customer-Managed Key (CMK) for TDE, the SQL server should access the Key Vault using a Managed Identity, avoiding the need for stored credentials.
- **Implementation:** The `azurerm_sql_server` identity block should be configured, and the Key Vault access policy should grant permissions to this identity.
- **Validation:** Custom check required to verify identity type and Key Vault permissions.

### SQ-008: Customer-Managed Key (CMK) enabled

- **MCSB:** DP-5 (Data Protection)
- **Priority:** **Should**
- **Relevance:** For workloads with strict regulatory requirements, using a CMK provides control over the encryption key lifecycle for Transparent Data Encryption (TDE).
- **Implementation:** The `key_uri` for the `transparent_data_encryption` block should be set to a valid Key Vault key.
- **Validation:** `CKV_AZURE_205: "Ensure SQL server TDE protector is encrypted with your own key"`

### SQ-009: Geo-redundant backup enabled

- **MCSB:** BR-1 (Backup and Recovery)
- **Priority:** **Should**
- **Relevance:** Ensures that backups are replicated to a secondary region, providing disaster recovery capabilities in case of a regional outage.
- **Implementation:** The `geo_backup_enabled` property should be set to `true` in the database resource.
- **Validation:** `CKV2_AZURE_21: "Ensure that Geo-Redundant backups are enabled for Azure SQL Database"`
