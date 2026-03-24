# Azure Service to MCSB Control Catalog

> Purpose: normalized service-control catalog for internal security documentation and CI/CD security check design.
> Scope in this version: prioritized catalog rows for the most mature deployable Azure services already modeled in this repository.
> Source of truth: Microsoft Learn MCSB overview and Azure service security baselines.
> Review date: 2026-03-23

## Method and scope

This document is designed to be exported to Excel or consumed directly as Markdown. Each row represents one applicable control for one Azure service.

This catalog is not the same thing as `controls/MCSB-control-matrix.md`:

- The matrix is the canonical deployable service index for the repository.
- This catalog is the normalized service-to-control table used for analysis, export, and CI/CD design.
- The matrix currently covers more deployable services than this normalized catalog. Expand this file in maturity order rather than forcing placeholder rows for every service immediately.
- Verified current Checkov traceability, broken rule references, and normalization priorities are tracked in `docs/checkov-coverage-audit.md`.

Important note on source versions:

- The Microsoft Cloud Security Benchmark overview page currently presents **MCSB v2 (preview)** and was last updated on **2026-01-15**.
- The Azure service security baseline pages currently exposed in Microsoft Learn for the services used in this repository still state that they apply **MCSB version 1.0** and most were last updated on **2025-02-25**.
- For repository consistency, this catalog keeps the existing service-level control structure already modeled in the repo, while treating Microsoft Learn service baselines as the authoritative source for service applicability.

Official references:

- MCSB overview: https://learn.microsoft.com/en-us/security/benchmark/azure/overview
- Storage baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/storage-security-baseline
- Key Vault baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/key-vault-security-baseline
- Virtual Network baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/virtual-network-security-baseline
- App Service baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/app-service-security-baseline
- AKS baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/azure-kubernetes-service-aks-security-baseline
- Azure SQL baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/azure-sql-security-baseline
- Azure Cosmos DB baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/azure-cosmos-db-security-baseline
- API Management baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/api-management-security-baseline
- Functions baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/functions-security-baseline
- Backup baseline: https://learn.microsoft.com/en-us/azure/backup/security-baseline
- Logic Apps baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/logic-apps-security-baseline
- Event Grid baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/event-grid-security-baseline
- Azure Private Link baseline: https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/azure-private-link-security-baseline

## Normalized Catalog

