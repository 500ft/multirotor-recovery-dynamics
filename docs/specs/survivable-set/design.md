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
via thrust reallocation — including two-adjacent loss in outdoor flight; parachute
recovery of small UAS **at ≥900 g** (not established at sub-250 g).

**What this study actually delivers, corrected 2026-09-24 (§6b):** a quantified
comparison of **design packages** over the post-failure state, with recovery delay
and authority loss as state coordinates, and a test of whether the mechanism is
justified. It does **not** deliver a runtime policy: its cases differ in installed
hardware, and no aircraft can choose its own mass in flight. A runtime policy over
`A(c)` for one fixed configuration remains **specified but not performed** — see
§6b and `literature/novelty-and-gaps.md`.

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
| `parachute` | Motors cut; ballistic fall through **deployment + inflation**, then closed-form quadratic-drag approach to terminal speed. Class-independent. v_t = 1.8 m/s ×U(0.85,1.15), t_d = 0.8 s ×U(0.8,1.5), **t_inflate = 0.6 s ×U(0.8,1.5)**, impact tilt U(0°,45°) — all EST, OQ-010 | bare |

**Coherence requirement + audit note.** A descent device's terminal speed must sit
below the impact-speed limit it is judged against, or the action is impossible by
construction. The first drafted value (2.5 m/s) violated this; the sweep that
exposed it (0/2000 in every cell) was discarded and the parameter corrected to
1.8 m/s (~0.47 m² canopy at 165 g, Cd 1.4 — still catalog-plausible) before any
committed run. Recorded here rather than silently edited.

**Inflation amendment, 2026-09-22** (`literature/claim-ledger.md` C1). The
action originally modelled deployment as a delay followed by an *instantly
effective* drag device. Measured data contradicts that: a canopy that has begun
to open is not yet decelerating. Against the only published system with two
usable data points — Siotia et al. (2026), 2 kg, 0.8 s deployment — the old model
predicted **3.2 m/s** impact from 10 m where **9.1 m/s** was measured, i.e. 2.8×
optimistic. A single added inflation interval, treated as producing no useful
drag, reproduces both their 10 m and 25 m results and is now part of the action
(`PARACHUTE_INFLATE_S`, EST 0.6 s, calibrated not measured). It is fitted to one
2 kg system. **Amended 2026-09-24 (critique C03): the claim that transferring it
to a smaller craft is "conservative in the safe direction" is withdrawn** — a
smaller canopy plausibly inflates faster, but that is an expectation, not a proof,
and the direction of the transfer error is unestablished. An unresolved
interpretation mismatch is recorded with the fit: we take `terminal = 3.2 m/s`
from their 25 m landing outcome, while their own stated m = 2 kg, Cd = 1.2,
A = 1.5 m², ρ = 1.225 give √(2mg/(ρ·Cd·A)) ≈ **4.22 m/s**. This is not to be
resolved by tuning; it needs their timing and drag definitions. Future
calibration requires separate failure, trigger, deployment-start and full-drag
timestamps. The prior sweep's parachute cells are superseded; the regenerated
data is in the same commit.

**Known sensitivity.** At ~10 m the ballistic distance approaches the available
height, so impact speed is steeply sensitive to the inflation estimate (6 ms of
inflation moves it >0.5 m/s). The low-altitude parachute cells therefore carry
more uncertainty than their binomial bounds alone express. Tested.

**Consequence: the parachute action is empty across this study's entire domain.**
Under the corrected model the nominal ballistic distance before useful drag is
**9.6 m**, and the break-even height for a survivable parachute landing is
**10.5 m** — against a tallest preregistered cell of **6.0 m**. The action is
therefore 0/2000 in every cell, where the previous model made it the
unambiguously best action in 22 class×cell combinations. Two things follow:

1. The 10.5 m break-even lands inside the 10–15 m range reported for 0.9–2 kg
   airframes. **Amended 2026-09-24 (critique C03): this is weaker than
   "corroboration".** Those published figures are simulation/HIL outputs and
   vendor test data, not independent physical drop measurements, and our
   inflation interval was *fitted to one of them*. Agreement is therefore partly
   circular — it confirms the fit reproduces its own calibration source at a
   third height, not that either model matches reality. The claim that a
   10–15 m floor is a **universal** property is withdrawn; it is a
   configuration-specific published result.
