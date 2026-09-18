# Control narrative and RCM mapping

## Purpose and boundary

`RCM-TPRM-001` addresses the risk that a potential regulatory concern present in third party master data is not identified and routed for review. It is a monitoring and workflow control, not a legal opinion. A generated finding means only that a configured signal was observed.

The control does not determine whether a listed entity and a master data entity are the same, whether a rule legally applies, whether a transaction is permitted, whether remediation is sufficient, or whether the organization complies with law or policy.

## Control activity

On the configured cadence, Compliance Operations obtains complete supplier, customer, and business partner master snapshots from AP, CRM, and ERP systems that are in scope. Automation validates source completeness and provenance, verifies that regulatory rule source snapshots have current counsel approval, reconciles the full population, and screens active records. Potential matches are assigned stable case identifiers and routed to qualified legal/compliance reviewers. Reviewers document identity resolution, applicability, disposition, remediation, evidence, and approval. Only a qualified legal/compliance reviewer may approve closure.

## RCM ready attributes

| Attribute | Value |
|---|---|
| Risk | Third party master records may indicate a potential regulatory concern that is not timely identified and routed. |
| Objective | Complete populations are screened against current approved sources, with dispositions that people review and evidence. |
| Owner | Compliance Operations |
| Reviewer | Qualified Legal or Compliance Reviewer |
| Frequency | Daily in production; on demand in the POC |
| Nature | Automated completeness and screening; manual investigation, decision, remediation approval, and closure |
| Population | All extracted records; active records screened, inactive records retained and reconciled as exclusions |
| Precision | Exact identifiers, normalized exact names, configurable fuzzy name threshold, and configured jurisdiction routing |
| Evidence | Source manifest and hashes, approvals, counts, rule configuration, findings, case activity, remediation evidence, closure approval |

## Rule mapping

| Rule | Automated signal | Required human work |
|---|---|---|
| RM-01 | Exact identifier or exact normalized name | Verify identity, rule source scope, applicability, and disposition. |
| RM-02 | Name similarity above the approved threshold | Disambiguate using aliases, identifiers, ownership, address, geography, and other evidence. |
| RM-03 | Country matches an approved jurisdiction routing condition | Determine policy/legal applicability and any required action. |

## Workflow

```text
open -> under_review -> remediation_pending -> closure_pending -> closed
                      \-> closure_pending -----^
```

The alternate `propose_no_match` route still ends at `closure_pending`; it does not close automatically. Each action requires a named actor, role, rationale, and evidence reference. Closure additionally requires a role containing `Legal` or `Compliance`. Production should enforce entitlement groups rather than relying on role text.

## Difference from ITGC vendor management

ITGC vendor/subservice organization management addresses whether critical technology providers are appropriately risk tiered and monitored and whether SOC/ISAE reports, bridge letters, complementary user entity controls, exceptions, and incidents are addressed. This control instead screens third party master records against regulatory/compliance sources that counsel has approved. It has different populations, evidence, decision rights, and conclusions; the two controls must not be represented as interchangeable.
