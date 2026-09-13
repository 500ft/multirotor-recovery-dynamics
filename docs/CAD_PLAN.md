# SelfStabilizingDrone — revised CAD work orders

Amended 2026-09-06 after source review. Planning only: no CAD, fixture, fabrication or calibration result exists from this amendment.

2026-09-08 update: [DR-CAD-01 input register](../cad/bench/design-inputs.md) is
complete with explicit unknowns; see [verification](../evidence/task-2026-09-08/README.md).
The placement-hold paragraph below records the original draft's state, not the
current main state: these work orders are already on main. Today's authorized
task PR does not authorize modeling with missing inputs or any physical operation.

**MERGE BLOCKED — owner decision pending.** The earlier public-planning cleanup has not been explicitly reversed. This draft PR keeps ledgers on its unmerged branch for review; it does not authorize them on main. See [CAD_REVIEW_DISPOSITION.md](CAD_REVIEW_DISPOSITION.md). Removing details from the current tree does not erase previous public commits.

[CAD_TASKS.csv](CAD_TASKS.csv) is the sole CAD status ledger. [SPRINT_TASKS.csv](SPRINT_TASKS.csv) remains byte-preserved for the earlier integrity sprint. [Scope tiers](specs/cad-development/scope.md) and [reproduction checks](CAD_PLAN_CHECKS.md) describe this amendment, not physical validation.

## Verified source context

The mass-property export is explicitly PENDING and the instrument plan requires pendulum validation. Bench safety names a stand, torque arm and guard but these lack individual design/release tasks.

Inspected source documents:

- [Engineering Data/cad_mass_properties_template.csv](../Engineering%20Data/cad_mass_properties_template.csv)
- [Engineering Data/hardware_interfaces.csv](../Engineering%20Data/hardware_interfaces.csv)
- [Instrumentation/README.md](../Instrumentation/README.md)
- [Instrumentation/propulsion-bench-safety-checklist.md](../Instrumentation/propulsion-bench-safety-checklist.md)


## Revised finish line and priority

Bench torque at 7.0 V first. DR-CAD-01 → bench inputs DR-CAD-02 and tooling DR-CAD-10 → stand DR-CAD-06 → bench release DR-CAD-08. Vehicle inputs/packaging cannot gate that path.

## Tool and verification decision

**Selected design approach:** CadQuery code-CAD for parameterized families and neutral STEP verification; Onshape for hand-modeled fixtures with confirmed owner account/access. No Onshape automation, credentials or paid access is assumed. Agent owns code-CAD generators/tests; Owner or an authorized CAD operator owns interactive Onshape work. Lack of Onshape access blocks only affected fixture modeling and requires a documented alternative, not the entire parameter pipeline.

The dedicated tooling task budgets environment locking and CI setup. Pin actual Python/CadQuery/OCP versions only after a clean isolated install plus STEP export/reimport smoke test. No version, environment or geometry CI is claimed tested today. CadQuery's official [installation](https://cadquery.readthedocs.io/en/stable/installation.html) and [STEP import/export](https://cadquery.readthedocs.io/en/stable/importexport.html) docs establish the chosen workflow, not a completed build.

Required future automated sequence: read reviewed parameters.csv → reject invalid/missing dimensions and units → regenerate native geometry → export STEP → reimport into a fresh process → calculate geometric metrics → assert against predeclared tolerances. Geometry acceptance uses numeric JSON plus source/export identity; retain screenshots only for explanatory views. A golden image or a hash is not a geometry test. Tests include analytic nominal cases, registered bounds and invalid cases; expected values cannot be copied from the candidate's own output. CAD geometry tests do not validate physical stiffness, safety or fatigue.

Proposed commands (files DO NOT exist yet): `python cad/generate.py --parameters <registered-parameters.csv> --output <temporary-output>`; `python -m pytest cad/tests -q`. The tooling task must replace placeholders with actual checked-in defaults and wire CI before a model task can close.

## Rebaselined allocation

**13 estimated hours in the prioritized phase; 24 estimated hours parked.** This supersedes the previous CAD allocation, not the original 30-hour software sprint. Only tasks marked todo are executable now; blocked/parked estimates are not scheduled work. Owner decisions, fabrication lead times and external calibration do not shrink into focused hours.

| Workload day | Hours | Order |
| --- | ---: | --- |
| 1 | 3 | DR-CAD-01 → DR-CAD-02 |
| 2 | 3 | DR-CAD-10 |
| 3 | 5 | DR-CAD-06 |
| 4 | 2 | DR-CAD-08 |

## Individual work orders

IDs retain continuity with the first PR. New IDs represent split inputs, tooling or release tasks; display order is execution priority rather than numerical ID order. Proposed deliverables below are NEW, not present artifacts. Current status exists only in CAD_TASKS.csv.

### DR-CAD-01 — Prepare bench-first mechanical inputs and evidence mapping

