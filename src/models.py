"""Data contracts for inputs, findings, cases, and audit evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class SourceStatus:
    source_id: str
    category: str
    path: str
    source_uri: str = ""
    query: str = ""
    extracted_at: str = ""
    expected_rows: int = 0
    actual_rows: int = 0
    expected_sha256: str = ""
    actual_sha256: str = ""
    missing_columns: list[str] = field(default_factory=list)
    duplicate_keys: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.missing_columns and not self.duplicate_keys

    def to_dict(self) -> dict:
        value = asdict(self)
        value["ok"] = self.ok
        return value


@dataclass(frozen=True)
class MasterRecord:
    source_id: str
    source_system: str
    record_id: str
    legal_name: str
    tax_or_registration_id: str
    country_code: str
    address: str
    active: bool
    source_updated_at: str


@dataclass(frozen=True)
class Finding:
    case_id: str
    control_id: str
    rule_id: str
    severity: str
    source_id: str
    source_system: str
    record_id: str
    third_party_name: str
    country_code: str
    potential_match_type: str
    matched_value: str
    matched_source_entry: str
    rule_source_id: str
    rule_source_reference: str
    match_score: float
    rationale: str
    status: str = "open"
    owner: str = "Compliance Operations"
    disposition: str = "Pending qualified legal/compliance review"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RunResult:
    run_id: str
    statuses: list[SourceStatus]
    findings: list[Finding]
    total_records: int
    active_records: int
    excluded_records: int
    screened_records: int
    approved_rule_sources: list[dict]

    @property
    def input_valid(self) -> bool:
        return bool(self.statuses) and all(status.ok for status in self.statuses)
