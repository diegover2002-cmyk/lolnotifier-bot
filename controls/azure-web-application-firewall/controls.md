# Azure Web Application Firewall — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

This document covers Azure WAF deployments attached to Application Gateway or Front Door. The baseline concentrates on prevention mode, managed rule sets, logging, and exception governance.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| WAF-001 | NS-2 | NS | WAF enabled in prevention mode for production | Must | Yes | `firewall_mode = "Prevention"` |
| WAF-002 | NS-2 | NS | OWASP managed rule set enabled and current | Must | Yes | rule set type and version |
| WAF-003 | LT-3 | LT | WAF logs enabled | Must | Partial | diagnostics |
| WAF-004 | NS-1 | NS | Custom rules and exclusions reviewed and minimal | Must | Partial | policy review |
| WAF-005 | PV-1 | PV | Rule tuning process documented to avoid silent bypass | Should | No | process and evidence control |

## Control Detail Highlights

- `WAF-001`: Prevention mode should be the production default. Detection mode is acceptable only during limited tuning windows.
- `WAF-002`: Managed rules must be enabled and kept current enough to avoid an effectively stale edge protection layer.
- `WAF-003`: WAF logs are required if the service is meant to provide attack visibility, not only blocking.
- `WAF-004`: Every exclusion or disabled rule should have a traceable justification because broad exclusions become silent bypass channels.
- `WAF-005`: Tuning is a lifecycle process, not a one-time deployment setting. Without governance, exceptions tend to accumulate without review.

## Agent Notes

- Review WAF together with the service it protects. A WAF policy with no route or listener attachment is not an effective control.
- Distinguish between temporary tuning exceptions and accepted permanent exclusions.
- Keep managed rules, custom rules, and exclusions readable enough for later audit and incident analysis.

## Suggested Validation Cases

- Secure: prevention mode, active managed rules, exported diagnostics, minimal exclusions with justification.
- Insecure: detection-only in production, unmanaged exclusions, missing logs, stale or partial policy attachment.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure WAF security baseline
