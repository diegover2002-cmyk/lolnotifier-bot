# Azure Service Bus — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 2 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| ASB-001 | NS-2 | NS | Public network access disabled or restricted | High | Must | Yes | Namespace network settings |
| ASB-002 | NS-2 | NS | Private endpoint configured for production | High | Must | Partial | `azurerm_private_endpoint` |
| ASB-003 | IM-1 | IM | RBAC preferred over long-lived SAS keys | High | Must | Partial | Authorization rule review |
| ASB-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Namespace diagnostics |
| ASB-005 | DP-5 | DP | Customer-managed keys where required | Medium | Should | Partial | CMK configuration |
| ASB-006 | DP-8 | DP | Geo-disaster recovery or resilience pattern defined | Medium | Should | Partial | Alias or replication strategy |

---

## ASB-001 — Public Network Access Disabled or Restricted

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict public exposure of messaging services |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all production namespaces |
| **Justification** | Messaging namespaces often carry internal and business-critical traffic. Broad public exposure increases risk without adding architectural value in most enterprise cases |
| **Validation** | Restrict public network access through namespace network settings and prefer private connectivity where possible |

## ASB-002 — Private Endpoint Configured for Production

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure private access paths |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production or internal-only messaging fabrics |
| **Justification** | Private endpoints reduce control-plane and data-plane exposure for systems that should stay inside trusted network boundaries |
| **Validation** | Deploy `azurerm_private_endpoint` for production namespaces and pair it with the expected DNS and VNet path |

## ASB-003 — RBAC Preferred over Long-Lived SAS Keys

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authorization |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all producers, consumers, and administrative integrations |
| **Justification** | SAS rules are shared credentials with broad blast radius and weak lifecycle control compared to Entra ID and RBAC |
| **Validation** | Minimize namespace authorization rules and prefer Entra-backed sender or receiver identities wherever supported |

## ASB-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all shared and production namespaces |
| **Justification** | Authentication failures, management operations, and service behavior need to be visible for both incident response and operational diagnosis |
| **Validation** | Export Service Bus diagnostics to Log Analytics or an approved SIEM sink |

## ASB-005 — Customer-Managed Keys Where Required

| Field | Detail |
|---|---|
| **MCSB** | DP-5 — Use customer-managed keys when regulatory posture requires it |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — regulated or customer-key-mandated namespaces |
| **Justification** | Some messaging workloads require explicit customer ownership of encryption lifecycle rather than platform-managed defaults |
| **Validation** | Enable CMK-backed encryption and document associated Key Vault and identity dependencies where required |

## ASB-006 — Geo-Disaster Recovery or Resilience Pattern Defined

| Field | Detail |
|---|---|
| **MCSB** | DP-8 — Preserve recoverability and continuity of critical message paths |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — critical business workflows and integration backbones |
| **Justification** | Messaging resilience should be explicit. Namespace aliasing, failover, and recovery expectations should not be left as implicit platform assumptions |
| **Validation** | Define and document alias-based disaster recovery, paired-region strategy, or equivalent resilience pattern |

---

## Agent Notes

- Review Service Bus together with sender and receiver authentication patterns.
- Namespace auth rules and queue or topic ownership boundaries are part of the security baseline.
- For critical workflows, resilience and security controls interact closely because message loss and compromise can have similar business impact.

## Suggested Validation Cases

- Secure: restricted network path, private endpoints, RBAC-first auth model, diagnostics enabled, resilience design documented.
- Insecure: open namespace, unmanaged SAS proliferation, no logging, no defined failover pattern.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Service Bus security baseline
