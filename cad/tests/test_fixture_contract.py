"""Bench-fixture geometry contract: pending inputs must prevent release; nothing is guessed."""
import csv, json, math, subprocess, sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cad import fixture_contract as FC  # noqa: E402


def _write_register(tmp_path, mutate):
    rows = list(csv.DictReader(FC.REGISTER.open(encoding="utf-8", newline="")))
    mutate(rows)
    p = tmp_path / "parameters.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return p


def test_committed_contract_is_current():
    assert FC.OUTPUT.read_text() == FC.render(FC.build(FC.load_register())), "run: python cad/fixture_contract.py --refresh"


def test_every_pending_register_row_used_by_the_contract_blocks_a_clause():
    reg = FC.load_register(); c = FC.build(reg)
    pending_rows = {n for n, v in reg.items() if v["state"] == "pending"}
    assert set(c["not_generated_pending_owner_inputs"]) == pending_rows
    assert len(c["pending_clauses"]) == 10 and len(c["evaluable_clauses"]) == 2


def test_groups_cover_interfaces_clearances_and_load_path():
    c = FC.build(FC.load_register())
    assert {cl["group"] for cl in c["clauses"]} == {"interface", "clearance", "load_path"}


def test_derived_values_match_register_arithmetic():
    c = FC.build(FC.load_register()); by = {cl["id"]: cl for cl in c["clauses"]}
    assert math.isclose(by["motor_envelope_volume"]["value"], math.pi / 4 * 13.5**2 * 15.5, rel_tol=1e-12)
    assert by["prop_static_swept_envelope"]["value"] == 52.17
    assert "STATIC" in by["prop_static_swept_envelope"]["note"]


def test_release_refuses_while_pending():
    p = subprocess.run([sys.executable, str(ROOT / "cad/fixture_contract.py"), "--release"], capture_output=True, text=True)
    assert p.returncode == 2 and "INPUTS_INCOMPLETE" in p.stderr and "motor_mount_pattern" in p.stderr and "load_cell_mount_spacing" in p.stderr


def test_filling_a_pending_row_makes_its_clause_evaluable_positive_control(tmp_path):
    def fill(rows):
        for r in rows:
            if r["parameter"] == "stand_anchor_spacing":
                r["value"], r["evidence_state"], r["source"] = "120", "inspection", "synthetic bench measurement"
    c = FC.build(FC.load_register(_write_register(tmp_path, fill)))
    assert "stand_anchor_pattern" in c["evaluable_clauses"] and len(c["pending_clauses"]) == 9


def _fill_all(rows, cap="60", state="inspection", src="synthetic inspection record", promote=False):
    for r in rows:
        if r["evidence_state"] == "pending":
            r["value"] = cap if r["parameter"] == "load_cell_capacity" else ("0.05" if r["parameter"] == "prop_hub_fit_tolerance" else "1")
            r["evidence_state"], r["source"] = state, src
        # distinct measurement records, each naming its datum -- values may coincide
        if r["parameter"] == "authority_arm_measured": r["value"], r["source"] = "0.061", (src + " #ARM-1: vehicle centre to motor axis (datum: frame centre)") if src else ""
        if r["parameter"] == "stand_calibration_lever": r["value"], r["source"] = "0.150", (src + " #LEV-1: pivot to calibration-force line (datum: pivot)") if src else ""
        if promote and r["evidence_state"] in ("vendor_nominal", "model_assumption"):
            r["evidence_state"], r["source"] = "inspection", src


