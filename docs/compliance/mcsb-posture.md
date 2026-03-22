# MCSB Compliance Posture — lolnotifier-bot

> **Last updated**: 2026-03-22 | **Environment**: dev | **Version**: v5.1.0
> **Initiative**: `mcsb-lolnotifier-dev` | **Scope**: `rg-lolnotifier-dev`

---

## Overall Posture

| Category | Compliant | Non-Compliant | Excepted | N/A |
|---|---|---|---|---|
| Key Vault | 4 | 0 | 2 | 0 |
| Storage Account | 3 | 0 | 2 | 0 |
| CosmosDB | 2 | 0 | 4 | 0 |
| Function App | 2 | 0 | 3 | 0 |
| Monitoring | 2 | 0 | 0 | 0 |
| **Total** | **13** | **0** | **11** | **0** |

> All non-compliant items have registered exceptions in [`exceptions-registry.json`](./exceptions-registry.json).
> Zero unregistered violations.

---

## Key Vault — `kv-lolnotifier-dev-h4dx`

| MCSB Control | Check ID | Status | Notes |
|---|---|---|---|
| Soft delete enabled | CKV_AZURE_42 | ✅ Compliant | 7 days retention |
| Purge protection enabled | CKV_AZURE_109 | ✅ Compliant | `purge_protection_enabled = true` |
| RBAC authorization | CKV_AZURE_110 | ✅ Compliant | `enable_rbac_authorization = true` |
| Secret expiration dates | MCSB-DP-8 | ✅ Compliant | All secrets have expiration dates |
| Audit logs to Log Analytics | MCSB-LT-3 | ✅ Compliant | AuditEvent category enabled |
| Network firewall (Deny default) | CKV_AZURE_189 | ⚠️ Excepted | [EXC-001](./exceptions-registry.json) — CI/CD runner constraint |
| Private endpoint / IP rules | CKV_AZURE_109 | ⚠️ Excepted | [EXC-001](./exceptions-registry.json) — dynamic runner IPs |

**Compensating controls for EXC-001**: RBAC-only access, all access audited, TruffleHog on every PR.

---

## Storage Account — `stlolnotifierdevh4dx`

| MCSB Control | Check ID | Status | Notes |
|---|---|---|---|
| HTTPS-only traffic | CKV_AZURE_33 | ✅ Compliant | `https_traffic_only_enabled = true` |
| Minimum TLS 1.2 | CKV_AZURE_3 | ✅ Compliant | `min_tls_version = "TLS1_2"` |
| Public blob access disabled | CKV_AZURE_59 | ✅ Compliant | `allow_nested_items_to_be_public = false` |
| Blob soft delete | MCSB-DP-8 | ✅ Compliant | 7 days retention |
| Network rules (Deny default) | CKV_AZURE_35 | ⚠️ Excepted | [EXC-002](./exceptions-registry.json) — Y1 Consumption plan |
| Shared access key disabled | CKV_AZURE_256 | ⚠️ Excepted | [EXC-002](./exceptions-registry.json) — required by Function App runtime |

**Compensating controls for EXC-002**: Access key in Key Vault, HTTPS-only, no public blob access.

---

## CosmosDB — `cosmos-lolnotifier-dev-h4dx`

| MCSB Control | Check ID | Status | Notes |
|---|---|---|---|
| Encryption at rest | MCSB-DP-5 | ✅ Compliant | Default AES-256 (Microsoft-managed) |
| Metadata write protection | CKV_AZURE_132 | ✅ Compliant | `access_key_metadata_writes_enabled = false` |
| Diagnostic logs | MCSB-LT-3 | ✅ Compliant | DataPlaneRequests + QueryRuntimeStatistics |
| Public network access disabled | CKV_AZURE_101 | ⚠️ Excepted | [EXC-003](./exceptions-registry.json) — serverless tier |
| VNet / firewall rules | CKV_AZURE_99 | ⚠️ Excepted | [EXC-003](./exceptions-registry.json) — serverless tier |
| Local authentication disabled | CKV_AZURE_140 | ⚠️ Excepted | [EXC-004](./exceptions-registry.json) — SDK connection string |
| Customer-managed keys | CKV_AZURE_100 | ⚠️ Excepted | [EXC-005](./exceptions-registry.json) — non-sensitive data |

**Data classification**: Non-sensitive. Match statistics, public player names, Telegram user IDs (public identifiers). No financial, health, or personal data.

