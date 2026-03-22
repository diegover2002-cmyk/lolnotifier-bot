# =============================================================================
# terraform/modules/policy/main.tf
#
# MCSB (Microsoft Cloud Security Benchmark) Policy Initiative
#
# Assigns built-in Azure Policy definitions that map to MCSB controls
# for the lolnotifier resource group. Uses Audit effect only — no Deny —
# because the Consumption Function App plan (Y1) structurally cannot meet
# certain network isolation controls (VNet injection, zone redundancy).
#
# Cost: Azure Policy is FREE. No additional Azure spend.
#
# Effect strategy:
#   - AuditIfNotExists / Audit  → reports non-compliance without blocking
#   - No DeployIfNotExists      → avoids unintended resource creation
#   - No Deny                   → Consumption plan constraints prevent full enforcement
#
# Exceptions are documented in docs/compliance/exceptions-registry.json
# =============================================================================

data "azurerm_subscription" "current" {}

# -----------------------------------------------------------------------------
# Policy Initiative (Policy Set) — MCSB controls for lolnotifier
# -----------------------------------------------------------------------------

resource "azurerm_policy_set_definition" "mcsb_lolnotifier" {
  name         = "mcsb-lolnotifier-${var.environment}"
  policy_type  = "Custom"
  display_name = "MCSB Controls — lolnotifier-bot (${var.environment})"
  description  = "Custom MCSB initiative scoped to lolnotifier resources. Maps to Microsoft Cloud Security Benchmark v1. Audit-only — no Deny effects."

  metadata = jsonencode({
    version  = "1.0.0"
    category = "Security Center"
  })

  # ── Key Vault controls ─────────────────────────────────────────────────────

  # MCSB DP-8: Ensure Key Vault soft delete is enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/1e66c121-a66a-4b1f-9b83-0fd99bf0fc2d"
    reference_id         = "kv-soft-delete"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB DP-8: Ensure Key Vault purge protection is enabled
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0b60c0b2-2dc2-4e1c-b5c9-abbed971de53"
    reference_id         = "kv-purge-protection"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB NS-2: Key Vault should use private link / restrict network access
  # NOTE: Audit only — exception EXC-001 applies (CI runners need public access)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/a6fb4358-5bf4-4ad7-ba82-2cd2f41ce5e9"
    reference_id         = "kv-private-endpoint"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB IM-1: Key Vault should use RBAC (not legacy access policies)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/12d4fa5e-1f9f-4c21-97a9-b99b3c6611b5"
    reference_id         = "kv-rbac"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # ── Storage Account controls ───────────────────────────────────────────────

  # MCSB DP-3: Storage accounts should use customer-managed key or at minimum secure transfer
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9"
    reference_id         = "storage-secure-transfer"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB NS-2: Storage accounts should restrict network access
  # NOTE: Audit only — exception EXC-002 applies (Function App Consumption plan)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/34c877ad-507e-4c82-993e-3452a6e0ad3c"
    reference_id         = "storage-network-rules"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB DP-3: Storage minimum TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/fe83a0eb-a853-422d-aac2-1bffd182c5d0"
    reference_id         = "storage-tls"
    parameter_values = jsonencode({
      effect          = { value = "Audit" }
      minimumTlsVersion = { value = "TLS1_2" }
    })
  }

  # ── CosmosDB controls ──────────────────────────────────────────────────────

  # MCSB NS-2: CosmosDB should disable public network access
  # NOTE: Audit only — exception EXC-003 applies (serverless, no VNet support)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/797b37f7-06b8-444c-b1ad-fc62867f335a"
    reference_id         = "cosmosdb-public-access"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB IM-1: CosmosDB local authentication should be disabled
  # NOTE: Audit only — exception EXC-004 applies (bot uses connection string)
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/5450f5bd-9c72-4390-a9c4-a7aba4edfdd2"
    reference_id         = "cosmosdb-local-auth"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # ── Function App controls ──────────────────────────────────────────────────

  # MCSB NS-8: Function App should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab"
    reference_id         = "func-https-only"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB IM-2: Function App should use managed identity
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/0da106f2-4ca3-48e8-bc85-c638fe6aea8f"
    reference_id         = "func-managed-identity"
    parameter_values = jsonencode({
      effect = { value = "Audit" }
    })
  }

  # MCSB NS-8: Function App minimum TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f9d614c5-c173-4d56-95a7-b4437057d193"
    reference_id         = "func-tls"
    parameter_values = jsonencode({
      effect = { value = "AuditIfNotExists" }
    })
  }

  # ── Log Analytics / Monitoring controls ───────────────────────────────────

  # MCSB LT-3: Log Analytics workspace should have 90+ day retention
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f47b5582-33ec-4c5c-87c0-b010a6b2e917"
    reference_id         = "log-retention"
    parameter_values = jsonencode({
      effect              = { value = "AuditIfNotExists" }
      requiredRetentionDays = { value = "90" }
    })
  }
}

# -----------------------------------------------------------------------------
# Initiative Assignment — scoped to the lolnotifier resource group
# -----------------------------------------------------------------------------

resource "azurerm_resource_group_policy_assignment" "mcsb_lolnotifier" {
  name                 = "mcsb-lolnotifier-${var.environment}"
  resource_group_id    = var.resource_group_id
  policy_definition_id = azurerm_policy_set_definition.mcsb_lolnotifier.id
  display_name         = "MCSB Controls — lolnotifier-bot (${var.environment})"
  description          = "Audits lolnotifier resources against MCSB controls. Non-compliant resources are documented in docs/compliance/exceptions-registry.json."

  metadata = jsonencode({
    assignedBy = "terraform"
    version    = "1.0.0"
  })

  # Non-compliance message shown in Azure Policy portal
  non_compliance_message {
    content = "Resource does not comply with MCSB controls for lolnotifier-bot. See docs/compliance/exceptions-registry.json for registered exceptions."
  }
}
