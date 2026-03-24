# Azure Monitor — Security Controls

> **MCSB Mapping** | **Severity:** 2 High / 4 Medium / 0 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|---|
| MON-001 | LT-3 | LT | Central Log Analytics workspace configured | Medium | Must | Partial | Workspace association |
| MON-002 | IM-1 | IM | Workspace access restricted with RBAC | High | Must | Partial | Role assignments |
| MON-003 | NS-2 | NS | Private Link used for sensitive telemetry ingestion or query | Medium | Should | Partial | AMPLS or private endpoint |
| MON-004 | LT-4 | LT | Retention aligned to incident response requirements | Medium | Must | Yes | Retention configuration |
| MON-005 | DP-2 | DP | Sensitive logs protected and export controlled | High | Must | Partial | Export rules and destination review |
| MON-006 | PV-1 | PV | Alerting enabled for critical posture signals | Medium | Should | Partial | Alerts, workbooks, or rules |

---

## MON-001 — Central Log Analytics Workspace Configured

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Centralize logging for monitoring and investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — subscriptions and landing zones using this framework |
| **Justification** | Fragmented telemetry reduces investigation quality, creates blind spots, and weakens cross-service correlation |
| **Validation** | Associate diagnostic settings and service logs with a central or intentionally governed set of Log Analytics workspaces |

## MON-002 — Workspace Access Restricted with RBAC

| Field | Detail |
|---|---|
| **MCSB** | IM-1 — Restrict access to security and operational telemetry |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all workspaces containing operational or security logs |
| **Justification** | Log data often contains infrastructure metadata, request content, secrets-by-observation, and incident evidence |
| **Validation** | Separate workspace readers, operators, and contributors through RBAC and avoid unnecessary broad access |

## MON-003 — Private Link Used for Sensitive Telemetry Ingestion or Query

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Protect sensitive data paths to monitoring systems |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — high-sensitivity or private-only telemetry environments |
| **Justification** | Some environments require telemetry ingestion and query traffic to remain on private paths rather than public service endpoints |
| **Validation** | Use Azure Monitor Private Link Scope, private endpoints, or equivalent private connectivity where required |

## MON-004 — Retention Aligned to Incident Response Requirements

| Field | Detail |
|---|---|
| **MCSB** | LT-4 — Preserve logs long enough for investigation and compliance |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all central monitoring workspaces |
| **Justification** | Retention that is too short makes security investigations and post-incident review incomplete or impossible |
| **Validation** | Configure retention explicitly rather than relying on defaults, and align it to incident response and regulatory requirements |

## MON-005 — Sensitive Logs Protected and Export Controlled

| Field | Detail |
|---|---|
| **MCSB** | DP-2 — Protect sensitive log data and downstream exports |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — workspaces and telemetry pipelines containing security or application logs |
| **Justification** | Export paths can become secondary data-exposure channels if logs are sent to weakly governed destinations |
| **Validation** | Review export rules, data collection destinations, and who can access downstream storage or SIEM sinks |

## MON-006 — Alerting Enabled for Critical Posture Signals

| Field | Detail |
|---|---|
| **MCSB** | PV-1 — Turn telemetry into actionable posture and security response |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — all environments where monitoring is relied on for security operations |
| **Justification** | Telemetry without alerting and ownership creates passive dashboards instead of operational security controls |
| **Validation** | Define alerts, workbooks, action groups, or equivalent rules for critical failure, security, and posture signals |

---

## Agent Notes

- Logging is a dependency for most other controls in this repository, so Monitor is foundational rather than optional.
- Review workspace RBAC and export destinations whenever sensitive logs are present.
- If data is exported, document where it goes and who can read it.

## Suggested Validation Cases

- Secure: central workspace, controlled RBAC, retention defined, export paths reviewed, critical alerts configured.
- Insecure: fragmented workspaces, overly broad reader access, short retention, uncontrolled log exports.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Monitor and Log Analytics security baseline
