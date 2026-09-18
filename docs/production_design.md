# Cloud native production design

## Reference flow

```text
AP / CRM / ERP snapshots -----> encrypted landing zone -----> completeness gate
Approved rule snapshots ------> versioned policy registry ----> approval gate
                                                               |
                                                               v
                                                   deterministic screening
                                                               |
                          immutable evidence <-----+-----------> case platform
                                                                  |
                                             qualified legal/compliance review
                                                                  |
                                      approved remediation / closure evidence
```

## Service boundaries

- **Extraction:** connectors with read only access and workload identities write immutable, dated snapshots and signed control totals.
- **Policy registry:** compliance owners version rule sources and thresholds; qualified counsel approval is a deployment gate.
- **Screening:** a containerized batch job normalizes and compares records. It emits explainable signals, never legal outcomes.
- **Evidence:** object storage with retention lock holds configurations, manifests, hashes, logs, approvals, findings, and run attestations.
- **Case management:** a managed workflow service enforces segregation of duties, SLAs, escalation, evidence attachment, and approval before closure.
- **Observability:** centralized logs and metrics alert on missing feeds, count drift, stale approvals, rule source expiration, job failure, and cases awaiting triage.

## Security and privacy

Use service identities with least privilege, encryption keys managed by the customer where required, private networking, managed secrets, data field minimization, tokenized identifiers, retention schedules, regional controls, and audited emergency access. Master data can be sensitive; evidence consumers should see only fields needed for investigation.

## Release and change governance

Treat source mappings, normalization behavior, thresholds, and rule sources as controlled changes. Require peer review, automated regression tests, reviewer approval, versioned deployment, and rollback. Test material changes retrospectively against approved synthetic data or data safe for privacy, and record expected precision and recall tradeoffs.

## Operational safeguards

- Stop rather than issue a clean result when a required source or approval is invalid.
- Quarantine malformed records and reconcile them as exceptions; never silently drop them.
- Do not automatically block, pay, onboard, offboard, notify, remediate, accept risk, or close cases.
- Require qualified human decisions for identity, applicability, response, and closure.
- Monitor duplicate and missing cases across reruns using stable identifiers and idempotent integrations.
- Periodically test the control with seeded records and independently reconcile case counts to evidence.
