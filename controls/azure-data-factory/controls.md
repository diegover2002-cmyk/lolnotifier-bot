# Azure Data Factory — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Data Factory orchestrates data movement and transformation. Its baseline focuses on managed identities, linked-service secret protection, private integration runtimes, and audit logging.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| ADF-001 | IM-1 | IM | Managed identity enabled | Must | Yes | identity block present |
| ADF-002 | IM-3 | IM | Linked service secrets stored in Key Vault | Must | Partial | Key Vault reference instead of plaintext |
| ADF-003 | NS-2 | NS | Managed virtual network or private endpoints used where needed | Must | Partial | private connectivity pattern |
| ADF-004 | LT-3 | LT | Diagnostic logging enabled | Must | Partial | factory diagnostics |
| ADF-005 | DP-3 | DP | Secure transport to sources and sinks | Must | Partial | connector configuration review |
| ADF-006 | PV-1 | PV | Defender recommendations monitored | Should | Partial | Defender posture evidence |

## Control Detail Highlights

- `ADF-001`: Managed identity should be the default for ADF interactions with Azure resources and downstream data services.
- `ADF-002`: Linked services are a common secret leak point and should use Key Vault-backed references rather than inline credentials.
- `ADF-003`: Internal data movement should use managed VNets, private endpoints, or equivalent private connectivity patterns.
- `ADF-004`: Pipeline, activity, and integration runtime telemetry should be centralized for operational and security review.
- `ADF-005`: The transport path to data sources and sinks must remain encrypted and explicitly reviewed for self-hosted or hybrid connectors.
- `ADF-006`: Defender and posture findings are useful because ADF is often a control plane over many higher-risk data systems.

## Agent Notes

- Treat ADF as a credential orchestration surface, not only as a data movement tool.
- Review the service together with linked services, integration runtimes, and destination systems.
- Self-hosted integration runtimes introduce extra host-hardening concerns outside the factory resource itself.

## Suggested Validation Cases

- Secure: managed identity, Key Vault-backed linked services, private data paths, diagnostics enabled.
- Insecure: plaintext secrets in linked services, public data paths where private access is expected, missing audit telemetry.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Data Factory security baseline
