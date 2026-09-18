# Third Party Regulatory Monitoring — Proof of Concept

![CI](https://github.com/MaxwellM-GRC/third-party-regulatory-monitoring-poc/actions/workflows/ci.yml/badge.svg)

This POC correlates fictional AP supplier, CRM customer, and ERP business partner populations with fictional regulatory rule source snapshots that counsel has approved.

> **Sanitized data:** All names, people, organizations, systems, accounts, and records in this repository are fictional. No employer, client, or production data is included.

## The problem it catches

Failure to screen complete third party master data against current, approved regulatory rule sources could leave a potential issue unidentified or prevent timely review by qualified legal/compliance personnel.

The sample catches transparent signals such as:

- an exact registration identifier or normalized name that may match a configured entity;
- a similar name that needs human disambiguation;
- a third party located in a jurisdiction configured for additional review;
- an incomplete or altered source extract; and
- a missing or expired approval for a rule source.

A signal is not a legal conclusion, an identity determination, or an assertion of noncompliance. The POC routes potential issues to qualified reviewers.

## What this control tests

| Control ID | Control description | Severity |
|---|---|---|
| `RM-01` | Exact identifiers or exact normalized names may match an entity in an approved regulatory source. | High |
| `RM-02` | Similar normalized names may match an entity in an approved regulatory source and require human disambiguation. | Medium |
| `RM-03` | A third party in an approved review jurisdiction requires qualified human review under the configured policy source. | Medium |

## How it works

```text
AP suppliers + CRM customers + ERP business partners ─┐
                                                       ├─> integrity gate ─> full population reconciliation
Rule source snapshots + counsel approvals ────────────┘                              │
                                                                                     v
                                                        deterministic rule evaluation
                                                                                     │
                                              audit evidence + RCM ready findings + exception cases
                                                                                     │
                                                                 qualified legal/compliance review
```

The integrity gate verifies expected files, required columns, populated and unique primary keys, retained row counts, extraction metadata, source provenance, and SHA-256 fingerprints. It fails closed when evidence is incomplete, altered, or unapproved.

The runner retains inactive records as evidenced exclusions and proves that total records equal active records plus inactive exclusions. Every active record is screened. Stable case IDs support repeatable follow up across runs.

Automation may identify a potential match and recommend review. It cannot determine legal applicability, select or approve remediation, accept risk, or close an exception case. The tested state machine requires a named actor, role, rationale, and evidence reference for every transition, and only a qualified legal/compliance reviewer may approve closure.

The absence of a default remediation policy is intentional. A qualified legal/compliance reviewer determines whether a response is required and, if so, the appropriate response, evidence, approvals, and closure basis.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m src.main
```

Normal demonstration runs return `0` even when potential matches exist. `--fail-on-potential-matches` returns `2` for alerting integrations. Invalid input returns `3` without producing a screening conclusion.

## Sample output

```text
RUN-63AF793598348CAF: screened 8/9 records; 3 potential matches
```

The sample contains nine source records: eight active records are screened and one inactive record remains in the reconciliation as an evidenced exclusion. Three potential match signals produce three exception case packets.

```text
output/
  audit_evidence.json       Run, source, approval, reconciliation, rule, and finding evidence
  potential_matches.csv     RCM ready potential match register
  cases/RM-*.md             Human triage, remediation, and closure checklists
```

## Continuous monitoring

- `ci.yml` runs tests, executes the sample, and uploads retained evidence for each push and pull request.
- `regulatory-monitor.yml` runs at 08:17 UTC on weekdays and on demand.
- The monitoring workflow creates or refreshes one GitHub Issue per stable potential match ID with the `potential-match` and `human-review-required` labels.
- The exception case lifecycle is `open` → `under_review` → `remediation_pending` or `closure_pending` → `closed`.
- Automation cannot skip human review or approve closure.

The POC does not impose a universal response SLA because response periods depend on the approved policy, source, severity, jurisdiction, and qualified advice. A production implementation should configure human approved severity targets, notify the case owner before the target expires, and escalate overdue high severity cases to the designated compliance and legal leadership roles.

## Production design and limitations

Production collectors should use read only identities to obtain signed snapshots and control totals from each authoritative source. The full population should land in immutable, encrypted storage before screening. Workload identities, managed secrets, least privilege, private networking, retention controls, and centralized audit logs should protect the pipeline.

Rule sources, normalization behavior, thresholds, and approval records should be controlled through versioning and review. A policy registry should block deployment when counsel approval is missing or expired. A managed case platform should enforce segregation of duties, human approved remediation, evidence attachment, response targets, escalation, and qualified closure approval.

This POC uses small CSV snapshots and deterministic matching to demonstrate control behavior. It does not connect to live regulatory providers, evaluate real parties or transactions, measure production precision and recall, provide legal advice, or assert legal compliance.

There is no automated remediation policy. That omission preserves the decision boundary: a qualified reviewer determines the response based on validated identity, applicable requirements, approved policy, and documented professional judgment.

### Separation from ITGC vendor management

This repository is intentionally separate from `vendor-management-poc`.

| Regulatory monitoring (this POC) | ITGC vendor and subservice management |
|---|---|
| Screens supplier and customer identities, identifiers, and locations against approved policy and rule sources. | Tracks critical service providers and subservice organizations supporting IT or financial reporting systems. |
| Produces potential regulatory matches for qualified legal/compliance review. | Evaluates risk assessments, SOC/ISAE coverage, bridge letters, CUECs, incidents, and reassessments. |
| Uses AP, CRM, and ERP master populations. | Uses TPRM, GRC, SOC report, CUEC, and incident evidence. |
| Does not assess SOC report coverage or CUEC operation. | Does not determine sanctions, trade, customer, or supplier regulatory applicability. |

The controls may share an inventory integration in production, but they address different risks, evidence, reviewers, and conclusions.

## Control mapping

| RCM attribute | Design |
|---|---|
| Control ID | `RCM-TPRM-001` |
| Category | `regulatory_monitoring` |
| Risk | Failure to screen complete third party master data against current, approved regulatory rule sources could leave a potential issue unidentified or prevent timely qualified review. |
| Control description | Management performs full population reconciliation and screens active AP, CRM, and ERP third party records against current rule sources that counsel has approved, then routes potential matches for qualified review, evidence, remediation, and closure approval. |
| Owner | Compliance Operations |
| Reviewer | Qualified Legal or Compliance Reviewer |
| Frequency | Daily in production; on demand in this POC |
| Nature | Automated integrity and screening; manual investigation, decision, remediation approval, and closure |
| Population | All extracted supplier, customer, and business partner records, with inactive records retained as evidenced exclusions |
| Frameworks | Organization specific compliance RCM; no mapping to a particular law or regulatory framework is asserted |
| Response policy | No default remediation is configured; the qualified reviewer determines whether and how to respond |
| Evidence contract | Source manifest and hashes, source provenance, counsel approvals, population reconciliation, configuration fingerprint, rule results, exception case packets, and workflow history in a production adapter |

See [RCM and control narrative](docs/rcm_and_control_narrative.md), [Evidence contract](docs/evidence_contract.md), and [Production design](docs/production_design.md).

## Repository layout

```text
config.yaml                 Control, review, rule, and source configuration
data/                       Fictional source populations and approval records
data/rule_sources/          Fictional regulatory rule source snapshots
data/source_manifest.json   Extraction metadata, row counts, and fingerprints
src/                        Integrity, loading, screening, workflow, reporting, and CLI logic
tests/                      Integrity, rule, workflow, output, and shared core tests
output/                     Committed sample audit evidence and exception cases
docs/                       Control narrative, evidence contract, and production design
.github/workflows/          CI and recurring regulatory monitoring
```

MIT — see [LICENSE](LICENSE).
