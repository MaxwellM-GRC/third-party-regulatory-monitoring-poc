"""Run the fictional third party regulatory monitoring proof of concept."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from .integrity import validate_sources
from .loaders import load
from .models import RunResult
from .reporting import write_outputs
from .screening import screen


ROOT = Path(__file__).resolve().parents[1]


def run(config_path: Path, manifest_path: Path) -> tuple[RunResult, dict]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    statuses, approvals = validate_sources(config, ROOT, manifest_path)
    signature = {
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "sources": [(status.source_id, status.actual_sha256) for status in statuses],
    }
    run_id = "RUN-" + hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()[:16].upper()
    if not statuses or not all(status.ok for status in statuses):
        return RunResult(run_id, statuses, [], 0, 0, 0, 0, approvals), config
    masters, entities, jurisdictions = load(config, ROOT)
    active = [record for record in masters if record.active]
    findings = screen(config, masters, entities, jurisdictions)
    return RunResult(run_id, statuses, findings, len(masters), len(active), len(masters) - len(active), len(active), approvals), config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/source_manifest.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--fail-on-potential-matches", action="store_true")
    args = parser.parse_args(argv)
    result, config = run(args.config, args.manifest)
    write_outputs(result, config, args.output_dir)
    if not result.input_valid:
        for status in result.statuses:
            if not status.ok:
                print(f"INVALID {status.source_id}: {status.errors + status.missing_columns + status.duplicate_keys}")
        return 3
    print(f"{result.run_id}: screened {result.screened_records}/{result.total_records} records; {len(result.findings)} potential matches")
    return 2 if args.fail_on_potential_matches and result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
