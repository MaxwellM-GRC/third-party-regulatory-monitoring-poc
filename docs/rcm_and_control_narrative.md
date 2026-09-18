# RCM and control narrative

## Control metadata

| Attribute | Value |
|---|---|
| Control ID | `RCM-TPRM-001` |
| Control name | Third Party Regulatory Monitoring |
| Category | `regulatory_monitoring` |
| Classification | Non ITGC compliance monitoring control |
| Owner | Compliance Operations |
| Reviewer | Qualified Legal or Compliance Reviewer |
| Frequency | Daily in production; on demand in the POC |
| Nature | Automated integrity and screening; manual investigation, decision, response, remediation approval, and closure |

## Risk and objective

**Risk:** Failure to screen complete third party master data against current, approved regulatory rule sources could leave a potential issue unidentified or prevent timely review by qualified legal/compliance personnel.

**Objective:** Complete supplier, customer, and business partner populations are reconciled and screened against current rule sources that counsel has approved, with potential matches routed for documented, qualified review.

This is a monitoring and workflow control, not a legal opinion. A generated finding means only that a configured signal was observed.

## Control activity

Management performs full population reconciliation and screens active AP, CRM, and ERP third party records against current regulatory rule sources that counsel has approved. Automation validates source completeness and provenance, confirms current approval of configured rule sources, applies transparent matching rules, retains explainable evidence, and creates stable potential match cases.

Automation identifies and routes potential matches only. A qualified legal/compliance reviewer determines identity, legal or policy applicability, response, remediation, risk disposition, and closure. The control does not determine whether two entities are the same, whether a requirement applies, whether a transaction is permitted, whether remediation is sufficient, or whether the organization complies with law or policy.

## Population and completeness

The control population consists of all supplier, customer, and business partner records extracted from the AP, CRM, and ERP systems in scope for the review date.

- Active records are screened.
- Inactive records remain in the retained population as evidenced exclusions.
- Total records must equal active records plus inactive exclusions.
- Screened records must equal active records.
- Missing files, schema gaps, blank or duplicate primary keys, row count differences, fingerprint differences, missing provenance, or unavailable approvals stop evaluation.

This fail closed design prevents incomplete evidence from producing a misleading clean result. Production connectors should also reconcile each extract to an authoritative source report or signed API control total.

## Rule evaluation

| Rule | Automated signal | Required qualified review |
|---|---|---|
| `RM-01` | Exact identifier or exact normalized name | Verify identity, rule source scope, applicability, and disposition. |
| `RM-02` | Name similarity above the configured threshold | Disambiguate using aliases, identifiers, ownership, address, geography, and other relevant evidence. |
| `RM-03` | Country matches an approved jurisdiction routing condition | Determine policy or legal applicability and whether a response is required. |

Signals are intentionally reported as potential matches. They are not legal conclusions or assertions of noncompliance.

## Evidence and source provenance

The retained evidence package includes:

- the versioned control and rule configuration, including a configuration fingerprint;
- the source manifest, fictional source URI, extraction/query description, timestamp, row count, and SHA-256 fingerprint for every source;
- required field and primary key validation results;
- the full population reconciliation and evidenced inactive exclusions;
- current counsel approvals for every configured rule source;
- the rule evaluated, matching basis, source record, matched rule entry, score, and explanation for every potential match;
- stable exception case IDs and human review checklists; and
- in production, the append only case history, response evidence, approvals, prior and new states, and closure basis.

`output/audit_evidence.json`, `output/potential_matches.csv`, and `output/cases/` are the committed sample evidence. The evidence contract is detailed in [evidence_contract.md](evidence_contract.md).

## Response and governance boundary

The absence of a default remediation policy is intentional. A qualified legal/compliance reviewer determines whether a response is required and, if so, the appropriate response, owner, due date, supporting evidence, approvals, and closure basis.

The automation must not block or permit transactions, contact a third party, select remediation, accept risk, assert legal compliance, or close an exception case. Production access controls should enforce reviewer qualifications and segregation of duties instead of relying only on role text.

The case workflow is:

```text
open -> under_review -> remediation_pending -> closure_pending -> closed
                      \-> closure_pending -----^
```

The `propose_no_match` route ends at `closure_pending`; it does not close automatically. Every action requires a named actor, role, rationale, and evidence reference. Only a qualified legal/compliance reviewer may approve closure.

### Exception case lifecycle requirements

| Requirement | Governance |
|---|---|
| Owner | Compliance Operations owns triage and assignment; a qualified legal/compliance reviewer owns the disposition. |
| Remediation | The qualified reviewer determines whether remediation or another response is required and approves its scope, owner, and evidence. |
| Lookback | The qualified reviewer determines the period and procedures from validated identity, applicability, exposure, and approved policy. |
| Root cause | Document root cause when a confirmed process or control breakdown contributed to the issue or delayed identification. |
| Closure evidence | Retain identity and applicability analysis, response evidence when required, reviewer rationale, supporting references, and qualified closure approval. |
| SLA | No universal remediation SLA is configured; the qualified reviewer assigns a human approved target when a response is required. |
| Escalation | Escalate a case when it exceeds its assigned target, presents urgent facts, or requires leadership attention. |
| Recurrence | Reopen the case or create a linked case and assess whether prior actions or monitoring require revision. |
| Human closure | Automation never closes a case; a qualified legal/compliance reviewer must approve and evidence closure. |

## RCM evidence mapping

| RCM component | Evidence |
|---|---|
| Control design | `config.yaml`, this narrative, and approved source/rule configuration |
| Population completeness | Source manifest, row counts, primary key checks, and population reconciliation |
| Source provenance | Source URI, extraction/query description, timestamp, and SHA-256 fingerprint |
| Rule source governance | Counsel approval records, validity dates, reviewer identity, and scope |
| Operating evidence | Run ID, configuration fingerprint, validation results, rules, and potential matches |
| Investigation | Stable exception case, reviewer identity, rationale, supporting evidence, and disposition |
| Response | Human approved action, owner, due date, and completion evidence when a response is required |
| Closure | Qualified legal/compliance approval and documented closure basis |

## Difference from ITGC vendor management

ITGC vendor and subservice organization management addresses whether critical technology providers are appropriately risk tiered and monitored and whether SOC/ISAE reports, bridge letters, complementary user entity controls, exceptions, and incidents are addressed.

This non ITGC control instead screens third party master records against regulatory/compliance rule sources that counsel has approved. It has different populations, evidence, decision rights, and conclusions. The controls may share inventory integrations, but they are not interchangeable.
