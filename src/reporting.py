"""Write RCM ready findings, case packets, and retained audit evidence."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .models import RunResult


MATCH_FIELDS = [
    "case_id", "control_id", "rule_id", "severity", "source_id", "source_system", "record_id",
    "third_party_name", "country_code", "potential_match_type", "matched_value", "matched_source_entry",
    "rule_source_id", "rule_source_reference", "match_score", "status", "owner", "disposition", "rationale",
]


def write_outputs(result: RunResult, config: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema_version": "1.0.0", "run_id": result.run_id,
        "configuration_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
        "legal_notice": "Potential matches are decision support signals, not legal conclusions or assertions of compliance.",
        "control": config["control"], "review": config["review"],
        "population_reconciliation": {
            "total_records": result.total_records, "active_records": result.active_records,
            "excluded_inactive_records": result.excluded_records, "screened_records": result.screened_records,
            "reconciled": result.input_valid and result.total_records == result.active_records + result.excluded_records and result.screened_records == result.active_records,
        },
        "source_validation": [status.to_dict() for status in result.statuses],
        "counsel_approvals": result.approved_rule_sources,
        "rules": config["rules"], "potential_matches": [finding.to_dict() for finding in result.findings],
    }
    (output_dir / "audit_evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "potential_matches.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATCH_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(finding.to_dict() for finding in result.findings)
    cases = output_dir / "cases"
    cases.mkdir(exist_ok=True)
    for stale in cases.glob("RM-*.md"):
        stale.unlink()
    for finding in result.findings:
        body = f"""# Potential match case {finding.case_id}

> This is a potential match for qualified legal/compliance review. It is not a legal conclusion or an assertion of noncompliance.

## RCM traceability

- Control: {finding.control_id}
- Rule: {finding.rule_id}
- Source population: {finding.source_system} / {finding.source_id}
- Source record: {finding.record_id}
- Third party: {finding.third_party_name}
- Match signal: {finding.potential_match_type} ({finding.match_score:.4f})
- Rule source entry: {finding.matched_source_entry}
- Rule source reference: {finding.rule_source_reference}

## Triage and response checklist

- [ ] Confirm the source record and evidence provenance.
- [ ] Resolve aliases, identifiers, ownership, geography, and other identity attributes.
- [ ] Ask a qualified legal/compliance reviewer to assess scope and applicability.
- [ ] If a response is required, record the human approved action, owner, target, and evidence.
- [ ] Determine and document any lookback procedures and conclusion.
- [ ] Document root cause when a confirmed process or control breakdown contributed.
- [ ] Check for recurrence and link related prior or subsequent cases.
- [ ] Escalate the case if it exceeds an assigned target or presents urgent facts.
- [ ] Attach disposition rationale and supporting evidence.
- [ ] Obtain qualified legal/compliance approval before closure.

Current status: **{finding.status}**

Owner: **{finding.owner}**

Default disposition: **{finding.disposition}**
"""
        (cases / f"{finding.case_id}.md").write_text(body, encoding="utf-8")
