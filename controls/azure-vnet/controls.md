# Azure Virtual Network — Security Controls

> **MCSB Mapping** | **Severity:** 5 High / 4 Medium / 1 Low
> **Back to matrix:** [MCSB-control-matrix.md](../MCSB-control-matrix.md)

---

## Controls Summary

| Control ID | MCSB | Domain | Control Name | Severity | Priority | IaC Checkable | Checkov Rule |
|---|---|---|---|---|---|---|---|
| VN-001 | NS-1 | NS | Subnets associated with NSG | High | Must | Yes | `CKV2_AZURE_31` |
| VN-002 | NS-1 | NS | NSG default deny inbound | High | Must | Yes | Custom |
| VN-003 | NS-2 | NS | No unrestricted inbound SSH (22) | High | Must | Yes | `CKV_AZURE_10` |
| VN-004 | NS-2 | NS | No unrestricted inbound RDP (3389) | High | Must | Yes | `CKV_AZURE_9` |
| VN-005 | NS-3 | NS | DDoS protection enabled | Medium | Should | Yes | `CKV_AZURE_182` |
| VN-006 | NS-4 | NS | Network Watcher enabled | Medium | Must | Partial | Custom |
| VN-007 | LT-3 | LT | NSG flow logs enabled | Medium | Must | Partial | `CKV_AZURE_12` |
| VN-008 | NS-2 | NS | No wildcard inbound rules (any/any) | High | Must | Yes | Custom |
| VN-009 | NS-7 | NS | Service endpoints scoped to subnet | Medium | Should | Yes | Custom |
| VN-010 | NS-1 | NS | Subnets not overly broad (/8, /16) | Low | Nice | Partial | Custom |

---

## VN-001 — Subnets Associated with NSG

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all subnets except gateway subnets |
| **Justification** | Subnets without an NSG have no traffic filtering. Any resource deployed into an unprotected subnet is reachable from within the VNet without restriction |
| **Checkov** | `CKV2_AZURE_31` |

```hcl
# Insecure — subnet with no NSG association
resource "azurerm_subnet" "bad" {
  name                 = "subnet-bad"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Secure
resource "azurerm_subnet" "good" {
  name                 = "subnet-good"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet_network_security_group_association" "good" {
  subnet_id                 = azurerm_subnet.good.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}
```

---

## VN-002 — NSG Default Deny Inbound

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all NSGs |
| **Justification** | Azure NSGs have implicit deny at the end of the rule list, but explicit deny rules must be present to prevent accidental allowance via rule priority gaps. Explicit deny also appears in audit logs |
| **Checkov** | Custom — assert no `security_rule` with `access = "Allow"` and `source_address_prefix = "*"` at high priority |

```hcl
# Insecure — allow-all inbound rule
resource "azurerm_network_security_group" "bad" {
  name                = "nsg-bad"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow-all-inbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Secure — explicit deny-all with specific allow rules
resource "azurerm_network_security_group" "good" {
  name                = "nsg-good"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "allow-https-inbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "10.0.0.0/8"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "deny-all-inbound"
    priority                   = 4096
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}
```

---

## VN-003 — No Unrestricted Inbound SSH (Port 22)

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all NSGs |
| **Justification** | SSH open to `0.0.0.0/0` exposes VMs to brute-force and credential stuffing attacks from the entire internet. SSH must be restricted to known IPs or accessed via Azure Bastion |
| **Checkov** | `CKV_AZURE_10` |

```hcl
# Insecure
resource "azurerm_network_security_rule" "bad_ssh" {
  name                        = "allow-ssh"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "*"       # open to internet
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.rg.name
  network_security_group_name = azurerm_network_security_group.nsg.name
}

# Secure — restrict to Bastion subnet or known IP
resource "azurerm_network_security_rule" "good_ssh" {
  name                        = "allow-ssh-bastion"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "10.0.2.0/27"  # Bastion subnet
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.rg.name
  network_security_group_name = azurerm_network_security_group.nsg.name
}
```

---

## VN-004 — No Unrestricted Inbound RDP (Port 3389)

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all NSGs |
| **Justification** | RDP open to `0.0.0.0/0` is one of the most exploited attack vectors for ransomware and lateral movement. Must be restricted to Azure Bastion or known management IPs |
| **Checkov** | `CKV_AZURE_9` |

```hcl
# Insecure
resource "azurerm_network_security_rule" "bad_rdp" {
  destination_port_range = "3389"
  source_address_prefix  = "*"
  access                 = "Allow"
  direction              = "Inbound"
  # ...
}

# Secure — no RDP rule, use Azure Bastion instead
resource "azurerm_bastion_host" "bastion" {
  name                = "bastion-host"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                 = "configuration"
    subnet_id            = azurerm_subnet.bastion.id
    public_ip_address_id = azurerm_public_ip.bastion_pip.id
  }
}
```

---

## VN-005 — DDoS Protection Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-3 — Deploy dedicated network-based DDoS protection |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Yes — VNets with public-facing resources |
| **Justification** | Azure DDoS Basic is free but limited. DDoS Network Protection provides adaptive tuning, attack telemetry, and SLA guarantees for production workloads |
| **Checkov** | `CKV_AZURE_182` |

