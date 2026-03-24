# Azure Event Grid — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 1 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| EVG-001 | IM-1 | IM | Managed identity or Entra auth used where supported | High | Must | Partial | Needs verification |
| EVG-002 | NS-2 | NS | Webhook and destination endpoints restricted | High | Must | Partial | Custom |
| EVG-003 | DP-3 | DP | HTTPS-only event delivery | High | Must | Partial | Custom |
| EVG-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| EVG-005 | NS-1 | NS | Private Link used for sensitive event domains where supported | High | Should | Partial | Needs verification |

---

## EVG-001 — Managed Identity or Entra Auth Used Where Supported

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Prefer centralized identity over shared secrets |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — topics, domains, and delivery paths that support Entra identity or managed identity integration |
| **Justification** | Event routing often spans multiple trust boundaries. Identity-based delivery reduces credential sprawl and clarifies authorization ownership |
| **Validation Coverage** | Needs verification for exact automated rule coverage; maintain as baseline policy and validate through subscription and destination auth model review |

## EVG-002 — Webhook and Destination Endpoints Restricted

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Limit outbound trust paths to approved endpoints |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all webhook, function, and external destination subscriptions |
| **Justification** | Event Grid subscriptions define outbound trust. Unrestricted destinations can exfiltrate data or create ungoverned integration paths |
| **Validation Coverage** | Custom validation of approved destination patterns, endpoint allowlists, and review of external webhook targets |

## EVG-003 — HTTPS-Only Event Delivery

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Protect event payloads in transit |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all event subscriptions that deliver over HTTP-based endpoints |
| **Justification** | Event payloads frequently carry metadata or business signals that should not traverse clear-text or weakly trusted transport |
| **Validation Coverage** | Custom validation of destination schemes, secure transport assumptions, and rejection of non-HTTPS webhook patterns |

## EVG-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Capture operational and security evidence for event routing |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — custom topics, domains, and system topics used in shared or production environments |
| **Justification** | Delivery failures, subscription changes, and management events are central to both troubleshooting and security review of event-driven systems |
| **Validation Coverage** | Custom validation through Event Grid diagnostic settings and central log destination review |

## EVG-005 — Private Link Used for Sensitive Event Domains Where Supported

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Prefer private routing for sensitive event domains where platform support exists |
| **Severity** | High |
| **Priority** | Should |
| **Applies** | Conditional — workloads with sensitive publishers, subscribers, or internal-only event fabrics |
| **Justification** | Some event-driven systems should stay on private paths rather than using public service endpoints, but platform support and deployment shape vary by Event Grid feature |
| **Validation Coverage** | Needs verification for exact service variants and enforceable rule coverage; validate through design review and supported private connectivity patterns |

---

## Agent Notes

- Review Event Grid subscriptions as outbound trust rules, not just delivery plumbing.
- Authentication, destination restriction, and logging matter more than the topic resource alone.
- Distinguish custom topics, system topics, domains, and newer Event Grid patterns when assessing applicability.

## Suggested Validation Cases

- Secure: identity-based delivery where supported, approved HTTPS destinations only, diagnostics enabled, private access used for sensitive event domains.
- Insecure: broad external webhooks, shared secrets with weak governance, no telemetry for delivery failures or subscription changes.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Event Grid security baseline
