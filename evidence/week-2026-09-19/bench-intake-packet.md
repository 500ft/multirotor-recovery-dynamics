# Bench intake packet — first physical-access session (W07, prepared 2026-09-19)

Availability is recorded once: **components and a usable bench are available**
(owner statement, 2026-09-19). Nothing here asks whether hardware exists; it asks
*which* hardware, and records what is observed without power. No entry below is a
measurement, a calibration or an approval until the person at the bench returns it.

Where things go (no new register is created):

| Kind of record | Destination |
| --- | --- |
| What is physically present | [`hardware-inventory.csv`](hardware-inventory.csv) (this folder) |
| Raw non-powered readings, one row per reading | [`interface-observations.csv`](interface-observations.csv) (this folder) |
| Bench sketch: origin, axes, anchors, obstructions, usable volume | `bench-layout.md` (this folder; create on return) |
| Accepted numeric inputs | `cad/bench/parameters.csv` only, via the existing D1–D5 route in [`docs/DAY4_PLAN.md`](../../docs/DAY4_PLAN.md) |
| Owner decisions D1–D6 | `cad/bench/owner-inputs.md` (create only to record an actual decision) |

## Session A–D (≈2–3 h at the bench)

**A. Inventory (20–30 min).** One row per item in `hardware-inventory.csv`: motor
model/KV/revision/count, prop variant, load cell model/rating/revision, bridge/ADC,
ESC/controller, reference masses, force/voltage instruments, dimensional tools. Mark
each `owned / accessible / absent / uncertain`; cite the label or drawing you read
it from; note any existing calibration record. The gate's six-sampled-motor
requirement is separate from how many motors are on the bench — record the count.

**B. Bench layout (20–30 min).** Dimensioned sketch with an origin and axes, usable
surface, actual anchor/clamp locations and spacing, edge distances, obstructions,
available fixture volume, where the load path enters the bench, where cables and
containment could attach. Record units, tool identity and resolution, observer,
date. Anchor spacing feeds `stand_anchor_spacing` only after review; it says
nothing about stability or containment rating.

**C. Non-powered interface inspection (45–75 min).** Choose one datum per part
(motor mount face; prop hub bore axis; cell loaded/fixed end face). For each
accessible feature: hole count, coordinates/clocking, thread designation *only if
a drawing or a thread gauge establishes it*, mounting-face geometry, known
screw/washer/adapter stacks. Take **three independently repositioned readings** of
each key dimension and save all three, not a mean. Do not infer thread pitch from
a caliper diameter, or safe screw penetration from body length. If the cell is not
present, record motor/prop/bench anyway.

**D. Disposition (20–30 min, with Claude).** Returned rows are mapped to D1–D4 and
the gap table in [`cad/bench/fixture-definition.md`](../../cad/bench/fixture-definition.md);
conflicts between delivered parts and [`source-candidates.md`](../../cad/bench/source-candidates.md)
are listed before any value is proposed. Each item gets one of: *accepted for the
named scope / needs clarification / pending*, recorded with the owner's actual
decision — never a manufactured approval.

## Questions returned with the packet, ordered by what they unlock

| # | Unlocks | Question | Notes |
| --- | --- | --- | --- |
| B1 | D1 → route implementation (T03–T08) | Direct axial force, or a lever arrangement? Show the sensor load path for each in plain words. | Direct force was the earlier *proposal*, not a choice. It removes only the `stand_calibration_lever` row; `authority_arm_measured` stays required either way. |
| B2 | D2 → load budget + uncertainty rows | Which exact cell / acquisition chain is owned or intended? Model, revision, both end drawings, operating direction and limits, bridge/ADC, calibration reference, design-load basis. | Reuse the Phidgets 3132_0 entry in `source-candidates.md`; only check sources for *changed* facts. No pricing or ordering unless asked. |
| B3 | D4 → `motor_mount_*`, `prop_mount_screw_spacing` | Which exact motor and prop revisions are on the bench? Any drawing or inspection record for mount holes, threads, depth, hub retention, screw/washer/adapter stacks? | EX1103 mount pattern has no accessible vendor source (C2). Photos and nominal shaft diameter do not establish fit. |
| B4 | D3 → `prop_hub_fit_tolerance` | What *signed* fit and retention requirement is intended, and on what engineering basis? | An absolute diameter difference is not a fit requirement. Leave the number blank if unresolved. |
| B5 | D5–D6 → geometry/calibration/facility review | Who reviews geometry, calibration/uncertainty, and facility readiness — named scope and actual availability? | "Approved" without scope unlocks nothing (DAY4_PLAN R-rules). |

**Arm geometry** is a separate question: if an assembled frame with a defined
center and motor axes exists, record its radius as its own observation. Loose
components → `authority_arm_measured` stays pending. Bench anchor spacing, a stand
lever, or the assumed 60 mm design radius must never fill `arm_m`.

**Calibration record**: if an installed-cell calibration record exists, inspect it
for identity, mounting/load direction, traceable reference, procedure and
uncertainty coverage. If none exists, that is the finding; the calibration plan is
drafted from it. An ordinary workbench is not a calibrated thrust facility.

## Measurement → model map (why each record matters)

| Observation | Feeds | Study it changes |
| --- | --- | --- |
| Thrust curves at 7.0 V (later, powered) | four-motor authority (`measured_authority_gate.py`) | EST-REC-007 gate; every survivable-set number assumes it passes |
| Actual vehicle radius | raw `arm_m`, separate from stand geometry | authority derivation |
| Calibration / alignment / force / radius uncertainties | torque-uncertainty artifact | gate 5th-percentile |
| Guard mass (weighed) and CAD inertia | OQ-010 mechanism credit (`MECH_MASS_G_EST`, `MECH_INERTIA_FRAC`) | mechanism vs reallocation comparison |
| Yaw spin-down behavior (later) | OQ-010 `A2_YAW_DRAG_N_M_S2` | A2 plant assumption (review F01) |
| Impact response (later, separate approved study) | landing-proxy criterion | Study C |

Priority is *which conclusion changes under the stated bracket*, not a probabilistic
value of information — there are no calibrated priors yet.
