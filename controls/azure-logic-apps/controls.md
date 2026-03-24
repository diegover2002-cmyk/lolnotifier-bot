# Azure Logic Apps — Security Controls

> **MCSB Mapping** | **Severity:** 3 High / 2 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation Coverage |
|---|---|---|---|---|---|---|---|
| LGA-001 | IM-1 | IM | Managed identity enabled | High | Must | Yes | Needs verification |
| LGA-002 | IM-3 | IM | Connector secrets stored in Key Vault | High | Must | Partial | Custom |
| LGA-003 | NS-2 | NS | Standard Logic Apps use private networking where required | Medium | Should | Partial | Needs verification |
| LGA-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | Custom |
| LGA-005 | DP-3 | DP | Secure transport to downstream systems | High | Must | Partial | Custom |

---

## LGA-001 — Managed Identity Enabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and avoid unmanaged credentials |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all Logic Apps that access Azure resources or supported connectors |
| **Justification** | Logic Apps often orchestrate privileged automation. Managed identity removes stored credentials and makes downstream authorization auditable through RBAC |
| **Validation Coverage** | Needs verification against provider and policy coverage; keep as an explicit baseline requirement even when validation is custom today |

## LGA-002 — Connector Secrets Stored in Key Vault

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Protect application identities, secrets, and connection material |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — any workflow using connector secrets, API keys, or service credentials |
| **Justification** | Workflow parameters and connection definitions are common secret-leak paths in serverless integration platforms |
| **Validation Coverage** | Custom validation of parameter sources, Key Vault references, and absence of plaintext secret values in workflow definitions |

## LGA-003 — Standard Logic Apps Use Private Networking Where Required

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict network exposure for integration workloads |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — Logic Apps Standard handling internal systems, regulated data, or private-only dependencies |
| **Justification** | Logic Apps frequently bridge trusted systems. Standard hosting should use VNet integration and private endpoints when workflows are not intended to be public |
| **Validation Coverage** | Needs verification for exact automated rule coverage; validate through App Service plan, private endpoint, and VNet integration pattern review |

## LGA-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for orchestration and security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all shared and production workflows |
| **Justification** | Run history, trigger failures, and management operations are often the primary evidence trail when Logic Apps automate access to sensitive systems |
| **Validation Coverage** | Custom validation through diagnostic settings and workflow telemetry destination review |

## LGA-005 — Secure Transport to Downstream Systems

| Field | Detail |
|---|---|
| **MCSB** | DP-3 — Encrypt data in transit across integration hops |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all connectors, webhooks, and downstream system calls |
| **Justification** | Logic Apps extend trust boundaries across many destinations. Weak transport settings or non-HTTPS endpoints weaken the entire automation chain |
| **Validation Coverage** | Custom validation of connector configuration, endpoint schemes, and approved trust boundaries |

---

## Agent Notes

- Treat Logic Apps as privileged integration control planes, not as low-risk workflow glue.
- Document whether the workload is Consumption or Standard because network and identity options differ materially.
- Review connectors and downstream trust paths together; the workflow definition alone is not the full security surface.

## Suggested Validation Cases

- Secure: managed identity, Key Vault-backed connection secrets, diagnostics enabled, private networking for Standard workflows that handle sensitive systems, HTTPS-only downstream endpoints.
- Insecure: plaintext connector credentials, unmanaged service principals, public exposure for internal workflows, no run-history telemetry.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Logic Apps security baseline
