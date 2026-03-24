# Azure Container Instances — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Container Instances provides lightweight container execution. The main risks are uncontrolled public exposure, weak secret handling, and ungoverned image sources.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| ACI-001 | NS-2 | NS | Public IP disabled unless required | Must | Yes | `ip_address_type` or network profile |
| ACI-002 | IM-1 | IM | Managed identity enabled where supported | Should | Partial | identity configuration |
| ACI-003 | IM-3 | IM | Registry credentials not embedded in code | Must | Partial | secure image pull secret pattern |
| ACI-004 | PV-5 | PV | Images pulled from approved registry | Must | Partial | ACR or trusted registry only |
| ACI-005 | LT-3 | LT | Logs exported to centralized monitoring | Must | Partial | diagnostics or workspace linkage |

## Control Detail Highlights

- `ACI-001`: Publicly exposed container groups should be the exception, not the baseline.
- `ACI-002`: Use managed identity where supported to reduce embedded credentials and simplify downstream Azure access.
- `ACI-003`: Registry credentials should not live in code, templates, or long-lived variables.
- `ACI-004`: Image trust is central because ACI runs whatever image is pulled without a stronger surrounding platform boundary.
- `ACI-005`: Stdout, stderr, and control-plane events should be exported because ACI workloads are often ephemeral and difficult to reconstruct later.

## Agent Notes

- ACI is suitable for lightweight scenarios but should not be treated as a strongly isolated platform for high-sensitivity workloads without surrounding controls.
- Review image provenance and networking together; both are first-order risks for this service.
- If the container group is internet-facing, justify it explicitly in the service baseline.

## Suggested Validation Cases

- Secure: no public IP unless required, trusted registry source, centralized logs, credentials not embedded.
- Insecure: public container group by default, plaintext registry password, unapproved image source, no retained logs.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Container Instances security baseline
