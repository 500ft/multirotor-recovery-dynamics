# Current Preliminary Results

Generated from the locked Stage 1 catalog selection on June 21, 2026. These are
not validated design results.

## Mass Budget

| Result | Value |
|---|---:|
| Best-case mass | 123.86 g |
| Nominal mass | 135.66 g |
| Worst-case mass | 156.0 g |
| Unmodeled-hardware allowance | 5.0 g |
| Proposed frozen maximum | 165.0 g |
| Nominal margin to proposed maximum | 29.34 g |
| Below 225 g abort threshold | PASS |

The `165 g` value is a proposal only. It cannot become the fixed maximum until
delivered components are weighed and the complete CAD mass model exists.

## Pre-Registered Component Gates

| Gate | Threshold | Status |
|---|---:|---|
| Full-reserve thrust at 7.0 V | 112.5 gf/motor | BENCH_REQUIRED |
| ESC unconditional current | <=10.4 A/motor | BENCH_REQUIRED |
| Battery unconditional current | <=44 A pack | BENCH_REQUIRED |
| Stage 1 Nicla p95 latency | <=100 ms | BENCH_REQUIRED |
| Future recovery Nicla p95 latency | <=50 ms | DEFERRED |
| Duplicate hardware resources | 0 | PASS (catalog map) |

## Preliminary Recovery Envelope

| Case | Minimum Height | Available Height | Testable Now |
|---|---:|---:|---|
| Best placeholder case | 0.88 m | 3.0 m | yes |
| Nominal placeholder case | 8.64 m | 3.0 m | no |
| Worst placeholder case | 58.42 m | 3.0 m | no |
| Nominal no-drag bound | 11.16 m | 3.0 m | no |

The model is first-order and uses estimated inertia, torque, thrust, latency, and drag. These results demonstrate why recovery cannot be assumed to work at low height. They do not predict the final vehicle.

## Guard Functional Check

All current placeholder guard cases fail the required clearance-to-deflection safety factor of `>=2`.

| Case | Predicted Deflection | Clearance SF | Elastic Stress SF | Functional Result |
|---|---:|---:|---:|---|
| Best placeholder case | 5.35 mm | 0.56 | 17.82 | FAIL |
| Nominal placeholder case | 10.54 mm | 0.24 | 7.50 | FAIL |
| Worst placeholder case | 20.00 mm | 0.10 | 4.00 | FAIL |

This does not prove a real guard will fail. It proves that the assumed stiffness and energy values do not close and must be replaced by analysis and test data.

## Classifier Confidence Bounds

| Observation | Exact 95% Upper Bound |
|---|---:|
| 0 false positives in 300 trials | 0.994% |
| 0 false positives in 1,000 trials | 0.299% |

An observation of zero is not reported as a true false-positive rate of zero.

## Closed-Loop Recovery Envelope (6-DoF, corrected 2026-07-02)

From `Analysis/run_release_recovery.py` (`Data/release_recovery_results.json`). The
envelope scan is capped at the gyro measurement range (2000 °/s): a release faster than
the gyro can report cannot be claimed recoverable regardless of the dynamics. Each edge
is labeled by what it actually is.

| Tier | Max recoverable tumble (60° tilt, 3 m budget) | Envelope edge |
|---|---:|---|
| Best | 34.5 rad/s (1977 °/s) | **gyro limit** (never failed up to sensor range) |
| Nominal | 3.5 rad/s (201 °/s) | real dynamic failure |
| Worst | 1.0 rad/s (57 °/s) | real dynamic failure |

The previously reported "best ≥ 40 rad/s" was the scan cap of the search loop — an
artifact, not a physical boundary — and exceeded the gyro range. Corrected.

## Monte Carlo Dispersion Sweep — GATE RESULT: FAIL at placeholder authority

From `Analysis/monte_carlo_recovery.py` (`Data/monte_carlo_results.json`). The validation
gates require recovery to hold "across a Monte Carlo sweep, not only a single
cherry-picked run." Dispersions per trial: mass ×[0.95, 1.10], inertia ×[0.85, 1.25],
torque ×[0.85, 1.10], thrust ×[0.85, 1.05], latencies ×[0.8, 1.5], battery sag ×[0.90, 1.00],
motor-mismatch torque bias ≤ 10% of budget, gyro noise 0.02 rad/s, attitude-estimate noise
2°, thrust-line (CG) offset uniform over a disk. Release: 60° tilt, nominal BOM tier.

