# Azure Public IP — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Public IP resources are direct internet exposure indicators. The baseline is intentionally restrictive and treats public IP allocation as a reviewed exception.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| PIP-001 | NS-2 | NS | Public IP used only when justified | Must | Yes | resource presence review |
| PIP-002 | NS-3 | NS | Standard SKU required | Must | Yes | `sku = "Standard"` |
| PIP-003 | NS-1 | NS | Resource associated with protected ingress control | Must | Partial | linked LB, AppGW, Firewall, or WAF |
| PIP-004 | LT-3 | LT | Changes and associations monitored | Must | Partial | activity logs |
| PIP-005 | PV-1 | PV | Idle or unattached public IPs removed | Should | Partial | inventory and governance |

## Control Detail Highlights

- `PIP-001`: The existence of a public IP should be treated as a first-order security signal and not as a neutral networking decision.
- `PIP-002`: Standard SKU should be the baseline because it provides the expected security posture for modern Azure networking patterns.
- `PIP-003`: A public IP should sit behind an intended ingress control, not expose a workload directly without compensating protections.
- `PIP-004`: Public IP attachment and detachment events matter because they can materially change exposure.
- `PIP-005`: Unattached public IPs are avoidable exposure artifacts and should be cleaned up through governance or automation.

## Agent Notes

- Public IP review is usually a correlated review of the entire ingress path, not the resource alone.
- If a public IP is present, document why it exists and which service boundary protects it.
- Inventory drift matters here because unused public IPs are easy to forget and hard to justify later.

## Suggested Validation Cases

- Secure: justified Standard SKU public IP attached to a protected ingress path with monitored changes.
- Insecure: Basic or unmanaged public IP, direct workload exposure, unattached addresses left in place.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure networking security baseline
