# MCSB Controls for Azure Backup & Recovery Services Vault

**Category:** Backup / Recovery
**Service:** `Microsoft.RecoveryServices/vaults`

## 1. Control Summary

This document outlines the Microsoft Cloud Security Benchmark (MCSB) controls applicable to Azure Backup, primarily managed through the Recovery Services Vault. The focus is on data protection, resilience, and secure access to backup data.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation (Checkov) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BK-001** | DP-2 | DP | Immutability & Soft Delete | **Must** | Yes | `CKV_AZURE_189` |
| **BK-002** | NS-2 | NS | Public network access disabled | **Must** | Yes | `CKV2_AZURE_33` |
| **BK-003** | BR-1 | BR | Cross-region restore enabled | **Should** | Yes | `CKV_AZURE_218` |
| **BK-004** | DP-4 | DP | Encryption at rest (Platform Key) | **Must** | No | Platform-managed |
| **BK-005** | DP-5 | DP | Customer-Managed Keys (CMK) | **Should** | Yes | `CKV2_AZURE_34` |
| **BK-006** | LT-4 | LT | Diagnostic logging enabled | **Must** | Yes | `CKV_AZURE_133` |
| **BK-007** | NS-2 | NS | Private Endpoints for Vault access | **Must** | Partial | `CKV2_AZURE_18` |
| **BK-008** | BR-2 | BR | Multi-User Authorization (MUA) | **Should** | Partial | Custom |

---

## 2. Control Details

### BK-001: Immutability & Soft Delete

- **MCSB:** DP-2 (Data Protection)
- **Priority:** **Must**
- **Relevance:** Protects backup data from accidental or malicious deletion. Soft delete retains data for a period after deletion, and immutability prevents any modification of recovery points. This is a critical defense against ransomware.
- **Implementation:** The `soft_delete_enabled` and `immutability` properties should be set to `true` on the vault.
- **Validation:** `CKV_AZURE_189: "Ensure Recovery Services Vault enables soft delete"`

### BK-002: Public network access disabled

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** The control plane for backup and recovery is a high-value target. Disabling public access ensures it can only be managed from private networks.
- **Implementation:** Set `public_network_access_enabled` to `false`.
- **Validation:** `CKV2_AZURE_33: "Ensure Recovery Services Vault public network access is disabled"`

### BK-003: Cross-region restore enabled

- **MCSB:** BR-1 (Backup and Recovery)
- **Priority:** **Should**
- **Relevance:** Enhances disaster recovery capabilities by allowing backups stored in a geo-redundant vault to be restored in a secondary region, even if the primary region is unavailable.
- **Implementation:** The `cross_region_restore_enabled` flag should be set to `true` on the vault.
- **Validation:** `CKV_AZURE_218: "Ensure that Cross-region restore is enabled for GRS recovery vaults"`

### BK-004: Encryption at rest (Platform Key)

- **MCSB:** DP-4 (Data Protection)
- **Priority:** **Must**
- **Relevance:** All data stored in a Recovery Services Vault is automatically encrypted at rest by default using platform-managed keys.
- **Implementation:** This is a default behavior and requires no specific Terraform configuration. It should be documented as an inherited control.
- **Validation:** Not applicable for IaC check.

### BK-005: Customer-Managed Keys (CMK)

- **MCSB:** DP-5 (Data Protection)
- **Priority:** **Should**
- **Relevance:** For workloads requiring stringent control over encryption, using a CMK allows the customer to manage the entire lifecycle of the key used to encrypt backup data.
- **Implementation:** Configure the `encryption` block with a `key_id` from a Key Vault and a user-assigned `identity_id`.
- **Validation:** `CKV2_AZURE_34: "Ensure Recovery Services Vault is encrypted with a customer-managed key"`

### BK-006: Diagnostic logging enabled

- **MCSB:** LT-4 (Logging and Threat Detection)
- **Priority:** **Must**
- **Relevance:** Logs provide visibility into all operations performed on the vault, which is critical for auditing, monitoring, and incident response.
- **Implementation:** An `azurerm_monitor_diagnostic_setting` resource should be configured to send vault logs to a Log Analytics workspace.
- **Validation:** `CKV_AZURE_133: "Ensure diagnostic logging is enabled for Recovery Services Vault"`

### BK-007: Private Endpoints for Vault access

- **MCSB:** NS-2 (Network Segmentation)
- **Priority:** **Must**
- **Relevance:** When public access is disabled, private endpoints are required to provide a secure access point to the vault from within a VNet.
- **Implementation:** An `azurerm_private_endpoint` must be deployed and associated with the vault for the `AzureBackup` and `AzureSiteRecovery` sub-resources.
- **Validation:** `CKV2_AZURE_18: "Ensure Recovery Services Vault is using a private endpoint"`

### BK-008: Multi-User Authorization (MUA)

- **MCSB:** BR-2 (Backup and Recovery) / PA-1 (Privileged Access)
- **Priority:** **Should**
- **Relevance:** MUA adds a layer of protection for critical operations on the vault (e.g., changing backup policies, disabling soft delete) by requiring a second administrator's approval via an Azure Resource Guard.
- **Implementation:** This is a complex setup involving an `azurerm_data_protection_resource_guard` and is partially configured on the vault and partially via RBAC.
- **Validation:** Custom check required to verify MUA is configured on critical operations.