| Scenario | 1.0 rad/s | 2.0 rad/s | 3.0 rad/s |
|---|---:|---:|---:|
| As-toleranced (cg ≤ 5 mm) | 3/75 (4.0%) | 6/150 (4.0%) | 1/75 (1.3%) |
| Balance-controlled (cg ≤ 1 mm) | 45/75 (60.0%) | 115/150 (76.7%) | 32/75 (42.7%) |

Success rates carry exact Clopper–Pearson 95% lower bounds in the JSON (same
zero-inflation-proof convention as the classifier stats above).

**Root cause.** The thrust-line-offset disturbance torque is `cg × thrust`. Against the
placeholder 0.004 N·m per-axis budget (EST-REC-007 — explicitly a placeholder,
"replace with measured thrust and arm length"):

| Thrust condition | CG offset that consumes 100% of budget | 50%-margin offset |
|---|---:|---:|
| Hover (1.27 N) | 3.15 mm | 1.57 mm |
| Recovery peak (4.2 N) | **0.95 mm** | 0.48 mm |

A thrust cap during righting does not rescue it: protecting torque margin trades directly
against the 3 m altitude budget and the vehicle hits the ground instead.

**What this means (requirement, not despair).** A real 4-motor mixer at this scale can
plausibly produce ~10× the placeholder differential torque, so the FAIL is most likely an
artifact of the conservative placeholder — but that is exactly the point: the claim is
unverifiable until measured. Derived actions:

1. **EST-REC-007 is the highest-value bench measurement in the project.** Measure
   per-motor thrust + arm length; the recovery-robustness story lives or dies on it.
2. **New build requirement:** thrust-line offset ≤ 0.5 mm (50%-margin at recovery thrust
   under the placeholder budget), to be verified from the Lane A+ CAD mass model and at
   assembly. Relax only after (1) demonstrates margin.
3. Until one of those lands, the single-point Lane A demo may be cited only alongside
   this gate result.

## Scenario C — Mixer-Authority Prediction (added 2026-07-02, later same day)

The follow-up the FAIL demanded: replace the placeholder torque clip with the
**physically-derived 4-motor mixer authority** (`with_mixer`,
`Analysis/sim_release_recovery.py`) — per-motor thrust in [0, T_max/4],
differential headroom `d_max = min(T/4, T_max/4 − T/4)`, giving
`τ_rp(T) = 2√2·arm·d_max` (zero at zero AND full collective — the coupling the
placeholder ignored). Arm = **60 mm, ASSUMED** until CAD/bench. Making the
authority real exposed three controller gaps, each fixed with the standard
technique and stated in-code:

1. **Integral trim** (clamped, upright-only): a PD loop trims a constant CG
   disturbance with a steady tilt of `τ/KP ≈ 30°` at 2 mm offset — the classic
   reason attitude stacks carry an I-term.
2. **Attitude-priority desaturation ("airmode")**: collective capped at 75% so
   differential headroom can never vanish at full thrust.
3. **Control-authority floor while inverted**: quarter-collective while the
   >78° thrust cut is active — motors keep spinning for torque, the physical
   reason a real quad can right itself from inverted.
4. **Gain rescale** (P and D together, 3×): the base gains were sized for the
   0.004 N·m clip and are too soft to out-torque a CG disturbance at 60° tilt
   once real authority exists.

Result (scenario C in `Data/monte_carlo_results.json`), same as-toleranced
dispersions as scenario A (cg ≤ 5 mm; the torque multiplier now scales the arm):

| Scenario | 1.0 rad/s | 2.0 rad/s | 3.0 rad/s |
|---|---:|---:|---:|
| A: placeholder authority | 3/75 (4.0%) | 6/150 (4.0%) | 1/75 (1.3%) |
| C: mixer authority (ASSUMED 60 mm arm) | **75/75 (100%, lb 96.1%)** | **150/150 (100%, lb 98.0%)** | **75/75 (100%, lb 96.1%)** |

Worst altitude loss in scenario C: 1.01 m of the 3.0 m budget (3 rad/s case).

