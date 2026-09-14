# Day-4 bounded work — 2026-09-15

Task: owner-decision intake for the bench-fixture register, then DR-CAD-06 preparation.
Base: `358872c` (main, CI green); branch `task/day-four-20260915`. This plan is a proposal
for Owner review, not a status claim: no task ledger row changes state and no gate closes
by this file existing.

**How this PR works:** the Owner edits the `DECISION:` lines below directly in this PR
(review → update). Each filled decision authorizes the matching build step in the work
order. Unfilled decisions stay pending; the release gate keeps refusing, which is correct.

## Track A — Owner decisions (edit in place)

### D1. Measurement route for differential authority (EST-REC-007)
Options:
- **direct-force** — load cell in the thrust line; no calibration lever; register rows
  `stand_calibration_lever` and the lever-vs-arm provenance clause become not-applicable.
- **lever-based** — pivot + calibration lever; requires `stand_calibration_lever` and keeps
  the lever/authority-arm provenance-identity requirement.

```
DECISION: (direct-force | lever-based)
BASIS:
```

### D2. Load cell (`load_cell_capacity`, `load_cell_mount_spacing`)
Prior shortlist: DIY 1–2 kg load-cell rig vs used RCbenchmark 1520. Peak per-motor thrust
context lives in `Engineering Data/` (EX1103 on 2S). Capacity margin is a release clause
(`load_cell_capacity_margin`), so state the overload rating and the drawing source.

```
DECISION (unit + capacity_N + drawing source/URL):
```

### D3. `prop_hub_fit_tolerance`
A fit class with a stated design basis (fit class, retention method, or vendor drawing).
The gate refuses a defaulted 0.05 mm.

```
DECISION (tolerance_mm + design basis):
```

### D4. Vendor-drawing rows (`motor_mount_hole_diameter`, `motor_mount_pitch_circle`,
`motor_mount_thread_engagement`, `prop_mount_screw_spacing`)
Either paste the dimensions with their drawing sources here, or authorize the Agent to
build a sourced candidate sheet (every value tagged confirmed-vs-inferred, drawings
linked) for your sign-off before any value enters the register.

```
DECISION: (values supplied below | agent builds candidate sheet | wait for calipers)
VALUES/SOURCES (if supplied):
```

### D5. DR-CAD-02 — approve bench-only geometry and access

```
DECISION: (approved | changes required | pending)
```

### D6. DR-S09 — review of REVIEW_READY.md

```
FEEDBACK: (or "pending")
```

## Track B — Agent build steps (each gated on its Track A decision)

1. **After D1:** mark not-applicable register rows/clauses for the chosen route in
   `cad/bench/input-requests.csv` and the contract, with the decision recorded as the
   source; rerun `python cad/input_requests.py --check` and `python cad/fixture_contract.py
   --check`.
2. **After D2/D3/D4:** enter each supplied value with its stated source; or deliver the D4
   candidate sheet for sign-off (no value enters the register unsigned).
3. **After D5 (approved):** start DR-CAD-06 — model the propulsion metrology stand and
   protective interfaces against the geometry contract; CI geometry tests must pass.
4. **Always:** rerun `unittest discover -s Analysis/tests`, `pytest cad/tests`,
   `cad/ledger_validator.py live`; update `SPRINT_TASKS.csv`/`CAD_TASKS.csv` only for
   steps actually completed, and retain commands + observed exits in
   `evidence/task-day4-2026-09-15/README.md`.

## Boundary and next gate

Physical rows (`stand_anchor_spacing`, `authority_arm_measured`,
`thrust_expanded_uncertainty`, `arm_expanded_uncertainty`, and `stand_calibration_lever`
if lever-based) stay pending until the bench exists; nothing in this plan authorizes
measurements, spending, powered hardware operation, or a fabricated approval. No guessed
dimensions: a decision line left blank keeps its row pending. If a cited source is
inaccessible, record the exact attempted source and access limit rather than substitute
an unsupported fact. Release stays `REFUSED INPUTS_INCOMPLETE` until the register is
complete — that refusal is the gate working, not a defect.