---

## Function App — `func-lolnotifier-dev-h4dx`

| MCSB Control | Check ID | Status | Notes |
|---|---|---|---|
| HTTPS-only | CKV_AZURE_190 | ✅ Compliant | `https_only = true` |
| Managed identity | CKV_AZURE_70 | ✅ Compliant | System-assigned identity |
| Secrets via Key Vault refs | MCSB-IM-8 | ✅ Compliant | No plaintext secrets in app settings |
| Minimum TLS 1.2 | CKV_AZURE_18 | ✅ Compliant | Default on Linux Function App |
| Public network access disabled | CKV_AZURE_221 | ⚠️ Excepted | [EXC-006](./exceptions-registry.json) — Y1 plan |
| Zone redundancy | CKV_AZURE_225 | ⚠️ Excepted | [EXC-007](./exceptions-registry.json) — Y1 plan |
| Minimum instances > 1 | CKV_AZURE_212 | ⚠️ Excepted | [EXC-007](./exceptions-registry.json) — Y1 plan |

---

## Monitoring — Log Analytics + App Insights

| MCSB Control | Check ID | Status | Notes |
|---|---|---|---|
| Log retention ≥ 90 days | MCSB-LT-3 | ✅ Compliant | 90 days on both workspaces |
| Diagnostic settings on all resources | MCSB-LT-4 | ✅ Compliant | KV, CosmosDB, Logic App, App Insights |
| Exception alerting | MCSB-IR-2 | ✅ Compliant | Alert on >10 exceptions in 5 min |

---

## CI/CD Security Controls

| Control | Tool | Status | Notes |
|---|---|---|---|
| Secret scanning | TruffleHog | ✅ Active | Every PR, verified secrets only |
| Python SAST | CodeQL + Bandit | ✅ Active | Every PR + weekly schedule |
| IaC scanning | Checkov + tfsec | ✅ Active | Every PR to terraform/ |
| Dependency updates | Dependabot | ✅ Active | Weekly pip + github-actions |
| Container CVE scan | Trivy | ✅ Active | Every release tag |
| Coverage gate | pytest-cov | ✅ Active | ≥55% required |

---

## Exceptions Summary

| ID | Resource | Risk | Expires | Type |
|---|---|---|---|---|
| EXC-001 | Key Vault | Low | 2026-06-22 | Temporary CI constraint |
| EXC-002 | Storage Account | Low | 2027-03-22 | Platform structural |
| EXC-003 | CosmosDB | Medium | 2027-03-22 | Platform structural |
| EXC-004 | CosmosDB | Low | 2026-12-31 | Code refactor pending |
| EXC-005 | CosmosDB | Low | 2027-03-22 | Cost constraint |
| EXC-006 | Function App | Low | 2027-03-22 | Platform structural |
| EXC-007 | App Service Plan | Info | 2027-03-22 | Platform structural |

**Highest risk**: EXC-003 (Medium) — CosmosDB public access. Mitigated by connection string in Key Vault and non-sensitive data classification.

---

## Secrets Compliance

| Secret | Storage | Rotation | Logged | Status |
|---|---|---|---|---|
| `TELEGRAM_TOKEN` | Key Vault | Annual | Never | ✅ |
| `RIOT_API_KEY` | Key Vault | Every 24h (manual) | Never | ✅ |
| `TELEGRAM_CHAT_ID` | Key Vault | Annual | Never | ✅ |
| `COSMOSDB_CONNECTION` | Key Vault | Annual | Never | ✅ |
| `ARM_CLIENT_SECRET` | GitHub Secrets | On rotation | Never | ✅ |

> `.env` file is excluded from git via `.gitignore`. Verified by TruffleHog on every PR.

---

## Remediation Roadmap

| Priority | Item | Effort | Cost Impact |
|---|---|---|---|
| P1 | EXC-001: OIDC federation for GitHub Actions (eliminates Key Vault firewall exception) | 2h | $0 |
| P2 | EXC-004: CosmosDB managed identity data plane (eliminates local auth) | 4h | $0 |
| P3 | EXC-002/003/006: Upgrade to EP1 Premium plan (enables VNet, private endpoints) | 1h | +~$150/month |
| P4 | EXC-005: Customer-managed keys for CosmosDB | 2h | +~$5/month |

---

*Generated by `compliance-report.yml` workflow. For exception details see [`exceptions-registry.json`](./exceptions-registry.json).*