2. **The earlier claim that a parachute is "the only nonzero action for
   two-adjacent loss" is withdrawn.** Within this grid, two-adjacent loss has
   *no* surviving action at all. That is a stronger and more useful negative
   result, and it agrees with the independent mass argument
   (`literature/notes/03-parachute-and-descent-recovery.md` §1).

The grid is **not** being extended to chase the break-even: it is preregistered,
and moving it after seeing results is precisely what §9 forbids. A taller-cell
domain extension would be a registered amendment with a new study ID.

**Second coherence gap (documented, not fixed).** The nominal terminal speed
(1.8 m/s) clears the 2.0 m/s bare limit, but the top of its dispersion
(1.8 × 1.15 = 2.07 m/s) does not — so roughly 13 % of parachute draws are
impossible at any height, independently of the inflation finding. Narrowing the
dispersion would mean inventing data, so the property is asserted in the tests
instead and left for OQ-010.

Both 6-DoF actions command a 1.0 m/s descent to touchdown (replaces the altitude
hold), so every run terminates at the ground and the impact state is judged; a run
that has not landed by t_max = 12 s is counted unsafe under every criterion.

The comparison is deliberately *system-level*: vehicle-with-mechanism flying the
mechanism policy vs. vehicle-without-mechanism flying reallocation. The mass/inertia
credit and the guarded-impact relaxation are therefore part of the action
definitions, not confounds.

## 5. Landing criterion (PREREGISTERED-ASSUMED — label retained)

Survivable touchdown: impact |vz| ≤ 2.0 m/s AND tilt ≤ 30° (bare vehicle). Guarded:
≤ 2.5 m/s and ≤ 60° (EST — the guard absorbs energy and tolerates attitude; owner
input OQ-010, to be replaced by drop-test evidence). Basis: impact KE at the frozen-
max 165 g and 2.0 m/s is 0.33 J, small against sub-250 g airframe damage thresholds;
the number is asserted, not measured, so sensitivity variants strict (1.5 m/s, 20°)
and lenient (3.0 m/s, 45°) are computed for every cell and reported alongside.
Lateral impact velocity is excluded (declared limitation — no wind or lateral
guidance is modeled).

