import pytest

from src.workflow import CaseAction, transition


def action(name, role="Compliance Analyst"):
    return CaseAction(name, "Fictional Reviewer", role, "Documented rationale", "fictional://case/evidence/1")


def test_happy_path_requires_human_steps():
    status = transition("open", action("triage"))
    status = transition(status, action("request_remediation"))
    status = transition(status, action("submit_remediation"))
    status = transition(status, action("approve_closure", "Qualified Compliance Reviewer"))
    assert status == "closed"


def test_analyst_cannot_approve_closure():
    with pytest.raises(ValueError, match="qualified legal or compliance"):
        transition("closure_pending", action("approve_closure", "Operations Analyst"))


def test_automation_cannot_skip_to_closed():
    with pytest.raises(ValueError, match="not permitted"):
        transition("open", action("approve_closure", "Qualified Legal Reviewer"))


def test_evidence_is_mandatory():
    with pytest.raises(ValueError, match="evidence reference"):
        transition("open", CaseAction("triage", "Reviewer", "Compliance", "Reason", ""))
