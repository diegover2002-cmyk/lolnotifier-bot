# MCSB Controls for the DevOps Security Domain

**Category:** Cross-cutting Domain
**Scope:** DevOps / CI/CD Lifecycle

## 1. Domain Summary

This document outlines security controls applicable to the **DevOps Security (DS)** domain as defined by the Microsoft Cloud Security Benchmark. Unlike service-specific baselines, these controls apply to the tools, processes, and infrastructure used to build and deploy applications and infrastructure. The focus is on "shifting left" to find and fix issues early in the development lifecycle.

The controls below are a starting point for establishing a secure CI/CD pipeline.

| Control ID | MCSB | Domain | Control Name | Priority | IaC Checkable | Validation Tool/Method |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DS-001** | DS-6 | DS | IaC linting and security scanning | **Must** | Yes | `Checkov`, `Trivy` |
| **DS-002** | DS-3 | DS | Static Application Security Testing (SAST) | **Must** | Yes | CodeQL, SonarQube |
| **DS-003** | DS-4 | DS | Software Composition Analysis (SCA) | **Must** | Yes | GitHub Dependabot, Trivy |
| **DS-004** | DS-5 | DS | Container Image / Base Image Scanning | **Must** | Yes | Trivy, Microsoft Defender |
| **DS-005** | DS-2 | DS | Secret scanning in repositories and artifacts| **Must** | Yes | GitHub Secret Scanning, Checkov |
| **DS-006** | DS-1 | DS | Secure access to CI/CD systems | **Must** | Partial | RBAC, MFA, OIDC |
| **DS-007** | DS-7 | DS | Secure pipeline agent/runner configuration| **Should**| Partial | Custom policies, monitoring |
| **DS-008** | DS-8 | DS | Enforce deployment gates/quality checks| **Must** | Yes | CI/CD platform features |

---

## 2. Control Details

### DS-001: IaC linting and security scanning

- **MCSB:** DS-6 (Harden deployment pipeline)
- **Priority:** **Must**
- **Relevance:** Infrastructure as Code (IaC) should be treated like application code and scanned for misconfigurations before deployment. This is the core purpose of the `iac-azure-security-framework` repository.
- **Implementation:** Integrate tools like `Checkov` or `Trivy` into the Pull Request pipeline to scan `.tf` files. The pipeline should fail if controls with `Priority=Must` are violated.
- **Validation:** CI/CD pipeline logs showing successful/failed `checkov` scans.

### DS-002: Static Application Security Testing (SAST)

- **MCSB:** DS-3 (Secure development workflow)
- **Priority:** **Must**
- **Relevance:** Analyzes application source code for common vulnerabilities (e.g., SQL injection, XSS) without executing the code.
- **Implementation:** Integrate a SAST tool like GitHub CodeQL or SonarQube into the PR pipeline. Fail the build on new high-severity findings.
- **Validation:** SAST tool reports and PR status checks.

### DS-003: Software Composition Analysis (SCA)

- **MCSB:** DS-4 (Manage third-party components)
- **Priority:** **Must**
- **Relevance:** Scans application dependencies (e.g., NuGet packages, npm modules) for known vulnerabilities (CVEs).
- **Implementation:** Enable tools like GitHub Dependabot, Trivy, or Snyk to scan dependency manifests. Automatically create PRs for patches or fail builds on critical vulnerabilities.
- **Validation:** SCA tool reports and dependency graphs.

### DS-004: Container Image / Base Image Scanning

- **MCSB:** DS-5 (Harden container images)
- **Priority:** **Must**
- **Relevance:** Scans OS packages and application layers within container images for known vulnerabilities.
- **Implementation:** Integrate `Trivy` or Microsoft Defender for Containers into the container build pipeline. Fail builds if high-severity CVEs are found in the final image.
- **Validation:** Image scanner reports.

### DS-005: Secret scanning in repositories and artifacts

- **MCSB:** DS-2 (Prevent secrets from being exposed)
- **Priority:** **Must**
- **Relevance:** Prevents credentials, tokens, and API keys from being accidentally committed to source control or included in build artifacts.
- **Implementation:** Enable native GitHub secret scanning. Use tools like Checkov's secret scanning capabilities in local pre-commit hooks and in the CI pipeline.
- **Validation:** Secret scanning alerts; pipeline jobs failing on found secrets.

### DS-006: Secure access to CI/CD systems

- **MCSB:** DS-1 (Secure DevOps infrastructure)
- **Priority:** **Must**
- **Relevance:** The CI/CD system itself is a privileged environment. Access must be tightly controlled.
- **Implementation:** Enforce MFA for all users. Use RBAC with least privilege. For cloud access, prefer short-lived OIDC tokens over static secrets for authenticating the pipeline to Azure.
- **Validation:** Azure AD and GitHub audit logs; OIDC configuration.

### DS-007: Secure pipeline agent/runner configuration

- **MCSB:** DS-7 (Secure deployment environment)
- **Priority:** **Should**
- **Relevance:** Self-hosted runners/agents must be hardened, patched, and monitored. They should run with least privilege and have limited network access.
- **Implementation:** Use minimal base images, run as non-root, regularly update the agent software, and use network policies to restrict outbound traffic.
- **Validation:** Agent configuration files; host vulnerability scans.

### DS-008: Enforce deployment gates/quality checks

- **MCSB:** DS-8 (Enforce quality gates)
- **Priority:** **Must**
- **Relevance:** Ensures that no deployment to a production (or sensitive) environment can proceed unless all required security checks have passed.
- **Implementation:** Use protected branches in GitHub and require status checks (SAST, IaC scan, etc.) to pass before a PR can be merged. Use deployment environments with required reviewers for production releases.
- **Validation:** Branch protection rule configuration.
