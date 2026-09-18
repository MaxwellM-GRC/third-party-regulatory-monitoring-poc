"""Load validated fictional master populations and regulatory rule snapshots."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import MasterRecord


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load(config: dict, root: Path) -> tuple[list[MasterRecord], list[dict], list[dict]]:
    masters: list[MasterRecord] = []
    rule_entities: list[dict] = []
    jurisdictions: list[dict] = []
    for source in config["sources"]:
        rows = _rows(root / source["path"])
        if source["category"] == "master_population":
            masters.extend(
                MasterRecord(
                    source_id=source["id"], source_system=source["system"],
                    record_id=row["record_id"], legal_name=row["legal_name"],
                    tax_or_registration_id=row["tax_or_registration_id"],
                    country_code=row["country_code"].upper(), address=row["address"],
                    active=row["active"].lower() == "true", source_updated_at=row["source_updated_at"],
                ) for row in rows
            )
        elif source["id"] == "regulatory_entities":
            rule_entities = rows
        elif source["id"] == "review_jurisdictions":
            jurisdictions = rows
    return masters, rule_entities, jurisdictions
