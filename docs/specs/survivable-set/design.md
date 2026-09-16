# Study A/B — Survivable Set and Recovery Policy After Partial Propulsion Loss (DR-SS-01)

Status: PREREGISTRATION + simulation-only prediction. Frozen before the first full
sweep was run (2026-09-16). Changing any number in this file after results exist
requires a new study ID, not an edit.

## 1. Research question

After a partial loss of propulsion authority, which recovery action maximises the
probability of a survivable landing from a given post-failure state — and does the
dedicated recovery mechanism (the guard) enlarge the survivable set beyond what
thrust reallocation alone achieves?

Known (not claimed as novel here): controlled flight after one- and two-rotor loss
via thrust reallocation; parachute recovery of small UAS. Open (this study's
contribution): a *policy* over the post-failure state that selects among actions,
with a quantified survivable set that includes recovery delay and authority loss —
and whether the mechanism is justified at all.

## 2. Post-failure state space

A cell is `(h, vz0, omega0, delay)`: height above ground, vertical speed at
failure, tumble rate at failure, detection delay (a state coordinate — it overrides
the dispersed BOM detection latency exactly; motor spool latency stays dispersed).
Tilt at failure is not a grid axis; it is drawn U(0°, 30°) per trial (in-flight
failure from near-level flight).

- Exploratory grid (24 cells): h ∈ {1.5, 3, 6} m × vz0 ∈ {0, −1.5} m/s ×
  omega0 ∈ {2, 6} rad/s × delay ∈ {0.11, 0.30} s. N = 30 trials per
  (class, cell, action) — mapping resolution, wide bounds, no claims.
- Primary cells (kill criterion): `(3.0, 0, 6, 0.11)` — the cage-testable Study-C
  drop condition — and `(1.5, −1.5, 2, 0.30)` — low and late. N = 300.
- Primary failure classes: `one_out`, `two_adjacent` (they bracket the easiest and
  hardest reallocation cases; `two_opposite` and `partial_authority` are exploratory).

## 3. Failure classes (motor-level, `Analysis/failure_allocation.py`)

X-quad wrench map `w = B f`, per-motor thrust in `[0, cap]`, failed motors forced to
zero; `partial_authority` caps all four at 60%. Allocation is reduced-attitude
(collective + roll/pitch tracked, yaw command dropped) because yaw is not
controllable after rotor loss; the achieved yaw torque — including the
spin-direction imbalance — is integrated by the dynamics, so the post-failure spin
is simulated, not ignored. Analytic anchors (one-out balanced flight on the
remaining diagonal pair, two-adjacent roll-trim impossibility) are unit-tested.

Declared simplifications (all conservative or neutral, revisit only with bench data):
single-pass least-squares + clip (a real allocator could redistribute saturation
residuals); no aerodynamic damping of the spin; rotor drag torque linear in thrust.

## 4. Actions

| Action | Model | Landing criterion |
|---|---|---|
| `realloc_only` | 6-DoF sim, per-motor allocation, PD controller, **no** inverted-authority floor; mechanism mass removed: mass ×(1−0.12), lateral inertia ×(1−0.30) — EST credit, OQ-010 | bare |
| `mechanism` | Same, **with** the quarter-collective inverted floor (the behavior the guard physically enables — motors keep spinning inverted) | guarded (EST) |
| `parachute` | Motors cut; ballistic fall during deployment (drag-free, conservative), then closed-form quadratic-drag approach to terminal speed. Class-independent. v_t = 1.8 m/s ×U(0.85,1.15), t_d = 0.8 s ×U(0.8,1.5), impact tilt U(0°,45°) — all EST, OQ-010 | bare |

**Coherence requirement + audit note.** A descent device's terminal speed must sit
below the impact-speed limit it is judged against, or the action is impossible by
construction. The first drafted value (2.5 m/s) violated this; the sweep that
exposed it (0/2000 in every cell) was discarded and the parameter corrected to
1.8 m/s (~0.47 m² canopy at 165 g, Cd 1.4 — still catalog-plausible) before any
committed run. Recorded here rather than silently edited.

