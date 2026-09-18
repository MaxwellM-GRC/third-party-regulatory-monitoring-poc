import csv
import json
from pathlib import Path

from src.main import run
from src.reporting import write_outputs


ROOT = Path(__file__).resolve().parents[1]


def test_rcm_outputs_reconcile(tmp_path):
    result, config = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    assert result.input_valid
    write_outputs(result, config, tmp_path)
    evidence = json.loads((tmp_path / "audit_evidence.json").read_text())
    with (tmp_path / "potential_matches.csv").open(newline="") as handle:
        matches = list(csv.DictReader(handle))
    assert evidence["population_reconciliation"]["reconciled"] is True
    assert len(matches) == len(evidence["potential_matches"]) == 3
    assert len(list((tmp_path / "cases").glob("RM-*.md"))) == 3
    assert "not legal conclusions" in evidence["legal_notice"]


def test_control_metadata_preserves_qualified_review_boundary():
    result, config = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    assert result.input_valid
    control = config["control"]
    assert control["category"] == "regulatory_monitoring"
    assert control["risk_category"] == "regulatory_monitoring"
    assert control["risk"].startswith("Failure to ")
    assert control["control_description"].startswith("Management performs")
    assert "qualified legal or compliance reviewer determines" in control["control_description"]
    assert control["activity"]
    assert "default_response" not in config
    assert "rule_responses" not in config


def test_release_metadata_is_complete_without_automated_remediation():
    _, config = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    required_rule_fields = {
        "id", "control_description", "severity", "detection_logic",
        "source_id", "source_provenance", "default_response_guidance",
    }
    assert len({rule["id"] for rule in config["rules"].values()}) == len(config["rules"])
    assert all(required_rule_fields <= set(rule) for rule in config["rules"].values())
    assert all("qualified" in rule["default_response_guidance"].lower() for rule in config["rules"].values())
    required_governance = {
        "owner", "remediation", "lookback", "root_cause", "closure_evidence",
        "sla", "escalation", "recurrence", "human_closure",
    }
    assert required_governance <= set(config["case_governance"])
    assert "automation never closes" in config["case_governance"]["human_closure"].lower()
