"""
Terraform SAST — Azure OpenAI Security Check
Analyses changed gold-tier Terraform modules against MCSB controls.
Token-efficient: extracts only the summary table from controls.md,
filters to Must-priority controls, and requests structured JSON output.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY  = os.getenv("AZURE_API_KEY")
ENDPOINT = (
    "https://ai-openaidiego-pro.openai.azure.com"
    "/openai/responses?api-version=2025-04-01-preview"
)
MODEL = "gpt-5.1-codex-mini"

# Gold-tier: module directory → controls file (relative to repo root)
MODULE_CONTROLS_MAP = {
    "terraform/modules/storage":  "controls/azure-storage/controls.md",
    "terraform/modules/keyvault": "controls/azure-key-vault/controls.md",
    "terraform/modules/aks":      "controls/azure-aks/controls.md",
}

# Human-readable service names for the report header
MODULE_NAMES = {
    "terraform/modules/storage":  "Azure Storage Account",
    "terraform/modules/keyvault": "Azure Key Vault",
    "terraform/modules/aks":      "Azure Kubernetes Service (AKS)",
}

STATUS_ICON = {
    "PASS":      "✅",
    "FAIL":      "❌",
    "WARN":      "⚠️",
    "EXCEPTION": "🔵",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_must_controls(controls_file: str) -> list[dict]:
    """
    Parse the summary table in controls.md and return only Must-priority rows.
    Skips HCL examples and all narrative text — much cheaper on tokens.
    Row formats vary across files; we normalise with a flexible regex.
    """
    with open(controls_file, encoding="utf-8") as f:
        content = f.read()

    controls = []
    # Match table data rows that contain a control ID like ST-001, KV-003, AK-007 …
    row_re = re.compile(
        r"\|\s*\*{0,2}([A-Z]{1,3}-\d{3})\*{0,2}\s*"   # Control ID
        r"\|\s*([^\|]+?)\s*"                             # MCSB
        r"\|\s*([^\|]+?)\s*"                             # Domain
        r"\|\s*([^\|]+?)\s*"                             # Control Name
        r"\|([^\|]*?)\|"                                 # Severity (optional col)
        r"([^\|]*?)\|"                                   # Priority
    )
    for m in row_re.finditer(content):
        ctrl_id   = m.group(1).strip()
        mcsb      = m.group(2).strip()
        domain    = m.group(3).strip()
        name      = m.group(4).strip()
        # Severity may be in group 5 or group 6 depending on column order
        g5, g6    = m.group(5).strip(), m.group(6).strip()
        # Identify which group contains the priority token
        priority  = g6 if re.search(r"Must|Should|Nice", g6, re.I) else g5
        severity  = g5 if priority == g6 else g6

        if not re.search(r"Must", priority, re.I):
            continue  # skip Should / Nice

        controls.append({
            "id":       ctrl_id,
            "mcsb":     mcsb,
            "domain":   domain,
            "name":     name,
            "severity": severity if severity else "—",
        })

    return controls


def controls_to_compact_table(controls: list[dict]) -> str:
    """Render a compact plain-text table to include in the prompt."""
    lines = ["Control ID | Domain | Severity | Name"]
    for c in controls:
        lines.append(f"{c['id']} | {c['domain']} | {c['severity']} | {c['name']}")
    return "\n".join(lines)


def call_openai(tf_code: str, controls_table: str, service_name: str) -> list[dict]:
    """
    Send one request per module to Azure OpenAI.
    Returns a list of dicts: [{id, status, finding}, ...]
    """
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

    # Extract text content from the Responses API shape
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

    # Parse JSON — strip any accidental markdown fences
    raw_text = re.sub(r"```[a-z]*", "", raw_text).strip()
    return json.loads(raw_text)


def render_module_report(module_dir: str, tf_file: str, findings: list[dict],
                         controls_meta: list[dict]) -> str:
    """Render one module's findings as a markdown table."""
    service_name = MODULE_NAMES.get(module_dir, module_dir)
    meta_by_id   = {c["id"]: c for c in controls_meta}

    pass_n      = sum(1 for f in findings if f["status"] == "PASS")
    fail_n      = sum(1 for f in findings if f["status"] == "FAIL")
    warn_n      = sum(1 for f in findings if f["status"] == "WARN")
    exc_n       = sum(1 for f in findings if f["status"] == "EXCEPTION")

    lines = [
        f"#### `{tf_file}` — {service_name}",
        "",
        "| Control | Domain | Severity | Status | Finding |",
        "|---|---|---|---|---|",
    ]
    for f in findings:
        meta   = meta_by_id.get(f["id"], {})
        icon   = STATUS_ICON.get(f["status"], "❓")
        status = f"{icon} {f['status']}"
        lines.append(
            f"| {f['id']} "
            f"| {meta.get('domain', '—')} "
            f"| {meta.get('severity', '—')} "
            f"| {status} "
            f"| {f.get('finding', '')} |"
        )

    lines += [
        "",
        f"**Summary: {pass_n} PASS · {fail_n} FAIL · {warn_n} WARN · {exc_n} EXCEPTION**",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: AZURE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Deduplicate modules — multiple changed files in the same module dir
    # should produce only one API call
    modules_to_check: dict[str, str] = {}  # module_dir → tf_file (first match)
    for tf_file in args.changed_files:
        p = Path(tf_file)
        module_dir = str(p.parent)
        if module_dir not in MODULE_CONTROLS_MAP:
            print(f"  skip: {tf_file} — no gold-tier controls mapping")
            continue
        if module_dir not in modules_to_check:
            modules_to_check[module_dir] = tf_file

    report_sections = [
        "## 🔒 Terraform SAST — AI Security Check\n",
        "> Gold-tier modules: Storage Account · Key Vault · AKS\n",
    ]

    total_fails = 0

    if not modules_to_check:
        report_sections.append("_No gold-tier Terraform changes detected._\n")
    else:
        for module_dir, tf_file in modules_to_check.items():
            controls_file = MODULE_CONTROLS_MAP[module_dir]
            service_name  = MODULE_NAMES.get(module_dir, module_dir)
            print(f"\n→ Checking {service_name} ({tf_file})")

            # Load controls (Must-priority only)
            try:
                controls_meta = extract_must_controls(controls_file)
            except FileNotFoundError:
                report_sections.append(
                    f"#### `{tf_file}`\n\n"
                    f"⚠️ Controls file not found: `{controls_file}` — skipped.\n\n---\n"
                )
                continue

            if not controls_meta:
                report_sections.append(
                    f"#### `{tf_file}`\n\n"
                    f"ℹ️ No Must-priority controls found in `{controls_file}` — skipped.\n\n---\n"
                )
                continue

            print(f"   {len(controls_meta)} Must-priority controls loaded")

            # Load Terraform file
            try:
                with open(tf_file, encoding="utf-8") as f:
                    tf_code = f.read()
            except FileNotFoundError:
                report_sections.append(
                    f"#### `{tf_file}`\n\n"
                    f"⚠️ Terraform file not found: `{tf_file}` — skipped.\n\n---\n"
                )
                continue

            controls_table = controls_to_compact_table(controls_meta)

            # Call Azure OpenAI
            try:
                findings = call_openai(tf_code, controls_table, service_name)
            except Exception as e:
                report_sections.append(
                    f"#### `{tf_file}` — {service_name}\n\n"
                    f"❌ API error: `{e}`\n\n---\n"
                )
                print(f"   API error: {e}", file=sys.stderr)
                continue

            module_fails = sum(1 for f in findings if f["status"] == "FAIL")
            total_fails += module_fails

            section = render_module_report(module_dir, tf_file, findings, controls_meta)
            report_sections.append(section)

    # ── Gate banner ───────────────────────────────────────────────────────────
    if modules_to_check:
        if total_fails == 0:
            gate_banner = "### ✅ Gate: PASSED — no unregistered FAIL findings\n"
        else:
            gate_banner = (
                f"### ❌ Gate: BLOCKED — {total_fails} FAIL finding(s) must be "
                f"remediated or registered as exceptions before merging\n"
            )
        report_sections.insert(2, gate_banner)

    full_report = "\n".join(report_sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\nReport written to {args.output}")
    print(full_report)

    if total_fails > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
