# Azure Event Hubs — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 2 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| EVH-001 | NS-2 | NS | Public network access disabled or restricted | High | Must | Yes | Namespace network settings |
| EVH-002 | NS-2 | NS | Private endpoint configured for production | High | Must | Partial | `azurerm_private_endpoint` |
| EVH-003 | IM-1 | IM | Local or SAS auth minimized in favor of RBAC | High | Must | Partial | Authorization rule review |
| EVH-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Namespace or hub diagnostics |
| EVH-005 | DP-5 | DP | Customer-managed keys where required | Medium | Should | Partial | CMK configuration |
| EVH-006 | DP-8 | DP | Capture or retention configured for recovery requirements | Medium | Should | Partial | Capture and retention settings |

---

## EVH-001 — Public Network Access Disabled or Restricted

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict public exposure of telemetry and event ingestion paths |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — production and shared namespaces |
| **Justification** | Event Hubs often carries internal telemetry, application events, or security data that should not rely on unrestricted public access |
| **Validation** | Restrict namespace network access and prefer private access for internal ingestion patterns |

## EVH-002 — Private Endpoint Configured for Production

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure private access paths |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production or private telemetry architectures |
| **Justification** | Private endpoints reduce unnecessary exposure of event ingestion services to the public internet |
| **Validation** | Deploy `azurerm_private_endpoint` for production namespaces and ensure the expected DNS path is in place |

## EVH-003 — Local or SAS Auth Minimized in Favor of RBAC

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Prefer centralized identity and least-privilege access |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — producers, consumers, and supporting services |
| **Justification** | Long-lived SAS credentials create avoidable credential sprawl and over-broad access patterns across telemetry pipelines |
| **Validation** | Prefer Entra-backed identities and RBAC, and minimize namespace authorization rules to the smallest necessary scope |

## EVH-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production namespaces |
| **Justification** | Namespace operations, auth failures, and service behavior need to be observable for both incident response and ingestion troubleshooting |
| **Validation** | Export Event Hubs diagnostics to Log Analytics or an approved SIEM destination |

## EVH-005 — Customer-Managed Keys Where Required

| Field | Detail |
|---|---|
| **MCSB** | DP-5 — Use customer-managed keys where customer key ownership is mandated |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — regulated or key-governed event pipelines |
| **Justification** | Some ingestion workloads require stronger customer control over encryption lifecycle and key revocation |
| **Validation** | Configure CMK-backed encryption and its supporting Key Vault and identity model where required |

## EVH-006 — Capture or Retention Configured for Recovery Requirements

| Field | Detail |
|---|---|
| **MCSB** | DP-8 — Preserve event recoverability and evidentiary retention |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — telemetry, audit, and business-event pipelines with replay or evidence requirements |
| **Justification** | Event retention and capture settings are part of security resilience when pipelines must be replayed, investigated, or retained |
| **Validation** | Configure retention and capture strategy appropriate to recovery and evidentiary needs |

---

## Agent Notes

- Review Event Hubs together with producer and consumer authentication design.
- Namespace authorization rules should be treated as high-risk objects because they can grant broad send or listen capability.
- If Event Hubs is part of the security telemetry path, diagnostics and resilience controls become more important, not less.

## Suggested Validation Cases

- Secure: restricted network access, private endpoints, RBAC-first auth, diagnostics enabled.
- Insecure: broad public access, unmanaged SAS use, no visibility into namespace activity.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Event Hubs security baseline
