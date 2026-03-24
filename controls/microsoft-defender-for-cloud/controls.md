# Microsoft Defender for Cloud — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Microsoft Defender for Cloud is a cross-cutting posture and threat-protection service. This file captures foundational controls for plan enablement, recommendation governance, and alert routing.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| MDC-001 | PV-1 | PV | Relevant Defender plans enabled for in-scope resources | Must | Partial | `azurerm_security_center_subscription_pricing` |
| MDC-002 | LT-1 | LT | Security alerts routed to monitored destination | Must | Partial | workflow automation or SIEM pattern |
| MDC-003 | PV-1 | PV | Secure Score and recommendations reviewed regularly | Must | No | operational evidence |
| MDC-004 | IM-1 | IM | Access to Defender findings restricted by RBAC | Must | Partial | role assignments |
| MDC-005 | LT-3 | LT | Continuous export configured where required | Should | Partial | export settings |
| MDC-006 | PV-5 | PV | Regulatory or compliance initiatives assigned where applicable | Should | Partial | policy initiative linkage |

## Control Detail Highlights

- `MDC-001`: Defender plans should be enabled for the services actually in scope, rather than broadly assumed or partially configured.
- `MDC-002`: Alerts need an owned response destination such as SIEM, ticketing, or workflow automation; otherwise they become passive noise.
- `MDC-003`: Secure Score and recommendation review are operating controls and need explicit ownership.
- `MDC-004`: Findings and posture data should be RBAC-scoped because they reveal security weaknesses across subscriptions.
- `MDC-005`: Continuous export should be enabled when central posture analytics or evidentiary retention require it.
- `MDC-006`: Regulatory initiatives should be tied to actual compliance requirements rather than enabled blindly.

## Agent Notes

- Defender for Cloud is not a single-resource service baseline in the same way as Storage or SQL; it is subscription and management-group scoped.
- Review plan coverage, export, and ownership together. An enabled plan with no response path is incomplete.
- Keep it separate from the deployable service catalog when reasoning about Azure resource baselines.

## Suggested Validation Cases

- Secure: relevant plans enabled, alerts routed, findings RBAC-scoped, review ownership defined.
- Insecure: partial plan coverage, no alert routing, open-ended access to findings, posture review with no owner.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Microsoft Defender for Cloud security baseline
