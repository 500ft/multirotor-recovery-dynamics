# Learning path — understanding and defending this project

`START_HERE.md` tells a reviewer how to *check* this repository. This file is for
the person who has to *defend* it: in a viva, a design review, or a conversation
with someone who knows more than you do about one specific part.

**The test of each module is not "did you read it" but "can you answer the
defence question without looking".** Each module ends with one. If you cannot
answer it, the module is not done.

Work in order. Later modules assume earlier ones.

---

## M0 — Why the question is shaped the way it is

The project does **not** ask "can this drone recover after a rotor fails". It
asks: *given a post-failure state, which recovery action maximises the
probability of a survivable landing, and does the mechanism enlarge the
survivable set beyond what thrust reallocation already achieves?*

That shape is deliberate, and three things follow from it:

1. It is a **comparison**, so it needs at least two actions and a criterion that
   can separate them.
2. It is **conditional on a state**, so the state space is part of the result —
   an answer without a state is meaningless.
3. It admits a **negative result**. The kill criterion was registered before the
   data existed, so "the mechanism is not justified" is a publishable outcome
   rather than a failure.

Read: `docs/specs/survivable-set/design.md` §1–2, then §6b (why what we
delivered is a *design comparison*, not a runtime policy).

> **Defence question.** Why can this study not currently claim to produce a
> runtime policy, and what exactly would have to change for it to do so?

---

## M1 — Evidence discipline (do this before any technical module)

This is the repository's distinguishing feature and the thing a reviewer will
probe first. Everything else is read *through* it.

Every consequential number carries two independent labels:

- **Provenance** — requirement · measured input · sourced assumption ·
  calculated result · selected design value · measured result · provisional
  estimate.
- **Evidence status** — unverified · analytically assessed · physically tested.

They are separate on purpose. A *selected design value* can be unverified; a
*calculated result* is never a *measured result*. **No quantity in this
repository has status `measured`** — there is no accepted physical measurement
yet, and `docs/TRACEABILITY.md` says so explicitly.

Read: `docs/ENGINEERING_AUDIT.md` (the three tiers), then `docs/TRACEABILITY.md`.

**Exercise.** Pick any number in `Analysis/`. Find its provenance, its status,
and the file that would have to change for it to become `measured`. If you can't
find all three in under two minutes, that number has a traceability defect —
report it.

> **Defence question.** A reviewer says "your simulation shows 90 % survival".
> What is wrong with that sentence, in three separate ways?

---

## M2 — The vehicle physics

`Analysis/sim_release_recovery.py` is a 6-DoF rigid-body simulation: quaternion
attitude, translational dynamics with attitude-coupled thrust, quadratic drag.

Learn, in this order:

1. **Why quaternions** — no gimbal lock, cheap renormalisation, and the
   integration `q̇ = ½ q ⊗ [0, ω]` used in the loop.
2. **Euler's equations with gyroscopic coupling**: `Iω̇ = τ − ω × Iω`. The
   `ω × Iω` term is why a spinning vehicle resists being re-pointed, and why the
   A2 variant tried to cancel it.
3. **The mixer**: `τ_rp(T) = 2√2 · arm · min(T/4, T_max/4 − T/4)`. Differential
   authority is **zero at both zero and full collective** and peaks at half.
4. **Airmode** — never commanding full collective, so differential headroom
   cannot vanish.

**Exercise.** Derive the mixer formula yourself from four rotors at
`(±a, ±a)` with per-rotor thrust in `[0, T_max/4]`. Then verify numerically that
the peak is at `T_max/2`.

> **Defence question.** Why does thrust-to-weight ≥ 2.0 place hover at exactly
> the point of maximum roll/pitch authority? (`Design Report/calculations.md`.)

---

## M3 — Failure classes and control allocation

`Analysis/failure_allocation.py`. The wrench map `w = B f` with
`w = (T, τx, τy, τz)`, failed motors forced to zero, per-motor caps.

Key ideas:

- **Reduced-attitude allocation.** Yaw is *dropped* from the command because it
  is not controllable after rotor loss — but the achieved yaw torque is still
  integrated, so the resulting spin is simulated, not ignored.
