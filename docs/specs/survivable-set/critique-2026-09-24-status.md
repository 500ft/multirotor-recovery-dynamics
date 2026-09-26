# External critique of 2026-09-24 — item status

Source: owner handoff `multirotor-recovery-dynamics_literature-critique_2026-09-24.txt`
(planning document, outside the repo). This file is the in-repo record of what was
applied, what was deferred and why, so that nothing survives only in a merged pull
request description. Created 2026-09-24 after noticing that C04/C06/C08/C10 were
described as "recorded" while existing nowhere in the repository.

Applied items were merged in PR #36; the consistency follow-ups in this file's own
change. Status values: **applied** / **partly applied** / **deferred (recorded)**.

| # | Item | Status | Where |
| --- | --- | --- | --- |
| C01 | Separate design selection from actions available in flight | **applied** | `design.md` §6b; `Analysis/current-results.md`; §1 and §8 reconciled 2026-09-24 |
| C02 | Correct novelty claims (detection-delay distribution; sub-35 g counterexample) | **applied** | `literature/notes/01` §6, `notes/02` §4, ledger G2/G3, `novelty-and-gaps.md` |
| C03 | Repair parachute evidence provenance; stop calling calibration validation | **applied** | `Analysis/survivable_set.py`, renamed test, `design.md` §4, ledger C1 |
| C04 | Make the failure scenario and recovery metric physically consistent | **model implemented, study open** | `in_flight_hold_matched` / `in_flight_hold_immediate` arms implemented and anchored (DR-SS-SCENARIO-01, `scenario-contract.md`); 288-trajectory diagnostic run. The three outcome definitions (regulation / contact-before-regulation / touchdown) and the full-grid rerun remain open — and the diagnostic showed the primary cells saturate the binary proxy |
| C05 | Do not attribute the guard's benefit to an arbitrary controller restriction | **applied** | `design.md` §6b |
| C06 | Preserve bench instrumentation; add an observability contract | **applied** | `docs/bench-acquisition.md` §4b observability table, offset-sensor caveat |
| C07 | Correct the spin-scaling argument | **applied** | `literature/notes/01` §6, ledger G2 |
| C08 | Treat touchdown limits as an unvalidated proxy, not airframe survival | **applied (documentation)** | `bench-acquisition.md` §4b static-vs-impact bandwidth and contact-state fields; `design.md` §5 keeps PREREGISTERED-ASSUMED with landing-gear context added as context only. Physical validation remains unmeasured |
| C09 | Improve statistics without overstating what pairing proves | **applied** | `Analysis/survivable_set.py` (Δ added), ledger E1/E2, `notes/05` |
| C10 | Bound what "the boundary" means | **applied** | `design.md` §6c conditional-bounds statement and parameter-provenance table |

## Deferred items, stated precisely enough to act on later

**C04 — scenario and metric consistency.** *Partly applied 2026-09-24: the mode is
now labelled `release_startup` in code and in every results file, with a test that
fails if the dynamics stop matching the label. The modelling work below is what
remains.* The simulator still cuts *all* motors
for detection + startup latency, which is a release-startup scenario, not an
in-flight failure: healthy motors should retain their states and follow the
nominal controller until reconfiguration. The failure mode also needs specifying
(motor stop vs propeller loss vs effectiveness loss vs power loss — these differ
in thrust, torque, drag and inertia transients). Separately, the generic settled
detector requires `‖ω‖ < 0.3 rad/s`, which is incompatible with a deliberately
spinning equilibrium; it is **not** the landing classifier used by this study, so
it did not cause the current results, but it cannot be reused as a
spinning-recovery success flag. Three outcomes should be distinguished:
(a) reduced-attitude regulation, (b) recovery before contact, with altitude
consumed recorded, (c) landing/impact outcome. This is already open as F02 in
`review-2026-09-19.md`; C04 sharpens it. **Blocks:** any claim that the study
models an in-flight failure.

**C06 — observability contract.** One row per desired output: quantity, sensor or
source, frame, timing, range, uncertainty, availability. Aggregate force/current,
specific force and beam events cannot establish per-motor thrust, body rates, full
attitude, trajectory or failure identity, and must not be plotted with surrogate
labels. For any future attitude sensing, record sample/filter delay, per-axis gyro
range, clipping, and sensor position relative to CG — an offset sensor also feels
`α × r` and `ω × (ω × r)` terms (20 rad/s at 10 mm ⇒ ~4 m/s² centripetal, which is
not gravity tilt). **Home when actioned:** `docs/bench-acquisition.md`.

**C08 remainder — contact-state record and instrument bandwidth.** A contact
record should carry vertical and lateral velocity, attitude, angular velocity,
surface, contact location, configuration and specimen history, with physical
damage and post-event function stored independently of the kinematic proxy. The
purchased static load-cell chain must not be promoted into an impact instrument:
at 80 SPS samples are 12.5 ms apart (3.125 ms even at 320 SPS) before filter
delay, so peak force needs demonstrated bandwidth and adequate samples over the
contact. Repeated drops on one damaged specimen are not independent trials.

**C10 — bound what "the boundary" means.** The map is conditional on limited
tilt/tumble axes, one failure location per class, assumed parameter distributions
and a landing proxy. Monte Carlo bounds quantify finite sampling *under that
model*; they do not cover model error or real-world reliability, and more samples
shrink only the first. Observational variation, specimen/condition variation and
unknown parameters should be reported separately, with a scenario bracket rather
than an invented uniform distribution where no data supports one. An executable
selector observes *estimates*, not true state, so state uncertainty and diagnosis
confidence belong in any future policy evaluation; an oracle policy is a labelled
upper benchmark only.

## Not accepted as stated

None of the ten was rejected. C02's sub-35 g counterexample was **narrowed** on
verification: Çintaş & Özyer (2026) demonstrate real-flight FTC at 30.6 g for
**partial rotor-speed degradation**, not complete rotor loss, and the paper draws
that distinction itself. It is therefore prior art for the `partial_authority`
class, and the complete-loss statement survives as search-bounded.
