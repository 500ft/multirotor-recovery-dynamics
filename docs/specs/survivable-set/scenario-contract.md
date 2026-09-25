# DR-SS-SCENARIO-01 — in-flight failure scenario correction

Status: **registration, frozen 2026-09-25 before the diagnostic was executed.**
Depends on PR #37 (`docs/scope-consistency-20260924`, head `a0b9aac`), from whose
head this work branches; rebase and re-check once #37 merges.

## Objective

Quantify the change caused by **retaining healthy-rotor thrust** during the
pre-reconfiguration interval, and separately the effect of **removing the
historical motor-start dead time**. Simulation on the historical design profile.
**Not** measured V995 performance, and not a claim about any real failure.

## Registration decisions

**R01 — fault abstraction.** `idealized_effectiveness_loss`: the selected rotors
lose thrust **and** their modelled reaction torque at `t_fault = 0`. No airframe
mass/inertia jump, ejected-object impulse, rotor angular-momentum impulse,
locked-rotor drag change, windmilling, voltage transient or controller brownout
is modelled. This is the simplest fault model available while the hardware
mechanism is unknown; it is **not** a validated motor stop, propeller loss or
power loss, and must not be described as one.

**R02 — mechanism vs indices.** `one_out`, `two_adjacent`, `two_opposite` are
**topology labels**: they say which outputs disappear, not why. `partial_authority`
keeps its existing meaning — a **60 % per-rotor cap on all four**, *not* a
multiplicative 60 % effectiveness. A cap can leave hover commands untouched; a
multiplier cannot. Implemented as `min(f, cap)` and pinned by an anchor test.
*(An earlier implementation of this branch multiplied instead of clipping; the
anchor caught it before any sweep ran.)*

**R03 — pre-fault actuator state.** Solve a healthy four-rotor equilibrium per
dispersed vehicle in the dynamics' own conventions
(`failure_allocation.solve_healthy_trim`): `Σf = mg`, and
`B_moment f + τ_cg(Σf) + bias = 0`, subject to `0 ≤ f_i ≤ cap`. With zero CG
offset and zero bias this returns `mg/4` per rotor. **Infeasible trims are
recorded as `trim_infeasible`, never silently replaced by equal thrust and never
dropped from the denominator**; attempted, feasible and conditional counts are
reported separately.

**R04 — initial motion, two cohorts with different claims.**
*Anchor cohort*: level, zero angular and linear velocity, healthy trim, fault at
t=0. *Matched diagnostic cohort*: retains the historical sampled tilt, tumble and
vertical speed at t=0 while initialising actuators from level healthy trim —
labelled **prescribed upset at fault**, not steady trimmed hover. It isolates
scenario mechanics against the same starting motion as the existing map. Neither
cohort claims the sampled states are a distribution of naturally occurring faults.

**R05 — healthy motors before detection.** Healthy commands equal their pre-fault
values through `t_switch`. Body force **and all three moments** are derived from
the realized rotor vector via the shared wrench map
(`failure_allocation.healthy_wrench_map`) — retaining ¾ of collective while
applying zero roll/pitch/yaw torque would not be rotor-loss physics. CG and bias
moments and body drag continue under their declared model.

**R06 — event clocks.** Fault onset is t=0. Detection delay is *fault onset →
fault identity available*; correct identity at detection is **assumed for this
study** (missed or wrong detection is out of scope, not established performance).
Fault-aware allocation starts at `t_switch`. Requested and realized switch times
are both logged; a delay off the integration grid is tested.

**R07 — actuator response.** Instantaneous commanded-thrust tracking after the
switch — explicitly an **ideal-actuation** case. Healthy motors are already
running, so the release spool-up dead time does not apply to them. Failed outputs
stay zero. All legacy timing is retained in the `release_startup` path. No
unidentified V995 lag parameter enters the primary claim.

**R08 — controller memory.** The recovery integral state is initialised to zero
at the transition, preserving the legacy transition controller. This is a
**reset-controller baseline**, not evidence of a seamless stock handover.

**R09 — outputs.** Regulation, contact-before-regulation and touchdown proxy stay
separate concepts. The primary outcome remains the **frozen touchdown proxy**. No
new reduced-attitude acceptance threshold is invented; unregistered regulation
success is reported as unavailable. The `‖ω‖ < 0.3` settling detector **cannot**
judge spinning equilibria and is not reused as a success flag.

**R10 — causal scope.** Controller gains, allocator version, parameter draws,
package definitions, guard criteria, drag coefficient and outcome criterion are
**fixed across arms**. Results quantify the registered scenario contrast only;
they do not resolve OQ-013 or make the package comparison causal evidence of
guard benefit.

## The three arms

| Arm | Pre-switch outputs | Recovery starts at |
| --- | --- | --- |
| **L** `release_startup` (legacy) | all rotors zero | `t_d + t_m` |
| **H** `in_flight_hold_matched` | failed zero, healthy hold trim | `t_d + t_m` (matched) |
| **I** `in_flight_hold_immediate` | failed zero, healthy hold trim | `t_d` |

- **H − L** isolates the pre-switch actuator history, including its force *and*
  moment consequences.
- **I − H** isolates transition timing.
- **I − L** is the combined corrected-mode effect.

**No directional expectation is registered.** Retained thrust can slow the
descent while unbalanced moments worsen attitude; "failure rate must decrease" is
explicitly *not* an acceptance condition.

## Diagnostic (exploratory, registered before execution)

2 failure classes (`one_out`, `two_adjacent`) × 2 primary cells × 2 packages ×
3 arms × 12 paired physical draws = **288 trajectories**, plus deterministic
anchors. One frozen controller/plant bundle (current A2 settings, unchanged
across arms — this does **not** estimate feedforward or drag effects).

It validates plumbing and reveals effect direction on a limited slice. It is
**not** a powered full-grid verdict, and N=12 pairs is not a sample-size
derivation. Identical physical initial states and nuisance draws per trial across
arms; matched case indices reported.

## Legacy preservation

`release_startup` remains the default path with its original numerics, seed
mapping and touchdown reader. Historical JSON is not overwritten by this study;
the diagnostic writes to its own output. If later measurement/event corrections
change L itself, that bridge is reported **separately** from the H − L change.
