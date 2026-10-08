# Completion reconciliation and bench-input return
Prepared 2026-09-11. Preparation is not fixture release, calibration, measured authority, or permission for powered work. Task status authority: [SPRINT_TASKS.csv](https://github.com/500ft/multirotor-recovery-dynamics/blob/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b/docs/SPRINT_TASKS.csv) and [CAD_TASKS.csv](https://github.com/500ft/multirotor-recovery-dynamics/blob/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b/docs/CAD_TASKS.csv).

## Each recommendation, separately

| Recommendation | What exists | What remains incomplete |
| --- | --- | --- |
| Identify required inputs | [Generated pending-input sheet](../cad/bench/input-requests.csv) and [register](../cad/bench/parameters.csv) | Eleven pending inputs have not been accepted |
| Select a plausible bench route | [Source-backed fixture preparation](../cad/bench/fixture-preparation.md) | Actual cell selection/revision, interfaces, installed load and uncertainty |
| Model nominal motor body | [Generator](../cad/generate.py) and [nominal geometry contract](../cad/contract.json) | Motor envelope is not a mount/stand/vehicle assembly |
| Specify fixture geometry acceptance | Numeric report requirements are written in fixture-preparation.md | No released, populated stand geometry contract or fixture STEP; no measured mount dimensions |
| Establish authority | [Tested evidence contract](specs/measured-authority-gate/evidence-contract.md) and admission code | Real six-motor dataset, physical arm geometry, calibration, uncertainty and review |
| Clear powered work | [Safety checklist](../Instrumentation/propulsion-bench-safety-checklist.md) exists | Facility/operator sign-off and physical safety assessment |
| Close owner gates | Requirements are prepared | DR-S02/DR-S09 and CAD physical-input acceptance remain open |

A numerical synthetic PASS is not a physical PASS. The model radius 0.060 m must not be copied into raw `arm_m`; raw `thrust_n` must not be filled using a vendor thrust table.

## Decisions retained, not silently approved

Keep the bench-first, direct axial thrust-sensing proposal. It isolates the measurement needed by the gate and avoids fabricating an entire vehicle first. Phidgets 3132 remains a proposed cell, not a purchased/delivered/selected part. Capacity must account for installed dead load and transients, not just the largest vendor thrust point.

Do not automatically mark `stand_calibration_lever` as zero or measured for a direct-sensing design. A reviewed applicability amendment is required if that quantity is not used. No change to the register is made by this document.

## One input-return session, followed by real metrology

The input sheet already supplies exact parameter names, units, acquisition routes and required evidence; fill that source rather than create a second numerical register. Base register SHA-256: `37fcd36e3ff9063c923dc8ba327fe6ced1160e9637959360131d58a438777349`.

1. **Identification/decision:** return actual motor/prop/cell model and revision, part-label photos, supplier drawing revision, selected force-sensing layout, and bench mounting constraints. Agent can transcribe an accessible identified vendor drawing as vendor_nominal; it cannot identify your delivered part remotely.
2. **Non-powered inspection:** for each pending interface/arm/anchor parameter, return datum, instrument ID/resolution, units, repeated raw readings, source image/record and uncertainty evaluation. Retain missing or ambiguous observations as pending. Safe screw engagement needs a real depth/stack check, not a guessed pitch circle.
3. **Calibration planning:** identify the instrument/reference/procedure and qualified reviewer. Calibration of the installed load path is a separate physical procedure, not something a ten-minute dimension sitting completes.
4. **Before powered acquisition:** obtain the physical safety review and preregister sampling/operating conditions. A completed form does not authorize motor operation.
5. **After real acquisition:** provide all artifacts required by the existing evidence contract, including the four-motor authority derivation and separately measured vehicle arm. The agent can run the intake and report its result without upgrading the evidence kind.

No fixed ten-minute promise covers calibration, fabrication or uncertainty review. These are dependencies with actual physical effort, not missing software that can be filled by web search.

## Required return fields — all currently unfilled

- Delivered component and drawing identities; source paths: **unfilled**.
- Register rows measured or supplied from drawings; raw records and units: **unfilled**.
- Installed calibration and uncertainty artifacts; reviewer identity/date: **unfilled**.
- Accepted fixture geometry metrics and expected tolerances: **unfilled**.
- Operator/facility/safety approval: **unfilled**.
- Six-motor raw/derived datasets and hashes: **unfilled**.

Smallest unblock action: identify the actual intended parts and provide the non-powered interface/arm measurements with source records. This unlocks a reviewed fixture definition, not a thrust verdict.

## Reproduce the prepared software checks

```sh
python cad/input_requests.py --check
python -m unittest Analysis.tests.test_bench_inputs -v
python -m unittest Analysis.tests.test_measured_authority_gate -q
```

These passed on the base and are rerun in [correction evidence](../evidence/correction-2026-09-11/README.md). Physical measurements, numerical acceptance thresholds and parameter values are unchanged.
