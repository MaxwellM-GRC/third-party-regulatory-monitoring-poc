from pathlib import Path

import yaml

from src.loaders import load
from src.models import MasterRecord
from src.screening import normalize_name, screen


ROOT = Path(__file__).resolve().parents[1]


def test_legal_suffixes_do_not_prevent_name_match():
    assert normalize_name("Orion Meridian Exports Ltd.") == normalize_name("Orion Meridian Exports")


def test_screening_routes_potential_matches_without_conclusions():
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    masters, entities, jurisdictions = load(config, ROOT)
    findings = screen(config, masters, entities, jurisdictions)
    assert len(findings) == 3
    assert {finding.rule_id for finding in findings} == {"RM-01", "RM-03"}
    assert {finding.record_id for finding in findings} == {"AP-1002", "ERP-3003"}
    assert all("review" in finding.rationale.lower() or "determination" in finding.rationale.lower() for finding in findings)
    assert not any(finding.record_id == "AP-1003" for finding in findings)


def test_case_identifiers_are_stable():
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    masters, entities, jurisdictions = load(config, ROOT)
    first = [finding.case_id for finding in screen(config, masters, entities, jurisdictions)]
    second = [finding.case_id for finding in screen(config, masters, entities, jurisdictions)]
    assert first == second


def test_fuzzy_name_signal_uses_configured_threshold():
    config = yaml.safe_load((ROOT / "config.yaml").read_text())
    _, entities, jurisdictions = load(config, ROOT)
    record = MasterRecord(
        "crm_customers", "CRM", "CRM-X", "Orion Meridan Exports", "UNRELATED", "GB",
        "Fictional address", True, "2026-09-17T00:00:00Z",
    )
    findings = screen(config, [record], entities, jurisdictions)
    assert len(findings) == 1
    assert findings[0].rule_id == "RM-02"
    assert findings[0].match_score >= config["review"]["fuzzy_name_threshold"]
