# Azure Container Registry — Security Controls

> **MCSB Mapping** | **Severity:** 4 High / 2 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| ACR-001 | NS-2 | NS | Public network access disabled | High | Must | Yes | `public_network_access_enabled = false` |
| ACR-002 | IM-1 | IM | Admin user disabled | High | Must | Yes | `admin_enabled = false` |
| ACR-003 | NS-2 | NS | Private endpoint configured for production | High | Must | Partial | `azurerm_private_endpoint` |
| ACR-004 | LT-3 | LT | Diagnostic logging enabled | Medium | Must | Partial | `azurerm_monitor_diagnostic_setting` |
| ACR-005 | PV-5 | PV | Image scanning or Defender enabled | Medium | Should | Partial | Defender for Containers or registry posture |
| ACR-006 | IM-3 | IM | Pull access via managed identity and RBAC | High | Must | Partial | `AcrPull` role assignments |

---

## ACR-001 — Public Network Access Disabled

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Restrict network exposure of sensitive services |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — production and shared registries |
| **Justification** | Container registries are software supply-chain roots; broad public reachability increases the risk of unauthorized pull or abuse paths |
| **Validation** | Set `public_network_access_enabled = false` unless a documented architecture exception exists |

## ACR-002 — Admin User Disabled

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Use centralized identity and authorization |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all enterprise registries |
| **Justification** | The admin account is a shared credential pattern that bypasses stronger Entra ID and RBAC governance |
| **Validation** | Set `admin_enabled = false` and use Entra-backed identities for both push and pull workflows |

## ACR-003 — Private Endpoint Configured for Production

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure access paths to internal platforms |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Conditional — production or internal-only registries |
| **Justification** | Private endpoints reduce direct exposure of the registry control and data plane to the public internet |
| **Validation** | Deploy `azurerm_private_endpoint` for production registries and pair it with private DNS resolution where needed |

## ACR-004 — Diagnostic Logging Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all shared and production registries |
| **Justification** | Push, pull, delete, and authentication telemetry are essential to investigate supply-chain incidents and unexpected artifact changes |
| **Validation** | Export registry diagnostic settings to Log Analytics or an approved SIEM destination |

## ACR-005 — Image Scanning or Defender Enabled

| Field | Detail |
|---|---|
| **MCSB** | PV-5 — Manage vulnerability posture of deployed components |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all registries used by runtime platforms |
| **Justification** | Registry-side vulnerability findings provide an earlier signal in the image lifecycle before workloads are deployed |
| **Validation** | Enable Defender for Containers or an equivalent registry scanning posture with review ownership |

## ACR-006 — Pull Access via Managed Identity and RBAC

| Field | Detail |
|---|---|
| **MCSB** | IM-3 — Avoid embedded and shared secrets |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all runtime consumers of the registry |
| **Justification** | Username/password or shared secret access creates avoidable supply-chain credential risk across consuming workloads |
| **Validation** | Grant `AcrPull` or equivalent roles to managed identities and avoid embedded registry credentials in applications or pipelines |

---

## Agent Notes

- Review ACR together with the services that pull from it; image trust and pull authorization are one control chain.
- A secure registry still needs secure deployment consumers. Do not stop at the registry resource alone.
- Artifact deletion and overwrite patterns can be operationally disruptive and should be monitored.

## Suggested Validation Cases

- Secure: admin user disabled, private access path, diagnostics enabled, managed identity pulls, scanning enabled.
- Insecure: public registry, admin account enabled, opaque image provenance, no artifact activity logs.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Container Registry security baseline