```hcl
# Insecure — no DDoS plan
resource "azurerm_virtual_network" "bad" {
  name                = "vnet-bad"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Secure
resource "azurerm_network_ddos_protection_plan" "ddos" {
  name                = "ddos-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_virtual_network" "good" {
  name                = "vnet-good"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ddos_protection_plan {
    id     = azurerm_network_ddos_protection_plan.ddos.id
    enable = true
  }
}
```

---

## VN-006 — Network Watcher Enabled

| Field | Detail |
|---|---|
| **MCSB** | NS-4 — Deploy intrusion detection/prevention systems |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all regions where VNets are deployed |
| **Justification** | Network Watcher is required for NSG flow logs, connection troubleshooting, and packet capture. Without it, network forensics and incident response are severely limited |
| **Checkov** | Custom — assert `azurerm_network_watcher` exists in the same region as the VNet |

```hcl
# Secure
resource "azurerm_network_watcher" "nw" {
  name                = "nw-westeurope"
  location            = "westeurope"
  resource_group_name = azurerm_resource_group.rg.name
}
```

---

## VN-007 — NSG Flow Logs Enabled

| Field | Detail |
|---|---|
| **MCSB** | LT-3 — Enable logging for security investigation |
| **Severity** | Medium |
| **Priority** | Must |
| **Applies** | Yes — all NSGs |
| **Justification** | Flow logs capture allowed and denied traffic at the NSG level. Required for threat detection, anomaly analysis, and post-incident forensics |
| **Checkov** | `CKV_AZURE_12` |

```hcl
# Secure
resource "azurerm_network_watcher_flow_log" "nsg_flow" {
  network_watcher_name = azurerm_network_watcher.nw.name
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "flowlog-nsg"

  network_security_group_id = azurerm_network_security_group.good.id
  storage_account_id        = azurerm_storage_account.logs.id
  enabled                   = true
  version                   = 2

  retention_policy {
    enabled = true
    days    = 90
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.law.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.law.location
    workspace_resource_id = azurerm_log_analytics_workspace.law.id
    interval_in_minutes   = 10
  }
}
```

---

## VN-008 — No Wildcard Inbound Rules (Any/Any)

| Field | Detail |
|---|---|
| **MCSB** | NS-2 — Secure cloud services with network controls |
| **Severity** | High |
| **Priority** | Must |
| **Applies** | Yes — all NSGs |
| **Justification** | Rules with `source = *`, `destination = *`, `port = *`, and `access = Allow` negate all network segmentation. Each rule must specify explicit source, destination, and port |
| **Checkov** | Custom — assert no rule has all four wildcards simultaneously with `access = "Allow"` |

```hcl
# Insecure — any/any allow
security_rule {
  source_address_prefix      = "*"
  destination_address_prefix = "*"
  source_port_range          = "*"
  destination_port_range     = "*"
  access                     = "Allow"
}

# Secure — explicit scope
security_rule {
  source_address_prefix      = "10.1.0.0/24"
  destination_address_prefix = "10.2.0.0/24"
  source_port_range          = "*"
  destination_port_range     = "443"
  access                     = "Allow"
}
```

---

## VN-009 — Service Endpoints Scoped to Subnet

| Field | Detail |
|---|---|
| **MCSB** | NS-7 — Simplify network security configuration |
| **Severity** | Medium |
| **Priority** | Should |
| **Applies** | Conditional — when PaaS services (Storage, Key Vault, SQL) are accessed from VNet |
| **Justification** | Service endpoints route traffic to PaaS services over the Azure backbone and restrict access to specific subnets, reducing exposure compared to public endpoints |
| **Checkov** | Custom — assert `service_endpoints` is set on subnets that access PaaS services |

```hcl
# Insecure — no service endpoints, PaaS accessed over public internet
resource "azurerm_subnet" "bad" {
  address_prefixes = ["10.0.1.0/24"]
}

# Secure
resource "azurerm_subnet" "good" {
  name                 = "subnet-app"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]

  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.Sql"
  ]
}
```

---

## VN-010 — Subnets Not Overly Broad

| Field | Detail |
|---|---|
| **MCSB** | NS-1 — Establish network segmentation boundaries |
| **Severity** | Low |
| **Priority** | Nice |
| **Applies** | Yes — all subnets |
| **Justification** | Overly broad subnets (/8, /16) reduce segmentation effectiveness. Subnets should be sized to the workload to limit lateral movement blast radius |
| **Checkov** | Custom — assert subnet prefix length ≥ /24 for workload subnets |

```hcl
# Insecure — /16 subnet gives 65,534 addresses with no segmentation benefit
resource "azurerm_subnet" "bad" {
  address_prefixes = ["10.0.0.0/16"]
}

# Secure — /24 or smaller per workload tier
resource "azurerm_subnet" "good" {
  address_prefixes = ["10.0.1.0/24"]  # 254 addresses, scoped to one tier
}
```

---

## Secure VNet — Full Reference

```hcl
resource "azurerm_virtual_network" "compliant" {
  name                = "vnet-compliant"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  # VN-005
  ddos_protection_plan {
    id     = azurerm_network_ddos_protection_plan.ddos.id
    enable = true
  }
}

resource "azurerm_subnet" "app" {
  name                 = "subnet-app"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.compliant.name
  address_prefixes     = ["10.0.1.0/24"]   # VN-010
  service_endpoints    = ["Microsoft.Storage", "Microsoft.KeyVault"]  # VN-009
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id           # VN-001
  network_security_group_id = azurerm_network_security_group.app_nsg.id
}
```
