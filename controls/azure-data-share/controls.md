# Azure Data Share — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Data Share governs cross-subscription and cross-tenant sharing of data assets. The baseline is centered on outbound sharing control, tenant boundaries, and traceability.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| ADS-001 | NS-1 | NS | Cross-tenant sharing limited to approved scenarios | Must | Partial | business approval and config review |
| ADS-002 | IM-1 | IM | Access governed by RBAC | Must | Partial | role assignments |
| ADS-003 | LT-3 | LT | Diagnostic logging enabled | Must | Partial | share account diagnostics |
| ADS-004 | DP-2 | DP | Shared datasets classified before publication | Must | No | process and evidence control |
| ADS-005 | DP-8 | DP | Revocation process defined for active shares | Should | No | operational control |

## Control Detail Highlights

- `ADS-001`: Cross-tenant data sharing should be explicitly approved and never treated as a convenience default.
- `ADS-002`: RBAC should constrain who can publish, invite, accept, or revoke shares.
- `ADS-003`: Share invitations, acceptance, and usage events should be logged to support audit and partner review.
- `ADS-004`: Data owners should classify or label the dataset before publication so sharing decisions are anchored in data sensitivity.
- `ADS-005`: Revocation should be operationally defined because long-lived external shares drift into unmanaged exposure quickly.

## Agent Notes

- Data Share is as much a governance control as a technical one.
- When documenting a share pattern, capture the tenant boundary and who approved it.
- Pair this service with classification and data-owner workflows rather than relying on Terraform alone.

## Suggested Validation Cases

- Secure: RBAC-limited administration, logged sharing activity, explicit approval for external recipients.
- Insecure: undocumented cross-tenant shares, unclear ownership, no revocation path for active consumers.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Data Share security baseline
