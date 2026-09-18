# Evidence contract

## Source requirements

Every configured input must appear exactly once in `data/source_manifest.json` with:

- a nonblank fictional source URI and extraction/query description;
- an extraction timestamp;
- the retained row count; and
- the SHA-256 fingerprint of the exact snapshot.

The validator also checks that the file exists, required columns are present, primary keys are populated and unique, no unconfigured manifest entries exist, and the actual row count and hash match. Any failure prevents screening and returns exit code `3`.

## Population reconciliation

The evidence package proves:

```text
total records = active records + inactive exclusions
screened records = active records
```

An inactive record is an evidenced exclusion, not an omitted source row. Production connectors should additionally reconcile extract control totals to source system reports or signed API metadata.

## Rule source governance

Each source referenced by a configured screening rule must have a current `approved` record in `counsel_approvals.csv`. The approval must identify the approver and reviewer role and cover the run's `as_of_date`. Expired or missing approval makes that rule source invalid and stops the run.

The fictional rule source snapshots include effective and expiration dates. Rows outside the effective period are not evaluated. The POC never downloads live regulatory content and should not be interpreted as reflecting any real list, law, policy, or jurisdiction.

## Outputs

`audit_evidence.json` contains the run ID, decision support notice, control configuration, reconciliation, complete source validation results, rule source approvals, rule configuration, and all findings. `potential_matches.csv` provides one RCM ready row per signal. Case Markdown files provide the human investigation and closure checklist.

Stable case IDs are derived from the rule, source, master record, matched rule entry, and signal type. They do not contain sensitive data. A production platform should retain immutable run evidence and a separate case action history that only permits additions and records actor identity, timestamps, rationale, attachments, prior and new states, and approval decisions.
