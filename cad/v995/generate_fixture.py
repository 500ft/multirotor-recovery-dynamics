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

# Land left around a fastener before the relief pocket starts. Design choice:
# it keeps a bearing surface under the bolt head and keeps the pocket from
# intersecting a through-hole.
HOLE_LAND_MM = 1.0

# Parts whose inputs may still be pending. Each lists the register rows it needs;
# the part is emitted when they are all populated and skipped (with the naming of
# the missing rows) when they are not. This is why cradle and base_plate are
# absent today rather than built on invented dimensions.
OPTIONAL_PARTS = {
    "cradle": ("aircraft_capture_width", "aircraft_capture_length",
               "cradle_wall_height", "cradle_wall_thickness",
               "cradle_floor_thickness", "cell_end_hole_spacing",
               "cell_end_hole_diameter"),
    "base_plate": ("bench_anchor_spacing", "bench_anchor_hole_diameter",
                   "base_plate_thickness", "cell_relief_depth",
                   "cell_end_hole_spacing", "cell_end_hole_diameter",
                   "cell_body_width", "adapter_edge_margin"),
}

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


def load_optional(path: Path, names) -> dict | None:
    """Return the named rows only if every one is populated and valid.

    Returns None (and the caller skips the part) when any is pending. A pending
    row is a missing measurement, not a zero.
    """
    rows = {r["parameter"]: r for r in csv.DictReader(path.open(encoding="utf-8"))}
    out = {}
    for name in names:
        row = rows.get(name)
        if row is None or not (row.get("value") or "").strip():
            return None
        try:
            value = float(row["value"])
        except ValueError as exc:
            raise GeometryInputError(f"non-numeric value for {name}: {row['value']!r}") from exc
        if not math.isfinite(value) or value <= 0.0:
            raise GeometryInputError(f"value for {name} must be finite and positive: {value}")
        out[name] = value
    return out


def cradle_dimensions(v: dict) -> dict:
    """U-channel that captures the airframe and bolts to the cell's loaded end.

    Inner width takes the measured capture width directly; the cradle must
    transmit uplift as well as downward load, so retention is a wall, not a
    gravity pocket.
    """
    inner_w = v["aircraft_capture_width"]
    t = v["cradle_wall_thickness"]
    floor_t = v["cradle_floor_thickness"]
    length = v["aircraft_capture_length"]
    wall_h = v["cradle_wall_height"]
    spacing = v["cell_end_hole_spacing"]
    hole_d = v["cell_end_hole_diameter"]
    if spacing + hole_d >= length:
        raise GeometryInputError(
            f"cell bolt pattern ({spacing} mm spacing, {hole_d} mm holes) does not fit "
            f"within a {length} mm cradle floor")
    return {"inner_width_mm": inner_w, "outer_width_mm": inner_w + 2.0 * t,
            "length_mm": length, "wall_height_mm": wall_h,
            "wall_thickness_mm": t, "floor_thickness_mm": floor_t,
            "hole_spacing_mm": spacing, "hole_diameter_mm": hole_d}


def cradle_volume_mm3(d: dict) -> float:
    """Oracle: floor slab + two walls - two through-holes in the floor."""
    floor = d["outer_width_mm"] * d["length_mm"] * d["floor_thickness_mm"]
    walls = 2.0 * d["wall_thickness_mm"] * d["length_mm"] * d["wall_height_mm"]
    holes = 2.0 * (math.pi / 4.0) * d["hole_diameter_mm"] ** 2 * d["floor_thickness_mm"]
    return floor + walls - holes


def base_plate_dimensions(v: dict) -> dict:
    """Plate carrying the cell's fixed end and the bench anchors.

    Includes a relief pocket so the cell's sensing section stays free to deform;
    a parallel force path through the plate would invalidate the measurement.
    """
    cell_sp = v["cell_end_hole_spacing"]
    cell_d = v["cell_end_hole_diameter"]
    anchor_sp = v["bench_anchor_spacing"]
    anchor_d = v["bench_anchor_hole_diameter"]
    margin = v["adapter_edge_margin"]
    width = v["cell_body_width"] + 2.0 * margin
    thickness = v["base_plate_thickness"]
    relief = v["cell_relief_depth"]
    if relief >= thickness:
        raise GeometryInputError(
            f"relief depth {relief} mm would breach a {thickness} mm plate")
    # Explicit left-to-right layout: margin | cell pattern | relief | anchors | margin.
    # Positions are computed here and consumed by the builder, so the two cannot
    # drift apart. (An earlier version placed the pattern centres by a formula and
    # put a cell hole off the edge of the plate; the volume oracle caught it.)
    length = cell_sp + anchor_sp + 4.0 * margin
    relief_len = length - 2.0 * margin - cell_sp - anchor_sp
    if relief_len <= 0.0:
        raise GeometryInputError(
            "no room between the cell pattern and the bench anchors for a relief pocket")
    left = -length / 2.0
    cell_x = (left + margin, left + margin + cell_sp)
    anchor_x = (cell_x[1] + relief_len, cell_x[1] + relief_len + anchor_sp)
    # The pocket must leave land around each fastener, and must not overlap a
    # through-hole: overlapping volumes would be subtracted twice by the oracle
    # AND would remove the bearing surface the bolt needs. (The first version
    # placed the pocket edges exactly on the boundary holes; the volume oracle
    # caught the double-subtraction, 35.54 mm^3 on the synthetic case.)
    relief_span = (cell_x[1] + cell_d / 2.0 + HOLE_LAND_MM,
                   anchor_x[0] - anchor_d / 2.0 - HOLE_LAND_MM)
    relief_len = relief_span[1] - relief_span[0]
    if relief_len <= 0.0:
        raise GeometryInputError(
            "no room for a relief pocket between the cell and anchor patterns once "
            "fastener land is allowed for")
    if anchor_x[1] + margin > length / 2.0 + 1e-9:
        raise GeometryInputError("layout overruns the plate length")
    for x, d in ((cell_x[0], cell_d), (cell_x[1], cell_d),
                 (anchor_x[0], anchor_d), (anchor_x[1], anchor_d)):
        if x - d / 2.0 < left or x + d / 2.0 > -left:
            raise GeometryInputError(f"hole at x={x} (d={d}) falls outside the plate")
    relief_w = v["cell_body_width"]
    if relief_w > width:
        raise GeometryInputError("relief pocket is wider than the plate")
    return {"length_mm": length, "width_mm": width, "thickness_mm": thickness,
            "cell_hole_spacing_mm": cell_sp, "cell_hole_diameter_mm": cell_d,
            "anchor_spacing_mm": anchor_sp, "anchor_hole_diameter_mm": anchor_d,
            "cell_hole_x_mm": list(cell_x), "anchor_hole_x_mm": list(anchor_x),
            "relief_centre_x_mm": (relief_span[0] + relief_span[1]) / 2.0,
            "relief_length_mm": relief_len, "relief_width_mm": relief_w,
            "relief_depth_mm": relief}


