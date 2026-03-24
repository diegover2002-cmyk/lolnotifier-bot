"""
Terraform SAST — Azure OpenAI Security Check
Analyses changed gold-tier Terraform modules against MCSB controls.

Layers:
  1. Static scan    — tfsec deterministic rules (optional, via --tfsec-output)
  2. Semantic scan  — Azure OpenAI LLM, MCSB Must-priority controls
  3. Exception gate — cross-references docs/compliance/exceptions-registry.json;
                      active exceptions are not counted as FAILs
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY  = os.getenv("AZURE_API_KEY")
ENDPOINT = (
    "https://ai-openaidiego-pro.openai.azure.com"
    "/openai/responses?api-version=2025-04-01-preview"
)
MODEL = "gpt-5.1-codex-mini"

EXCEPTIONS_REGISTRY = "docs/compliance/exceptions-registry.json"

MODULE_CONTROLS_MAP = {
    "terraform/modules/storage":  "controls/azure-storage/controls.md",
    "terraform/modules/keyvault": "controls/azure-key-vault/controls.md",
    "terraform/modules/aks":      "controls/azure-aks/controls.md",
}

MODULE_NAMES = {
    "terraform/modules/storage":  "Azure Storage Account",
    "terraform/modules/keyvault": "Azure Key Vault",
    "terraform/modules/aks":      "Azure Kubernetes Service (AKS)",
}

STATUS_ICON   = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "EXCEPTION": "🔵"}
TFSEC_SEV_ICON = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

# ── Exceptions registry ────────────────────────────────────────────────────────

def load_exempt_controls(registry_file: str) -> set[str]:
    """
    Returns a set of identifiers (Checkov rule IDs + MCSB composite keys) that
    have an active, non-expired registered exception.
    e.g. {"CKV_AZURE_109", "CKV_AZURE_35", "MCSB-NS-2"}
    """
    now = datetime.now(timezone.utc)
    exempt: set[str] = set()
    try:
        with open(registry_file, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return exempt
    for exc in data.get("registry", []):
        if exc.get("status") != "active":
            continue
        expires = datetime.fromisoformat(exc["expires_at"].replace("Z", "+00:00"))
        if expires <= now:
            continue
        for ctrl in exc.get("policy_controls", []):
            exempt.add(ctrl)
    return exempt


def is_exempt(ctrl_meta: dict, exempt: set[str]) -> str | None:
    """Returns matched exception ID if this control is covered, else None."""
    checkov = ctrl_meta.get("checkov", "")
    if checkov and checkov in exempt:
        return checkov
    mcsb = ctrl_meta.get("mcsb", "")
    mcsb_key = f"MCSB-{mcsb}" if mcsb else ""
    if mcsb_key and mcsb_key in exempt:
        return mcsb_key
    return None


# ── Controls extraction ────────────────────────────────────────────────────────

def extract_must_controls(controls_file: str) -> list[dict]:
    """
    Parse the summary table in controls.md.
    Returns only Must-priority rows; captures Checkov rule for exception lookup.
    """
    with open(controls_file, encoding="utf-8") as f:
        content = f.read()

    checkov_re = re.compile(r"`?(CKV2?_AZURE_\d+)`?")
    controls: list[dict] = []

    for line in content.splitlines():
        if not re.match(r"\|\s*\*{0,2}[A-Z]{1,3}-\d{3}\*{0,2}\s*\|", line):
            continue
        fields = [f.strip() for f in line.split("|") if f.strip()]
        if len(fields) < 5:
            continue

        ctrl_id  = re.sub(r"\*", "", fields[0]).strip()
        priority = next((f for f in fields if re.search(r"Must|Should|Nice", f, re.I)), "")
        if not re.search(r"Must", priority, re.I):
            continue

        severity = next((f for f in fields if re.match(r"^(High|Medium|Low)$", f, re.I)), "—")
        domain   = next((f for f in fields if re.match(r"^[A-Z]{2}$", f)), "—")
        mcsb     = next((f for f in fields if re.match(r"^[A-Z]{2}-\d+$", f)), "")
        name     = re.sub(r"\*", "", fields[3]).strip() if len(fields) > 3 else ""
        checkov  = next((checkov_re.search(f).group(1) for f in fields if checkov_re.search(f)), "")

        controls.append({"id": ctrl_id, "mcsb": mcsb, "domain": domain,
                         "name": name, "severity": severity, "checkov": checkov})
    return controls


def controls_to_compact_table(controls: list[dict]) -> str:
    lines = ["Control ID | Domain | Severity | Name"]
    for c in controls:
        lines.append(f"{c['id']} | {c['domain']} | {c['severity']} | {c['name']}")
    return "\n".join(lines)


# ── tfsec ─────────────────────────────────────────────────────────────────────

def parse_tfsec_findings(tfsec_file: str, module_dir: str) -> list[dict]:
    try:
        with open(tfsec_file, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    findings = []
    for result in data.get("results", []):
        loc = result.get("location", {})
        if module_dir not in loc.get("filename", ""):
            continue
        findings.append({
            "rule_id":     result.get("rule_id", result.get("legacy_rule_id", "?")),
            "description": result.get("description", result.get("rule_description", "")),
            "severity":    result.get("severity", "?").upper(),
            "resource":    result.get("resource", ""),
            "start_line":  loc.get("start_line", "?"),
        })
    return findings


def render_tfsec_section(findings: list[dict], exempt: set[str]) -> str:
    if not findings:
        return "**tfsec:** ✅ No findings\n"
    lines = [
        "**tfsec static scan:**\n",
        "| Rule | Severity | Resource | Line | Status |",
        "|---|---|---|---|---|",
    ]
    for f in findings:
        sev_icon = TFSEC_SEV_ICON.get(f["severity"], "⚪")
        status   = "🔵 EXCEPTION" if f["rule_id"] in exempt else f"{sev_icon} {f['severity']}"
        lines.append(
            f"| `{f['rule_id']}` | {sev_icon} {f['severity']} "
            f"| `{f['resource']}` | {f['start_line']} | {status} |"
        )
    return "\n".join(lines) + "\n"


# ── Azure OpenAI ──────────────────────────────────────────────────────────────

def call_openai(tf_code: str, controls_table: str, service_name: str) -> list[dict]:
    system_prompt = (
        "You are a Terraform security reviewer for Azure infrastructure. "
        "For each control ID in the list, inspect the Terraform code and decide: "
        "PASS (correctly implemented), FAIL (missing or wrong), "
        "WARN (partially met or conditional), "
        "EXCEPTION (a checkov:skip annotation is present for this control). "
        "Reply ONLY with a JSON array — no markdown, no prose — like: "
        '[{"id":"ST-001","status":"PASS","finding":"allow_nested_items_to_be_public = false"}]'
    )
    user_prompt = (
        f"Service: {service_name}\n\n"
        f"Must-priority MCSB controls to check:\n{controls_table}\n\n"
        f"Terraform code:\n```hcl\n{tf_code}\n```"
    )
    headers = {"Content-Type": "application/json", "api-key": API_KEY}
    payload = {
        "model": MODEL,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "max_output_tokens": 1024,
    }
    resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()

    raw_text = ""
    for item in result.get("output", []):
        if isinstance(item, dict):
            content = item.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "output_text":
                        raw_text += block.get("text", "")
            elif isinstance(content, str):
                raw_text += content

    raw_text = re.sub(r"```[a-z]*", "", raw_text).strip()
    return json.loads(raw_text)


# ── Report rendering ──────────────────────────────────────────────────────────

def render_module_report(
    module_dir:    str,
    tf_file:       str,
    ai_findings:   list[dict],
    controls_meta: list[dict],
    exempt:        set[str],
    tfsec_section: str,
) -> tuple[str, int]:
    """Returns (markdown_section, fail_count). Demotes FAIL→EXCEPTION when registered."""
    service_name = MODULE_NAMES.get(module_dir, module_dir)
    meta_by_id   = {c["id"]: c for c in controls_meta}

    for f in ai_findings:
        if f["status"] == "FAIL":
            exc_id = is_exempt(meta_by_id.get(f["id"], {}), exempt)
            if exc_id:
                f["status"]  = "EXCEPTION"
                f["finding"] = f"{f['finding']} [registered exception: {exc_id}]"

    pass_n = sum(1 for f in ai_findings if f["status"] == "PASS")
    fail_n = sum(1 for f in ai_findings if f["status"] == "FAIL")
    warn_n = sum(1 for f in ai_findings if f["status"] == "WARN")
    exc_n  = sum(1 for f in ai_findings if f["status"] == "EXCEPTION")

    lines = [
        f"#### `{tf_file}` — {service_name}", "",
        tfsec_section,
        "**AI semantic analysis (MCSB Must-priority):**\n",
        "| Control | Domain | Severity | Status | Finding |",
        "|---|---|---|---|---|",
    ]
    for f in ai_findings:
        meta = meta_by_id.get(f["id"], {})
        lines.append(
            f"| {f['id']} | {meta.get('domain','—')} | {meta.get('severity','—')} "
            f"| {STATUS_ICON.get(f['status'],'❓')} {f['status']} | {f.get('finding','')} |"
        )
    lines += ["", f"**Summary: {pass_n} PASS · {fail_n} FAIL · {warn_n} WARN · {exc_n} EXCEPTION**",
              "", "---", ""]
    return "\n".join(lines), fail_n


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: AZURE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", nargs="+", required=True)
    parser.add_argument("--output",        required=True)
    parser.add_argument("--tfsec-output",  default=None)
    args = parser.parse_args()

    exempt = load_exempt_controls(EXCEPTIONS_REGISTRY)
    print(f"Loaded {len(exempt)} exempt control identifiers from registry")

    modules_to_check: dict[str, str] = {}
    for tf_file in args.changed_files:
        module_dir = str(Path(tf_file).parent)
        if module_dir in MODULE_CONTROLS_MAP and module_dir not in modules_to_check:
            modules_to_check[module_dir] = tf_file
        else:
            print(f"  skip: {tf_file} — no gold-tier controls mapping")

    report_sections = [
        "## 🔒 Terraform SAST — AI Security Check\n",
        "> Gold-tier modules: Storage Account · Key Vault · AKS\n",
    ]
    total_fails = 0

    if not modules_to_check:
        report_sections.append("_No gold-tier Terraform changes detected._\n")
    else:
        for module_dir, tf_file in modules_to_check.items():
            service_name   = MODULE_NAMES.get(module_dir, module_dir)
            controls_file  = MODULE_CONTROLS_MAP[module_dir]
            print(f"\n→ Checking {service_name} ({tf_file})")

            tfsec_findings = parse_tfsec_findings(args.tfsec_output, module_dir) \
                             if args.tfsec_output else []
            tfsec_section  = render_tfsec_section(tfsec_findings, exempt)

            try:
                controls_meta = extract_must_controls(controls_file)
            except FileNotFoundError:
                report_sections.append(
                    f"#### `{tf_file}`\n\n⚠️ Controls file not found: `{controls_file}` — skipped.\n\n---\n")
                continue

            if not controls_meta:
                report_sections.append(
                    f"#### `{tf_file}`\n\nℹ️ No Must-priority controls found — skipped.\n\n---\n")
                continue

            print(f"   {len(controls_meta)} Must-priority controls loaded")

            try:
                with open(tf_file, encoding="utf-8") as f:
                    tf_code = f.read()
            except FileNotFoundError:
                report_sections.append(
                    f"#### `{tf_file}`\n\n⚠️ File not found — skipped.\n\n---\n")
                continue

            try:
                ai_findings = call_openai(tf_code, controls_to_compact_table(controls_meta), service_name)
            except Exception as e:
                report_sections.append(
                    f"#### `{tf_file}` — {service_name}\n\n❌ API error: `{e}`\n\n---\n")
                print(f"   API error: {e}", file=sys.stderr)
                continue

            section, module_fails = render_module_report(
                module_dir, tf_file, ai_findings, controls_meta, exempt, tfsec_section)
            total_fails += module_fails
            report_sections.append(section)

    if modules_to_check:
        banner = "### ✅ Gate: PASSED — no unregistered FAIL findings\n" if total_fails == 0 else \
                 f"### ❌ Gate: BLOCKED — {total_fails} FAIL finding(s) must be remediated or registered before merging\n"
        report_sections.insert(2, banner)

    full_report = "\n".join(report_sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\nReport written to {args.output}")
    print(full_report)

    if total_fails > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