Both 6-DoF actions command a 1.0 m/s descent to touchdown (replaces the altitude
hold), so every run terminates at the ground and the impact state is judged; a run
that has not landed by t_max = 12 s is counted unsafe under every criterion.

The comparison is deliberately *system-level*: vehicle-with-mechanism flying the
mechanism policy vs. vehicle-without-mechanism flying reallocation. The mass/inertia
credit and the guarded-impact relaxation are therefore part of the action
definitions, not confounds.

## 5. Landing criterion (PREREGISTERED-ASSUMED)

Survivable touchdown: impact |vz| ≤ 2.0 m/s AND tilt ≤ 30° (bare vehicle). Guarded:
≤ 2.5 m/s and ≤ 60° (EST — the guard absorbs energy and tolerates attitude; owner
input OQ-010, to be replaced by drop-test evidence). Basis: impact KE at the frozen-
max 165 g and 2.0 m/s is 0.33 J, small against sub-250 g airframe damage thresholds;
the number is asserted, not measured, so sensitivity variants strict (1.5 m/s, 20°)
and lenient (3.0 m/s, 45°) are computed for every cell and reported alongside.
Lateral impact velocity is excluded (declared limitation — no wind or lateral
guidance is modeled).

## 6. Statistics

Exact one-sided Clopper–Pearson bounds at 95%, reusing the gated implementation
(`monte_carlo_recovery.clopper_pearson_lower`; upper bound by symmetry). Dispersions
are exactly the gated Monte Carlo draw (`draw_case`): mass, inertia, authority,
thrust, latency multipliers, CG offset disk, motor bias, gyro/attitude noise,
battery sag. Deterministic seeding per (class, cell, action, chunk) — base seed
20260916 — so totals are independent of scheduling and worker count.

## 7. Kill criterion (frozen)

The mechanism is justified **only if**, in at least one primary (class × cell), its
95% lower bound exceeds `realloc_only`'s 95% upper bound — dominance beyond Monte
Carlo uncertainty. Ties inside uncertainty do **not** justify it. If killed, the
result is reported as such and the work redirects to the policy alone (Study B);
the mechanism is not redesigned first (see the plan's "do not" clause).

Interpretation clause: a kill reached because **both** actions fail in a cell
(`both_actions_fail` in the output) is a controller finding, not evidence that the
actions are interchangeable — it redirects to the controller follow-on below, and
the mechanism question stays open only if a future controller separates the actions.

## 7b. Verification anchors (run before trusting any sweep)

The no-failure allocation control case and the `partial_authority` class must land
softly (impact ≈ descent rate, tilt ≈ 0) from both tumble rates — they do
(1.0 m/s, ~1°), which verifies the allocation + descent machinery against the
gated full-complement behavior. The observed collapse of `one_out` /
`two_opposite` at 6 rad/s is then attributable to the controller: the PD attitude
loop is not spin-aware, and the unbalanced drag torque spins the vehicle beyond
what a fixed-frame PD can track — consistent with the published rotor-out result
that spinning flight needs a reduced-attitude, spin-aware controller. That
controller is the study's follow-on (Study A2), and it is a *controls* work item,
not a mechanism redesign.

## 8. Study B — policy map

Best action per (class, cell) by exact lower bound; every alternative whose interval
overlaps the winner's lower bound is listed as ambiguous. The map must say where it
cannot distinguish.

## 9. Outputs and evidence category

`Data/survivable_set_results.json` (preregistration echo, per-cell bounds, kill
verdict, policy) and `Figures/survivable_set_{psafe,policy}.png`, regenerated only
by `python -m Analysis.run_survivable_set`. Everything here is **simulation output
on EST inputs** — no survivable-set claim leaves this study until the EST-REC-007
bench gate and a Study-C drop test (predicted *before* the drop from these cells)
have run.

## 10. Owner inputs required (OQ-010)

Mechanism mass/inertia fractions, guarded impact tolerance, parachute terminal
speed and deployment delay — or the decision that no parachute variant exists, which
removes that action from the policy.
