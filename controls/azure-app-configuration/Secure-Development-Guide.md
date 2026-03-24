# Secure Development Best Practices and Standards Guide

This document defines the mandatory standards for contributing to the `iac-azure-security-framework`. It is designed to guide both developers and AI agents in creating consistent security controls.

## 1. Framework Philosophy

* **MCSB First**: Every control must originate from a *Microsoft Cloud Security Benchmark* requirement.
* **Code over Text**: Documentation is not theoretical; it must include executable Terraform examples.
* **Explicit vs. Implicit**: In secure examples, define attributes explicitly, even if they match Azure defaults (to avoid regressions if defaults change).

## 2. `controls.md` Structure

Each control file (e.g., `controls/azure-sql/controls.md`) must strictly follow this structure. Use Azure Storage as the golden reference.

### Control Header

Each individual control must start with its ID and name, followed by a standardized metadata table:

| Field | Description | Rule |
|---|---|---|
| **MCSB** | Benchmark ID (e.g. NS-1) | Must exist in the official MCSB. |
| **Severity** | High, Medium, Low | Based on the impact of a breach. |
| **Priority** | Must, Should, Nice | **Must**: Blocks PRs. **Should**: Alert/Warning. |
| **Justification** | The "Why" | Clearly explains the technical risk (e.g., "Allows data exfiltration"). |
| **Checkov** | Rule ID | Use the official ID (e.g., `CKV_AZURE_59`) or "Custom". |

### Code Blocks: Insecure vs. Secure

It is **mandatory** to show the contrast. This trains agents and developers to detect incorrect patterns.

#### HCL Code Rules

1. Use `resource "type" "bad"` for the insecure example.
2. Use `resource "type" "good"` for the secure example.
3. Include comments explaining which specific property is missing or wrong.

**Example:**

```hcl
# Insecure — Enables unnecessary public access
resource "azurerm_storage_account" "bad" {
  # Missing public_network_access_enabled = false
  allow_nested_items_to_be_public = true
}

# Secure — Blocks public access and enforces HTTPS
resource "azurerm_storage_account" "good" {
  public_network_access_enabled   = false
  allow_nested_items_to_be_public = false
  enable_https_traffic_only       = true
}
```

## 3. Priority Criteria

* **Must (Mandatory)**:
  * Direct public exposure (internet-facing).
  * Lack of encryption in transit (HTTP).
  * Weak or nonexistent authentication (anonymous access).
  * *Action*: The CI/CD pipeline must fail if this is not met.

* **Should (Recommended)**:
  * Advanced encryption (CMK, infrastructure encryption).
  * Logging/audit logs (important, but not release-blocking by default).
  * Delete protections (soft delete).
  * *Action*: The pipeline generates warnings and may require manual approval or justification.

## 4. Checklist for Agents

Before committing a change or generating a new control file:

1. [ ] Is the `Control ID` (for example, `SQ-001`) unique and sequential?
2. [ ] Is there a valid mapping to MCSB (Domain-Number)?
3. [ ] Is the HCL block syntactically valid? Do not invent Terraform arguments.
4. [ ] Did you verify whether a Checkov rule exists for this control?
5. [ ] Does the justification explain the actual security risk?

## 5. File Locations

* Controls: `controls/<azure-service>/controls.md`
* Tests: `tests/terraform/<azure-service>/`