def base_plate_volume_mm3(d: dict) -> float:
    """Oracle: plate - 2 cell holes - 2 anchor holes - relief pocket.

    Holes and pocket are placed so they do not intersect (enforced in build()),
    so the terms simply subtract.
    """
    plate = d["length_mm"] * d["width_mm"] * d["thickness_mm"]
    cell_holes = 2.0 * (math.pi / 4.0) * d["cell_hole_diameter_mm"] ** 2 * d["thickness_mm"]
    anchors = 2.0 * (math.pi / 4.0) * d["anchor_hole_diameter_mm"] ** 2 * d["thickness_mm"]
    pocket = d["relief_length_mm"] * d["relief_width_mm"] * d["relief_depth_mm"]
    return plate - cell_holes - anchors - pocket


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


def build_cradle(d: dict):
    import cadquery as cq
    half = d["hole_spacing_mm"] / 2.0
    floor = (cq.Workplane("XY")
             .box(d["length_mm"], d["outer_width_mm"], d["floor_thickness_mm"]))
    wall_y = (d["outer_width_mm"] - d["wall_thickness_mm"]) / 2.0
    walls = (cq.Workplane("XY")
             .pushPoints([(0.0, wall_y), (0.0, -wall_y)])
             .box(d["length_mm"], d["wall_thickness_mm"], d["wall_height_mm"])
             .translate((0, 0, (d["floor_thickness_mm"] + d["wall_height_mm"]) / 2.0)))
    solid = floor.union(walls)
    solid = (solid.faces("<Z").workplane(origin=(0, 0, 0))
             .pushPoints([(-half, 0.0), (half, 0.0)])
             .hole(d["hole_diameter_mm"]))
    return solid


def build_base_plate(d: dict):
    import cadquery as cq
    L, T = d["length_mm"], d["thickness_mm"]
    solid = cq.Workplane("XY").box(L, d["width_mm"], T)
    solid = (solid.faces(">Z").workplane(origin=(0, 0, 0))
             .pushPoints([(x, 0.0) for x in d["cell_hole_x_mm"]])
             .hole(d["cell_hole_diameter_mm"]))
    solid = (solid.faces(">Z").workplane(origin=(0, 0, 0))
             .pushPoints([(x, 0.0) for x in d["anchor_hole_x_mm"]])
             .hole(d["anchor_hole_diameter_mm"]))
    # relief pocket between the two patterns, cut from the top face. It sits
    # strictly between them, so it removes no material a hole already removed and
    # the volume oracle can simply subtract the terms.
    pocket = (cq.Workplane("XY")
              .box(d["relief_length_mm"], d["relief_width_mm"], d["relief_depth_mm"])
              .translate((d["relief_centre_x_mm"], 0.0, (T - d["relief_depth_mm"]) / 2.0)))
    return solid.cut(pocket)


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

    # Optional parts: emitted only when every registered input they need exists.
    optional_out = {}
    for part, names in OPTIONAL_PARTS.items():
        vals = load_optional(Path(args.parameters), names)
        if vals is None:
            rows = {r["parameter"]: r for r in
                    csv.DictReader(Path(args.parameters).open(encoding="utf-8"))}
            missing = [n for n in names
                       if n not in rows or not (rows[n].get("value") or "").strip()]
            optional_out[part] = {"generated": False, "pending_inputs": missing}
            print(f"[skipped] {part}: pending {', '.join(missing)}")
            continue
        if part == "cradle":
            dims, expected, built = cradle_dimensions(vals), None, None
            expected = cradle_volume_mm3(dims)
            built = build_cradle(dims)
        else:
            dims = base_plate_dimensions(vals)
            expected = base_plate_volume_mm3(dims)
            built = build_base_plate(dims)
        m = measure(built)
        part_step = out_dir / f"{part}.step"
        cq.exporters.export(built, str(part_step))
        rt = measure(cq.importers.importStep(str(part_step)))
        optional_out[part] = {"generated": True, "derived_dimensions": dims,
                              "analytic_volume_mm3": expected, "measured": m,
                              "step_roundtrip": rt}
        print(f"[written] {part_step}")
        print(f"  {part}: analytic {expected:.6f} | measured {m['volume_mm3']:.6f} | "
              f"step {rt['volume_mm3']:.6f}")

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
        "optional_parts": optional_out,
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
