#!/usr/bin/env python3
"""Evaluate the preregistered EST-REC-007 differential-authority gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional


# Provenance notes (docs/ENGINEERING_AUDIT.md). MIN_AUTHORITY_N_M is Tier A --
# derived in docs/specs/measured-authority-gate/design.md from the 225 g
# full-reserve requirement and a 5 mm thrust-line offset, with ~20% margin. The
# four constants around it are Tier C: they gate the same decision but their
# values are not derived anywhere. Recorded here rather than left implicit.
ACCEPTANCE_VOLTAGE_V = 7.0      # REQ-PROP-002: worst permitted loaded pack voltage
COLLECTIVE_GRID = (0.25, 0.375, 0.50, 0.625, 0.75)  # Tier C: band not derived
MIN_REPEATS_PER_POINT = 6       # Tier C: an empirical 5th percentile of 6 samples
                                # IS the minimum, not a confidence-qualified bound
LOWER_QUANTILE = 0.05           # Tier C: conservatism of the gate, not derived
MIN_AUTHORITY_N_M = 0.020       # Tier A: derived, see spec
CALIBRATION_QUANTITIES = {"thrust_n", "voltage_v", "current_a", "temperature_c", "rpm", "time_s", "arm_m"}


@dataclass(frozen=True)
class CollectiveResult:
    collective_fraction: float
    samples: int
    fifth_percentile_tau_n_m: float
    motor_ids: List[str]


@dataclass(frozen=True)
class AuthorityVerdict:
    classification: str
    threshold_n_m: float
    conservative_minimum_n_m: Optional[float]
    voltage_v: float
    points: List[CollectiveResult]
    reasons: List[str]
    evidence_kind: str = "missing"
    numerical_result: Optional[str] = None
    evidence_sha256: Optional[str] = None
    decision_scope: str = "static authority only; not flight readiness or data authenticity"


def mixer_torque_authority(
    total_max_thrust_n: float,
    arm_m: float,
    collective_fraction: float,
) -> float:
    """Four-motor X-frame roll/pitch authority at a collective fraction."""

    if total_max_thrust_n <= 0 or arm_m <= 0:
        raise ValueError("thrust and arm must be positive")
    if not 0.0 <= collective_fraction <= 1.0:
        raise ValueError("collective_fraction must lie in [0, 1]")
    per_motor_max = total_max_thrust_n / 4.0
    per_motor_collective = collective_fraction * per_motor_max
    differential_headroom = min(
        per_motor_collective,
        per_motor_max - per_motor_collective,
    )
    return 2.0 * math.sqrt(2.0) * arm_m * differential_headroom


def minimum_authority_over_band(total_max_thrust_n: float, arm_m: float) -> float:
    """Minimum authority on the closed 25–75% collective interval."""

    return min(
        mixer_torque_authority(total_max_thrust_n, arm_m, fraction)
        for fraction in (COLLECTIVE_GRID[0], COLLECTIVE_GRID[-1])
    )


def _empirical_lower_quantile(values: List[float], quantile: float) -> float:
    if not values:
        raise ValueError("at least one sample is required")
    ordered = sorted(values)
    index = max(0, int(math.ceil(quantile * len(ordered))) - 1)
    return ordered[index]


def _finite(value: object) -> float:
    if isinstance(value, bool):
        raise ValueError("boolean is not a measurement")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError("measurement overflows finite representation") from exc
    if not math.isfinite(number):
        raise ValueError("nonfinite measurement")
    return number


def _within(value: float, target: float, tolerance: float) -> bool:
    """Inclusive acquisition tolerance, allowing only floating-point roundoff."""
    return abs(value - target) <= tolerance + 4 * math.ulp(max(abs(value), abs(target)))


def _text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonempty string identifier required")
    return value.strip()


def _artifact(root: Path, item: object) -> Path:
    if not isinstance(item, dict):
        raise ValueError("artifact requires path and sha256")
    relative = Path(_text(item["path"]))
    path = (root / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(root):
        raise ValueError("artifact must be inside the manifest directory")
    digest = _text(item["sha256"])
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("missing or checksum-mismatched artifact: " + str(relative))
    if path.stat().st_size == 0:
        raise ValueError("empty artifact: " + str(relative))
    return path


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if not headers or len(set(headers)) != len(headers):
            raise ValueError("CSV has missing or duplicated headers")
        records = list(reader)
    if any(None in row or None in row.values() for row in records):
        raise ValueError("CSV row length does not match header")
    return records


def _load_evidence(path: Path, rows: List[Dict[str, object]]):
    """Validate supplied bundle consistency, not whether its assertions are true."""
    root = path.resolve().parent
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("manifest schema_version must be integer 1")
    if manifest.get("evidence_kind") not in ("measured", "synthetic"):
        raise ValueError("evidence_kind must be measured or synthetic")
    motors = manifest["motor_ids"]
    if not isinstance(motors, list) or len(motors) != 6:
        raise ValueError("roster must contain the six sampled motors (four-motor craft)")
    motors = [_text(motor) for motor in motors]
    if len(set(motors)) != 6:
        raise ValueError("motor roster must be distinct")
    quantities = manifest["calibration_quantities"]
    if not isinstance(quantities, list) or not CALIBRATION_QUANTITIES.issubset(set(quantities)):
        raise ValueError("calibration quantity coverage incomplete")
    calibration_id = _text(manifest["calibration_id"])
    review = manifest["review"]
    if review["status"] != "accepted":
        raise ValueError("owner evidence review must be accepted")
    _text(review["reviewer"])
    date.fromisoformat(_text(review["reviewed_on"]))
    artifacts = manifest["artifacts"]
    paths = {name: _artifact(root, artifacts[name]) for name in
             ("derived", "raw", "calibration", "uncertainty", "derivation")}
    if _read_csv(paths["derived"]) != [{key: str(value) for key, value in row.items()} for row in rows]:
        raise ValueError("supplied rows differ from hashed derived CSV")
    raw = {}
    for record in _read_csv(paths["raw"]):
        identity = _text(record["record_id"])
        if identity in raw:
            raise ValueError("duplicate raw record_id")
        if _text(record["motor_id"]) not in motors or record["calibration_id"] != calibration_id:
            raise ValueError("raw record motor/calibration does not match manifest")
        values = {key: _finite(record[key]) for key in CALIBRATION_QUANTITIES | {"collective_fraction"}}
        if (values["voltage_v"] <= 0 or values["arm_m"] <= 0 or values["temperature_c"] <= -273.15
                or not 0 <= values["collective_fraction"] <= 1
                or any(values[key] < 0 for key in ("thrust_n", "current_a", "rpm", "time_s"))):
            raise ValueError("raw telemetry contains unphysical values")
        raw[identity] = record
    return manifest, set(motors), raw


def evaluate_rows(rows: Iterable[Dict[str, object]], evidence_path: Optional[Path] = None) -> AuthorityVerdict:
    """Evaluate uncertainty-adjusted samples; absence of evidence cannot PASS."""

    rows = list(rows)
    by_collective: Dict[float, List[float]] = {point: [] for point in COLLECTIVE_GRID}
    motors_by_collective = {point: set() for point in COLLECTIVE_GRID}
    reasons = []
    manifest, motors, raw = {}, set(), {}
    evidence_digest = None
    if evidence_path is None:
        reasons.append("evidence manifest missing; three numeric columns cannot authorize a verdict")
    else:
        try:
            evidence_path = Path(evidence_path)
            manifest, motors, raw = _load_evidence(evidence_path, rows)
            evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            reasons.append("evidence incomplete or inconsistent: {}".format(exc))
    sample_ids, raw_ids = set(), set()
    for index, row in enumerate(rows, 1):
        try:
            voltage = _finite(row["voltage_v"])
            collective = _finite(row["collective_fraction"])
            torque = _finite(row["tau_rp_n_m"])
            uncertainty = _finite(row["expanded_uncertainty_n_m"])
        except (KeyError, TypeError, ValueError) as exc:
            reasons.append("row {} has missing/invalid numeric data: {}".format(index, exc))
            continue
        if voltage <= 0 or not 0 <= collective <= 1 or torque < 0 or uncertainty < 0:
            reasons.append("row {} has unphysical measurement values".format(index))
            continue
        try:
            sample_id = _text(row["sample_id"])
            raw_id = _text(row["raw_record_id"])
            motor_id = _text(row["motor_id"])
            if sample_id in sample_ids or raw_id in raw_ids:
                raise ValueError("duplicate derived sample or reused raw observation")
            sample_ids.add(sample_id)
            raw_ids.add(raw_id)
            source = raw[raw_id]
            if motor_id not in motors or source["motor_id"] != motor_id:
                raise ValueError("derived motor does not match raw source")
            if not all(math.isclose(value, _finite(source[field]), abs_tol=1e-9, rel_tol=0)
                       for field, value in (("voltage_v", voltage), ("collective_fraction", collective))):
                raise ValueError("derived operating point does not match raw source")
        except (KeyError, TypeError, ValueError) as exc:
            reasons.append("row {} has invalid provenance: {}".format(index, exc))
            continue
        if not _within(voltage, ACCEPTANCE_VOLTAGE_V, 0.05):
            continue
        match = min(COLLECTIVE_GRID, key=lambda point: abs(point - collective))
        if _within(collective, match, 0.002):
            by_collective[match].append(max(0.0, torque - uncertainty))
            motors_by_collective[match].add(motor_id)

    point_results = []
    for point in COLLECTIVE_GRID:
        values = by_collective[point]
        if motors_by_collective[point] != motors or len(motors_by_collective[point]) != 6:
            reasons.append("collective {:.3f} lacks six-motor coverage".format(point))
        if len(values) < MIN_REPEATS_PER_POINT:
            reasons.append(
                "collective {:.3f} has {} samples; {} required".format(
                    point, len(values), MIN_REPEATS_PER_POINT
                )
            )
            continue
        point_results.append(
            CollectiveResult(
                collective_fraction=point,
                samples=len(values),
                fifth_percentile_tau_n_m=_empirical_lower_quantile(values, LOWER_QUANTILE),
                motor_ids=sorted(motors_by_collective[point]),
            )
        )

    if reasons:
        return AuthorityVerdict(
            classification="INCONCLUSIVE",
            threshold_n_m=MIN_AUTHORITY_N_M,
            conservative_minimum_n_m=None,
            voltage_v=ACCEPTANCE_VOLTAGE_V,
            points=point_results,
            reasons=reasons,
            evidence_kind=manifest.get("evidence_kind", "missing"),
            evidence_sha256=evidence_digest,
        )

    conservative = min(point.fifth_percentile_tau_n_m for point in point_results)
    if conservative >= MIN_AUTHORITY_N_M:
        classification = "PASS"
        reasons.append("uncertainty-adjusted empirical fifth percentile clears 0.020 N m at every grid point")
    else:
        classification = "FAIL"
        reasons.append("uncertainty-adjusted empirical fifth percentile falls below 0.020 N m in the band")
    numerical_result = classification
    if manifest["evidence_kind"] == "synthetic":
        classification = "DEVELOPMENT_ONLY"
        reasons.append("synthetic fixture is not a physical gate result")
    reasons.append("empirical quantile is not a confidence-qualified population bound; source assertions require human review")
    return AuthorityVerdict(
        classification=classification,
        threshold_n_m=MIN_AUTHORITY_N_M,
        conservative_minimum_n_m=conservative,
        voltage_v=ACCEPTANCE_VOLTAGE_V,
        points=point_results,
        reasons=reasons,
        evidence_kind=manifest["evidence_kind"],
        numerical_result=numerical_result,
        evidence_sha256=evidence_digest,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="derived authority CSV with sample/source/motor IDs and expanded uncertainty")
    parser.add_argument("--manifest", type=Path, help="version-1 source/calibration/uncertainty evidence manifest")
    parser.add_argument("--output", type=Path, help="optional verdict JSON")
    args = parser.parse_args()
    try:
        verdict = evaluate_rows(_read_csv(args.csv), evidence_path=args.manifest)
    except (OSError, ValueError) as exc:
        verdict = AuthorityVerdict("INCONCLUSIVE", MIN_AUTHORITY_N_M, None, ACCEPTANCE_VOLTAGE_V, [], [str(exc)])
    payload = json.dumps(asdict(verdict), indent=2, sort_keys=True, allow_nan=False)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2, "DEVELOPMENT_ONLY": 3}[verdict.classification]


if __name__ == "__main__":
    raise SystemExit(main())
