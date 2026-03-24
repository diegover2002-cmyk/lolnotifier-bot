# Azure App Configuration — Security Controls

> **MCSB Mapping** | **Severity:** 3 High / 3 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| ACF-001 | NS-2 | NS | Public network access disabled | High | Must | Yes | Custom or needs verification |
| ACF-002 | NS-2 | NS | Private endpoint configured | High | Must | Partial | Custom |
| ACF-003 | IM-1 | IM | Local auth disabled where supported | Medium | Should | Partial | Needs verification |
| ACF-004 | DP-5 | DP | Customer-managed key where required | Medium | Should | Partial | Needs verification |
| ACF-005 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| ACF-006 | IM-3 | IM | Key Vault references used for secrets | High | Must | Partial | Custom |

---

## ACF-001 — Public Network Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict public access to configuration stores |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — production and internal application configuration stores |
| **Justification** | Configuration stores often hold high-value operational settings that can change runtime behavior without code changes |
| **Validation Coverage** | Treat as custom or `needs verification` until Checkov coverage is confirmed against the provider resource model in use |

## ACF-002 — Private Endpoint Configured

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Use private connectivity for internal-only service access |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production and regulated workloads |
| **Justification** | Private endpoints are the preferred production access path for internal applications and reduce unnecessary public exposure |
| **Validation Coverage** | Custom validation of paired private endpoint and store linkage |

## ACF-003 — Local Auth Disabled Where Supported

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Prefer centralized identity and RBAC |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — resource modes and capabilities that support the control directly |
| **Justification** | Key-based access should be minimized so applications consume configuration through managed identity and RBAC |
| **Validation Coverage** | Mark as `needs verification` until upstream rule and provider support are confirmed consistently |

## ACF-004 — Customer-Managed Key Where Required

| Field | Detail |
|---|---|
| **MCSB** | DP-5 — Use customer-managed keys where stricter encryption governance is required |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — regulated or key-governed workloads |
| **Justification** | CMK is a conditional hardening control for workloads with stronger key ownership requirements |
| **Validation Coverage** | Mark as `needs verification` until provider-level support and rule coverage are confirmed |

## ACF-005 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Log configuration changes and access patterns |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production configuration stores |
| **Justification** | Request and audit logs help explain runtime incidents and suspicious configuration changes |
| **Validation Coverage** | Custom validation of diagnostic-setting presence and expected category export |

## ACF-006 — Key Vault References Used for Secrets

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Keep secret values out of application configuration stores |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all stores carrying secret-like values |
| **Justification** | App Configuration should hold references to secrets, not the secrets themselves |
| **Validation Coverage** | Custom validation of Key Vault reference patterns and absence of plaintext secret values |

---

## Agent Notes

- Treat App Configuration and Key Vault as a paired pattern for secure settings and secret delivery.
- Review both data-plane exposure and the application authentication model when documenting this service.
- For this service, several controls are intentionally marked custom or `needs verification` rather than guessed as Checkov-covered.

## Suggested Validation Cases

- Secure: private endpoint, diagnostics enabled, managed identity consumers, Key Vault references for secret values.
- Insecure: public store access, local auth dependence, plaintext secrets or tokens stored as configuration values.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure App Configuration security baseline
- Existing repo patterns under `controls/azure-storage` and `controls/azure-key-vault`