- **Topology matters more than count.** Losing the *adjacent* pair leaves rotors
  with opposite spins, so yaw drag cancels. Losing the *opposite* pair leaves the
  same spin, so it does not. Same collective loss, different dynamics.
- **One motor out forces flight on the remaining diagonal pair** — the balanced
  collective ceiling is `2 f_max`, not `3 f_max`, because the odd rotor's thrust
  cannot be used without unbalancing.
- **Our allocator is the redistributed pseudo-inverse** (Virnig & Bodden 1994),
  which the literature documents as *approximate and sometimes unreliable*
  relative to active-set methods.

Read: `literature/notes/02-control-allocation-and-fdi.md`.

**Exercise.** Run `cad`-free: in a REPL, build `MotorAllocation` for each failure
class and confirm the two-adjacent no-trim result and the yaw-cancellation
asymmetry yourself.

> **Defence question.** Why can a quadrotor with two adjacent rotors out not hold
> a zero-roll trim at any positive thrust — and why is that not the same as
> saying it cannot fly?

---

## M4 — The controller, and why it fails

A saturated PD attitude loop plus an altitude/descent loop. The A2 variant added
gyroscopic feedforward and a yaw-drag plant term.

The finding to understand: **at 6 rad/s tumble the rotor-out classes fail at
every tested height.** Tilt passes 78° before the reduced authority can arrest.
This is a *control-family* limit, not a tuning problem — the registered next step
is a spin-aware reduced-attitude controller, which is **adoption of known
(patented) prior art**, not invention.

Read: `docs/specs/survivable-set/design-a2.md` §6, `literature/notes/01` §2.

> **Defence question.** The A2 variant made things slightly *worse*. Why is that
> a more useful result than "no significant difference"?

---

## M5 — The statistics

The part most likely to be attacked, and where this repo has already made and
corrected real errors.

1. **Clopper–Pearson** — exact, conservative, coverage ≥ 1−α for every *p*. Know
   the standard criticism (Brown/Cai/DasGupta: "wastefully conservative") and why
   it is still right here: our grid lands near p = 0 and p = 1 constantly, and a
   conservative *lower* bound errs toward understating survivability.
2. **Sidedness.** A 95 % lower plus a 95 % upper on **one** proportion is a 90 %
   central interval. On **two different** proportions it is *not an interval at
   all* — it is a decision rule. We got this wrong and corrected it.
3. **Paired designs.** Common random numbers reduce variance via
   `Var(A−B) = Var(A)+Var(B)−2Cov(A,B)`. Analyse with McNemar on discordant
   pairs, reporting **both** π (conditional win-rate among discordant pairs) and
   Δ = (n₁₀−n₀₁)/N (unconditional difference). They are different numbers.
4. **What bounds do not cover.** They are *conditional Monte Carlo sampling
   bounds*: finite sampling under this model. Not model error, not real-world
   reliability. More samples shrink only the first.

Read: `literature/notes/05`, `literature/claim-ledger.md` E1–E3.

**Exercise.** Compute the rule of three for one of the zero-count cells and
confirm it equals the one-sided CP bound at x = 0.

> **Defence question.** Zero discordant pairs in 300 paired trials. What may you
> conclude, and what may you explicitly not conclude?

---

## M6 — Study design and its failure modes

Cells, criteria, the kill criterion, and the saturation problem.

The lesson worth internalising: **a measure that cannot move tells you nothing.**
71 of 96 class-cell combinations are saturated at 0 or 1, and all four registered
primary cells are pinned at zero — so the scenario diagnostic returned
`no_discordant_pairs` everywhere *by saturation, not by agreement*. A full rerun
on those cells would have measured nothing.

Also learn the **scenario** distinction: the simulator cuts all four motors
during detection latency, which is a *release/startup* transient, not an
in-flight failure. Every rotor-out number is conditional on that reading.

Read: `docs/specs/survivable-set/scenario-contract.md`,
`primary-cell-reselection-proposal.md`.

> **Defence question.** Why is choosing new cells by looking at existing results
> legitimate for designing an experiment but not a confirmatory test of the same
> hypothesis?

---

