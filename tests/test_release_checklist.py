from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_required_control_metadata_and_language():
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    required = {
        "id", "risk_category", "risk", "control_description", "objective",
        "activity", "frequency", "owner",
    }
    assert required <= set(config["control"])
    assert config["control"]["risk"].startswith("Failure to ")
    assert config["control"]["control_description"].startswith("Management performs")


def test_readme_and_required_documents_follow_release_contract():
    readme = (ROOT / "README.md").read_text()
    assert "## What this control tests" in readme
    assert "| Control ID | Control description | Severity |" in readme
    assert all(rule_id in readme for rule_id in ("RM-01", "RM-02", "RM-03"))
    for relative in (
        "docs/evidence_contract.md",
        "docs/rcm_and_control_narrative.md",
        "docs/production_design.md",
    ):
        assert (ROOT / relative).is_file()


def test_shared_core_and_workflow_release_gates():
    requirements = (ROOT / "requirements.txt").read_text()
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    monitor = (ROOT / ".github/workflows/regulatory-monitor.yml").read_text()
    assert "grc-control-core.git@v0.1.0" in requirements
    assert "python -m pytest" in ci
    assert "python -m src.main" in ci
    assert "schedule:" in monitor
    assert "issues: write" in monitor
    assert "output/audit_evidence.json" in monitor
