# Azure Container Apps — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Container Apps hosts containerized workloads with managed ingress and revision support. The baseline focuses on ingress restriction, managed identity, secret handling, and telemetry.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| ACA-001 | NS-2 | NS | External ingress disabled unless explicitly required | Must | Yes | ingress `external_enabled = false` by default |
| ACA-002 | IM-1 | IM | Managed identity enabled | Must | Yes | identity block present |
| ACA-003 | IM-3 | IM | Secrets not hardcoded in template or env | Must | Partial | secret refs or Key Vault integration |
| ACA-004 | LT-3 | LT | Diagnostic logging enabled | Must | Partial | environment or app diagnostics |
| ACA-005 | NS-2 | NS | Environment integrated with private networking where needed | Should | Partial | managed environment VNet pattern |
| ACA-006 | PV-5 | PV | Images sourced from approved registry | Must | Partial | ACR allowlist or image provenance |

## Control Detail Highlights

- `ACA-001`: Internal-only ingress should be the default for APIs and backend workloads. Public exposure must be deliberate.
- `ACA-002`: Managed identity should be used for downstream Azure access and, where applicable, registry pull workflows.
- `ACA-003`: Secrets should come from Key Vault or managed secret stores, not inline environment variables or template literals.
- `ACA-004`: Logs and revision telemetry are required to investigate ingress misuse, rollout drift, and runtime failures.
- `ACA-005`: Private networking becomes important when the app consumes internal databases, messaging, or restricted PaaS services.
- `ACA-006`: Image provenance matters because Container Apps depends directly on the trustworthiness of the pulled container image.

## Agent Notes

- Review Container Apps together with the managed environment, ingress mode, identity model, and registry source.
- Treat revision and rollout features as operationally useful but security-relevant because they can retain old configurations and secrets.
- If the app is internet-facing, correlate this service with Front Door, App Gateway, or WAF controls.

## Suggested Validation Cases

- Secure: internal ingress by default, managed identity, approved registry, centralized diagnostics, secrets not embedded inline.
- Insecure: public ingress without justification, plaintext secrets in env vars, untrusted image sources, missing telemetry.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Container Apps security baseline
