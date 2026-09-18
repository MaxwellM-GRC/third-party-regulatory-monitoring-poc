# Third Party Regulatory Monitoring — Proof of Concept

![CI](https://github.com/MaxwellM-GRC/third-party-regulatory-monitoring-poc/actions/workflows/ci.yml/badge.svg)

Cloud native screening with retained evidence for fictional AP suppliers, CRM customers, and ERP business partners against fictional regulatory rule source snapshots that counsel has approved.

> **Decision support boundary:** The POC identifies and routes potential issues. It does not make legal conclusions, determine that two entities are the same, assert noncompliance, select remediation, accept risk, or close a case. Those decisions belong to qualified legal/compliance reviewers. Every organization, person, identifier, jurisdiction, URI, and source record in this repository is fictional.

## What it demonstrates

The runner:

1. validates every expected master data and rule source snapshot against retained row counts, schemas, primary keys, extraction metadata, and SHA-256 fingerprints;
2. fails closed unless every configured rule source has a current approval from a named legal/compliance reviewer;
3. reconciles the full AP, CRM, and ERP population, retaining inactive records as evidenced exclusions;
4. screens active records using transparent exact identifier, normalized name, fuzzy name, and jurisdiction routing rules;
5. creates stable potential match records with RCM traceability and case packets owned by people; and
6. enforces a tested state machine in which automation cannot approve remediation or close a case.

The sample intentionally produces three potential match signals across two source records. Multiple signals remain separate so a reviewer can resolve the entity and jurisdiction questions independently.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m src.main
```

Generated evidence is written to:

```text
output/
  audit_evidence.json       Run, source, approval, reconciliation, rule, and finding evidence
  potential_matches.csv     RCM ready potential match register
  cases/RM-*.md             Human triage, remediation, and closure checklists
```

Normal demonstration runs return `0` even when potential matches exist. `--fail-on-potential-matches` returns `2` for alerting integrations. Incomplete, altered, or unapproved input returns `3` and no screening conclusion is produced.

## Control and RCM mapping

| Item | Design |
|---|---|
| Control ID | `RCM-TPRM-001` |
| Risk | A potential regulatory concern in third party master data may not be timely identified and routed. |
| Population | Full AP supplier, CRM customer, and ERP business partner snapshots, including evidenced inactive exclusions. |
| Frequency | Daily in production; on demand in this POC. |
| Evidence | Immutable source manifest, source hashes, approvals, population reconciliation, rule results, case packets, and workflow history in a production adapter. |
| Human control | Qualified reviewers decide identity, applicability, remediation, risk response, and closure. |

See [Control narrative and RCM](docs/control_narrative_and_rcm.md), [Evidence contract](docs/evidence_contract.md), and [Production design](docs/production_design.md).

## This is not ITGC vendor/SOC management

This repository is intentionally separate from `vendor-management-poc`.

| Regulatory monitoring (this POC) | ITGC vendor/subservice management |
|---|---|
| Screens supplier and customer identities, identifiers, and locations against approved policy/rule sources. | Tracks critical service providers and subservice organizations supporting IT or financial reporting systems. |
| Produces potential regulatory matches for qualified legal/compliance review. | Evaluates risk assessments, SOC/ISAE coverage, bridge letters, CUECs, incidents, and reassessments. |
| Uses AP/CRM/ERP master populations. | Uses TPRM, GRC, SOC report, CUEC, and incident evidence. |
| Does not assess SOC report coverage or CUEC operation. | Does not determine sanctions, trade, customer, or supplier regulatory applicability. |

The controls may share an inventory integration in production, but they address different risks, evidence, reviewers, and conclusions.

## Cloud native operating model

GitHub Actions runs tests and retains generated evidence on each change. A weekday and on demand monitoring workflow creates or refreshes one GitHub Issue per stable potential match ID and explicitly requires qualified review. A production implementation should replace repository CSVs with read only snapshot exports, object lock evidence storage, a case platform, workload identity, secrets management, centralized logging, and approved regulatory data providers.

MIT — see [LICENSE](LICENSE).
