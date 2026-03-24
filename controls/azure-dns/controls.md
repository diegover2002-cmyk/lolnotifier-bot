# Azure DNS — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure DNS provides public and private name resolution. The main security goals are change control, least privilege over zones, and protection of records that steer traffic to sensitive services.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| DNS-001 | IM-1 | IM | Zone management restricted with RBAC | Must | Partial | role assignments |
| DNS-002 | LT-3 | LT | Activity logging enabled and retained | Must | Partial | subscription and activity log coverage |
| DNS-003 | NS-1 | NS | Private DNS used for private endpoint resolution | Should | Partial | private DNS zone linkage |
| DNS-004 | DP-3 | DP | DNSSEC or equivalent integrity protection where available | Should | Partial | service capability dependent |
| DNS-005 | PV-1 | PV | Critical public records protected by change review | Must | No | workflow and evidence control |

## Control Detail Highlights

- `DNS-001`: DNS zone ownership should be tightly scoped. A small number of identities can redirect all application traffic if zone access is too broad.
- `DNS-002`: DNS changes should be visible in retained audit logs so record changes can be traced during outage and incident response.
- `DNS-003`: Private endpoints need matching private DNS design. Without it, workloads may silently resolve public endpoints and bypass the intended private path.
- `DNS-004`: DNS integrity controls should be enabled where the service and resolver path support them.
- `DNS-005`: High-impact records such as apex records, MX, TXT, and public CNAME entries should be subject to explicit review, not casual edits.

## Agent Notes

- Treat DNS as a traffic control plane, not as low-risk metadata.
- Evaluate public and private DNS responsibilities separately because their access and blast radius differ.
- When documenting a private-link pattern, include the DNS dependency as part of the same baseline.

## Suggested Validation Cases

- Secure: RBAC-limited zone ownership, audited changes, private zones linked to the correct VNets.
- Insecure: broad contributor access, unmanaged public records, private endpoints without matching DNS integration.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure DNS security baseline