- Owner: Agent; priority: P1; estimate: 2 h; day: 1.
- Dependencies: none.
- Proposed output: `NEW cad/bench/parameters.csv; cad/bench/design-inputs.md`.
- Done when: Source motor/prop/load-cell/stand mounting dimensions from actual vendor drawings or owner measurements. hardware_interfaces.csv is a UART/pad register, NOT mounting-pattern evidence. Separate stand axes, effective authority arm_m, measured thrust_n, calibration lever and uncertainty; unknowns remain pending.
- Verification/evidence: Trace dimensions to inspected mechanical sources and map arm_m/thrust_n to docs/specs/measured-authority-gate/evidence-contract.md.

### DR-CAD-02 — Approve bench-only geometry and access

- Owner: Owner; priority: P1; estimate: 1 h; day: 1.
- Dependencies: DR-CAD-01.
- Proposed output: `NEW cad/bench/owner-inputs.md`.
- Done when: Approve selected motor/prop, load cell, bench mounting, effective authority lever, 7.0 V operating envelope, metrology and qualified containment. Battery/electronics layout and complete vehicle CAD are NOT required.
- Verification/evidence: Check actual motor-center geometry, guard and packaging fit drawings, bought-part mass sources, fabrication capability and authorized Onshape source access; bench calibration is handled in DR-CAD-02.

### DR-CAD-10 — Establish code-CAD regeneration and CI geometry tests

- Owner: Agent; priority: P1; estimate: 3 h; day: 2.
- Dependencies: DR-CAD-01.
- Proposed output: `NEW cad/requirements.lock; cad/generate.py; cad/tests/; .github/workflows/cad-geometry.yml`.
- Done when: Use CadQuery for parameter-driven families and neutral STEP checks, Onshape for hand-modeled fixtures after confirming account/access. Pin Python/CadQuery/OCP dependencies after a clean isolated install and export/reimport smoke test. Add geometry CI before accepting a parametric model; screenshots are supplementary, not acceptance.
- Verification/evidence: Proposed commands, NOT YET IMPLEMENTED: python cad/generate.py --parameters <registered-parameters.csv> --output <temporary-output>; python -m pytest cad/tests -q. Assert geometry metrics against a reviewed contract with declared tolerances; prove failure on an altered parameter, invalid dimensions, missing inputs and bad STEP. Retain version lock, numeric JSON and STEP outputs.

### DR-CAD-06 — Model propulsion metrology stand and protective interfaces

- Owner: Agent; priority: P0; estimate: 5 h; day: 3.
- Dependencies: DR-CAD-02;DR-CAD-10.
- Proposed output: `NEW cad/bench/propulsion/ (source, STEP, drawings)`.
- Done when: Specify load-cell mounts, thrust axis, calibrated torque-arm lever, hard mounting/ballast, cable restraint, remote stop access and independent containment interface. Document nominal applied loads and stability calculations; qualified containment is an external input, not a printed-shell claim. Bind actual thrust_n and effective arm_m to the evidence contract, units/datums/calibration and mixer derivation. The stand calibration lever is not automatically the vehicle authority lever. Preserve 7.0 V and registered grid.
- Verification/evidence: Review calibration-load path, tip-over/sliding/fastener assumptions and prop exclusion envelope against the existing safety checklist. Retain review issues; no energized approval implied. Numerically check STEP dimensions, effective lever and load-axis alignment; retain arm/thrust uncertainty and raw-to-tau_rp_n_m mapping.

### DR-CAD-08 — Release bench-only fabrication and calibration-review pack

- Owner: Agent; priority: P1; estimate: 2 h; day: 4.
- Dependencies: DR-CAD-06;DR-CAD-10.
- Proposed output: `NEW cad/bench/release/ (drawings, STEP, calibration mapping)`.
- Done when: Release only stand, qualified-containment interface and instrument datums. Include arm_m/thrust_n mapping, load/stability calculations and pre-run uncertainty requirements. No vehicle packaging/pendulum dependency. Preserve 0.020 N m and 962/1000; no motor operation is authorized.
- Verification/evidence: Reimport STEP and assert critical dimensions; owner reviews actual fabrication/safety/calibration separately.

### DR-CAD-02V — Approve vehicle-only mechanical interfaces

- Owner: Owner; priority: P2; estimate: 1 h; day: conditional.
- Dependencies: DR-CAD-01.
- Proposed output: `NEW cad/vehicle/owner-inputs.md`.
- Done when: After bench authority supports proceeding, confirm four-motor vehicle, battery/electronics and guard interfaces and Onshape source access. This task cannot gate the bench.
- Verification/evidence: Record actual fit-critical drawings, arm_m meaning/calibration and operator/facility availability; no approval is assumed.

### DR-CAD-03 — Model the full vehicle packaging assembly

- Owner: Agent; priority: P2; estimate: 6 h; day: conditional.
- Dependencies: DR-CAD-02V.
- Proposed output: `NEW cad/vehicle/assembly/ (editable source, STEP, layout drawing)`.
- Done when: Model motor mounts, frame, electronics/battery retention, connector service space and wire routing using sourced envelopes. Assign mass basis per part; model all four rotor swept envelopes and retained fasteners.
- Verification/evidence: Retain interference report, top/side/section views and service-access checks at the documented configuration.

