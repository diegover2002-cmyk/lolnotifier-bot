# Azure Private Link — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 1 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| PLS-001 | NS-2 | NS | Private endpoint used for sensitive PaaS services | High | Must | Partial | Custom |
| PLS-002 | NS-1 | NS | Private endpoint subnet governed by NSG or policy as applicable | High | Must | Partial | Custom |
| PLS-003 | NS-2 | NS | Public network access disabled on paired service where feasible | High | Must | Partial | Custom |
| PLS-004 | LT-3 | LT | Private endpoint connection events monitored | Medium | Should | Partial | Custom |
| PLS-005 | NS-1 | NS | Private DNS zones linked correctly | High | Must | Partial | Custom |

---

## PLS-001 — Private Endpoint Used for Sensitive PaaS Services

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Use private access paths for sensitive services |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production and internal-only services that expose sensitive data or control planes |
| **Justification** | Private Link is a foundational pattern for reducing internet exposure of PaaS data-plane traffic and management dependencies |
| **Validation Coverage** | Custom validation correlating the target PaaS resource, `azurerm_private_endpoint`, and intended service exposure model |

## PLS-002 — Private Endpoint Subnet Governed by NSG or Policy as Applicable

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Apply segmentation and governance to network boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all subnets hosting private endpoints, subject to service-specific policy support |
| **Justification** | Endpoint subnets can become unmanaged trust corridors if teams treat them as passive plumbing rather than governed network zones |
| **Validation Coverage** | Custom validation of subnet policy posture, NSG model, and documented exceptions for service-specific platform behavior |

## PLS-003 — Public Network Access Disabled on Paired Service Where Feasible

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Avoid leaving parallel public access paths open |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — target services that support disabling or tightly restricting public network access |
| **Justification** | A private endpoint without public exposure reduction is only a partial control and often leaves the primary attack path unchanged |
| **Validation Coverage** | Custom validation across the endpoint and paired service configuration, including public network access flags and firewall settings |

## PLS-004 — Private Endpoint Connection Events Monitored

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Observe connection approvals and lifecycle changes |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — shared and production private endpoint estates |
| **Justification** | Connection approvals, rejections, and state changes are operational and security-relevant events that support change control and incident review |
| **Validation Coverage** | Custom validation through activity logs, diagnostics, and documented monitoring of connection lifecycle events |

## PLS-005 — Private DNS Zones Linked Correctly

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Maintain correct name resolution inside private trust boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all private endpoint deployments that rely on private DNS resolution |
| **Justification** | Broken or missing private DNS linkage silently routes traffic back to public endpoints, undermining the intended private-access architecture |
| **Validation Coverage** | Custom validation of private DNS zone groups, VNet links, and endpoint-specific zone alignment |

---

## Agent Notes

- Private Link is a correlated control spanning the endpoint, DNS, subnet governance, and the paired service configuration.
- Do not document Private Link as complete unless the paired service also reduces public exposure where supported.
- Watch for endpoint sprawl and duplicate DNS patterns that create hard-to-audit connectivity paths.

## Suggested Validation Cases

- Secure: private endpoint deployed, paired service public access disabled or tightly restricted, DNS zones linked correctly, endpoint lifecycle events monitored.
- Insecure: endpoint exists but service remains broadly public, no private DNS linkage, unmanaged endpoint subnet, no monitoring of approvals or changes.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Private Link security baseline
