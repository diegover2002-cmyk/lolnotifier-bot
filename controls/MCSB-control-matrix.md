# MCSB Control Matrix — Deployable Azure Services

> **Purpose:** Maps deployable Azure services to MCSB controls. Used as the foundation for CI/CD security checks, security documentation, and compliance tracking.
> **Last updated:** 2026-03-23
> **Source of truth:** [Microsoft Cloud Security Benchmark](https://learn.microsoft.com/en-us/security/benchmark/azure/)
> **Checkov traceability audit:** See [../docs/checkov-coverage-audit.md](../docs/checkov-coverage-audit.md) for verified current Checkov coverage, broken references, and normalization priorities.

---

## How to read this matrix

| Column | Description |
|---|---|
| **Control ID** | Internal ID (service prefix + number) |
| **MCSB** | MCSB control ID |
| **Domain** | MCSB domain (NS, IM, DP, LT, PA, PV, AM, IR, ES, BR, DS, IA) |
| **Control Name** | Short name |
| **Applies** | Yes / No / Conditional |
| **Severity** | High / Medium / Low |
| **Priority** | Must / Should / Nice |
| **IaC Checkable** | Yes / Partial / No |
| **Validation** | How to detect in code |

---

## Services Index

This index is intentionally limited to deployable Azure services and resource baselines.
Cross-cutting security domains such as DevOps Security, Endpoint Security, and AI Security are tracked separately and are not part of this resource catalog.

| # | Service | Category | Controls | Detail |
|---|---|---|---|---|
| 1 | [Azure Storage Account](#1-azure-storage-account) | Storage | 12 | [controls.md](azure-storage/controls.md) |
| 2 | [Azure Key Vault](#2-azure-key-vault) | Security | 11 | [controls.md](azure-key-vault/controls.md) |
| 3 | [Azure Virtual Network](#3-azure-virtual-network) | Networking | 10 | [controls.md](azure-vnet/controls.md) |
| 4 | [Azure App Service](#4-azure-app-service) | Compute | 12 | [controls.md](azure-app-service/controls.md) |
| 5 | [Azure Kubernetes Service](#5-azure-kubernetes-service-aks) | Compute | 13 | [controls.md](azure-aks/controls.md) |
| 6 | [Azure SQL Database](#6-azure-sql-database) | Database | 9 | [controls.md](azure-sql/controls.md) |
| 7 | [Azure Cosmos DB](#7-azure-cosmos-db) | Database | 9 | [controls.md](azure-cosmosdb/controls.md) |
| 8 | [Azure API Management](#8-azure-api-management) | Integration | 10 | [controls.md](azure-apim/controls.md) |
| 9 | [Azure Functions](#9-azure-functions) | Compute | 9 | [controls.md](azure-functions/controls.md) |
| 10 | [Azure Backup](#10-azure-backup) | Backup/Recovery | 8 | [controls.md](azure-backup/controls.md) |
| 11 | [Azure Application Gateway](#11-azure-application-gateway) | Networking | 6 | [controls.md](azure-application-gateway/controls.md) |
| 12 | [Azure Bastion](#12-azure-bastion) | Networking | 5 | [controls.md](azure-bastion/controls.md) |
| 13 | [Azure App Configuration](#13-azure-app-configuration) | Configuration | 6 | [controls.md](azure-app-configuration/controls.md) |
| 14 | [Azure Cache for Redis](#14-azure-cache-for-redis) | Cache | 6 | [controls.md](azure-cache-for-redis/controls.md) |
| 15 | [Azure Container Apps](#15-azure-container-apps) | Compute | 6 | [controls.md](azure-container-apps/controls.md) |
| 16 | [Azure Container Instances](#16-azure-container-instances) | Compute | 5 | [controls.md](azure-container-instances/controls.md) |
| 17 | [Azure Container Registry](#17-azure-container-registry) | Supply Chain | 6 | [controls.md](azure-container-registry/controls.md) |
| 18 | [Azure Data Factory](#18-azure-data-factory) | Data Integration | 6 | [controls.md](azure-data-factory/controls.md) |
| 19 | [Azure Data Share](#19-azure-data-share) | Data Governance | 5 | [controls.md](azure-data-share/controls.md) |
| 20 | [Azure DNS](#20-azure-dns) | Networking | 5 | [controls.md](azure-dns/controls.md) |
| 21 | [Azure Event Grid](#21-azure-event-grid) | Integration | 5 | [controls.md](azure-event-grid/controls.md) |
| 22 | [Azure Event Hubs](#22-azure-event-hubs) | Integration | 6 | [controls.md](azure-event-hubs/controls.md) |
| 23 | [Azure Firewall](#23-azure-firewall) | Networking | 6 | [controls.md](azure-firewall/controls.md) |
| 24 | [Azure Front Door](#24-azure-front-door) | Networking | 5 | [controls.md](azure-front-door/controls.md) |
| 25 | [Azure Load Balancer](#25-azure-load-balancer) | Networking | 5 | [controls.md](azure-load-balancer/controls.md) |
| 26 | [Azure Logic Apps](#26-azure-logic-apps) | Integration | 5 | [controls.md](azure-logic-apps/controls.md) |
| 27 | [Azure Monitor](#27-azure-monitor) | Observability | 6 | [controls.md](azure-monitor/controls.md) |
| 28 | [Azure Private Link](#28-azure-private-link) | Networking | 5 | [controls.md](azure-private-link/controls.md) |
| 29 | [Azure Public IP](#29-azure-public-ip) | Networking | 5 | [controls.md](azure-public-ip/controls.md) |
| 30 | [Azure Service Bus](#30-azure-service-bus) | Integration | 6 | [controls.md](azure-service-bus/controls.md) |
| 31 | [Azure Web Application Firewall](#31-azure-web-application-firewall) | Networking | 5 | [controls.md](azure-web-application-firewall/controls.md) |

---

## 1. Azure Storage Account

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ST-001 | NS-1 | NS | Public blob access disabled | Yes | High | Must | Yes | `CKV_AZURE_59` |
| ST-002 | DP-3 | DP | HTTPS only (secure transfer) | Yes | High | Must | Yes | `CKV_AZURE_3` |
| ST-003 | DP-3 | DP | Minimum TLS 1.2 | Yes | High | Must | Yes | `CKV_AZURE_44` |
| ST-004 | DP-4 | DP | Infrastructure encryption | Yes | Medium | Should | Yes | `CKV_AZURE_256` |
| ST-005 | DP-5 | DP | Customer-managed keys (CMK) | Conditional | Medium | Should | Partial | `CKV_AZURE_206` |
| ST-006 | NS-2 | NS | Network firewall default deny | Yes | High | Must | Yes | `CKV_AZURE_35` |
| ST-007 | NS-2 | NS | Public network access disabled | Conditional | High | Must | Yes | `CKV_AZURE_190` |
| ST-008 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ST-009 | DP-8 | DP | Soft delete ≥ 7 days | Yes | Medium | Should | Yes | `CKV_AZURE_111` |
| ST-010 | DP-8 | DP | Blob versioning enabled | Yes | Low | Nice | Yes | `CKV_AZURE_119` |
| ST-011 | IM-1 | IM | Shared key access disabled | Yes | High | Must | Yes | `CKV2_AZURE_40` |
| ST-012 | NS-1 | NS | Cross-tenant replication disabled | Yes | High | Must | Yes | `CKV_AZURE_92` |

---

## 2. Azure Key Vault

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| KV-001 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | `CKV_AZURE_109` |
| KV-002 | NS-2 | NS | Private endpoint configured | Conditional | High | Must | Partial | `CKV_AZURE_109` + custom |
| KV-003 | NS-1 | NS | Network default action deny | Yes | High | Must | Yes | `CKV_AZURE_109` |
| KV-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| KV-005 | DP-7 | DP | Soft delete enabled | Yes | High | Must | Yes | `CKV_AZURE_42` |
| KV-006 | DP-7 | DP | Purge protection enabled | Yes | High | Must | Yes | `CKV_AZURE_110` |
| KV-007 | IM-1 | IM | RBAC authorization model | Yes | High | Must | Yes | `CKV2_AZURE_38` |
| KV-008 | DP-6 | DP | Key rotation policy defined | Yes | Medium | Should | Partial | Custom |
| KV-009 | DP-6 | DP | Key expiration date set | Yes | Medium | Should | Yes | `CKV_AZURE_112` |
| KV-010 | DP-6 | DP | Secret expiration date set | Yes | Medium | Should | Yes | `CKV_AZURE_114` |
| KV-011 | PV-1 | PV | Defender for Key Vault enabled | Yes | Medium | Should | Partial | `CKV_AZURE_234` |

---

## 3. Azure Virtual Network

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| VN-001 | NS-1 | NS | Subnets associated with NSG | Yes | High | Must | Yes | `CKV2_AZURE_31` |
| VN-002 | NS-1 | NS | NSG default deny inbound | Yes | High | Must | Yes | Custom |
| VN-003 | NS-2 | NS | No unrestricted inbound SSH (22) | Yes | High | Must | Yes | `CKV_AZURE_10` |
| VN-004 | NS-2 | NS | No unrestricted inbound RDP (3389) | Yes | High | Must | Yes | `CKV_AZURE_9` |
| VN-005 | NS-3 | NS | DDoS protection enabled | Yes | Medium | Should | Yes | `CKV_AZURE_182` |
| VN-006 | NS-4 | NS | Network Watcher enabled | Yes | Medium | Must | Partial | Custom |
| VN-007 | LT-3 | LT | NSG flow logs enabled | Yes | Medium | Must | Partial | `CKV_AZURE_12` |
| VN-008 | NS-2 | NS | No wildcard inbound rules (any/any) | Yes | High | Must | Yes | Custom |
| VN-009 | NS-7 | NS | Service endpoints scoped to subnet | Conditional | Medium | Should | Yes | Custom |
| VN-010 | NS-1 | NS | Subnets not overly broad (/8, /16) | Yes | Low | Nice | Partial | Custom |

---

## 4. Azure App Service

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AS-001 | DP-3 | DP | HTTPS only enabled | Yes | High | Must | Yes | `CKV_AZURE_14` |
| AS-002 | DP-3 | DP | Minimum TLS 1.2 | Yes | High | Must | Yes | `CKV_AZURE_154` |
| AS-003 | NS-2 | NS | Public network access restricted | Conditional | High | Must | Yes | `CKV_AZURE_222` |
| AS-004 | NS-2 | NS | VNet integration configured | Conditional | High | Should | Partial | Custom |
| AS-005 | IM-1 | IM | Managed identity enabled | Yes | High | Must | Yes | `CKV_AZURE_16` |
| AS-006 | IM-3 | IM | No credentials in app settings | Yes | High | Must | Partial | Custom / Checkov secrets |
| AS-007 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | `CKV_AZURE_13` |
| AS-008 | LT-3 | LT | HTTP logging enabled | Yes | Medium | Must | Yes | `CKV_AZURE_13` |
| AS-009 | PV-5 | PV | Latest runtime version | Yes | Medium | Should | Yes | Custom |
| AS-010 | DP-4 | DP | Data encryption at rest | Yes | Medium | Must | No | Platform-managed |
| AS-011 | NS-1 | NS | IP restrictions configured | Conditional | Medium | Should | Yes | `CKV_AZURE_17` |
| AS-012 | PV-1 | PV | Defender for App Service enabled | Yes | Medium | Should | Partial | `CKV_AZURE_65` |

---

## 5. Azure Kubernetes Service (AKS)

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AK-001 | NS-2 | NS | API server authorized IP ranges | Yes | High | Must | Yes | `CKV_AZURE_6` |
| AK-002 | NS-2 | NS | Private cluster enabled | Conditional | High | Should | Yes | `CKV_AZURE_115` |
| AK-003 | IM-1 | IM | Azure AD integration enabled | Yes | High | Must | Yes | `CKV_AZURE_5` |
| AK-004 | IM-1 | IM | Local accounts disabled | Yes | High | Must | Yes | `CKV_AZURE_141` |
| AK-005 | PA-7 | PA | RBAC enabled | Yes | High | Must | Yes | `CKV_AZURE_5` |
| AK-006 | NS-1 | NS | Network policy enabled (Calico/Azure) | Yes | High | Must | Yes | `CKV_AZURE_7` |
| AK-007 | PV-2 | PV | Auto-upgrade channel configured | Yes | Medium | Should | Yes | `CKV_AZURE_170` |
| AK-008 | PV-5 | PV | Node OS auto-patching enabled | Yes | Medium | Should | Yes | `CKV_AZURE_141` |
| AK-009 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| AK-010 | LT-1 | LT | Defender for Containers enabled | Yes | Medium | Must | Yes | `CKV_AZURE_117` |
| AK-011 | DP-4 | DP | Disk encryption at rest | Yes | Medium | Must | Yes | `CKV_AZURE_226` |
| AK-012 | NS-2 | NS | Ingress with WAF / App Gateway | Conditional | Medium | Should | Partial | Custom |
| AK-013 | PV-1 | PV | Azure Policy add-on enabled | Yes | Medium | Should | Yes | `CKV_AZURE_116` |

---

## Applicability Notes

### Conditional controls

| Control | Condition |
|---|---|
| ST-005 (CMK) | Required for storage accounts handling sensitive/regulated data |
| ST-007 (No public network) | Required when storage is accessed only from private networks |
| KV-002 (Private endpoint) | Required in production environments |
| VN-009 (Service endpoints) | Only when PaaS services are accessed from VNet |
| AS-003 (Public access restricted) | Required unless the app is a public-facing web application |
| AS-004 (VNet integration) | Required when app needs access to private resources |
| AK-002 (Private cluster) | Required in production; dev clusters may be public with IP restrictions |
| AK-012 (WAF/Ingress) | Required when AKS exposes public HTTP endpoints |

### Controls that do NOT apply (and why)

| Service | MCSB Control | Reason Not Applicable |
|---|---|---|
| Azure VNet | DP-3 (Encrypt in transit) | VNet is a network construct, not a data service — transit encryption is enforced at the workload level |
| Azure VNet | IM-1 (Centralized identity) | VNet has no authentication surface — identity controls apply to resources within the VNet |
| Azure Key Vault | NS-5 (DDoS) | Key Vault is a PaaS service — DDoS protection is handled at the platform level, not configurable per vault |
| Azure Storage | PA-7 (RBAC) | Covered by ST-011 (shared key disabled) — RBAC is the implicit result of disabling shared keys |

---

## MCSB Domain Reference

| Domain | Full Name | Focus |
|---|---|---|
| NS | Network Security | Network segmentation, firewall, private endpoints |
| IM | Identity Management | Authentication, authorization, managed identities |
| PA | Privileged Access | Admin access, JIT, RBAC |
| DP | Data Protection | Encryption at rest/transit, key management, backup |
| AM | Asset Management | Inventory, tagging, lifecycle, governance |
| LT | Logging & Threat Detection | Diagnostics, SIEM, Defender |
| IR | Incident Response | Detection, containment, recovery |
| PV | Posture & Vulnerability Mgmt | Patching, scanning, Defender for Cloud |
| ES | Endpoint Security | EDR, antimalware, endpoint protection |
| BR | Backup & Recovery | Data/config backup, validation, protection |
| DS | DevOps Security | Secure DevOps, supply chain, SAST, threat modeling |
| IA | AI Security | Secure AI platform, model, monitoring |

# 6. Azure SQL Database

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| SQ-001 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | `CKV_AZURE_46` |
| SQ-002 | NS-2 | NS | Private endpoint enabled | Conditional | High | Must | Partial | `CKV2_AZURE_18` |
| SQ-003 | IM-1 | IM | Azure AD-only authentication enabled | Yes | High | Must | Yes | `CKV_AZURE_192` |
| SQ-004 | LT-1 | LT | Defender for Cloud for SQL enabled | Yes | Medium | Should | Yes | `CKV_AZURE_47` |
| SQ-005 | LT-4 | LT | Auditing to Log Analytics enabled | Yes | High | Must | Yes | `CKV_AZURE_49`, `CKV_AZURE_21` |
| SQ-006 | DP-3 | DP | Minimum TLS version 1.2 | Yes | High | Must | Yes | `CKV_AZURE_191` |
| SQ-007 | IM-3 | IM | Managed identity for CMK access | Conditional | Medium | Should | Partial | Custom |
| SQ-008 | DP-5 | DP | Customer-managed key enabled | Conditional | Medium | Should | Yes | `CKV_AZURE_205` |
| SQ-009 | BR-1 | BR | Geo-redundant backup enabled | Conditional | Medium | Should | Yes | `CKV2_AZURE_21` |

# 7. Azure Cosmos DB

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| CO-001 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | `CKV_AZURE_101` |
| CO-002 | NS-2 | NS | Private endpoint enabled | Conditional | High | Must | Partial | `CKV2_AZURE_18` |
| CO-003 | IM-1 | IM | RBAC for data plane (Core API) | Conditional | High | Must | Yes | `CKV2_AZURE_68` |
| CO-004 | IM-3 | IM | Local authentication disabled | Yes | Medium | Should | Yes | `CKV_AZURE_217` |
| CO-005 | LT-1 | LT | Defender for Cosmos DB enabled | Yes | Medium | Should | Yes | `CKV_AZURE_65` |
| CO-006 | LT-4 | LT | Diagnostic logging enabled | Yes | High | Must | Yes | `CKV_AZURE_102` |
| CO-007 | DP-5 | DP | Customer-managed key enabled | Conditional | Medium | Should | Yes | `CKV_AZURE_100` |
| CO-008 | BR-1 | BR | Automatic failover enabled | Conditional | Medium | Should | Yes | `CKV_AZURE_99` |
| CO-009 | NS-1 | NS | IP filter enabled | Conditional | High | Must | Yes | `CKV_AZURE_101` |

# 8. Azure API Management

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AP-001 | NS-1 | NS | Use virtual network (Internal mode) | Conditional | Medium | Should | Yes | `CKV_AZURE_33` |
| AP-002 | DP-3 | DP | Encrypt communication with backend | Yes | High | Must | Yes | `CKV_AZURE_104` |
| AP-003 | DP-6 | DP | Use certificates from Key Vault | Yes | High | Must | Yes | `CKV_AZURE_105` |
| AP-004 | IM-1 | IM | Use managed identity | Yes | High | Must | Yes | `CKV_AZURE_106` |
| AP-005 | IM-1 | IM | Authenticate with Azure AD | Conditional | Medium | Should | Partial | Custom |
| AP-006 | LT-1 | LT | Defender for APIs enabled | Yes | Medium | Should | Yes | `CKV_AZURE_65` |
| AP-007 | LT-4 | LT | API Management logging enabled | Yes | High | Must | Yes | `CKV_AZURE_103` |
| AP-008 | DP-3 | DP | Enforce minimum TLS 1.2 | Yes | High | Must | Yes | `CKV2_AZURE_3` |
| AP-009 | DP-3 | DP | Disable weak ciphers and protocols | Yes | High | Must | Yes | `CKV2_AZURE_2` |
| AP-010 | IM-3 | IM | Use Named Values from Key Vault | Yes | High | Must | Yes | `CKV2_AZURE_6` |

# 9. Azure Functions

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| FN-001 | DP-3 | DP | HTTPS Only enabled | Yes | High | Must | Yes | `CKV_AZURE_14` |
| FN-002 | IM-1 | IM | Managed identity enabled | Yes | High | Must | Yes | `CKV_AZURE_16` |
| FN-003 | IM-3 | IM | Secrets in app settings avoided | Yes | High | Must | Yes | `CKV_SECRET_2` |
| FN-004 | DP-3 | DP | Minimum TLS version 1.2 | Yes | High | Must | Yes | `CKV_AZURE_154` |
| FN-005 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Yes | `CKV_AZURE_13` |
| FN-006 | NS-2 | NS | VNet integration for private access | Conditional | Medium | Should | Yes | `CKV2_AZURE_28` |
| FN-007 | NS-1 | NS | Inbound access restricted (IP filter) | Conditional | Medium | Should | Yes | `CKV_AZURE_17` |
| FN-008 | PV-5 | PV | Use latest runtime version | Yes | Medium | Should | Yes | `CKV2_AZURE_11` |
| FN-009 | LT-1 | LT | Defender for App Service enabled | Yes | Medium | Should | Yes | `CKV_AZURE_65` |

# 10. Azure Backup

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| BK-001 | DP-2 | DP | Immutability and soft delete enabled | Yes | High | Must | Yes | `CKV_AZURE_189` |
| BK-002 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | `CKV2_AZURE_33` |
| BK-003 | BR-1 | BR | Cross-region restore enabled | Conditional | Medium | Should | Yes | `CKV_AZURE_218` |
| BK-004 | DP-4 | DP | Encryption at rest (platform key) | Yes | Medium | Must | No | Platform-managed |
| BK-005 | DP-5 | DP | Customer-managed keys enabled | Conditional | Medium | Should | Yes | `CKV2_AZURE_34` |
| BK-006 | LT-4 | LT | Diagnostic logging enabled | Yes | Medium | Must | Yes | `CKV_AZURE_133` |
| BK-007 | NS-2 | NS | Private endpoints for vault access | Conditional | High | Must | Partial | `CKV2_AZURE_18` |
| BK-008 | BR-2 | BR | Multi-user authorization enabled | Conditional | Medium | Should | Partial | Custom |

---

## Cross-Cutting Domains

The following are intentionally excluded from this matrix because they are not modeled as one deployable Azure resource per folder:

- DevOps Security
- Endpoint Security
- AI Security

They should be maintained as separate guidance or domain catalogs rather than entries in the deployable resource matrix.

---

## 11. Azure Application Gateway

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AGW-001 | NS-2 | NS | WAF enabled | Yes | High | Must | Yes | `CKV_AZURE_120` |
| AGW-002 | NS-2 | NS | WAF in Prevention mode | Yes | High | Must | Yes | `CKV_AZURE_122` |
| AGW-003 | DP-3 | DP | TLS 1.2+ enforced | Yes | High | Must | Partial | Custom |
| AGW-004 | LT-3 | LT | Diagnostic and access logs enabled | Yes | Medium | Must | Partial | Custom |
| AGW-005 | IM-3 | IM | Certificates sourced from Key Vault | Yes | High | Must | Partial | Custom |
| AGW-006 | NS-2 | NS | Public frontend only when required | Conditional | Medium | Should | Yes | Custom |

---

## 12. Azure Bastion

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| BAS-001 | NS-2 | NS | Bastion used instead of public RDP/SSH | Yes | High | Must | Partial | Custom |
| BAS-002 | NS-1 | NS | Dedicated `AzureBastionSubnet` | Yes | High | Must | Yes | Custom |
| BAS-003 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| BAS-004 | IM-1 | IM | Access governed by RBAC/PIM | Yes | High | Must | Partial | Not Applicable |
| BAS-005 | NS-2 | NS | Standard SKU used for production | Conditional | Medium | Should | Yes | Custom |

---

## 13. Azure App Configuration

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ACF-001 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | Custom |
| ACF-002 | NS-2 | NS | Private endpoint configured | Conditional | High | Must | Partial | Custom |
| ACF-003 | IM-1 | IM | Local auth disabled where supported | Conditional | Medium | Should | Partial | Custom |
| ACF-004 | DP-5 | DP | Customer-managed key where required | Conditional | Medium | Should | Partial | Custom |
| ACF-005 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ACF-006 | IM-3 | IM | Key Vault references used for secrets | Yes | High | Must | Partial | Custom |

---

## 14. Azure Cache for Redis

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| RED-001 | DP-3 | DP | Non-TLS port disabled | Yes | High | Must | Yes | Custom |
| RED-002 | NS-2 | NS | Private endpoint or restricted network access | Conditional | High | Must | Partial | Custom |
| RED-003 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| RED-004 | DP-5 | DP | Customer-managed key where required | Conditional | Medium | Should | Partial | Custom |
| RED-005 | IM-3 | IM | Access keys rotated and minimized | Yes | Medium | Should | Partial | Custom |
| RED-006 | PV-1 | PV | Defender recommendations monitored | Yes | Medium | Should | Partial | Custom |

---

## 15. Azure Container Apps

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ACA-001 | NS-2 | NS | External ingress disabled unless explicitly required | Conditional | High | Must | Yes | Custom |
| ACA-002 | IM-1 | IM | Managed identity enabled | Yes | High | Must | Yes | Custom |
| ACA-003 | IM-3 | IM | Secrets not hardcoded in template or env | Yes | High | Must | Partial | Custom |
| ACA-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ACA-005 | NS-2 | NS | Environment integrated with private networking where needed | Conditional | Medium | Should | Partial | Custom |
| ACA-006 | PV-5 | PV | Images sourced from approved registry | Yes | High | Must | Partial | Custom |

---

## 16. Azure Container Instances

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ACI-001 | NS-2 | NS | Public IP disabled unless required | Conditional | High | Must | Yes | Custom |
| ACI-002 | IM-1 | IM | Managed identity enabled where supported | Conditional | Medium | Should | Partial | Custom |
| ACI-003 | IM-3 | IM | Registry credentials not embedded in code | Yes | High | Must | Partial | Custom |
| ACI-004 | PV-5 | PV | Images pulled from approved registry | Yes | High | Must | Partial | Custom |
| ACI-005 | LT-3 | LT | Logs exported to centralized monitoring | Yes | Medium | Must | Partial | Custom |

---

## 17. Azure Container Registry

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ACR-001 | NS-2 | NS | Public network access disabled | Yes | High | Must | Yes | Custom |
| ACR-002 | IM-1 | IM | Admin user disabled | Yes | High | Must | Yes | Custom |
| ACR-003 | NS-2 | NS | Private endpoint configured for production | Conditional | High | Must | Partial | Custom |
| ACR-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ACR-005 | PV-5 | PV | Image scanning or Defender enabled | Yes | Medium | Should | Partial | Custom |
| ACR-006 | IM-3 | IM | Pull access via managed identity and RBAC | Yes | High | Must | Partial | Custom |

---

## 18. Azure Data Factory

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ADF-001 | IM-1 | IM | Managed identity enabled | Yes | High | Must | Yes | Custom |
| ADF-002 | IM-3 | IM | Linked service secrets stored in Key Vault | Yes | High | Must | Partial | Custom |
| ADF-003 | NS-2 | NS | Managed virtual network or private endpoints used where needed | Conditional | High | Must | Partial | Custom |
| ADF-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ADF-005 | DP-3 | DP | Secure transport to sources and sinks | Yes | High | Must | Partial | Custom |
| ADF-006 | PV-1 | PV | Defender recommendations monitored | Yes | Medium | Should | Partial | Custom |

---

## 19. Azure Data Share

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ADS-001 | NS-1 | NS | Cross-tenant sharing limited to approved scenarios | Conditional | High | Must | Partial | Custom |
| ADS-002 | IM-1 | IM | Access governed by RBAC | Yes | High | Must | Partial | Custom |
| ADS-003 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ADS-004 | DP-2 | DP | Shared datasets classified before publication | Yes | High | Must | No | Process control |
| ADS-005 | DP-8 | DP | Revocation process defined for active shares | Yes | Medium | Should | No | Process control |

---

## 20. Azure DNS

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| DNS-001 | IM-1 | IM | Zone management restricted with RBAC | Yes | High | Must | Partial | Custom |
| DNS-002 | LT-3 | LT | Activity logging enabled and retained | Yes | Medium | Must | Partial | Custom |
| DNS-003 | NS-1 | NS | Private DNS used for private endpoint resolution | Conditional | Medium | Should | Partial | Custom |
| DNS-004 | DP-3 | DP | DNSSEC or equivalent integrity protection where available | Conditional | Medium | Should | Partial | Custom |
| DNS-005 | PV-1 | PV | Critical public records protected by change review | Yes | High | Must | No | Process control |

---

## 21. Azure Event Grid

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| EVG-001 | IM-1 | IM | Managed identity or Entra auth used where supported | Conditional | High | Must | Partial | Custom |
| EVG-002 | NS-2 | NS | Webhook and destination endpoints restricted | Yes | High | Must | Partial | Custom |
| EVG-003 | DP-3 | DP | HTTPS-only event delivery | Yes | High | Must | Partial | Custom |
| EVG-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| EVG-005 | NS-1 | NS | Private Link used for sensitive event domains where supported | Conditional | Medium | Should | Partial | Custom |

---

## 22. Azure Event Hubs

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| EVH-001 | NS-2 | NS | Public network access disabled or restricted | Yes | High | Must | Yes | Custom |
| EVH-002 | NS-2 | NS | Private endpoint configured for production | Conditional | High | Must | Partial | Custom |
| EVH-003 | IM-1 | IM | Local or SAS auth minimized in favor of RBAC | Yes | High | Must | Partial | Custom |
| EVH-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| EVH-005 | DP-5 | DP | Customer-managed keys where required | Conditional | Medium | Should | Partial | Custom |
| EVH-006 | DP-8 | DP | Capture or retention configured for recovery requirements | Conditional | Medium | Should | Partial | Custom |

---

## 23. Azure Firewall

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AFW-001 | NS-2 | NS | Firewall policy used instead of ad hoc local rules | Yes | High | Must | Yes | Custom |
| AFW-002 | NS-1 | NS | Rule collections follow deny-by-default model | Yes | High | Must | Partial | Custom |
| AFW-003 | LT-3 | LT | Application, network, and threat logs enabled | Yes | Medium | Must | Partial | Custom |
| AFW-004 | NS-3 | NS | Threat intelligence mode enabled | Yes | Medium | Should | Yes | Custom |
| AFW-005 | NS-2 | NS | Forced tunneling or egress inspection used where required | Conditional | Medium | Should | Partial | Custom |
| AFW-006 | PV-1 | PV | Premium TLS inspection considered for high-risk workloads | Conditional | Medium | Should | Partial | Custom |

---

## 24. Azure Front Door

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| AFD-001 | NS-2 | NS | WAF policy associated with each public route | Yes | High | Must | Partial | Custom |
| AFD-002 | DP-3 | DP | HTTPS enforced and HTTP redirected or disabled | Yes | High | Must | Partial | Custom |
| AFD-003 | NS-1 | NS | Origins locked down to Front Door only | Yes | High | Must | Partial | Custom |
| AFD-004 | LT-3 | LT | Access and WAF logs enabled | Yes | Medium | Must | Partial | Custom |
| AFD-005 | IM-3 | IM | Certificates managed securely | Yes | High | Must | Partial | Custom |

---

## 25. Azure Load Balancer

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ALB-001 | NS-2 | NS | Public load balancer used only when required | Conditional | High | Must | Yes | Custom |
| ALB-002 | NS-1 | NS | Backend pool limited to intended workloads | Yes | High | Must | Partial | Custom |
| ALB-003 | NS-2 | NS | NSGs enforce inbound restrictions on backend subnets or NICs | Yes | High | Must | Partial | Custom |
| ALB-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ALB-005 | NS-3 | NS | DDoS protection considered for public ingress VNets | Conditional | Medium | Should | Partial | Custom |

---

## 26. Azure Logic Apps

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| LGA-001 | IM-1 | IM | Managed identity enabled | Yes | High | Must | Yes | Custom |
| LGA-002 | IM-3 | IM | Connector secrets stored in Key Vault | Yes | High | Must | Partial | Custom |
| LGA-003 | NS-2 | NS | Standard Logic Apps use private networking where required | Conditional | Medium | Should | Partial | Custom |
| LGA-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| LGA-005 | DP-3 | DP | Secure transport to downstream systems | Yes | High | Must | Partial | Custom |

---

## 27. Azure Monitor

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| MON-001 | LT-3 | LT | Central Log Analytics workspace configured | Yes | Medium | Must | Partial | Custom |
| MON-002 | IM-1 | IM | Workspace access restricted with RBAC | Yes | High | Must | Partial | Custom |
| MON-003 | NS-2 | NS | Private Link used for sensitive telemetry ingestion or query | Conditional | Medium | Should | Partial | Custom |
| MON-004 | LT-4 | LT | Retention aligned to incident response requirements | Yes | Medium | Must | Yes | Custom |
| MON-005 | DP-2 | DP | Sensitive logs protected and export controlled | Yes | High | Must | Partial | Custom |
| MON-006 | PV-1 | PV | Alerting enabled for critical posture signals | Yes | Medium | Should | Partial | Custom |

---

## 28. Azure Private Link

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| PLS-001 | NS-2 | NS | Private endpoint used for sensitive PaaS services | Conditional | High | Must | Partial | Custom |
| PLS-002 | NS-1 | NS | Private endpoint subnet governed by NSG or policy as applicable | Yes | High | Must | Partial | Custom |
| PLS-003 | NS-2 | NS | Public network access disabled on paired service where feasible | Conditional | High | Must | Partial | Custom |
| PLS-004 | LT-3 | LT | Private endpoint connection events monitored | Yes | Medium | Should | Partial | Custom |
| PLS-005 | NS-1 | NS | Private DNS zones linked correctly | Yes | High | Must | Partial | Custom |

---

## 29. Azure Public IP

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| PIP-001 | NS-2 | NS | Public IP used only when justified | Conditional | High | Must | Yes | Custom |
| PIP-002 | NS-3 | NS | Standard SKU required | Yes | High | Must | Yes | Custom |
| PIP-003 | NS-1 | NS | Resource associated with protected ingress control | Yes | High | Must | Partial | Custom |
| PIP-004 | LT-3 | LT | Changes and associations monitored | Yes | Medium | Must | Partial | Custom |
| PIP-005 | PV-1 | PV | Idle or unattached public IPs removed | Yes | Medium | Should | Partial | Custom |

---

## 30. Azure Service Bus

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| ASB-001 | NS-2 | NS | Public network access disabled or restricted | Yes | High | Must | Yes | Custom |
| ASB-002 | NS-2 | NS | Private endpoint configured for production | Conditional | High | Must | Partial | Custom |
| ASB-003 | IM-1 | IM | RBAC preferred over long-lived SAS keys | Yes | High | Must | Partial | Custom |
| ASB-004 | LT-3 | LT | Diagnostic logging enabled | Yes | Medium | Must | Partial | Custom |
| ASB-005 | DP-5 | DP | Customer-managed keys where required | Conditional | Medium | Should | Partial | Custom |
| ASB-006 | DP-8 | DP | Geo-disaster recovery or resilience pattern defined | Conditional | Medium | Should | Partial | Custom |

---

## 31. Azure Web Application Firewall

| Control ID | MCSB | Domain | Control Name | Applies | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|---|
| WAF-001 | NS-2 | NS | WAF enabled in prevention mode for production | Yes | High | Must | Yes | Custom |
| WAF-002 | NS-2 | NS | OWASP managed rule set enabled and current | Yes | High | Must | Yes | Custom |
| WAF-003 | LT-3 | LT | WAF logs enabled | Yes | Medium | Must | Partial | Custom |
| WAF-004 | NS-1 | NS | Custom rules and exclusions reviewed and minimal | Yes | High | Must | Partial | Custom |
| WAF-005 | PV-1 | PV | Rule tuning process documented to avoid silent bypass | Yes | Medium | Should | No | Process control |

---

## Usage

### Generate CI/CD checks

Each row where `IaC Checkable = Yes` maps directly to a Checkov rule or custom check.
Filter by `Priority = Must` + `Severity = High` to define the blocking gate in PRs.

### Standardize across repositories

Use this matrix as the contract between the security team and development teams.
Each service module in Terraform must pass all `Must` controls before merge.

### Scale to new services

1. Add a new row block to this file
2. Create `controls/<service>/controls.md` with full control detail
3. Add custom Checkov checks to `.checkov/custom_checks/` for any gaps
