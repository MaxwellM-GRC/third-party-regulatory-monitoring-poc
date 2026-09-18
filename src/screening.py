"""Deterministic potential match screening that never makes a legal conclusion."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher

from .models import Finding, MasterRecord


LEGAL_SUFFIXES = {"co", "company", "corp", "corporation", "inc", "limited", "llc", "ltd", "plc"}


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    tokens = [token for token in re.findall(r"[a-z0-9]+", value) if token not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def _active(row: dict, as_of: date) -> bool:
    return date.fromisoformat(row["effective_date"]) <= as_of <= date.fromisoformat(row["expiration_date"])


def _finding(config: dict, record: MasterRecord, rule_id: str, match_type: str, matched_value: str,
             source_entry: str, reference: str, score: float, rationale: str) -> Finding:
    stable = "|".join((rule_id, record.source_id, record.record_id, source_entry, match_type))
    case_id = "RM-" + hashlib.sha256(stable.encode()).hexdigest()[:12].upper()
    return Finding(
        case_id=case_id, control_id=config["control"]["id"], rule_id=rule_id,
        severity=config["rules"][rule_id]["severity"], source_id=record.source_id,
        source_system=record.source_system, record_id=record.record_id,
        third_party_name=record.legal_name, country_code=record.country_code,
        potential_match_type=match_type, matched_value=matched_value,
        matched_source_entry=source_entry, rule_source_id=config["rules"][rule_id]["source_id"],
        rule_source_reference=reference, match_score=round(score, 4), rationale=rationale,
    )


def screen(config: dict, masters: list[MasterRecord], entities: list[dict], jurisdictions: list[dict]) -> list[Finding]:
    as_of = date.fromisoformat(config["review"]["as_of_date"])
    threshold = float(config["review"]["fuzzy_name_threshold"])
    findings: list[Finding] = []
    for record in masters:
        if not record.active:
            continue
        record_name = normalize_name(record.legal_name)
        for entity in entities:
            if not _active(entity, as_of):
                continue
            candidate_names = [entity["entity_name"], *entity["aliases"].split("|")]
            normalized = [(name, normalize_name(name)) for name in candidate_names if name]
            identifier_match = bool(record.tax_or_registration_id and record.tax_or_registration_id == entity["identifier"])
            exact = next(((raw, value) for raw, value in normalized if value == record_name), None)
            best_raw, best_norm = max(normalized, key=lambda pair: SequenceMatcher(None, record_name, pair[1]).ratio())
            score = SequenceMatcher(None, record_name, best_norm).ratio()
            if identifier_match or exact:
                matched = f"identifier:{entity['identifier']}" if identifier_match else f"name:{exact[0]}"
                basis = "exact identifier" if identifier_match else "exact normalized name"
                findings.append(_finding(config, record, "RM-01", basis, matched, entity["source_entry_id"], entity["source_reference"], 1.0,
                    "Potential match only; qualified review must verify identity, scope, applicability, and disposition."))
            elif score >= threshold:
                findings.append(_finding(config, record, "RM-02", "similar normalized name", f"name:{best_raw}", entity["source_entry_id"], entity["source_reference"], score,
                    "Name similarity exceeded the configured threshold; this is not an identity or legal determination."))
        for jurisdiction in jurisdictions:
            if _active(jurisdiction, as_of) and record.country_code == jurisdiction["jurisdiction_code"]:
                findings.append(_finding(config, record, "RM-03", "jurisdiction routing", f"country:{record.country_code}", jurisdiction["jurisdiction_code"], jurisdiction["source_reference"], 1.0,
                    "Configured jurisdiction routing condition met; qualified review must determine applicability and next steps."))
    return sorted(findings, key=lambda item: item.case_id)
