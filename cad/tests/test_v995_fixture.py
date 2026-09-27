"""V995 fixture geometry: oracle, fail-closed behaviour and parameter re-drive.

Follows the engineering-audit CAD briefing: an independent analytic oracle before
trusting the kernel, a parameter re-drive against newly computed expectations, and
a STEP round-trip. Skips cleanly where CadQuery is absent (the analysis CI env).
"""
import csv
import json
import math
from pathlib import Path

import pytest

from cad.v995 import generate_fixture as gf

ROOT = Path(__file__).resolve().parents[2]
PARAMS = ROOT / "cad" / "v995" / "parameters.csv"
CONTRACT = ROOT / "cad" / "v995" / "contract.json"
cq = pytest.importorskip("cadquery", reason="CadQuery not installed in this environment")


def _params(tmp_path, **overrides):
    rows = list(csv.DictReader(PARAMS.open(encoding="utf-8")))
    for r in rows:
        if r["parameter"] in overrides:
            r["value"] = str(overrides[r["parameter"]])
    p = tmp_path / "parameters.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return p


def test_analytic_oracle_matches_the_kernel_and_the_contract():
    params = gf.load_parameters(PARAMS)
    dims = gf.adapter_dimensions(params)
    expected = gf.analytic_volume_mm3(dims)
    measured = gf.measure(gf.build(dims))
    assert measured["n_solids"] == 1
    assert measured["volume_mm3"] == pytest.approx(expected, rel=1e-9)
    contract = json.loads(CONTRACT.read_text())
    assert expected == pytest.approx(contract["expected"]["volume_mm3"], rel=1e-9)
    assert measured["bbox_mm"] == pytest.approx(contract["expected"]["bbox_mm"], abs=1e-9)


def test_step_roundtrip_preserves_volume(tmp_path):
    params = gf.load_parameters(PARAMS)
    dims = gf.adapter_dimensions(params)
    solid = gf.build(dims)
    step = tmp_path / "part.step"
    cq.exporters.export(solid, str(step))
    back = gf.measure(cq.importers.importStep(str(step)))
    assert back["volume_mm3"] == pytest.approx(gf.measure(solid)["volume_mm3"], rel=1e-9)


def test_parameter_redrive_matches_newly_computed_expectation(tmp_path):
    """Briefing item 4: change a named variable to a second admissible value and
    compare against a freshly computed expectation -- not the old one."""
    for thickness in (6.0, 2.5):
        params = gf.load_parameters(_params(tmp_path, adapter_thickness=thickness))
        dims = gf.adapter_dimensions(params)
        assert dims["thickness_mm"] == thickness
        expected = gf.analytic_volume_mm3(dims)
        measured = gf.measure(gf.build(dims))
        assert measured["volume_mm3"] == pytest.approx(expected, rel=1e-9)
        assert measured["bbox_mm"][2] == pytest.approx(thickness, abs=1e-9)


def test_hole_spacing_redrive_moves_the_footprint(tmp_path):
    params = gf.load_parameters(_params(tmp_path, cell_end_hole_spacing=10.0))
    dims = gf.adapter_dimensions(params)
    # length must track the hole pattern, not stay at its registered value
    assert dims["length_mm"] == pytest.approx(10.0 + 2 * 6.0, abs=1e-9)
    measured = gf.measure(gf.build(dims))
    assert measured["bbox_mm"][0] == pytest.approx(dims["length_mm"], abs=1e-9)


@pytest.mark.parametrize("override,reason", [
    ({"adapter_thickness": ""}, "pending"),
    ({"cell_end_hole_diameter": "abc"}, "non-numeric"),
    ({"cell_body_width": "-3"}, "non-positive"),
    ({"cell_end_hole_diameter": "20"}, "hole wider than the section"),
    ({"adapter_edge_margin": "1.0"}, "no material around the hole"),
])
def test_fails_closed_on_bad_inputs(tmp_path, override, reason):
    p = _params(tmp_path, **override)
    with pytest.raises(gf.GeometryInputError):
        gf.adapter_dimensions(gf.load_parameters(p))


def test_register_keeps_evidence_states_and_never_claims_measurement():
    rows = list(csv.DictReader(PARAMS.open(encoding="utf-8")))
    states = {r["evidence_state"] for r in rows}
    assert states <= {"candidate_drawing", "design_choice", "vendor_nominal", "measured"}
    assert "measured" not in states, "no V995 fixture input has been physically measured"
    for r in rows:
        assert r["source"].strip(), f"{r['parameter']} has no source"
        assert r["release_requirement"].strip(), f"{r['parameter']} has no release requirement"


def test_blocked_parts_are_declared_with_reasons():
    assert set(gf.NOT_GENERATED) == {"cradle", "base_plate", "full_assembly"}
    for part, reason in gf.NOT_GENERATED.items():
        assert len(reason) > 30, f"{part} needs a real reason"
