import copy
import json
from pathlib import Path

import yaml

from src.integrity import file_sha256, validate_sources


ROOT = Path(__file__).resolve().parents[1]


def config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def test_all_sources_are_complete_and_provenanced():
    statuses, approvals = validate_sources(config(), ROOT, ROOT / "data/source_manifest.json")
    assert all(status.ok for status in statuses)
    assert {row["rule_source_id"] for row in approvals} == {"regulatory_entities", "review_jurisdictions"}


def test_manifest_count_mismatch_fails_closed(tmp_path):
    manifest = json.loads((ROOT / "data/source_manifest.json").read_text())
    manifest["sources"][0]["row_count"] = 999
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    statuses, _ = validate_sources(config(), ROOT, path)
    assert not next(status for status in statuses if status.source_id == "ap_suppliers").ok


def test_missing_current_counsel_approval_fails_rule_source(tmp_path):
    cfg = copy.deepcopy(config())
    approval_source = next(source for source in cfg["sources"] if source["id"] == "counsel_approvals")
    expired = tmp_path / "expired_approvals.csv"
    expired.write_text(
        "approval_id,rule_source_id,approved_by,reviewer_role,approved_at,valid_through,scope,status\n"
        "CA-X,regulatory_entities,Reviewer,Legal,2025-01-01,2025-12-31,test,approved\n"
    )
    approval_source["path"] = str(expired)
    manifest = json.loads((ROOT / "data/source_manifest.json").read_text())
    entry = next(item for item in manifest["sources"] if item["source_id"] == "counsel_approvals")
    entry["row_count"] = 1
    entry["sha256"] = file_sha256(expired)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    statuses, approvals = validate_sources(cfg, ROOT, manifest_path)

    entity_status = next(status for status in statuses if status.source_id == "regulatory_entities")
    jurisdiction_status = next(status for status in statuses if status.source_id == "review_jurisdictions")
    assert "no current counsel approval" in entity_status.errors
    assert "no current counsel approval" in jurisdiction_status.errors
    assert approvals == []
