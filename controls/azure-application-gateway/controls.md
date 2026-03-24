# Azure Application Gateway — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 2 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| AGW-001 | NS-2 | NS | WAF enabled | High | Must | Yes | Known Checkov: `CKV_AZURE_120` |
| AGW-002 | NS-2 | NS | WAF in Prevention mode | High | Must | Yes | Known Checkov: `CKV_AZURE_122` |
| AGW-003 | DP-3 | DP | TLS 1.2+ enforced | High | Must | Partial | Custom or needs verification |
| AGW-004 | LT-3 | LT | Diagnostic and access logs enabled | Medium | Must | Partial | Custom |
| AGW-005 | IM-3 | IM | Certificates sourced from Key Vault | High | Must | Partial | Custom |
| AGW-006 | NS-2 | NS | Public frontend only when required | Medium | Should | Yes | Custom |

---

## AGW-001 — WAF Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure internet-facing services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — internet-facing application gateways |
| **Justification** | Application Gateway without WAF leaves the web edge without the intended request inspection and rule enforcement layer |
| **Validation Coverage** | Known Checkov mapping in repo matrix: `CKV_AZURE_120` |

## AGW-002 — WAF in Prevention Mode

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Enforce active filtering at the web edge |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — production internet-facing application gateways |
| **Justification** | Detection-only mode provides visibility but not enforcement; production web edges should block known malicious patterns by default |
| **Validation Coverage** | Known Checkov mapping in repo matrix: `CKV_AZURE_122` |

## AGW-003 — TLS 1.2+ Enforced

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — listeners and TLS policy on application gateways |
| **Justification** | Weak or legacy TLS settings expose public applications to downgrade and compatibility risk at the edge |
| **Validation Coverage** | Treat as custom validation unless a verified Checkov rule is confirmed upstream |

## AGW-004 — Diagnostic and Access Logs Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production application gateways |
| **Justification** | Access, performance, and WAF logs are often the primary evidence source for web ingress incidents |
| **Validation Coverage** | Custom validation through diagnostic-setting presence and category coverage |

## AGW-005 — Certificates Sourced from Key Vault

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Protect secret and certificate material |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all TLS-enabled listeners using customer-managed certificates |
| **Justification** | Inline or manually managed certificate material creates rotation, governance, and secret-handling risk |
| **Validation Coverage** | Custom validation of Key Vault references and certificate sourcing model |

## AGW-006 — Public Frontend Only When Required

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Limit public exposure to justified ingress scenarios |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — architectures where internal-only ingress is viable |
| **Justification** | Public frontends should be architectural decisions, not defaults, especially for internal applications and APIs |
| **Validation Coverage** | Custom validation based on public IP presence and documented exposure intent |

---

## Agent Notes

- Correlate Application Gateway posture with WAF, subnets, NSGs, Key Vault, and the protected backend service.
- For internet-facing workloads, review WAF enablement and prevention mode together.
- The current repo has known Checkov coverage for WAF presence and prevention mode, but other controls still need custom validation or upstream confirmation.

## Suggested Validation Cases

- Secure: `WAF_v2`, prevention mode, modern TLS policy, diagnostics enabled, certificate from Key Vault, private frontend where possible.
- Insecure: Standard or non-WAF edge, detection-only mode in production, unmanaged certificate material, missing diagnostics.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Application Gateway security baseline
- AKS ingress guidance already referenced in this repo
