#!/usr/bin/env python3
"""Bench-fixture geometry contract for the propulsion thrust stand, derived from the register.

usage: python cad/fixture_contract.py --refresh   # (re)write cad/bench/fixture-contract.json
       python cad/fixture_contract.py --check     # exit 1 if the committed contract is stale
       python cad/fixture_contract.py --release   # exit 2 REFUSED while any clause is pending

This is the contract cad/bench/fixture-preparation.md ("Geometry contract before a model")
requires BEFORE any fixture model exists. It names every interface, clearance and load-path
quantity a fixture model must be compared against, derives the few the register can support
(prop swept envelope from vendor nominal, envelope-only motor volume), and carries every
unmeasured interface as a PENDING clause with its release requirement copied from the
register. It models nothing and measures nothing: a clause becomes evaluable only when its
register row is filled by inspection, a drawing, or an owner decision -- never by this script.
Vendor-nominal rows are evaluable for geometry planning but are labelled so; they are not
inspected values and do not satisfy the "Confirm delivered ..." release requirements.
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "cad/bench/parameters.csv"
OUTPUT = ROOT / "cad/bench/fixture-contract.json"
CONTRACT_VERSION = "2026-09-12"
UNITS = {
    "motor_body_diameter": "mm", "motor_body_length": "mm", "motor_shaft_diameter": "mm",
    "prop_diameter": "mm", "prop_hub_bore": "mm", "prop_hub_fit_tolerance": "mm",
    "motor_mount_pitch_circle": "mm", "motor_mount_hole_diameter": "mm", "motor_mount_thread_engagement": "mm",
    "prop_mount_screw_spacing": "mm", "load_cell_mount_spacing": "mm", "load_cell_capacity": "N",
    "stand_anchor_spacing": "mm", "stand_calibration_lever": "m", "authority_arm_measured": "m",
    "total_thrust_model": "N", "thrust_expanded_uncertainty": "N",
}
STATE_RANK = ["pending", "model_assumption", "vendor_nominal", "reported_vendor_nominal", "design_choice", "inspection", "protocol"]
# The ONLY evidence states a register row may carry. Anything else is refused, not ranked.
ALLOWED_STATES = {"pending", "model_assumption", "vendor_nominal", "reported_vendor_nominal", "design_choice",
                  "inspection", "drawing", "calibration_record", "owner_decision", "protocol"}
# States that make an input RELEASE-GRADE for a fixture model. Vendor nominal and model
# assumptions are planning inputs and never satisfy release; protocol values are frozen by decision.
RELEASE_GRADE = {"inspection", "drawing", "calibration_record", "owner_decision", "protocol"}
PLACEHOLDERS = {"", "tbd", "todo", "x", "?", "n/a", "na", "none", "null", "placeholder", "pending", "unknown", "-"}


class ContractInputError(ValueError):
    """The register cannot support the contract as written. Fail closed."""


def load_register(path: Path = REGISTER) -> dict:
    rows = list(csv.DictReader(Path(path).open(encoding="utf-8", newline="")))
    have: dict = {}
    for row in rows:
        if row["parameter"] in have:
            raise ContractInputError("duplicate parameter in register: " + row["parameter"])
        have[row["parameter"]] = row
    out = {}
    for name, unit in UNITS.items():
        if name not in have:
            raise ContractInputError("required parameter missing from register: " + name)
        r = have[name]
        if r["unit"].strip() != unit:
            raise ContractInputError(f"unit mismatch for {name}: register {r['unit']!r}, contract expects {unit!r}")
        state = r["evidence_state"].strip(); raw = r["value"].strip()
        if state not in ALLOWED_STATES:
            raise ContractInputError(f"unsupported evidence_state {state!r} for {name}; allowed: {sorted(ALLOWED_STATES)}")
        if state != "pending" and r["source"].strip().lower() in PLACEHOLDERS:
            raise ContractInputError(f"{name} carries evidence_state {state!r} with no source; a value without provenance is not evidence")
        if state == "pending":
            if raw:
                raise ContractInputError("pending parameter carries a value; refuse to treat it as measured: " + name)
            out[name] = dict(value=None, state="pending", source=r["source"], release=r["release_requirement"]); continue
        try:
            value = float(raw)
        except ValueError:
            raise ContractInputError(f"non-numeric value for {name}: {raw!r}")
        if not math.isfinite(value) or value <= 0:
            raise ContractInputError(f"value must be finite and positive: {name}={raw}")
        out[name] = dict(value=value, state=state, source=r["source"], release=r["release_requirement"])
    return out


def _state(*names, reg):
    states = [reg[n]["state"] for n in names]
    return min(states, key=lambda s: STATE_RANK.index(s) if s in STATE_RANK else len(STATE_RANK))


def _clause(cid, group, requirement, inputs, reg, *, value=None, unit=None, formula=None, verification=None, note=None):
    pending = [n for n in inputs if reg[n]["state"] == "pending"]
    c = {"id": cid, "group": group, "requirement": requirement, "inputs": list(inputs),
         "status": "pending" if pending else "evaluable",
         "evidence_state": _state(*inputs, reg=reg) if inputs else "protocol"}
    if pending:
        c["pending_inputs"] = pending
        c["release_requirement"] = {n: reg[n]["release"] for n in pending}
    if formula: c["formula"] = formula
    if value is not None: c["value"] = value
    if unit: c["unit"] = unit
    if verification: c["verification"] = verification
    if note: c["note"] = note
    return c


def build(reg: dict) -> dict:
    D, L, ds = (reg[k]["value"] for k in ("motor_body_diameter", "motor_body_length", "motor_shaft_diameter"))
    Dp, bore = reg["prop_diameter"]["value"], reg["prop_hub_bore"]["value"]
    if Dp <= D:
        raise ContractInputError(f"prop diameter {Dp} mm does not clear the motor body {D} mm")
    if ds > bore * 1.5 or ds <= 0:
        raise ContractInputError(f"shaft {ds} mm and hub bore {bore} mm are not a plausible pair")
    Tm = reg["total_thrust_model"]["value"]
    clauses = [
        # ── interfaces ──
        _clause("motor_mount_pattern", "interface", "Fixture motor plate hole coordinates equal the measured EX1103 pattern (pitch circle, hole diameter) within the drawing tolerance",
                ["motor_mount_pitch_circle", "motor_mount_hole_diameter"], reg, unit="mm", verification="Dimensioned drawing or measured hole coordinates with uncertainty"),
        _clause("motor_mount_thread_engagement", "interface", "Screw penetration into the motor bell is at or below the safe depth and at or above the minimum engagement, across the plate + adapter stack",
                ["motor_mount_thread_engagement"], reg, unit="mm", verification="Owner confirms safe penetration; stack drawing lists every plate/washer thickness"),
        _clause("prop_hub_interface", "interface", "Prop hub bore and T-mount screw spacing match the delivered bell; hub bore equals shaft nominal until the delivered shaft is measured",
                ["prop_hub_bore", "motor_shaft_diameter", "prop_mount_screw_spacing", "prop_hub_fit_tolerance"], reg, value={"hub_bore_mm": bore, "shaft_nominal_mm": ds}, unit="mm",
                note="Vendor-nominal bore/shaft are planning values; the mating fit is confirmed only by measuring the delivered shaft and hub."),
        _clause("load_cell_end_interfaces", "interface", "Both load-cell end interfaces (mount spacing, thread, orientation) match the identified, calibrated cell revision",
                ["load_cell_mount_spacing", "load_cell_capacity"], reg, unit="mm", verification="Engineering Data/instrumentation.csv names the cell; its drawing is the source"),
        _clause("stand_anchor_pattern", "interface", "Fixture base anchor pattern equals the measured bench mounting and the documented stability/load path",
                ["stand_anchor_spacing"], reg, unit="mm", verification="Instrumentation/propulsion-bench-safety-checklist.md"),
        # ── clearances ──
        _clause("prop_static_swept_envelope", "clearance", "No fixture, cable or guard element lies inside the static prop swept disc of diameter prop_diameter about the motor axis",
                ["prop_diameter"], reg, value=Dp, unit="mm", formula="static swept diameter = prop_diameter",
                note="STATIC envelope only. Dynamic clearance (blade flap, whirl) and containment envelope are a separately approved addition per the register's release requirement, NOT derived here."),
        _clause("motor_envelope_volume", "clearance", "Motor keep-out cylinder D x L; the only solid cad/generate.py produces today",
                ["motor_body_diameter", "motor_body_length"], reg, value=math.pi / 4 * D**2 * L, unit="mm^3", formula="pi/4 * D^2 * L",
                note="Envelope only (vendor nominal); no mount features are modelled until the pattern is measured."),
        _clause("sensor_deflection_clearance", "clearance", "Load-cell deflection at predicted peak load plus dead load does not close any clearance to a hard stop or preload path",
                ["load_cell_capacity", "total_thrust_model"], reg, unit="mm",
                note=f"Model peak thrust {Tm} N is a planning value (model_assumption); the cell's stiffness comes from its drawing once identified."),
        # ── load path ──
        _clause("force_axis_datum", "load_path", "Thrust axis passes through the load-cell sensitive axis; offset recorded, off-axis moment bounded, never bypassing the cell",
                ["load_cell_mount_spacing"], reg, unit="mm", verification="Interface coordinates in the machine-readable report; cable and containment attachments traced"),
        _clause("load_cell_capacity_margin", "load_path", "Cell capacity exceeds dead load + predicted peak thrust + reaction transients with the owner-selected overload margin",
                ["load_cell_capacity", "total_thrust_model"], reg, unit="N", formula="capacity >= margin * (dead_load + peak_thrust); margin is an owner decision",
                note=f"Planning peak thrust {Tm} N total (model_assumption, per-motor share is a design decision). Dead load and predicted peak are to be recorded separately."),
        _clause("stand_calibration_lever", "load_path", "If a lever-type calibration is used, the perpendicular pivot-to-force-line distance is calibrated and distinct from the vehicle authority arm",
                ["stand_calibration_lever", "authority_arm_measured"], reg, unit="m", verification="docs/specs/measured-authority-gate/evidence-contract.md: arm_m is measured separately from stand calibration"),
        _clause("thrust_uncertainty_budget", "load_path", "The expanded thrust uncertainty artifact exists and covers calibration, alignment and dead-load subtraction before any authority number is computed",
                ["thrust_expanded_uncertainty"], reg, unit="N", verification="Reviewed calibration and uncertainty artifact"),
    ]
    return {
        "family": "propulsion_bench_fixture",
        "contract_version": CONTRACT_VERSION,
        "status": "pending_inputs",
        "source_parameters": "cad/bench/parameters.csv",
        "governing_documents": ["cad/bench/fixture-preparation.md", "cad/bench/design-inputs.md",
                                 "docs/specs/measured-authority-gate/evidence-contract.md", "Instrumentation/propulsion-bench-safety-checklist.md"],
        "release_gate": "Verdicts, in order and never conflated: INPUTS_INCOMPLETE -> INPUTS_COMPLETE_NOT_RELEASE_GRADE (vendor_nominal/model_assumption rows remain) -> REQUIREMENTS_FAILED -> REQUIREMENTS_EVALUATED. Geometry match and physical validation are separate gates. A CAD collision check does not prove structural stability or prop containment.",
        "allowed_evidence_states": sorted(ALLOWED_STATES), "release_grade_states": sorted(RELEASE_GRADE),
        "clauses": clauses,
        "evaluable_clauses": [c["id"] for c in clauses if c["status"] == "evaluable"],
        "pending_clauses": [c["id"] for c in clauses if c["status"] == "pending"],
        "not_generated_pending_owner_inputs": sorted({n for c in clauses for n in c.get("pending_inputs", [])}),
        "vendor_nominal_inputs_awaiting_confirmation": sorted(n for n, v in reg.items() if v["state"] in ("vendor_nominal", "reported_vendor_nominal")),
        "evidence_note": "Derived from the register on the stated version; no fixture STEP exists; nothing here authorises fabrication, spending, pressurisation or rotor operation.",
    }


def evaluate_requirements(reg: dict, contract: dict) -> list[dict]:
    """Numerically evaluate the requirements the register can support. Each result is pass /
    fail / unresolved with the arithmetic shown. 'unresolved' means an input is pending or the
    requirement needs a quantity not in the register (never guessed here)."""
    R = []
    def val(n): return reg[n]["value"]
    def add(cid, status, detail, **kw): R.append(dict(clause=cid, status=status, detail=detail, **kw))
    Tm = val("total_thrust_model")
    cap = val("load_cell_capacity")
    if cap is None:
        add("load_cell_capacity_margin", "unresolved", "load_cell_capacity pending")
    else:
        # Hard floor, no margin chosen for the owner: capacity must at least exceed the model peak thrust.
        ratio = cap / Tm
        add("load_cell_capacity_margin", "pass" if ratio >= 1.0 else "fail",
            f"capacity {cap} N / model peak thrust {Tm} N = {ratio:.3g}; floor is >= 1 (owner margin still to be chosen; dead load not yet recorded)",
            capacity_n=cap, model_peak_thrust_n=Tm, ratio=ratio)
    lever, arm = val("stand_calibration_lever"), val("authority_arm_measured")
    if lever is None or arm is None:
        add("stand_calibration_lever", "unresolved", "stand_calibration_lever and/or authority_arm_measured pending")
    else:
        # The evidence contract requires the two lengths to be measured SEPARATELY. Separate means
        # distinct measurement records with their own datum -- not different numbers: two
        # independent measurements can both read 0.060 m (review 2, 2026-09-12). The check is
        # therefore on provenance identity: source records must differ, and each must name a datum.
        ls, as_ = reg["stand_calibration_lever"]["source"].strip(), reg["authority_arm_measured"]["source"].strip()
        problems = []
        if ls == as_: problems.append("both lengths cite the same source record")
        for n, src in (("stand_calibration_lever", ls), ("authority_arm_measured", as_)):
            if "datum" not in src.lower() and "pivot" not in src.lower() and "center" not in src.lower() and "centre" not in src.lower():
                problems.append(f"{n} source does not name its datum (pivot / vehicle centre)")
        add("stand_calibration_lever", "fail" if problems else "pass",
            ("; ".join(problems) if problems else f"lever {lever} m and authority arm {arm} m carry distinct source records with named datums (equal values are permitted)"),
            lever_m=lever, arm_m=arm, lever_source=ls, arm_source=as_)
    D, Dp = val("motor_body_diameter"), val("prop_diameter")
    add("prop_static_swept_envelope", "pass" if Dp > D else "fail", f"prop {Dp} mm clears motor body {D} mm (static only)")
    bore, shaft, fit = val("prop_hub_bore"), val("motor_shaft_diameter"), val("prop_hub_fit_tolerance")
    if fit is None:
        # The fit tolerance is an engineering choice with a design basis (fit class, retention
        # method, vendor drawing). It is a register row the owner fills; nothing is assumed here.
        add("prop_hub_interface", "unresolved", f"bore {bore} mm vs shaft {shaft} mm recorded; prop_hub_fit_tolerance pending (design basis not yet chosen)")
    else:
        add("prop_hub_interface", "pass" if abs(bore - shaft) <= fit else "fail",
            f"hub bore {bore} mm vs shaft {shaft} mm within the registered fit tolerance {fit} mm (nominal check; delivered parts unmeasured)", fit_tolerance_mm=fit)
        if val("prop_mount_screw_spacing") is None: R[-1]["status"] = "unresolved"; R[-1]["detail"] += "; prop_mount_screw_spacing pending"
    eng = val("motor_mount_thread_engagement")
    if eng is None: add("motor_mount_thread_engagement", "unresolved", "motor_mount_thread_engagement pending")
    else:
        add("motor_mount_thread_engagement", "pass" if 0 < eng < val("motor_body_length") else "fail", f"engagement {eng} mm must be positive and less than the motor body length {val('motor_body_length')} mm (safe depth still an owner confirmation)")
    for cid in ("motor_mount_pattern", "load_cell_end_interfaces", "stand_anchor_pattern", "force_axis_datum", "sensor_deflection_clearance", "thrust_uncertainty_budget"):
        inputs = next(c["inputs"] for c in contract["clauses"] if c["id"] == cid)
        pend = [n for n in inputs if reg[n]["state"] == "pending"]
        add(cid, "unresolved", ("pending: " + ", ".join(pend)) if pend else "requires a drawing / cell datasheet quantity not in the register; not evaluated here")
    add("motor_envelope_volume", "pass", "envelope only; derived value present")
    return R


VERDICTS = {
    "INPUTS_UNSUPPORTED": 2, "INPUTS_INCOMPLETE": 2, "INPUTS_COMPLETE_NOT_RELEASE_GRADE": 2,
    "REQUIREMENTS_FAILED": 3, "REQUIREMENTS_EVALUATED": 0,
}


def verdict(reg: dict, contract: dict) -> tuple[str, list[str]]:
    """Four separable conclusions, never conflated:
         inputs complete  ->  requirements evaluated  ->  (separately) geometry matches  ->  (separately) physical validation.
    This function reaches at most the second."""
    if contract["pending_clauses"]:
        return "INPUTS_INCOMPLETE", [f"pending clause: {c}" for c in contract["pending_clauses"]] + ["pending rows: " + ", ".join(contract["not_generated_pending_owner_inputs"])]
    weak = sorted(n for n, v in reg.items() if v["state"] not in RELEASE_GRADE and v["state"] != "pending")
    if weak:
        return "INPUTS_COMPLETE_NOT_RELEASE_GRADE", [f"{n}: {reg[n]['state']}" for n in weak]
    req = evaluate_requirements(reg, contract)
    failed = [r for r in req if r["status"] == "fail"]
    if failed:
        return "REQUIREMENTS_FAILED", [f"{r['clause']}: {r['detail']}" for r in failed]
    unresolved = [r for r in req if r["status"] == "unresolved"]
    return "REQUIREMENTS_EVALUATED", [f"{r['clause']}: {r['detail']}" for r in unresolved]


def render(contract: dict) -> str:
    return json.dumps(contract, indent=2) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if the committed contract is stale")
    mode.add_argument("--release", action="store_true", help="exit 2 REFUSED while any clause is pending")
    mode.add_argument("--refresh", action="store_true", help="rewrite the committed contract from the register")
    parser.add_argument("--parameters", type=Path, default=REGISTER)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    a = parser.parse_args(argv)
    try:
        reg = load_register(a.parameters)
        contract = build(reg)
    except ContractInputError as e:
        print("REFUSED INPUTS_UNSUPPORTED:", e, file=sys.stderr); return 2
    if a.check:
        if not a.output.exists() or a.output.read_text() != render(contract):
            print("STALE: committed fixture contract does not match the register; run --refresh", file=sys.stderr); return 1
        print(f"fixture contract current: {len(contract['evaluable_clauses'])} evaluable, {len(contract['pending_clauses'])} pending"); return 0
    if a.release:
        v, notes = verdict(reg, contract)
        code = VERDICTS[v]
        stream = sys.stdout if code == 0 else sys.stderr
        head = {"INPUTS_INCOMPLETE": "REFUSED", "INPUTS_COMPLETE_NOT_RELEASE_GRADE": "REFUSED", "REQUIREMENTS_FAILED": "FAILED", "REQUIREMENTS_EVALUATED": "OK"}[v]
        print(f"{head} {v}" + ("\n  - " + "\n  - ".join(notes) if notes else ""), file=stream)
        if code == 0:
            print("  This is an INPUT-REVIEW verdict only. Geometry comparison against a fixture model and physical\n"
                  "  validation are separate gates and are not claimed. Unresolved items above still need owner input.")
        return code
    a.output.write_text(render(contract))
    print(f"wrote {a.output.relative_to(ROOT) if a.output.is_relative_to(ROOT) else a.output}: {len(contract['evaluable_clauses'])} evaluable, {len(contract['pending_clauses'])} pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
