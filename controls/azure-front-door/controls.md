# Azure Front Door — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 1 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| AFD-001 | NS-2 | NS | WAF policy associated with each public route | High | Must | Partial | Route-to-policy linkage |
| AFD-002 | DP-3 | DP | HTTPS enforced and HTTP redirected or disabled | High | Must | Partial | Route configuration |
| AFD-003 | NS-1 | NS | Origins locked down to Front Door only | High | Must | Partial | Origin ACL, header, or Private Link review |
| AFD-004 | LT-3 | LT | Access and WAF logs enabled | Medium | Must | Partial | Diagnostic settings |
| AFD-005 | IM-3 | IM | Certificates managed securely | High | Must | Partial | Managed certificate or Key Vault reference |

---

## AFD-001 — WAF Policy Associated with Each Public Route

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure internet-facing services with filtering controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all public Azure Front Door routes |
| **Justification** | Any unprotected route becomes a bypass path at the global edge and undermines the intended application protection model |
| **Validation** | Ensure each internet-facing route or endpoint is associated with an approved WAF policy |

## AFD-002 — HTTPS Enforced and HTTP Redirected or Disabled

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all public endpoints and routes |
| **Justification** | Leaving plaintext HTTP available weakens edge posture and allows inconsistent client behavior |
| **Validation** | Configure Front Door routes to require HTTPS and redirect or reject HTTP traffic |

## AFD-003 — Origins Locked Down to Front Door Only

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Maintain trusted traffic boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all protected backend origins |
| **Justification** | Front Door does not provide effective edge protection if the origin still accepts direct internet traffic |
| **Validation** | Restrict origins using Private Link, header validation, IP allowlists, or equivalent controls so traffic cannot bypass Front Door |

## AFD-004 — Access and WAF Logs Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production Front Door profiles |
| **Justification** | Edge access logs and WAF telemetry are required to investigate abuse, routing errors, rule behavior, and origin issues |
| **Validation** | Export access logs, WAF logs, and relevant metrics to Log Analytics or an approved SIEM sink |

## AFD-005 — Certificates Managed Securely

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Protect secret and certificate material |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all custom domains and TLS endpoints |
| **Justification** | Weak certificate handling introduces lifecycle and secret-management risk at the global edge |
| **Validation** | Use managed certificates or Key Vault-backed certificate material instead of unmanaged manual processes |

---

## Agent Notes

- Front Door is only part of the control story; the origin must also be protected against direct bypass.
- Review route-to-domain and route-to-origin mappings because exposure mistakes often happen in configuration joins rather than in a single resource.
- For high-value web apps, correlate Front Door with App Gateway, WAF, and private-origin patterns.

## Suggested Validation Cases

- Secure: WAF on all public routes, HTTPS enforced, origin isolated from direct traffic, diagnostics enabled.
- Insecure: public route without WAF, HTTP left open, origin still internet-reachable directly, missing logs.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Front Door security baseline