## M7 — Measurement, uncertainty and the bench

1. **Calibration is not adjustment.** VIM 2.39 Note 2 — taring removes an offset
   from data, not physical load. ADC internal calibration is not calibration in
   newtons.
2. **Uncertainty budgets**: Type A (statistical) and Type B (everything else),
   combined *with covariance where components share a source*, reported as
   `y ± U` with `k` stated and U to at most two significant digits.
3. **%FS is the trap.** Load cells specify errors as a fraction of *full scale*,
   so a 5 kg cell measuring 0.49 N can have uncertainty larger than the quantity.
   This is why the 1 kg cell is recommended and why it must be better than
   0.0625 %FS per term.
4. **Ground effect.** Whole-vehicle thrust inflation reaches ≈1.4× near z/R ≈ 1
   and does not settle until z/R ≈ 5–6 — the *fountain effect*. Clearance is
   measured in rotor diameters, in every direction including the ceiling.

Read: `literature/notes/06`, `docs/bench-acquisition.md` §4b.

> **Defence question.** Your bench reads a stable 0.49 N. Name four reasons that
> number might not be the aircraft's thrust.

---

## M8 — CAD discipline

The pattern: **register → generator → analytic oracle → STEP round-trip →
reviewed contract**, failing closed on any pending input.

Why the oracle matters: in `cad/v995/`, the independent volume calculation caught
a hole placed 1.5 mm off the plate and a pocket double-subtracting 35.54 mm³ with
a bolt hole. **Neither is visible in a rendered view.** A screenshot is not
acceptance; the numbers are.

Read: `cad/v995/README.md`, `cad/v995/generate_fixture.py`.

> **Defence question.** Why does the generator refuse to build the cradle, and
> why is that better than building it with estimated dimensions?

---

## M9 — The literature position

Know what is **established** (so you never claim it): rotor-loss flight with yaw
sacrificed, the primary-axis relaxed-hover mechanism — which is *patented* —
two-opposite loss flight-validated, all four failure classes in outdoor flight
with one non-switching controller, and upset recovery from arbitrary tumbling.

Know what is **open**: action selection over the post-failure state, detection
delay as a policy input rather than a performance metric, and the abort boundary
where the vertical budget runs out.

Know who is **contesting your gap**: Siotia et al. (2026) publish an adjacent
claim. You must cite them and state your difference.

Read: `literature/novelty-and-gaps.md`.

> **Defence question.** State your contribution in one sentence that survives a
> reviewer finding one more paper.

---

## M10 — The history (where real understanding lives)

Read the corrections, not just the conclusions. Each was a real error, found and
fixed in the open:

| Correction | The lesson |
| --- | --- |
| Parachute terminal speed 2.5 → 1.8 m/s | a descent device whose terminal speed exceeds the impact limit is impossible *by construction* |
| Parachute inflation transient added | the model was 2.8× optimistic against measured data; "deployment time" is not "time until it works" |
| Allocator single-pass → cascaded | a defect that only appears under saturation, i.e. exactly when it matters |
| `partial_authority` multiplier → cap | a cap and an effectiveness loss are different faults |
| Spin-scaling claim withdrawn | terminal spin is independent of `Izz` — the algebra disagreed with the intuition |
| "No detection-delay distribution exists" withdrawn | the claim was false; the literature had it |
| Unpaired → paired comparison | the design was valid but low-powered; the fix was precision, not repair |

Read: `docs/specs/survivable-set/critique-2026-09-24-status.md`,
`literature/claim-ledger.md`.

> **Defence question.** Pick the correction you find most embarrassing and
> explain why publishing it strengthens rather than weakens the work.

---

## How to use this against a real audience

When challenged on a number, answer in this order — it is the same order the
repository is built in:

1. **What is it?** requirement, calculation, assumption or measurement
2. **Where does it come from?** the file, and the derivation if there is one
3. **What happens if it is wrong?** sensitivity, and what it blocks
4. **How would you close it?** the specific measurement or analysis

If step 4 has no answer, the number is a liability. Say so before the reviewer
does — in this project, that is the strongest move available, and it is the whole
reason the audit and the open-question ledger exist.