def _release(reg_path):
    p = subprocess.run([sys.executable, str(ROOT / "cad/fixture_contract.py"), "--release", "--parameters", str(reg_path)], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def test_filling_every_pending_row_still_refuses_release_on_unconfirmed_vendor_nominals(tmp_path):
    # Geometry can be complete while the delivered parts are still catalogue values.
    reg_path = _write_register(tmp_path, _fill_all)
    assert not FC.build(FC.load_register(reg_path))["pending_clauses"]
    rc, out = _release(reg_path)
    assert rc == 2 and "INPUTS_COMPLETE_NOT_RELEASE_GRADE" in out and "vendor_nominal" in out


# ── review 2026-09-12: unsupported evidence and numerically wrong inputs were RELEASABLE ──
def test_unsupported_evidence_state_is_refused_not_ranked(tmp_path):
    reg_path = _write_register(tmp_path, lambda rows: _fill_all(rows, cap="0.001", state="not_evidence", src=""))
    with pytest.raises(FC.ContractInputError, match="unsupported evidence_state"):
        FC.load_register(reg_path)
    rc, out = _release(reg_path)
    assert rc == 2 and "INPUTS_UNSUPPORTED" in out


def test_evidence_without_a_source_is_refused(tmp_path):
    reg_path = _write_register(tmp_path, lambda rows: _fill_all(rows, src=""))
    with pytest.raises(FC.ContractInputError, match="no source"):
        FC.load_register(reg_path)


def test_absurd_load_cell_capacity_fails_requirements(tmp_path):
    reg_path = _write_register(tmp_path, lambda rows: _fill_all(rows, cap="0.001", promote=True))
    rc, out = _release(reg_path)
    assert rc == 3 and "REQUIREMENTS_FAILED" in out and "load_cell_capacity_margin" in out


def test_equal_lengths_with_distinct_records_pass_and_shared_record_fails(tmp_path):
    # Review 2 (2026-09-12): equal numbers do not prove reused evidence. Identity is provenance.
    def equal_values_distinct_records(rows):
        _fill_all(rows, promote=True)
        for r in rows:
            if r["parameter"] in ("authority_arm_measured", "stand_calibration_lever"): r["value"] = "0.060"
    rc, out = _release(_write_register(tmp_path, equal_values_distinct_records))
    assert rc == 0 and "REQUIREMENTS_EVALUATED" in out, out
    def same_record(rows):
        _fill_all(rows, promote=True)
        for r in rows:
            if r["parameter"] in ("authority_arm_measured", "stand_calibration_lever"): r["source"] = "synthetic inspection record #X (datum: pivot)"
    rc, out = _release(_write_register(tmp_path, same_record))
    assert rc == 3 and "same source record" in out, out
    def no_datum(rows):
        _fill_all(rows, promote=True)
        for r in rows:
            if r["parameter"] == "stand_calibration_lever": r["source"] = "synthetic inspection record #LEV-1"
    rc, out = _release(_write_register(tmp_path, no_datum))
    assert rc == 3 and "does not name its datum" in out, out


def test_hub_fit_tolerance_is_a_registered_choice_not_a_default(tmp_path):
    reg = FC.load_register()
    assert reg["prop_hub_fit_tolerance"]["state"] == "pending"
    req = FC.evaluate_requirements(reg, FC.build(reg))
    hub = next(r for r in req if r["clause"] == "prop_hub_interface")
    assert hub["status"] == "unresolved" and "design basis" in hub["detail"]
    def tight(rows):
        _fill_all(rows, promote=True)
        for r in rows:
            if r["parameter"] == "prop_hub_fit_tolerance": r["value"] = "0.01"
            if r["parameter"] == "prop_hub_bore": r["value"] = "1.6"
    rc, out = _release(_write_register(tmp_path, tight))
    assert rc == 3 and "prop_hub_interface" in out


def test_release_grade_inputs_with_consistent_numbers_reach_requirements_evaluated_only(tmp_path):
    rc, out = _release(_write_register(tmp_path, lambda rows: _fill_all(rows, promote=True)))
    assert rc == 0 and "REQUIREMENTS_EVALUATED" in out
    assert "INPUT-REVIEW verdict only" in out and "not claimed" in out
    reg = FC.load_register(_write_register(tmp_path, lambda rows: _fill_all(rows, promote=True)))
    req = FC.evaluate_requirements(reg, FC.build(reg))
    assert {r["status"] for r in req} <= {"pass", "unresolved"}
    assert any(r["clause"] == "load_cell_capacity_margin" and r["status"] == "pass" and r["ratio"] > 10 for r in req)
    # requirements needing quantities the register does not hold stay UNRESOLVED, never passed silently
    assert any(r["clause"] == "sensor_deflection_clearance" and r["status"] == "unresolved" for r in req)


def test_pending_row_carrying_a_value_is_refused(tmp_path):
    def poison(rows):
        for r in rows:
            if r["parameter"] == "load_cell_capacity": r["value"] = "50"
    with pytest.raises(FC.ContractInputError, match="pending parameter carries a value"):
        FC.load_register(_write_register(tmp_path, poison))


def test_unit_mismatch_missing_row_and_nonnumeric_are_refused(tmp_path):
    def bad_unit(rows):
        for r in rows:
            if r["parameter"] == "prop_diameter": r["unit"] = "in"
    with pytest.raises(FC.ContractInputError, match="unit mismatch"):
        FC.load_register(_write_register(tmp_path, bad_unit))
    def drop(rows): rows[:] = [r for r in rows if r["parameter"] != "motor_body_length"]
    with pytest.raises(FC.ContractInputError, match="missing from register"):
        FC.load_register(_write_register(tmp_path, drop))
    def text(rows):
        for r in rows:
            if r["parameter"] == "motor_body_diameter": r["value"] = "thirteen"
    with pytest.raises(FC.ContractInputError, match="non-numeric"):
        FC.load_register(_write_register(tmp_path, text))


def test_geometrically_impossible_inputs_are_refused(tmp_path):
    def shrink_prop(rows):
        for r in rows:
            if r["parameter"] == "prop_diameter": r["value"] = "10"
    with pytest.raises(FC.ContractInputError, match="does not clear"):
        FC.build(FC.load_register(_write_register(tmp_path, shrink_prop)))


def test_stale_committed_contract_is_detected(tmp_path):
    def bump(rows):
        for r in rows:
            if r["parameter"] == "motor_body_length": r["value"] = "16.0"
    reg_path = _write_register(tmp_path, bump)
    p = subprocess.run([sys.executable, str(ROOT / "cad/fixture_contract.py"), "--check", "--parameters", str(reg_path)], capture_output=True, text=True)
    assert p.returncode == 1 and "STALE" in p.stderr


def test_cli_check_passes_on_committed_state():
    p = subprocess.run([sys.executable, str(ROOT / "cad/fixture_contract.py"), "--check"], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
