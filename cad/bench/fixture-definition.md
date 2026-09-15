# Fixture definition — gap inventory (T11, started 2026-09-15)

Status: **gap inventory only; schema not frozen**. T12 (field/unit/source-to-criterion
freeze) is blocked until the relevant D2–D5 reviews land; per
[DAY4_PLAN.md](../../docs/DAY4_PLAN.md), unknown dimensions and unchosen tolerances
cannot be frozen. Load-path and budget rules follow the plan's R4. Candidate values
live only in [source-candidates.md](source-candidates.md).

Load path to cover end to end: motor/prop → adapter → cell loaded end → cell fixed
end → anchored base, plus cable forces, torque reaction, off-axis loading and
containment attachments (none may bypass or preload the measurement).

## Required fields and their current state

| Field group | Required content | State | Route to close |
| --- | --- | --- | --- |
| Cell identity | Part, revision, delivered serial | candidate (C1) | D2 selection + delivered-part record |
| Cell loaded-end interface | Hole coordinates, thread, engagement depth, datum | partial candidate (C1: 2× M3×0.5 THRU, 7.5 mm derived pitch; end designation unknown) | D2 + drawing confirmation + inspection |
| Cell fixed-end interface | Same as loaded end | partial candidate (C1, same unknowns) | D2 + drawing confirmation + inspection |
| Motor mount interface | Hole count/coordinates/clocking, thread, usable depth | **absent** (C2: no accessible source) | D4: vendor drawing request or caliper inspection |
| Prop/adapter interface | Bore, signed fit limits, retention, side-hole pattern | partial candidate (C3: 1.5 mm nominal bore; no tolerance, no side-hole coordinates) | D3 fit spec + D4 part identity + inspection |
| Screw/washer/adapter stacks | Per-joint stack-up, penetration vs winding clearance | absent | D4 after motor/cell interfaces exist |
| Bench anchors | Anchor pattern, available space, constraints | absent (physical) | D4 `await inspection`; person with access |
| Force-axis datum | Axis definition, allowable offset, measurement method | absent | D5 geometry-scope review |
| Design loads | `F_sensor = F_thrust + F_dead,projected + F_cable + F_transient`; `M_sensor = Σ(r × F) + M_motor`; signed cases, simultaneity, margins vs operating limits | formulas identified (R4); **no numeric case yet** — single-motor design load needs its own sourced basis; the register's 4.2 N total is a four-motor simulation input, not a bench design limit | D2 load-budget record |
| Uncertainty allocation | Target force/geometry uncertainty, bridge/ADC, excitation, sampling, calibration reference | absent (datasheet resolution ≠ budget) | D2 acquisition-chain record |
| Stability/containment | Base reactions, sliding/tipping, fastener engagement, deflection clearances | absent | DR-CAD-06 calculations after geometry definition |
| Inspection methods | Per-feature method and instrument | absent | T12 freeze + D5 |

## Numerical comparisons required at geometry acceptance

Deferred to T13/T14 (fixture verifier + `cad/tests/test_fixture_geometry.py`):
per-interface coordinate comparison, minimum screw penetration and clearance,
force-axis offset, sensor deflection clearance, exclusion envelopes — each against
numeric limits fixed before the model is accepted, with STEP reimport comparison and
negative controls. The nominal motor-envelope contract stays separate.