| Azure Service | Category | Control ID | MCSB | Control Name | Relevance | Recommendation / Implementation Note | Priority | IaC Checkable | Primary Source |
|---|---|---|---|---|---|---|---|---|---|
| Azure Storage Account | Storage | ST-001 | NS-1 | Public blob access disabled | Prevents anonymous exposure of containers and blobs. | Set `allow_nested_items_to_be_public = false` and block any public container pattern by default. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-002 | DP-3 | HTTPS only | Ensures clients cannot use clear-text transport. | Set `enable_https_traffic_only = true`; treat any exception as non-compliant. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-003 | DP-3 | Minimum TLS 1.2 | Reduces downgrade and legacy protocol exposure. | Enforce `min_tls_version = "TLS1_2"` in all storage modules. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-004 | DP-4 | Infrastructure encryption | Adds defense in depth for regulated data sets. | Enable `infrastructure_encryption_enabled = true` for sensitive and production workloads. | Should | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-005 | DP-5 | Customer-managed keys | Required where customer control over key lifecycle is mandated. | Use CMK backed by Key Vault when workload classification or regulation requires it. | Should | Partial | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-006 | NS-2 | Network firewall default deny | Prevents unrestricted public network reachability. | Enforce `default_action = "Deny"` and explicitly allow only trusted IPs or subnets. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-007 | NS-2 | Public network access disabled | Removes internet exposure for internal-only storage workloads. | Use `public_network_access_enabled = false` with private endpoints for private access patterns. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-008 | LT-3 | Diagnostic logging enabled | Required for auditability and incident investigation of data operations. | Configure diagnostic settings for blob services to Log Analytics or approved sink. | Must | Partial | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-009 | DP-8 | Soft delete enabled | Supports recovery after accidental or malicious deletion. | Configure blob and container retention; use 30 days in production unless a stronger standard exists. | Should | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-010 | DP-8 | Blob versioning enabled | Preserves prior object states and reduces overwrite risk. | Enable versioning when workload needs recovery of overwritten data or ransomware resilience. | Nice | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-011 | IM-1 | Shared key access disabled | Forces identity-based access and removes anonymous-like key sprawl risk. | Set `shared_access_key_enabled = false` and move consumers to Entra ID and RBAC. | Must | Yes | Repo matrix + Storage baseline |
| Azure Storage Account | Storage | ST-012 | NS-1 | Cross-tenant replication disabled | Reduces uncontrolled data replication to external tenants. | Set `cross_tenant_replication_enabled = false` unless a formally approved B2B scenario exists. | Must | Yes | Repo matrix + Storage baseline |
| Azure Key Vault | Security / Secrets | KV-001 | NS-2 | Public network access disabled | Key Vault is a high-value target and should not be internet-exposed. | Set `public_network_access_enabled = false` by default in production patterns. | Must | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-002 | NS-2 | Private endpoint configured | Keeps secret retrieval on private address space. | Pair public access disablement with a private endpoint in trusted VNets. | Must | Partial | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-003 | NS-1 | Network default action deny | Ensures only explicitly trusted paths can reach the vault. | Use `network_acls.default_action = "Deny"` and restrict by subnet/IP as needed. | Must | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-004 | LT-3 | Diagnostic logging enabled | Required to track secret, key, and certificate access. | Send `AuditEvent` and related logs to centralized monitoring. | Must | Partial | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-005 | DP-7 | Soft delete enabled | Prevents irreversible loss from accidental deletion. | Set high retention, typically 90 days, in standard enterprise modules. | Must | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-006 | DP-7 | Purge protection enabled | Blocks permanent deletion before retention expires. | Set `purge_protection_enabled = true` and treat it as baseline mandatory. | Must | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-007 | IM-1 | RBAC authorization model | Aligns access management with centralized Entra ID and auditable role assignments. | Use `enable_rbac_authorization = true` and avoid legacy access policies except documented exceptions. | Must | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-008 | DP-6 | Key rotation policy defined | Limits exposure window for cryptographic key compromise. | Require `rotation_policy` for customer-managed keys used by applications or encryption services. | Should | Partial | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-009 | DP-6 | Key expiration date set | Ensures keys do not remain valid indefinitely. | Set expiration on all managed keys and align with rotation cadence. | Should | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-010 | DP-6 | Secret expiration date set | Reduces long-lived credential risk. | Require expiration dates on secrets and connect renewal to application lifecycle. | Should | Yes | Repo matrix + Key Vault baseline |
| Azure Key Vault | Security / Secrets | KV-011 | PV-1 | Defender for Key Vault enabled | Adds anomaly detection for suspicious vault access. | Enable Defender plan at subscription scope for production subscriptions. | Should | Partial | Repo matrix + Key Vault baseline |
| Azure Virtual Network | Networking | VN-001 | NS-1 | Subnets associated with NSG | Establishes segmentation and subnet-level traffic control. | Require NSG association on every workload subnet except justified platform subnets. | Must | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-002 | NS-1 | NSG default deny inbound | Prevents implicit broad exposure through permissive rule design. | Use explicit allow rules only where needed and ensure deny-all inbound remains effective. | Must | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-003 | NS-2 | No unrestricted inbound SSH | Removes one of the most common external attack paths. | Disallow `0.0.0.0/0` on port 22; use Bastion or approved management ranges. | Must | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-004 | NS-2 | No unrestricted inbound RDP | Prevents ransomware-oriented exposure on management endpoints. | Disallow `0.0.0.0/0` on port 3389 and prefer Bastion or JIT access. | Must | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-005 | NS-3 | DDoS protection enabled | Required for VNets hosting public-facing critical services. | Associate DDoS Network Protection plan to internet-facing production VNets. | Should | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-006 | NS-4 | Network Watcher enabled | Enables troubleshooting and some network forensics capabilities. | Deploy Network Watcher in each active region used by the landing zone. | Must | Partial | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-007 | LT-3 | NSG flow logs enabled | Provides evidence of allowed and denied network flows. | Enable flow logs with retention and traffic analytics for sensitive environments. | Must | Partial | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-008 | NS-2 | No wildcard inbound rules | Prevents segmentation collapse caused by any-any allows. | Reject NSG rules that use wildcards for source, destination, and port with `Allow`. | Must | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-009 | NS-7 | Service endpoints scoped to subnet | Reduces reliance on public routing for PaaS consumption from VNets. | Use service endpoints only where private endpoints are not the selected pattern and scope them per subnet. | Should | Yes | Repo matrix + Virtual Network baseline |
| Azure Virtual Network | Networking | VN-010 | NS-1 | Subnets not overly broad | Better segmentation limits lateral movement blast radius. | Avoid large flat subnets for workload tiers; design CIDR per application boundary. | Nice | Partial | Repo matrix + Virtual Network baseline |
| Azure App Service | Compute / PaaS Web | AS-001 | DP-3 | HTTPS only enabled | Prevents clear-text application traffic. | Set `https_only = true` on every app and slot. | Must | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-002 | DP-3 | Minimum TLS 1.2 | Blocks legacy protocol negotiation. | Enforce `min_tls_version = "1.2"` in all web app modules. | Must | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-003 | NS-2 | Public network access restricted | Internal APIs and admin apps should not be broadly reachable. | Apply IP restrictions or private access pattern unless the service is intentionally public-facing. | Must | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-004 | NS-2 | VNet integration configured | Allows secure outbound access to private dependencies. | Use VNet integration when the app consumes private endpoints, internal APIs, or restricted PaaS services. | Should | Partial | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-005 | IM-1 | Managed identity enabled | Eliminates stored credentials for Azure resource access. | Enable system- or user-assigned managed identity and use RBAC for downstream services. | Must | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-006 | IM-3 | No credentials in app settings | Prevents secret leakage in Terraform state, portal configuration, and CI logs. | Store secrets in Key Vault and use references instead of plaintext app settings. | Must | Partial | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-007 | LT-3 | Diagnostic logging enabled | Centralized telemetry is needed for investigation and platform monitoring. | Configure diagnostics to Log Analytics for app, audit, console, and HTTP telemetry. | Must | Partial | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-008 | LT-3 | HTTP logging enabled | Supports attack analysis, abuse detection, and troubleshooting. | Enable HTTP access logging with retention aligned to incident response needs. | Must | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-009 | PV-5 | Latest runtime version | Outdated runtimes introduce known CVEs and unsupported components. | Standardize on supported runtime versions and fail builds for EOL runtimes. | Should | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-010 | DP-4 | Data encryption at rest | Data is platform-encrypted by default and must be documented as inherited control. | Record as platform-managed baseline; no Terraform assertion unless service mode changes. | Must | No | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-011 | NS-1 | IP restrictions configured | Limits inbound exposure to trusted paths. | Use allowlists for internal or administrative apps and propagate the same policy to SCM. | Should | Yes | Repo matrix + App Service baseline |
| Azure App Service | Compute / PaaS Web | AS-012 | PV-1 | Defender for App Service enabled | Improves posture visibility and attack detection for web workloads. | Enable Defender plan in production subscriptions and track recommendations centrally. | Should | Partial | Repo matrix + App Service baseline |
| Azure Kubernetes Service | Containers | AK-001 | NS-2 | API server authorized IP ranges | The control plane is a high-value interface and must not be world-reachable. | Restrict API server access to corporate egress or trusted administration networks. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-002 | NS-2 | Private cluster enabled | Removes the API endpoint from the public internet. | Use private cluster mode for production unless there is a formally accepted exception. | Should | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-003 | IM-1 | Azure AD integration enabled | Centralizes cluster authentication and supports enterprise identity controls. | Use managed Entra integration and avoid certificate-only access patterns. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-004 | IM-1 | Local accounts disabled | Prevents bypass of centralized identity and weakens shared admin credential use. | Set `local_account_disabled = true` for all enterprise clusters. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-005 | PA-7 | RBAC enabled | Enforces least privilege on cluster administration and workload operations. | Require Kubernetes RBAC and prefer Azure RBAC integration where supported. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-006 | NS-1 | Network policy enabled | Limits east-west traffic and pod lateral movement. | Require `network_policy` with Azure or Calico in every cluster network profile. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-007 | PV-2 | Auto-upgrade channel configured | Reduces lag on critical control-plane security patches. | Use `patch` in production by default and document stricter cadence for non-prod if needed. | Should | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-008 | PV-5 | Node OS auto-patching enabled | Keeps node image vulnerabilities under control. | Enforce node OS upgrade channel such as `NodeImage` unless a managed exception exists. | Should | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-009 | LT-3 | Diagnostic logging enabled | Captures audit and control plane logs required for incident response. | Send `kube-audit`, `kube-audit-admin`, and control plane categories to Log Analytics. | Must | Partial | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-010 | LT-1 | Defender for Containers enabled | Adds runtime threat detection and image security posture. | Enable Defender for Containers at subscription level and onboard all production clusters. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-011 | DP-4 | Disk encryption at rest | Protects node and attached disk data, especially in regulated workloads. | Use platform encryption as baseline and CMK-backed Disk Encryption Set where required. | Must | Yes | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-012 | NS-2 | Ingress with WAF / App Gateway | Public HTTP exposure needs a web application protection layer. | Front internet-facing clusters with Application Gateway WAF or equivalent approved control. | Should | Partial | Repo matrix + AKS baseline |
| Azure Kubernetes Service | Containers | AK-013 | PV-1 | Azure Policy add-on enabled | Enforces preventive guardrails on cluster objects. | Enable Azure Policy add-on and map required Gatekeeper constraints to platform standards. | Should | Yes | Repo matrix + AKS baseline |
| Azure SQL Database | Database | SQ-001 | NS-1 | Virtual network integration | Azure SQL supports private network integration and should be isolated from uncontrolled network paths. | Use VNet rules or equivalent private connectivity patterns for workloads that should not traverse open network paths. | Should | Partial | Azure SQL baseline |
| Azure SQL Database | Database | SQ-002 | NS-2 | Private Link enabled | Private endpoints reduce exposure of the data plane and align with enterprise private access patterns. | Deploy Private Link for production databases and route application access through approved private networks. | Must | Partial | Azure SQL baseline |
| Azure SQL Database | Database | SQ-003 | IM-1 | Azure AD authentication for data plane | Centralized identity reduces reliance on SQL logins and supports enterprise access governance. | Use Entra ID as the default authentication method and provision an Entra admin on logical servers. | Must | Partial | Azure SQL baseline |
| Azure SQL Database | Database | SQ-004 | IM-7 | Conditional access for data plane | Sensitive database access should be controlled by user and device conditions where supported. | Apply Conditional Access for privileged and user access patterns that reach Azure SQL through Entra ID. | Should | No | Azure SQL baseline |
| Azure SQL Database | Database | SQ-005 | DP-3 | Encryption in transit | Azure SQL encrypts data in transit and this must remain part of the documented baseline. | Treat TLS-encrypted transport as mandatory and prevent clients from using downgraded or weak connectivity settings. | Must | No | Azure SQL baseline |
| Azure SQL Database | Database | SQ-006 | DP-4 | Encryption at rest with platform keys | At-rest encryption is built in and should be captured as inherited control. | Document TDE/platform encryption as baseline default for all databases. | Must | No | Azure SQL baseline |
| Azure SQL Database | Database | SQ-007 | DP-5 | Customer-managed keys for TDE when required | Regulated data sets may require customer control over encryption keys. | Use CMK-backed Transparent Data Encryption when workload classification or regulation requires customer key ownership. | Should | Partial | Azure SQL baseline |
| Azure SQL Database | Database | SQ-008 | LT-1 | Defender for Azure SQL enabled | Defender adds threat detection and vulnerability insights for database workloads. | Enable Defender for Azure SQL in production subscriptions and integrate alerts with SecOps workflows. | Should | Partial | Azure SQL baseline |
| Azure SQL Database | Database | SQ-009 | LT-4 | Resource and audit logging enabled | SQL telemetry is required for investigation, anomaly review, and evidentiary retention. | Enable server-level auditing and send diagnostic logs to Log Analytics or approved SIEM storage. | Must | Partial | Azure SQL baseline |
| Azure Cosmos DB | Database | CO-001 | NS-1 | Virtual network integration | Cosmos DB supports network restriction patterns that should be used for internal workloads. | Restrict account exposure through VNet integration or equivalent approved network boundary. | Should | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-002 | NS-2 | Private Link enabled | Private endpoints reduce public exposure of database endpoints. | Use Private Link for production accounts and align DNS and routing with enterprise private network standards. | Must | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-003 | IM-1 | Azure AD authentication for data plane | Identity-based access is preferable to key-only access, but support varies by API. | Use Entra ID and data-plane RBAC for Core (SQL) API accounts; document exceptions for APIs that still depend on keys. | Must | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-004 | IM-3 | Managed identities for application access | Managed identity avoids embedding keys and secrets in applications. | Prefer managed identities for supported authentication scenarios and remove static secrets from app configuration. | Should | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-005 | PA-7 | Data plane RBAC enabled | Least privilege is required for applications and operators interacting with the data plane. | Use Azure RBAC for supported Cosmos DB data-plane actions instead of broad account-level key sharing. | Must | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-006 | DP-3 | Encryption in transit | Transport encryption is enabled by the platform and should be preserved as a documented baseline. | Treat TLS 1.2+ transport as mandatory and avoid client configurations that weaken transport security assumptions. | Must | No | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-007 | DP-4 | Encryption at rest with platform keys | Default platform encryption protects customer data at rest. | Record this as an inherited control in service templates and compliance evidence. | Must | No | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-008 | DP-5 | Customer-managed keys when required | Some regulated workloads require customer ownership of encryption keys. | Enable CMK with Key Vault where compliance, segregation, or key lifecycle control requires it. | Should | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-009 | LT-1 | Defender for Azure Cosmos DB enabled | Defender improves visibility on anomalous and malicious database activity. | Enable Defender plan for production use and route findings into central monitoring and response. | Should | Partial | Azure Cosmos DB baseline |
| Azure Cosmos DB | Database | CO-010 | LT-4 | Resource logging enabled | Operational and security investigations depend on Cosmos DB diagnostics. | Send Cosmos DB diagnostic logs and metrics to Log Analytics or approved telemetry sinks. | Must | Partial | Azure Cosmos DB baseline |
| Azure API Management | Integration / API | AP-001 | NS-1 | VNet integration | APIM often fronts critical internal and external APIs and benefits from network isolation. | Deploy APIM into a VNet where backend dependencies or exposure profile require private network control. | Should | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-002 | NS-2 | Private Link enabled | Private endpoints provide a private ingress option when full VNet deployment is not used. | Use a private endpoint for inbound access when APIM cannot be deployed in internal VNet mode. | Should | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-003 | NS-2 | Public network access disabled or tightly restricted | API gateways should not remain broadly internet-exposed by default. | Disable public network access where feasible or restrict exposure using approved ACL and frontend controls. | Must | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-004 | IM-1 | Azure AD authentication | Centralized identity is required for administrator and developer-facing access patterns where supported. | Use Entra ID for developer portal and API protection workflows whenever possible. | Should | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-005 | PA-1 | Local accounts restricted | Local user and admin patterns increase unmanaged credential risk. | Avoid local accounts except for break-glass use and keep them disabled or tightly governed. | Should | No | API Management baseline |
| Azure API Management | Integration / API | AP-006 | DP-3 | Encrypted protocols only | API consumers should only reach exposed APIs over encrypted protocols. | Publish APIs over HTTPS or WSS only and deny HTTP or WS in gateway configurations. | Must | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-007 | DP-4 | Encryption at rest with platform keys | APIM stores configuration and metadata that are encrypted at rest by platform services. | Document this as inherited platform encryption in service modules. | Must | No | API Management baseline |
| Azure API Management | Integration / API | AP-008 | DP-6 | Key Vault integration for secrets and certificates | Certificates and named values should not be managed as inline secrets in APIM. | Store secret named values, certificates, and customer keys in Key Vault and reference them from APIM. | Must | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-009 | LT-1 | Defender for APIs enabled | API-specific threat detection improves visibility into exposed API attack surface. | Enable Defender for APIs and onboard unmanaged APIs in APIM instances used in production. | Should | Partial | API Management baseline |
| Azure API Management | Integration / API | AP-010 | LT-4 | Resource logging enabled | Gateway and websocket logs are required for troubleshooting and forensic review. | Enable APIM diagnostic categories such as `GatewayLogs` and `WebSocketConnectionLogs`. | Must | Partial | API Management baseline |
| Azure Functions | Compute / Serverless | FN-001 | NS-1 | VNet integration | Functions frequently connect to private services and should honor enterprise network boundaries. | Use VNet integration and subnet-level NSG controls for functions that access private resources. | Should | Partial | Functions baseline |
| Azure Functions | Compute / Serverless | FN-002 | NS-2 | Private Link enabled | Private endpoints reduce direct public reachability for function apps. | Use Private Link for production apps that should not expose public endpoints. | Should | Partial | Functions baseline |
| Azure Functions | Compute / Serverless | FN-003 | IM-1 | Azure AD authentication for endpoints and deployment access | Identity-based access reduces reliance on publishing credentials and weak endpoint exposure. | Require Entra ID where supported for customer-owned endpoints and disable publishing credentials when not required. | Must | Partial | Functions baseline |
| Azure Functions | Compute / Serverless | FN-004 | IM-3 | Managed identity enabled | Serverless workloads should not carry embedded credentials for downstream Azure access. | Enable managed identity for each function app and consume downstream services through RBAC. | Must | Yes | Functions baseline |
| Azure Functions | Compute / Serverless | FN-005 | DP-3 | HTTPS only and minimum TLS 1.2 | Functions can be configured below the desired transport baseline if not explicitly hardened. | Enforce HTTPS-only access and retain TLS 1.2 as the minimum accepted protocol version. | Must | Yes | Functions baseline |
| Azure Functions | Compute / Serverless | FN-006 | LT-1 | Defender for App Service enabled | Defender for App Service covers Azure Functions and improves runtime threat visibility. | Enable Defender for App Service in production subscriptions and triage alerts through SecOps. | Should | Partial | Functions baseline |
| Azure Functions | Compute / Serverless | FN-007 | LT-4 | Resource logging enabled | Diagnostics are necessary for security investigation and reliability troubleshooting. | Send Azure Functions resource logs and metrics to Log Analytics or an approved SIEM sink. | Must | Partial | Functions baseline |
| Azure Backup | Backup / Recovery | BK-001 | NS-2 | Private Link enabled | Recovery Services vault exposure should be limited for sensitive backup control planes. | Use Private Link for vault access in production environments with private connectivity standards. | Should | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-002 | NS-2 | Public network access disabled | Backup vaults should not be broadly reachable from the public internet. | Deny public network access on vaults unless there is a justified operational dependency. | Must | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-003 | IM-8 | Key Vault for credentials and secret storage | Backup-related secrets and encryption material should not be stored insecurely. | Store supported credentials and keys in Key Vault instead of code, config, or local files. | Should | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-004 | DP-2 | Immutable and anti-deletion protections for backup data | Backup data is high-value and must be protected against tampering and destructive actions. | Use immutable vault, soft delete, and multi-user authorization features for critical workloads. | Must | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-005 | DP-3 | Encryption in transit | Backup traffic is encrypted by default and should be documented as baseline behavior. | Record transport encryption as inherited control and preserve secure connectivity assumptions in client design. | Must | No | Backup baseline |
| Azure Backup | Backup / Recovery | BK-006 | DP-4 | Encryption at rest with platform keys | Backup data at rest is protected by platform-managed encryption. | Document platform encryption as baseline for vault-stored backup data. | Must | No | Backup baseline |
| Azure Backup | Backup / Recovery | BK-007 | DP-5 | Customer-managed keys when required | Some backup data sets may require customer ownership of encryption keys. | Use CMK-backed vault encryption where regulatory or contractual obligations require it. | Should | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-008 | DP-6 | Key lifecycle in Key Vault | CMK usage requires secure generation, rotation, and revocation processes. | Manage backup encryption keys in Key Vault with defined rotation and revocation procedures. | Should | Partial | Backup baseline |
| Azure Backup | Backup / Recovery | BK-009 | BR-1 | Automated backup protection enabled | Backup service value depends on consistent protection being actually enabled for scoped assets. | Ensure protected items are onboarded and policy-backed; treat unprotected critical assets as a gap. | Must | Partial | Backup baseline |
| Azure Logic Apps | Integration / Workflow | LGA-001 | IM-1 | Managed identity enabled | Logic Apps often orchestrate privileged automation and should not rely on embedded credentials. | Enable system- or user-assigned managed identity for supported connectors and downstream Azure access patterns. | Must | Partial | Repo matrix + Logic Apps baseline |
| Azure Logic Apps | Integration / Workflow | LGA-002 | IM-3 | Connector secrets stored in Key Vault | Workflow definitions and connection parameters are common secret exposure paths. | Keep connector secrets in Key Vault or equivalent secure references instead of plaintext workflow parameters. | Must | Partial | Repo matrix + Logic Apps baseline |
| Azure Logic Apps | Integration / Workflow | LGA-003 | NS-2 | Standard Logic Apps use private networking where required | Internal workflows should not default to public exposure when Standard hosting supports stronger network boundaries. | Use VNet integration, private endpoints, and internal networking for Standard Logic Apps handling sensitive systems. | Should | Partial | Repo matrix + Logic Apps baseline |
| Azure Logic Apps | Integration / Workflow | LGA-004 | LT-3 | Diagnostic logging enabled | Run history and trigger telemetry are required for investigation of workflow abuse and failures. | Export Logic Apps diagnostics and workflow telemetry to Log Analytics or an approved SIEM sink. | Must | Partial | Repo matrix + Logic Apps baseline |
| Azure Logic Apps | Integration / Workflow | LGA-005 | DP-3 | Secure transport to downstream systems | Logic Apps cross multiple trust boundaries and should not call weakly protected endpoints. | Restrict downstream calls to HTTPS and approved connector trust paths; reject non-encrypted destinations. | Must | Partial | Repo matrix + Logic Apps baseline |
| Azure Event Grid | Integration / Eventing | EVG-001 | IM-1 | Managed identity or Entra auth used where supported | Identity-based delivery reduces shared-secret sprawl across event-driven integrations. | Prefer managed identity or Entra-backed auth where platform support exists and document exceptions clearly. | Must | Partial | Repo matrix + Event Grid baseline |
| Azure Event Grid | Integration / Eventing | EVG-002 | NS-2 | Webhook and destination endpoints restricted | Subscriptions define outbound trust paths and can become data-exfiltration channels if left open-ended. | Allow only approved webhook and destination endpoints and review all external targets explicitly. | Must | Partial | Repo matrix + Event Grid baseline |
| Azure Event Grid | Integration / Eventing | EVG-003 | DP-3 | HTTPS-only event delivery | Event payloads and metadata should not traverse unencrypted delivery paths. | Require HTTPS for webhook delivery and reject non-encrypted transport patterns. | Must | Partial | Repo matrix + Event Grid baseline |
| Azure Event Grid | Integration / Eventing | EVG-004 | LT-3 | Diagnostic logging enabled | Delivery failures, subscription changes, and management operations are needed for investigation and troubleshooting. | Send Event Grid diagnostics to central monitoring and retain delivery-failure visibility. | Must | Partial | Repo matrix + Event Grid baseline |
| Azure Event Grid | Integration / Eventing | EVG-005 | NS-1 | Private Link used for sensitive event domains where supported | Sensitive event fabrics may require private routing instead of default public service endpoints. | Use supported private connectivity patterns for sensitive topics or domains and document feature-specific limitations. | Should | Partial | Repo matrix + Event Grid baseline |
| Azure Private Link | Networking / Private Access | PLS-001 | NS-2 | Private endpoint used for sensitive PaaS services | Sensitive PaaS workloads should prefer private data-plane access over default public reachability. | Deploy `azurerm_private_endpoint` for production or internal-only PaaS services that expose sensitive data or control planes. | Must | Partial | Repo matrix + Azure Private Link baseline |
| Azure Private Link | Networking / Private Access | PLS-002 | NS-1 | Private endpoint subnet governed by NSG or policy as applicable | Endpoint subnets still need explicit network governance and should not become unmanaged trust corridors. | Apply subnet governance, policies, and supported NSG controls to private endpoint subnets with documented exceptions. | Must | Partial | Repo matrix + Azure Private Link baseline |
| Azure Private Link | Networking / Private Access | PLS-003 | NS-2 | Public network access disabled on paired service where feasible | Private Link is incomplete if the paired service remains broadly exposed over the internet. | Disable or tightly restrict public network access on the target service whenever platform support exists. | Must | Partial | Repo matrix + Azure Private Link baseline |
| Azure Private Link | Networking / Private Access | PLS-004 | LT-3 | Private endpoint connection events monitored | Connection approvals and lifecycle changes are relevant security and change-control signals. | Monitor activity logs and diagnostics for private endpoint approvals, rejections, and state changes. | Should | Partial | Repo matrix + Azure Private Link baseline |
| Azure Private Link | Networking / Private Access | PLS-005 | NS-1 | Private DNS zones linked correctly | Incorrect DNS linkage silently reroutes traffic away from intended private paths. | Validate private DNS zone groups and VNet links for each endpoint pattern and prevent fallback to public name resolution. | Must | Partial | Repo matrix + Azure Private Link baseline |

## Use in CI/CD documentation

Recommended documentation columns for Excel export:

1. `Azure Service`
2. `Category`
3. `Control ID`
4. `MCSB`
5. `Control Name`
6. `Relevance`
7. `Recommendation / Implementation Note`
8. `Priority`
9. `IaC Checkable`
10. `Primary Source`
11. `Planned Validation Rule`
12. `Exception Criteria`

Recommended interpretation for pipeline design:

- `Must` + `IaC Checkable = Yes`: candidate for blocking PR gate.
- `Must` + `IaC Checkable = Partial`: candidate for combined IaC + evidence review.
- `Should`: candidate for non-blocking advisory gate or backlog control.
- `No` or platform-managed: document as inherited or manual evidence control.

## Current gap versus full Azure service catalog

The deployable service matrix now covers significantly more services than this normalized catalog. This file should be expanded in the following order:

1. Networking and edge services
2. Messaging and integration services
3. Supply chain and observability services
4. Remaining configuration and data movement services

The remaining items that should not be modeled here as a single deployable Azure resource baseline are:

- Endpoint Security
- DevOps Security
- AI Security
- Microsoft Defender for Cloud

These should be treated as cross-cutting domain catalogs or posture guidance, not as one service-per-folder deployable baselines.
