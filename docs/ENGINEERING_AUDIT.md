# Engineering traceability audit (2026-09-25)

Goal: a technically literate reader should be able to see *"this number was
selected because these inputs and assumptions produced this result"* for every
consequential quantity — or see explicitly that it is unresolved.

**Method.** Every row below was checked against the file that defines the value,
not against a summary. No rationale was inferred: where a constant's origin is
not recorded, this audit says so rather than reconstructing a plausible story.
Where a value *is* already derived, that is reported too — the repository does
better than a first glance suggests, and overstating the gap would be its own
error.

## Provenance categories used

`requirement` · `measured input` · `sourced assumption` · `calculated result` ·
`selected design value` · `measured result` · `provisional estimate`

**Evidence status is tracked separately from provenance.** A selected value may
be unverified, analytically assessed, or physically tested. A calculated result
is not a measured result. **No quantity in this repository has status
`measured result`** — no accepted physical measurement exists yet.

## Tier A — derived, with the derivation recorded

These need no work. Listed so the audit is not mistaken for a blanket criticism.

| Quantity | Value | Where derived | Note |
| --- | --- | --- | --- |
| Authority threshold | 0.020 N·m over 25–75 % collective | [`measured-authority-gate/design.md`](specs/measured-authority-gate/design.md) §Authority threshold | Derived from the 225 g full-reserve requirement → 4.41 N total → 3.31 N at 75 % → a 5 mm thrust-line offset gives ≈0.0166 N·m disturbance → 0.020 N·m retains ≈20 % margin. Frozen before data. **This is the standard the rest of the repo should meet.** |
| Mass rollup | best 123.86 / nominal 135.66 / worst 156.0 g | `Analysis/budget.py` + `mass_budget.csv` | Per-item basis, source and status columns; gated by `test_results_numbers` |
| Study parameters (criteria, cells, seeds, kill rule) | various | `specs/survivable-set/design.md`, `design-a2.md`, `scenario-contract.md` | Preregistered before execution, with EST labels and OQ links |
| Landing criterion | 2.0 m/s / 30° (2.5 / 60° guarded) | `design.md` §5 | Explicitly `PREREGISTERED-ASSUMED`, sensitivity variants reported, context added without changing the label |
| Parachute inflation | 0.6 s | `survivable_set.py` | Labelled calibration-against-another-model, with the unresolved terminal-speed mismatch asserted in a test |

## Tier B — purpose stated, derivation absent

`Engineering Data/requirements.csv` carries a one-line `rationale` for each
requirement. Those lines state **what the number is for**, not **why that
number**. A reader cannot tell why 2.0 rather than 1.8, or 225 g rather than 230 g.

| ID | Value | Current rationale | What is missing | Consequence if wrong | Priority |
| --- | --- | --- | --- | --- | --- |
| REQ-PROP-001 | T/W ≥ 2.0 | "Minimum static control authority" | No derivation of the number. **Now supplied as a retrospective assessment** — see `calculations.md` §T/W | Under-specified thrust → hover sits off the authority optimum; over-specified → unnecessary mass/current | **P1 — addressed** |
| REQ-MASS-002 | ≤ 225 g | "Preserves a buffer below the FAA 250 g threshold" | The 25 g buffer is not allocated to anything. What must it absorb? **Structure now supplied, allocation still open** — see `calculations.md` §Abort threshold | Buffer too small → regulatory class breach on build growth; too large → unnecessary design constraint | **P1 — partly addressed** |
| REQ-GUARD-002 | clearance SF ≥ 2.0 | "Prevent prop contact during repeated elastic impacts" | Why 2.0? What variation does it cover? No sensitivity | Prop strike on impact, or over-stiff/over-heavy guard | P2 |
| REQ-GUARD-003 | stress SF ≥ 3.0 | "Account for printed PETG variability" | PETG property scatter is not quantified or sourced; 3.0 not tied to it | Guard fracture, or unnecessary mass | P2 |
| REQ-PWR-001 | ≥ 25 % rail margin | "Prevent FC rail brownout" | Peak peripheral load is not characterised | Brownout in flight | P2 |
| REQ-VISION-002 | ≤ 50 ms | "Limit uncommanded rotation before recovery" | No link from 50 ms to an allowed rotation angle | Detection too slow to matter | P2 |
| REQ-CLASS-001/002/003 | 1 % / 90 % / 0.3 % | handling-event and detection bounds | Not derived from a risk model or trial-count argument | Classifier gates mis-set | P3 |

## Tier C — bare constants, no requirement ID, no recorded rationale

These gate real decisions but are defined only as literals in code.

| Constant | Value | File | Consequence | Priority |
| --- | --- | --- | --- | --- |
| `UNMODELED_HARDWARE_G` | 5.0 g | `Analysis/budget.py:13` | Sets the frozen maximum directly; 5 g is ~3 % of the vehicle | **P1** |
| `roundup_to_5g` | 5 g quantum | `Analysis/budget.py` | Adds up to 5 g on top of the above | P2 |
| `LOWER_QUANTILE` | 0.05 | `measured_authority_gate.py:19` | Chooses how conservative the authority gate is | P2 |
| `MIN_REPEATS_PER_POINT` | 6 | `measured_authority_gate.py:18` | Sets the sampling requirement; an empirical 5th percentile from 6 samples **is the minimum**, not a confidence-qualified bound (already noted in `current-results.md`) | P2 |
| `COLLECTIVE_GRID` | 0.25–0.75 | `measured_authority_gate.py:17` | Defines the band the gate tests; band edges are where the mixer authority formula is weakest | P2 |
| `available_height_m` | 3.0 m | `sim_release_recovery.py` | The whole descent budget; **OQ-006 is open** — no enclosure evidence | **P1, blocked** |
| `arm_m` | 0.060 m | `with_mixer()` | Scales all mixer authority; labelled ASSUMED in the docstring but has no requirement row | **P1, blocked on CAD** |

## What this audit does *not* claim

- It does not reconstruct original design intent. Where a number's origin is not
  recorded, new analysis beside it is a **retrospective assessment** of whether
  the value is defensible, not a claim about why it was first chosen.
- It does not treat added documentation as validation. Nothing here moves any
  quantity to `measured result`.
- Tier B/C entries are not errors. They are decisions whose justification is not
  yet inspectable.

## Actions taken in this pass

1. Calculation blocks in the standard format, **beside the decisions they
   support**, for REQ-PROP-001 and REQ-MASS-002 (`Design Report/calculations.md`).
2. A traceability index ([`TRACEABILITY.md`](TRACEABILITY.md)) linking each major
   decision to its requirement, local analysis, canonical inputs, validation and
   status — without duplicating the mathematics.
3. Tier-C constants given explicit provenance notes at their definitions.
4. Outstanding measurements recorded as tasks rather than guessed.
