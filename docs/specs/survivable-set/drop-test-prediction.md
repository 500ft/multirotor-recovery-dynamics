# Study C — Registered Drop-Test Prediction (DR-SS-03)

Status: PREREGISTERED PREDICTION, registered 2026-09-16 — **before any hardware
drop exists**. The point of this file is to be wrong in public if the model is
wrong: every number below was produced by the committed sweeps and is
machine-checked against `Data/survivable_set_results{,_a2}.json` by
`Analysis/tests/test_survivable_set.py`. After the drops, outcomes are compared
against these bounds; editing this file after drop data exists voids the
registration.

## Conditioning gates (must pass first, in order)

1. **EST-REC-007 bench torque** (`Analysis/measured_authority_gate.py`): the
   measured 5th-percentile roll/pitch authority must clear 0.020 N·m over the
   25–75% collective band at 7.0 V. Every prediction below assumes mixer-level
   authority; a bench FAIL invalidates the table and stops the drop campaign.
2. **Release-recovery drop (no failure injected)**: the standing gated
   prediction (`Data/monte_carlo_results.json`, mixer-authority scenario,
   2 rad/s, 60° tilt) is 150/150 recoveries, exact 95% lower bound 0.9802,
   within 3.0 m. This is the repo's core demo and runs before any
   failure-injected drop.

## The registered cell

The cage-testable primary cell: release from **h = 3.0 m**, vz₀ = 0,
tumble **6 rad/s**, detection delay **0.11 s** (`h3_vz0_w6_d0.11`) — chosen in
design.md §2 *because* it is what the 3 m enclosure (OQ-006) can actually
reproduce. Failure injection = commanded motor cut(s) at release
(`Controls/state_machine.json` failsafe path). Landing judged by the
preregistered criteria of design.md §5.

## Predictions (exact 95% Clopper–Pearson bounds, simulation on EST inputs)

Machine-checked table; columns are variant, class, action, successes/n, lower,
upper. Variant `a` = baseline PD, `a2` = spin-aware (design-a2.md).

| variant | class | action | s/n | lower | upper |
|---|---|---|---|---|---|
| a | partial_authority | mechanism | 30/30 | 0.9050 | 1.0000 |
| a | partial_authority | realloc_only | 30/30 | 0.9050 | 1.0000 |
| a | one_out | mechanism | 0/300 | 0.0000 | 0.0099 |
| a | one_out | realloc_only | 0/300 | 0.0000 | 0.0099 |
| a | two_adjacent | mechanism | 0/300 | 0.0000 | 0.0099 |
| a | two_adjacent | realloc_only | 0/300 | 0.0000 | 0.0099 |
| a | two_opposite | mechanism | 0/30 | 0.0000 | 0.0950 |
| a | two_opposite | realloc_only | 0/30 | 0.0000 | 0.0950 |
| a | one_out | parachute | 114/2000 | 0.0487 | 0.0663 |
| a2 | partial_authority | mechanism | 30/30 | 0.9050 | 1.0000 |
| a2 | one_out | mechanism | 0/300 | 0.0000 | 0.0099 |
| a2 | two_adjacent | realloc_only | 0/300 | 0.0000 | 0.0099 |

## What the drops can falsify

* **Positive prediction**: with 60% partial authority injected, the vehicle
  lands survivably — P_safe lower bound 0.905. Ten drops with ≥1 hard failure
  beyond the criterion, or three consecutive hard failures, falsifies the model
  in the direction that matters (over-optimism).
* **Negative prediction**: with one motor cut at a 6 rad/s tumble, the vehicle
  does NOT land survivably (upper bound 0.0099, either controller variant). A
  survivable landing observed in a handful of drops is *good news that the model
  is broken* — it would send the model, not the vehicle, back for repair.
* **Do-not-test prediction**: two adjacent motors out has no surviving thrust
  action; drops for that class are only justified to characterize impact, with
  the vehicle considered expendable.

Parachute rows apply only if the owner adds a descent device (OQ-010); a
decision not to fit one removes those rows without voiding the registration.

## Safety boundary

All failure-injected drops stay inside the netted 3 m enclosure (OQ-006) with
the guard fitted, per `Safety/`. The negative predictions above are the reason
failure injection outside a net is not an option.
