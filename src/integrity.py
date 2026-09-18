"""Fail closed validation of source completeness, provenance, and rule approval."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path

from .models import SourceStatus


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> tuple[list[dict], set[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def _approval_errors(config: dict, root: Path) -> dict[str, str]:
    as_of = date.fromisoformat(config["review"]["as_of_date"])
    approvals_source = next(source for source in config["sources"] if source["id"] == "counsel_approvals")
    rows, _ = _read_csv(root / approvals_source["path"])
    approved: dict[str, str] = {}
    for row in rows:
        if (
            row["status"].lower() == "approved"
            and date.fromisoformat(row["approved_at"]) <= as_of <= date.fromisoformat(row["valid_through"])
            and row["approved_by"].strip()
            and row["reviewer_role"].strip()
        ):
            approved[row["rule_source_id"]] = row["approval_id"]
    required = {rule["source_id"] for rule in config["rules"].values()}
    return {source_id: "no current counsel approval" for source_id in required - set(approved)}


def validate_sources(config: dict, root: Path, manifest_path: Path) -> tuple[list[SourceStatus], list[dict]]:
    """Validate all configured snapshots and return current source approvals."""
    if not manifest_path.exists():
        return ([SourceStatus(source["id"], source["category"], source["path"], errors=["source manifest is missing"]) for source in config["sources"]], [])

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {entry["source_id"]: entry for entry in manifest.get("sources", [])}
    statuses: list[SourceStatus] = []
    configured_ids = {source["id"] for source in config["sources"]}

    for source in config["sources"]:
        entry = entries.get(source["id"], {})
        path = root / source["path"]
        status = SourceStatus(
            source_id=source["id"], category=source["category"], path=source["path"],
            source_uri=entry.get("source_uri", ""), query=entry.get("query", ""),
            extracted_at=entry.get("extracted_at", ""), expected_rows=entry.get("row_count", 0),
            expected_sha256=entry.get("sha256", ""),
        )
        if not entry:
            status.errors.append("source is absent from manifest")
        if not path.exists():
            status.errors.append("source file is missing")
            statuses.append(status)
            continue
        rows, headers = _read_csv(path)
        status.actual_rows = len(rows)
        status.actual_sha256 = file_sha256(path)
        status.missing_columns = sorted(set(source["required_columns"]) - headers)
        keys = [row.get(source["primary_key"], "").strip() for row in rows]
        status.duplicate_keys = sorted({key for key in keys if key and keys.count(key) > 1})
        if any(not key for key in keys):
            status.errors.append("blank primary key")
        if status.expected_rows != status.actual_rows:
            status.errors.append("manifest row count does not match source")
        if not status.expected_sha256 or status.expected_sha256 != status.actual_sha256:
            status.errors.append("manifest SHA-256 does not match source")
        for field in ("source_uri", "query", "extracted_at"):
            if not getattr(status, field):
                status.errors.append(f"manifest {field} is blank")
        statuses.append(status)

    unexpected = sorted(set(entries) - configured_ids)
    if unexpected and statuses:
        statuses[0].errors.append(f"unexpected manifest sources: {unexpected}")

    approval_errors = _approval_errors(config, root) if all(status.ok for status in statuses) else {}
    for source_id, error in approval_errors.items():
        next(status for status in statuses if status.source_id == source_id).errors.append(error)

    approvals_path = root / next(source["path"] for source in config["sources"] if source["id"] == "counsel_approvals")
    approvals, _ = _read_csv(approvals_path) if approvals_path.exists() else ([], set())
    as_of = date.fromisoformat(config["review"]["as_of_date"])
    current = [
        row for row in approvals
        if row.get("rule_source_id") not in approval_errors
        and row.get("status", "").lower() == "approved"
        and row.get("approved_by", "").strip()
        and row.get("reviewer_role", "").strip()
        and date.fromisoformat(row["approved_at"]) <= as_of <= date.fromisoformat(row["valid_through"])
    ]
    return statuses, current
