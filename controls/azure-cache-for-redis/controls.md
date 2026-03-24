# Azure Cache for Redis — Security Controls

> **MCSB Mapping** | **Severity:** 3 High / 3 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| RED-001 | DP-3 | DP | Non-TLS port disabled | High | Must | Yes | Custom or needs verification |
| RED-002 | NS-2 | NS | Private endpoint or restricted network access | High | Must | Partial | Custom |
| RED-003 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| RED-004 | DP-5 | DP | Customer-managed key where required | Medium | Should | Partial | Needs verification |
| RED-005 | IM-3 | IM | Access keys rotated and minimized | Medium | Should | Partial | Process and custom control |
| RED-006 | PV-1 | PV | Defender recommendations monitored | High | Should | Partial | Custom posture control |

---

## RED-001 — Non-TLS Port Disabled

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt cache traffic in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all caches |
| **Justification** | Plaintext Redis connectivity is unacceptable for services that often hold sessions, tokens, and transient authorization state |
| **Validation Coverage** | Treat as custom or `needs verification` until an upstream Checkov mapping is explicitly confirmed for the resource variant in use |

## RED-002 — Private Endpoint or Restricted Network Access

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict access to internal-only data stores |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production and high-sensitivity caches |
| **Justification** | Production caches should prefer private connectivity or very restrictive network paths rather than default public access |
| **Validation Coverage** | Custom validation of private endpoint presence or equivalent restricted network configuration |

## RED-003 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logs for security and operational analysis |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production caches |
| **Justification** | Cache diagnostics help correlate performance anomalies, failed auth, and abusive access patterns |
| **Validation Coverage** | Custom validation of diagnostic-setting export to approved monitoring destinations |

## RED-004 — Customer-Managed Key Where Required

| Field | Detail |
|---|---|
| **MCSB** | DP-5 — Use customer-managed keys when encryption governance requires it |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — enterprise or regulated cache workloads |
| **Justification** | CMK is relevant for workloads with stricter key ownership and revocation requirements |
| **Validation Coverage** | Mark as `needs verification` until provider and rule coverage are confirmed for the relevant Redis tier |

## RED-005 — Access Keys Rotated and Minimized

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Avoid long-lived shared secret dependency |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all caches using access keys |
| **Justification** | Redis keys are high-risk shared secrets and should be rotated through controlled processes rather than treated as static credentials |
| **Validation Coverage** | Process and custom control; not a reliable static IaC check by itself |

## RED-006 — Defender Recommendations Monitored

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Monitor posture findings for exposed or weakly configured caches |
| **Severity** | High |
| **Priority** | Should |
| **Applies** | Yes — all production caches |
| **Justification** | Redis misconfigurations can expose authentication and state data quickly, so posture findings should be owned and reviewed |
| **Validation Coverage** | Custom posture control rather than a direct deployable-resource rule |

---

## Agent Notes

- Redis often sits behind application layers, so exposure is easy to underestimate.
- Review application secret handling together with Redis authentication and key rotation.
- For this service, prefer `Custom` or `Needs verification` labels over guessing Checkov coverage.

## Suggested Validation Cases

- Secure: non-SSL port disabled, private access path, diagnostics enabled, controlled key lifecycle.
- Insecure: plaintext port enabled, public access without restriction, stale keys reused across applications.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Cache for Redis security baseline
