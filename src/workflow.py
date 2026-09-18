"""Human controlled case state transitions for the POC and production adapters."""

from __future__ import annotations

from dataclasses import dataclass


ALLOWED_TRANSITIONS = {
    "open": {"triage": "under_review"},
    "under_review": {"request_remediation": "remediation_pending", "propose_no_match": "closure_pending"},
    "remediation_pending": {"submit_remediation": "closure_pending"},
    "closure_pending": {"approve_closure": "closed", "reject_closure": "under_review"},
    "closed": {"reopen": "under_review"},
}


@dataclass(frozen=True)
class CaseAction:
    action: str
    actor: str
    actor_role: str
    rationale: str
    evidence_reference: str


def transition(status: str, action: CaseAction) -> str:
    """Apply a documented action, requiring qualified approval to close a case."""
    if not all((action.actor.strip(), action.actor_role.strip(), action.rationale.strip(), action.evidence_reference.strip())):
        raise ValueError("actor, role, rationale, and evidence reference are required")
    next_status = ALLOWED_TRANSITIONS.get(status, {}).get(action.action)
    if not next_status:
        raise ValueError(f"action {action.action!r} is not permitted from {status!r}")
    if action.action == "approve_closure" and not any(term in action.actor_role.lower() for term in ("legal", "compliance")):
        raise ValueError("case closure requires a qualified legal or compliance reviewer")
    return next_status
