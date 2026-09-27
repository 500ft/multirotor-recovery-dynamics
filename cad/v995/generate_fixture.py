#!/usr/bin/env python3
"""Regenerate the V995 whole-aircraft fixture parts from the registered parameter file.

usage: python cad/v995/generate_fixture.py --parameters cad/v995/parameters.csv --output <dir>

Platform: the stock Veeniix V995 (owner decision 2026-09-27). This register is
SEPARATE from cad/bench/parameters.csv, which describes the historical
EX1103/Gemfan single-motor stand and keeps its own gates. No value crosses between
them.

Reads ONLY registered parameters. Fails closed if a parameter is missing, empty
(pending), non-numeric, has the wrong unit, or is geometrically invalid. Writes:
  <dir>/cell_end_adapter.step   neutral STEP export
  <dir>/geometry.json           metrics measured on the CadQuery solid, the same
                                metrics re-measured after STEP re-import, and the
                                analytic expectation

Evidence states carry through: a candidate_drawing or design_choice input does not
become measured by being modelled. Passing the contract means the code regenerates
the registered geometry, not that a delivered part matches it.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

REQUIRED = {
    "cell_end_hole_spacing": "mm",
    "cell_end_hole_diameter": "mm",
    "cell_body_width": "mm",
    "adapter_edge_margin": "mm",
    "adapter_thickness": "mm",
}
FAMILY = "cell_end_adapter"

# Parts deliberately NOT generated, and why. Each names the input that blocks it,
# so the absence is auditable rather than an oversight.
NOT_GENERATED = {
    "cradle": "V995 flight-ready mass, rotor coordinates and contact/retention geometry are unmeasured; the aircraft has not been inspected",
    "base_plate": "stand_anchor_spacing is pending -- no bench/clamp geometry exists",
    "full_assembly": "requires both of the above, plus the delivered load-cell revision and the signed load cases",
}


class GeometryInputError(ValueError):
    """Raised when the registered inputs cannot produce valid geometry. Fail closed."""


def load_parameters(path: Path) -> dict:
    if not path.is_file():
        raise GeometryInputError(f"parameter file not found: {path}")
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    have: dict[str, dict] = {}
    for row in rows:
        name = row["parameter"]
        if name in have:
            raise GeometryInputError(f"duplicate parameter in register: {name}")
        have[name] = row
    out: dict[str, dict] = {}
    for name, unit in REQUIRED.items():
        if name not in have:
            raise GeometryInputError(f"required parameter missing from register: {name}")
        row = have[name]
        raw = (row.get("value") or "").strip()
        if not raw:
            raise GeometryInputError(f"parameter is pending (empty value): {name}")
        if (row.get("unit") or "").strip() != unit:
            raise GeometryInputError(
                f"unit mismatch for {name}: register has {row.get('unit')!r}, expected {unit!r}")
        try:
            value = float(raw)
        except ValueError as exc:
            raise GeometryInputError(f"non-numeric value for {name}: {raw!r}") from exc
        if not math.isfinite(value) or value <= 0.0:
            raise GeometryInputError(f"value for {name} must be finite and positive: {value}")
        out[name] = {"value": value, "unit": unit,
                     "evidence_state": (row.get("evidence_state") or "").strip(),
                     "source": (row.get("source") or "").strip()}
    return out


def adapter_dimensions(p: dict) -> dict:
    """Plate footprint follows from the hole pattern plus the declared edge margin."""
    spacing = p["cell_end_hole_spacing"]["value"]
    hole_d = p["cell_end_hole_diameter"]["value"]
    width = p["cell_body_width"]["value"]
    margin = p["adapter_edge_margin"]["value"]
    thickness = p["adapter_thickness"]["value"]
    length = spacing + 2.0 * margin
    if hole_d >= width:
        raise GeometryInputError(
            f"hole diameter {hole_d} mm does not fit across the {width} mm section")
    if 2.0 * margin <= hole_d:
        raise GeometryInputError(
            f"edge margin {margin} mm leaves no material around a {hole_d} mm hole")
    return {"length_mm": length, "width_mm": width, "thickness_mm": thickness,
            "hole_spacing_mm": spacing, "hole_diameter_mm": hole_d}


def analytic_volume_mm3(d: dict) -> float:
    """Oracle, computed independently of the CAD kernel: plate minus two through-holes."""
    plate = d["length_mm"] * d["width_mm"] * d["thickness_mm"]
    holes = 2.0 * (math.pi / 4.0) * d["hole_diameter_mm"] ** 2 * d["thickness_mm"]
    return plate - holes


def build(d: dict):
    import cadquery as cq
    half = d["hole_spacing_mm"] / 2.0
    solid = (cq.Workplane("XY")
             .box(d["length_mm"], d["width_mm"], d["thickness_mm"])
             .faces(">Z").workplane()
             .pushPoints([(-half, 0.0), (half, 0.0)])
             .hole(d["hole_diameter_mm"]))
    return solid


def measure(solid) -> dict:
    shape = solid.val()
    bb = shape.BoundingBox()
    return {"volume_mm3": shape.Volume(),
            "bbox_mm": [bb.xlen, bb.ylen, bb.zlen],
            "n_solids": len(solid.solids().vals())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parameters", default="cad/v995/parameters.csv")
    ap.add_argument("--output", required=True)
    args = ap.parse_args(argv)

    params = load_parameters(Path(args.parameters))
    dims = adapter_dimensions(params)
    expected_volume = analytic_volume_mm3(dims)

    import cadquery as cq
    solid = build(dims)
    measured = measure(solid)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    step_path = out_dir / f"{FAMILY}.step"
    cq.exporters.export(solid, str(step_path))

    reimported = cq.importers.importStep(str(step_path))
    roundtrip = measure(reimported)

    payload = {
        "family": FAMILY,
        "platform": "veeniix_v995_stock",
        "source_parameters": args.parameters,
        "inputs": {k: v for k, v in params.items()},
        "derived_dimensions": dims,
        "analytic": {"volume_mm3": expected_volume,
                     "bbox_mm": [dims["length_mm"], dims["width_mm"], dims["thickness_mm"]],
                     "n_solids": 1},
        "measured": measured,
        "step_roundtrip": roundtrip,
        "not_generated": NOT_GENERATED,
        "evidence_note": ("Inputs are candidate_drawing or design_choice. Regenerating "
                          "this geometry does NOT confirm the delivered load cell, the "
                          "aircraft, or any load case. No calibration or physical fit is "
                          "claimed."),
    }
    (out_dir / "geometry.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[written] {step_path}")
    print(f"[written] {out_dir / 'geometry.json'}")
    print(f"analytic {expected_volume:.6f} mm^3 | measured {measured['volume_mm3']:.6f} | "
          f"step {roundtrip['volume_mm3']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
