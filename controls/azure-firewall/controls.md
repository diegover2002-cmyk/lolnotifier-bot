# Azure Firewall — Security Controls

> **MCSB Mapping** | **Severity:** 2 High / 4 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| AFW-001 | NS-2 | NS | Firewall policy used instead of ad hoc local rules | High | Must | Yes | Firewall Policy attachment |
| AFW-002 | NS-1 | NS | Rule collections follow deny-by-default model | High | Must | Partial | Policy review |
| AFW-003 | LT-3 | LT | Application, network, and threat logs enabled | Medium | Must | Partial | Diagnostic settings |
| AFW-004 | NS-3 | NS | Threat intelligence mode enabled | Medium | Should | Yes | `threat_intel_mode` |
| AFW-005 | NS-2 | NS | Forced tunneling or egress inspection used where required | Medium | Should | Partial | Topology and routing review |
| AFW-006 | PV-1 | PV | Premium TLS inspection considered for high-risk workloads | Medium | Should | Partial | SKU and policy capabilities |

---

## AFW-001 — Firewall Policy Used Instead of Local Rules

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Azure Firewall deployments |
| **Justification** | Resource-local rule drift makes review, reuse, and governance inconsistent across hubs and landing zones |
| **Validation** | Attach the firewall to a shared `azurerm_firewall_policy` rather than depending on ad hoc local rule definitions |

## AFW-002 — Rule Collections Follow Deny-by-Default Model

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Azure Firewall policy rule collections |
| **Justification** | Broad allow-any rules collapse segmentation and reduce the firewall to a logging hop instead of an enforcement control |
| **Validation** | Review rule collections for explicit allow intent, narrow destinations, and absence of structural any-any exceptions |

## AFW-003 — Application, Network, and Threat Logs Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all production and shared-platform firewalls |
| **Justification** | Azure Firewall is often the primary evidence source for egress, ingress, and threat-intel decisions; missing logs undermine both security and troubleshooting |
| **Validation** | Export application rule, network rule, DNS proxy, and threat intelligence logs to Log Analytics or an approved SIEM destination |

## AFW-004 — Threat Intelligence Mode Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-3 — Control network traffic with threat-aware protections |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — internet-connected or shared egress firewalls |
| **Justification** | Threat intelligence mode adds Microsoft-curated reputation and known-bad destination handling that improves the baseline without changing application architecture |
| **Validation** | Set `threat_intel_mode` to an enabled state appropriate for the workload, typically block or alert as policy requires |

## AFW-005 — Forced Tunneling or Egress Inspection Used Where Required

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure outbound service access paths |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — environments where egress control is the design objective |
| **Justification** | A firewall that is not on the effective route path does not enforce outbound security intent, even if the resource exists |
| **Validation** | Confirm UDRs, hub-spoke routing, or forced tunneling patterns send intended traffic through the firewall |

## AFW-006 — Premium TLS Inspection Considered for High-Risk Workloads

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Strengthen posture for sensitive workloads |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — regulated or high-risk egress scenarios |
| **Justification** | Encrypted outbound traffic can hide malicious destinations or unsafe patterns that basic layer-3 and layer-4 controls cannot inspect |
| **Validation** | Evaluate Firewall Premium capabilities, certificate management, and policy readiness where encrypted traffic visibility is a requirement |

---

## Agent Notes

- Evaluate Azure Firewall together with route tables, hub-spoke topology, public IP usage, and the workloads whose traffic should traverse it.
- A firewall deployment without deterministic routing is not an effective control.
- Prefer one centralized policy model over resource-local rule drift.

## Suggested Validation Cases

- Secure: shared Firewall Policy, diagnostics enabled, no broad allow-any collections, routing forces intended traffic through the firewall.
- Insecure: local unmanaged rules, no logs, public egress paths bypassing the firewall entirely.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Firewall security baseline
