# Azure Bastion — Security Controls

> **Status:** Expanded baseline on 2026-03-23 from repository control conventions.
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Service Scope

Azure Bastion provides managed RDP and SSH access to virtual machines without exposing management ports directly to the internet. The baseline centers on replacing public management exposure, enforcing segmentation, and preserving session visibility.

## Recommended Baseline Controls

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation |
|---|---|---|---|---|---|---|
| BAS-001 | NS-2 | NS | Bastion used instead of public RDP/SSH on VMs | Must | Partial | correlated VM and public IP review |
| BAS-002 | NS-1 | NS | Dedicated `AzureBastionSubnet` with correct sizing | Must | Yes | subnet naming and CIDR |
| BAS-003 | LT-3 | LT | Diagnostic logging enabled | Must | Partial | `azurerm_monitor_diagnostic_setting` |
| BAS-004 | IM-1 | IM | Access governed by RBAC and PIM | Must | Partial | role assignments outside resource code path |
| BAS-005 | NS-2 | NS | Standard SKU used for production | Should | Yes | `sku = "Standard"` |

## Control Detail Highlights

- `BAS-001`: Bastion only adds value if direct VM exposure is removed. Review related VMs and ensure there are no unnecessary public IPs or open 22/3389 rules.
- `BAS-002`: Bastion requires its own subnet with the reserved name. Undersized or misnamed subnets create fragile deployments and inconsistent policy behavior.
- `BAS-003`: Session and operational telemetry should be exported because administrative access paths are high-value evidence for incident review.
- `BAS-004`: Administrative access to Bastion should be controlled through RBAC and ideally privileged workflows such as PIM or JIT.
- `BAS-005`: Standard SKU should be the production default because it enables a stronger feature set and avoids treating a minimal deployment as the enterprise baseline.

## Agent Notes

- Bastion is a correlated control. Evaluate it together with VM network exposure, NSGs, and public IP allocation.
- The secure pattern is "Bastion plus no direct management ingress", not "Bastion plus existing public admin paths".
- Session access should align with identity governance rather than shared operator accounts.

## Suggested Validation Cases

- Secure: dedicated subnet, diagnostics enabled, Standard SKU, no public SSH/RDP path on protected VMs.
- Insecure: Bastion deployed but VMs still expose management ports publicly, no diagnostics, ad hoc admin permissions.

## Expansion Sources

- Microsoft Cloud Security Benchmark
- Azure Bastion security baseline
