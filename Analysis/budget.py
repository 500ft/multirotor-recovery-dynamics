#!/usr/bin/env python3
"""Roll up the mass budget without treating margin as a component."""

from __future__ import annotations

import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASS_BUDGET = ROOT / "Engineering Data" / "mass_budget.csv"
# Provenance (docs/ENGINEERING_AUDIT.md). REQ-MASS-002. A selected round buffer
# of 25 g (10%) below the 250 g regulatory class boundary; the buffer is NOT
# allocated against quantified contributors. Derivation and what would close it:
# "Design Report/calculations.md" -> Decision: the 225 g abort threshold.
ABORT_THRESHOLD_G = 225.0
# Provenance: BARE CONSTANT -- audit Tier C, priority P1. An allowance for
# hardware not itemised in mass_budget.csv (fasteners, adhesive, wire dressing).
# No requirement ID, and the 5 g is not derived from any itemised estimate. It
# sets the frozen maximum directly, so it is consequential. Do not treat it as
# justified because it is small.
UNMODELED_HARDWARE_G = 5.0


def roundup_to_5g(value: float) -> float:
    return math.ceil(value / 5.0) * 5.0


def load_mass_budget(path: Path = MASS_BUDGET) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rollup(rows: list[dict[str, str]]) -> dict[str, float | bool]:
    best = sum(float(row["best_g"]) for row in rows)
    nominal = sum(float(row["nominal_g"]) for row in rows)
    worst = sum(float(row["worst_g"]) for row in rows)
    frozen_max = roundup_to_5g(worst + UNMODELED_HARDWARE_G)
    return {
        "best_g": best,
        "nominal_g": nominal,
        "worst_g": worst,
        "unmodeled_hardware_g": UNMODELED_HARDWARE_G,
        "proposed_frozen_max_g": frozen_max,
        "nominal_margin_g": frozen_max - nominal,
        "worst_case_closes": worst + UNMODELED_HARDWARE_G <= frozen_max,
        "below_abort_threshold": frozen_max <= ABORT_THRESHOLD_G,
    }


def main() -> None:
    result = rollup(load_mass_budget())
    print("Mass budget rollup (planning estimates)")
    for key, value in result.items():
        print(f"{key}: {value}")
    if not result["below_abort_threshold"]:
        raise SystemExit("FAIL: proposed frozen maximum exceeds 225 g abort threshold")


if __name__ == "__main__":
    main()