**Context added 2026-09-25 — the evidence label does NOT change.** Rotorcraft and
transport landing-gear drop tests sit in a comparable speed range: 14 CFR 27.725
specifies a 13-inch drop (or a justified lesser height of at least 8 inches) and
27.727 uses 1.5× the chosen height, whose nominal free-fall equivalents are about
**2.55 and 3.12 m/s**. That is *context for why the band is not arbitrary*, and
nothing more. Those are **landing-gear qualification tests for other vehicle
classes at other scales** — they do not supply our band, they do not validate a
2.0/2.5 m/s impact limit or a 30°/60° tilt limit for a sub-250 g plastic drone,
and this study must not be described as satisfying any standard. The thresholds
remain **assumed**, with sensitivity variants reported per cell; only a drop test
of the actual vehicle can change that.

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
result is reported as such and the work redirects to the package ranking alone (Study B);
the mechanism is not redesigned first (see the plan's "do not" clause).

Interpretation clause: a kill reached because **both** actions fail in a cell
(`both_actions_fail` in the output) is a controller finding, not evidence that the
actions are interchangeable — it redirects to the controller follow-on below, and
the mechanism question stays open only if a future controller separates the actions.

## 6a. Scenario label (amendment, 2026-09-24)

Critique C04. The simulator cuts **all four motors** for
`detection_latency + motor_start_latency` and only then engages the controller.
That is a **release/startup transient** — a vehicle dropped with motors off which
must spool up. It is **not** an in-flight failure, where healthy motors keep
running under the nominal controller until detection and reconfiguration.

The mode is now named in code (`Analysis/survivable_set.py: SCENARIO`) and emitted
in every results file as `scenario: "release_startup"`, with a test asserting the
dynamics still match the label. **Every rotor-out result in this study is
conditional on that reading and must be reported with it.**

An `in_flight_loss` mode needs its own registration before use, specifying: the
pre-failure command; the failed rotor's residual thrust during detection; the
healthy motors' behaviour during detection; when fault-aware allocation begins;
whether actuator response is instantaneous or lagged; and whether the initial
state is trim-consistent. Failure type must also be specified — motor stop,
propeller loss, effectiveness loss and power loss differ in their thrust, torque,
drag and inertia transients.

## 6b. Configuration vs action — scope correction (amendment, 2026-09-24)

Critique C01/C05. **The comparison in §4 is a comparison of complete
design/control packages, not a policy over actions available in flight.** It must
not be described as a runtime policy, and the `policy` field in the generated
JSON is a *ranking of packages*, not an executable selector.

Why: `realloc_only` removes the guard's mass and rim inertia and disables the
inverted-authority floor; `mechanism` retains both. **An airborne vehicle cannot
choose to have launched without its guard.** The same applies to a carried
descent device: its mass is present whether or not it is deployed. A comparison
that varies installed hardware between "actions" is answering *which aircraft
should we build*, which is a legitimate and useful question — but a different one.

### Corrected structure for any successor study

Define a **hardware configuration `c`** before launch, and the set of actions
`A(c)` that *that* aircraft can actually execute. Then:

- **Design comparison:** compare `c₁` against `c₂`, each under its own declared
  policy. Mass, inertia and installed protection differ *by construction*.
- **Runtime policy:** `π_c(observed state, uncertainty) → a ∈ A(c)`, evaluated on
  **one fixed** mass, inertia, propulsion and installed protection. Outcome
  definitions may not change between actions inside one runtime comparison.

An action requiring hardware the configuration lacks is **UNAVAILABLE**, not a
low-scoring option. Passive protection is part of `c`; it is not a command unless
a deployment mechanism exists.

### Configuration register (initial)

| Configuration | Installed | Available actions `A(c)` | Status |
| --- | --- | --- | --- |
| `guarded` (designed vehicle) | guard, no descent device | reallocation; inverted-floor control law | modelled |
| `bare` (designed vehicle) | no guard, no descent device | reallocation | modelled |
| `v995_stock` | stock guards, no descent device, **no established per-motor command access** | *none established* — see `evidence/week-2026-09-19/platform-capabilities.md` | **actions UNAVAILABLE pending board access (OQ-011)** |

**The `parachute` action is UNAVAILABLE in every configuration we own**: no
characterised deployable device exists in the inventory. It remains admissible
only as a clearly-labelled hypothetical-device sensitivity study, never as a
hardware capability.

### C05 — the guard/inverted-floor coupling is unjustified

The code enables the quarter-collective inverted-authority floor **iff** the guard
is present. No mechanical reason is stated, and in free air inversion alone does
not prevent an unguarded rotor from producing thrust. Contact, obstruction or an
explicit operational rule might justify it; none is represented by the switch.

Before any claim that the guard *enables* airborne recovery, its causal mechanism
must be written down and evidenced separately: does it prevent rotor contact,
preserve clearance under load, decouple contact torque, absorb deformation energy,
or change drag? Briod et al. (2014, doi:10.1002/rob.21495) support one particular
construction — a cage on a passive three-axis gimbal — which is **not** equivalent
to rigid propeller rings.

**Successor-study rule:** run the same admissible airborne controller on both
architectures, varying mass/inertia/aerodynamics/clearance explicitly; then toggle
the control floor on **one fixed** architecture as a separate diagnostic. The
historical package comparison is retained and cannot isolate guard causation.

## 6c. What the bounds cover, and where inputs come from (C10, 2026-09-25)

The Clopper–Pearson bounds in this study are **conditional Monte Carlo sampling
bounds**: they quantify finite sampling *under this model, these distributions and
this landing proxy*. They do not cover model error, scenario error or real-world
reliability, and more samples shrink only the first. A scenario bracket has no
implied probability or confidence level.

### Parameter provenance

| Parameter | Provenance |
| --- | --- |
| mass, inertia, torque, thrust, latency multipliers | **assumed dispersion** (stated engineering bounds on the locked BOM, deliberately wider than expected build tolerance) |
| CG offset, motor bias, gyro/attitude noise, battery sag | **assumed dispersion** |
| guard mass share (EST-MASS-012 split) | **assumed**, tied to the live rollup (OQ-010) |
| guard inertia share, guarded impact tolerance | **assumed** (OQ-010) |
| parachute terminal speed, deployment, inflation | **calibrated to another model's outputs**, not measured (OQ-010) |
| A2 yaw rotational drag | **assumed** (OQ-010) |
| detection delay cells | **scenario bracket** — 0.11 s sits inside the published 20–130 ms envelope; 0.30 s is a deliberate stress case beyond it |
| arm length, landing criterion | **assumed** |
| measured variation / measurement uncertainty | **none yet** — no accepted physical measurement exists |

Existing uniform distributions are **preserved** in the historical study and in
the matched scenario contrast so inputs stay comparable; replacing them with
brackets would change the experiment and needs its own registration.

## 7a. Paired comparison (amendment, 2026-09-23)

`literature/claim-ledger.md` E1. The action comparison is **paired by
construction** — mechanism and reallocation see the same dispersed vehicle, the
same imperfections, the same initial tilt and the same sensor-noise stream — but
until this amendment the trial seed included the action index, so the two arms
drew *different* vehicles and the design was paired in intent only. Analysing
paired binary outcomes as two independent proportions discards the pairing,
inflates the variance of the comparison, and manufactures the
"intervals overlap" non-result that variant A and A2 both reported.

**Change.** The seed prefix drops both the action index and the variant index, so
every action and both controller variants pair one-to-one per trial. A regression
test asserts that at least one `(class, cell, variant, seed)` is shared by both
actions, so the pairing cannot silently regress.

**Inference.** Exact conditional on the discordant pairs (McNemar's conditioning):
given `m = b + c` discordant trials, `b ~ Binomial(m, ½)` under the null that
either action is equally likely to win a discordant pair. Reported per
(class, cell):

| Verdict | Meaning |
| --- | --- |
| `a_superior` / `b_superior` | the exact interval on π = b/m excludes ½ |
| `no_discordant_pairs` | the actions produced **identical** outcomes on every paired trial — a far stronger statement of indistinguishability than overlapping marginal intervals, and one the unpaired analysis could not make |
| `not_distinguished` | discordant evidence exists but the interval spans ½; the discordant count is reported so the reader sees how little evidence there is |

The mid-p McNemar p-value is reported alongside, because Fagerland, Lydersen &
Laake (2013, doi:10.1186/1471-2288-13-91) show the exact conditional test is
needlessly conservative and recommend mid-p as the default. Both are given; the
interval is exact.

**Deliberately not implemented.** The unconditional score interval on the
*marginal* difference (Tango 1998, doi:10.1002/(SICI)1097-0258(19980430)17:8<891::AID-SIM780>3.0.CO;2-B)
is the recommended complement and is what a preregistered non-inferiority margin
δ would be tested against. It is **not** implemented here rather than coded from
half-remembered algebra with no reference to validate against — a wrong interval
is worse than a missing one. Registering δ and adding Tango's interval is a
follow-on with its own study ID.

**What this does not change.** The marginal Clopper–Pearson bounds and the
preregistered kill criterion stay exactly as registered; the paired analysis is
*additional*. §7's sidedness caveat still applies to the marginal bounds.

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

## 8. Study B — package ranking (formerly "policy map")

Best-performing **package** per (class, cell) by exact lower bound; every
alternative whose interval overlaps the winner's lower bound is listed as
ambiguous. The map must say where it cannot distinguish.

**Naming, corrected 2026-09-24 (§6b):** the generated field is still called
`policy` for file compatibility, but it ranks *configurations*, not in-flight
choices. Read "best action" as "best-performing package". A genuine runtime policy
needs one fixed configuration and `A(c)` executable on it.

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
removes that action from the ranking. (As of 2026-09-24 the parachute action is UNAVAILABLE in every configuration we own — §6b.)
