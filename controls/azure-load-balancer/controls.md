# Azure Load Balancer — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Load Balancer distributes Layer 4 traffic. The baseline focuses on limiting public exposure, constraining backend pools, and pairing the load balancer with subnet or NIC security controls.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| ALB-001 | NS-2 | NS | Public load balancer used only when required | Must | Yes | public frontend config review |
| ALB-002 | NS-1 | NS | Backend pool limited to intended workloads | Must | Partial | backend pool membership |
| ALB-003 | NS-2 | NS | NSGs enforce inbound restrictions on backend subnets or NICs | Must | Partial | correlated network review |
| ALB-004 | LT-3 | LT | Diagnostic logging enabled | Must | Partial | load balancer diagnostics |
| ALB-005 | NS-3 | NS | DDoS protection considered for public ingress VNets | Should | Partial | VNet-level control |

## Control Detail Highlights

- `ALB-001`: A public frontend should be treated as a controlled exception rather than the default deployment pattern.
- `ALB-002`: Backend pools should contain only the intended workload members so accidental exposure or shared blast radius is minimized.
- `ALB-003`: Azure Load Balancer is not a security boundary by itself. NSGs remain the enforcement layer for backend traffic.
- `ALB-004`: Logging and platform telemetry help correlate health probe changes, configuration updates, and frontend issues.
- `ALB-005`: Public ingress VNets should consider DDoS protections at the network level when the service is critical or internet-facing.

## Agent Notes

- Always correlate load balancer posture with the associated public IP, NSG design, and backend subnet controls.
- A "secure" load balancer often depends more on surrounding network design than on the resource alone.
- Avoid treating health probes as benign metadata; overly permissive probes can reveal unnecessary backend surfaces.

## Suggested Validation Cases

- Secure: justified public frontend, tightly scoped backend pool, NSGs in place, diagnostics enabled.
- Insecure: public frontend with permissive backend exposure, no NSG correlation, shared backends for unrelated services.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Load Balancer security baseline