### DR-CAD-04 — Model guard attachments and analyze geometric load paths

- Owner: Agent; priority: P2; estimate: 4 h; day: conditional.
- Dependencies: DR-CAD-03.
- Proposed output: `NEW cad/vehicle/guard/ (source, STEP, load-path drawing)`.
- Done when: Detail attachment interfaces, joints and minimum prop clearance over declared tolerance/deflection assumptions; distinguish contact guard from blade-fragment containment. Do not claim a CAD guard is impact-qualified.
- Verification/evidence: Inspect worst-case fit and removal/access; link load paths to Analysis/guard.py assumptions and log mismatches for later analysis.

### DR-CAD-05 — Export CAD mass, CG and inertia with source provenance

- Owner: Agent; priority: P2; estimate: 3 h; day: conditional.
- Dependencies: DR-CAD-03;DR-CAD-04.
- Proposed output: `NEW cad/vehicle/mass-properties.csv; cad/vehicle/mass-reconciliation.md`.
- Done when: Use the existing Engineering Data/cad_mass_properties_template.csv columns; document inertia frame, origin, units, products-of-inertia convention, density/source and uncertain bought-part masses. Keep modeled values separate from measured values.
- Verification/evidence: Reconcile component sums with assembly mass; verify frame translations and symmetric/positive inertia; compare current mass budget without silently overwriting assumed inputs.

### DR-CAD-07 — Model mass-property verification fixture

- Owner: Agent; priority: P2; estimate: 3 h; day: conditional.
- Dependencies: DR-CAD-02V;DR-CAD-05.
- Proposed output: `NEW cad/bench/pendulum/ (source, STEP, datums)`.
- Done when: Define bifilar or trifilar suspension attachment, spacing, suspension-length measurement, body-frame alignment and securing points for a props-off vehicle. Include fixture inertia/tare identification in the measurement plan.
- Verification/evidence: Check support loads and unobstructed small-angle motion; retain dimensioned datums and fixture contribution calculation before an approved calibration run.

### DR-CAD-11 — Release vehicle and inertia-verification pack

- Owner: Agent; priority: P2; estimate: 2 h; day: conditional.
- Dependencies: DR-CAD-04;DR-CAD-05;DR-CAD-07.
- Proposed output: `NEW cad/release/ (BOM, drawings, source/export manifest, inspection plan)`.
- Done when: Include vehicle/bench revisions, material/process and critical fits, assembly/exploded views and inspection checks. List mass-property physical validation and safety approval as unresolved until observed; preserve 0.020 N m and 962/1000 gates.
- Verification/evidence: Reopen neutral exports, compare selected dimensions and mass against native source; review every critical interface and hardware-data dependency.

### DR-CAD-09 — Design a restrained release/synchronization fixture

- Owner: Agent; priority: P2; estimate: 5 h; day: conditional.
- Dependencies: DR-CAD-11.
- Proposed output: `NEW cad/bench/release-fixture/ (source and reviewed concept drawing)`.
- Done when: Only after qualified operator approves a bounded recovery campaign and measured propulsion readiness exists: define restraint, release clearance and common trigger/visible-LED mounts. No free-flight claim or test authorization from CAD.
- Verification/evidence: Review prop/vehicle trajectory envelope and release-failure modes with the facility; record approval separately from geometry.

## Stop and release rules

Do not equate prepared drawings with fabricated/inspected apparatus. Unknown fit-critical dimensions block manufacture. Owner/facility review, actual metrology and prospective reference freezes remain separate gates. No spending, manufacture, pressurization, rotor operation, flight, publication or new third-party drawing disclosure is authorized here.

If time overruns, cut decorative views and already-parked variants first. Keep reference controls, fit/clearance tests, source provenance, filled measurement budgets and pre-load model freeze. Update estimates explicitly rather than claiming blocked hours as progress. Every future public visual needs a source/version, problem explained and CAD-only label.


### DR-CAD-12 — Bench-fixture geometry contract (2026-09-12)

The contract `cad/bench/fixture-preparation.md` requires before any fixture model: twelve clauses
over interfaces (motor pattern, thread engagement, prop hub, load-cell ends, bench anchors),
clearances (static prop swept disc, motor envelope, sensor deflection) and load path (force-axis
datum, capacity margin, calibration lever vs authority arm, thrust uncertainty budget), each bound
to register rows. `--check` gates staleness in the existing CAD job; `--release` returns one of four separable verdicts — `INPUTS_INCOMPLETE`, `INPUTS_COMPLETE_NOT_RELEASE_GRADE`, `REQUIREMENTS_FAILED`, `REQUIREMENTS_EVALUATED` — and only the last exits 0; it is an input-review verdict, never a geometry match or physical validation. Unsupported evidence states and source-less values are refused before any verdict. Separately-measured lengths are checked by provenance identity (distinct records, named datums), never by numerical inequality; the hub fit tolerance is a registered owner design choice. No STEP, no fabrication, no measurement.