**Status of this result: a PREDICTION, not a validation.** The A→C contrast changes
both the authority model and controller behavior; it does not isolate a causal
effect of torque, nor demonstrate measured recovery. Everything above is
conditional on the ASSUMED 60 mm arm and datasheet per-motor thrust. The
scenario exists to make the EST-REC-007 bench measurement decisive: measure
per-motor thrust and arm, plug them in, and the recovery-robustness claim is
evaluated under those measured inputs; static thrust/arm data alone cannot
validate dynamic recovery or motor response. Until then the summary is: *fails at placeholder
authority, predicted to pass at mixer authority, measurement pending.*

## Frozen measured-authority verdict (registered 2026-07-17)

The next result is no longer governed by “comfortably above” or “sufficient
trials.” At 7.0 V, the empirical fifth-percentile `tau_rp(T)` must be at least
**0.020 N·m at every registered point from 25–75% collective**. If that passes,
the measured-distribution simulation runs 1,000 primary trials at 2 rad/s,
60° tilt, and CG ≤5 mm. PASS requires at least **962/1,000** recoveries, exact
one-sided 95% Clopper–Pearson lower bound ≥0.95, and maximum descent ≤3.0 m.
The 250-trial 1 and 3 rad/s cases are descriptive only.

The automated gate is committed in `Analysis/measured_authority_gate.py` and
`Analysis/monte_carlo_recovery.py`; the physical result remains **measurement
pending**. See `docs/specs/measured-authority-gate/`.

The evidence-admission correction dated 2026-09-05 requires a source manifest,
six sampled-motor identities, calibrated uncertainty, and unique raw references.
It validates supplied file consistency, not source authenticity or calibration
quality. The empirical fifth percentile (the minimum with six observations)
is not a confidence-qualified population bound. Synthetic bundles cannot issue
a physical PASS. The fixed thresholds above are unchanged.

## Survivable-Set Study A/A2/B (registered 2026-09-16)

Full definitions and audit trail: `docs/specs/survivable-set/design.md` (Study
A/B preregistration), `design-a2.md` (spin-aware variant + machinery revision),
`drop-test-prediction.md` (registered Study C prediction). Generated data:
`Data/survivable_set_results{,_a2}.json`, figures
`Figures/survivable_set_{psafe,policy}{,_a2}.png`. Everything below is
**simulation on EST action inputs (OQ-010)** — no survivable-set claim is
released until the bench and drop gates run.

Question: after a partial propulsion loss at state (height, vertical speed,
tumble rate, detection delay), which action — thrust reallocation, the
guard-enabled mechanism behavior, or a parachute-like device — maximises the
probability of a survivable landing, judged by a preregistered impact criterion
with exact Clopper–Pearson bounds?

Results, both controller variants (baseline PD and spin-aware A2):

- **Mechanism kill criterion fired in both variants**: in no primary
  (class × cell) does the mechanism's exact lower bound clear reallocation's
  exact upper bound. Every primary comparison is flagged `both_actions_fail` —
  under the registered interpretation clause this is a *controller* finding,
  not evidence the actions are interchangeable, and it blocks mechanism
  redesign rather than motivating it.
- **A2 hypothesis outcome**: H-A2.1 (gyroscopic feedforward + bounded terminal
  spin helps in tall cells) was NOT supported — all A-vs-A2 differences sit
  inside Monte Carlo uncertainty; H-A2.2 (parity at low height) held. The next
  controls step is a spin-locked rotor-out controller, not more feedforward.
- **Class structure**: 60% partial authority is benign nearly everywhere
  (lower bound 0.90 in the registered cage cell); one rotor out is marginal at
  2 rad/s and unrecoverable at 6 rad/s tumble; two adjacent out has no
  surviving thrust action in any cell — a parachute-like device is its only
  nonzero action. The device itself is worthless below ~3 m because deployment
  consumes that height.
- **Boundary finding**: a 6 rad/s tumble at failure is outside the arrest
  envelope of this control family for the rotor-out classes at every tested
  height.
- **Integrator defense**: halving dt moves primary-cell impact speeds by at
  most 0.0044 m/s with full landed/not-landed agreement
  (`Data/survivable_set_convergence.json`).
