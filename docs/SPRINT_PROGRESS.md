# Progress log

What changed and when, newest first, one line per change that matters. The
plan is in the [roadmap](../ROADMAP.md). The earlier, longer version of this
log is kept at
[commit 246d163](https://github.com/500ft/multirotor-recovery-dynamics/blob/246d163dcd8ce25242baee585e6ea1d05a53e7f4/docs/SPRINT_PROGRESS.md).

## Week of 2026-10-04

- **10-04** Platform changed to the Bitcraze Crazyflie (owner decision). Added the documented parameter register `Engineering Data/platform_crazyflie.csv`; retired the V995 (unmarked chips; OQ-011 closed); new finish line uses the public NanoBench flights and CrazySim; OQ-018 to OQ-021 opened.

## Week of 2026-09-28

- **09-30** OQ-016 resolved with a new registered comparison (scenario 02):
  four cases, both packages, three scenarios, 300 fresh paired draws each,
  7,200 trajectories. All eight primary comparisons of in-flight against
  release/startup differ after a Bonferroni correction. Losing one rotor gets
  worse (−18 to −53 points of landing pass rate); two opposite rotors and
  reduced authority improve (+9 to +41 points). The registration was committed
  before the run ([#53](https://github.com/500ft/multirotor-recovery-dynamics/pull/53)).
- **09-30** Proposed finish line for the V995: bench thrust and power, logged
  releases with an airborne logger board, and a comparison with the model.
  Waiting for the owner to confirm. README rewritten
  ([#51](https://github.com/500ft/multirotor-recovery-dynamics/pull/51)).
- **09-29** Bench firmware for the QT Py RP2040 (load cell through an NAU7802,
  INA260 power monitor, LIS3DH accelerometer) and host capture code. A device
  reset mid-run marks the run incomplete rather than splicing it. Tested on
  synthetic serial output, not yet on hardware
  ([#44](https://github.com/500ft/multirotor-recovery-dynamics/pull/44)).
- **09-29** Static tip-over bound for the landing criterion: 64–80° on an
  assumed CG height, so the 30° and 60° limits sit inside it
  ([#45](https://github.com/500ft/multirotor-recovery-dynamics/pull/45)).
- **09-29** V995 whole-aircraft fixture: its own parameter register, a
  generator and a contract. The load-cell end adapter builds; the cradle and
  base plate wait on five measurements
  ([#41](https://github.com/500ft/multirotor-recovery-dynamics/pull/41)).
- **09-29** The study's primary cells can't show a scenario effect: every
  trajectory fails the binary landing criterion in every arm, so the paired
  comparison is empty by saturation, not by agreement
  ([#40](https://github.com/500ft/multirotor-recovery-dynamics/pull/40)).

## Week of 2026-09-21

- **09-27** Owner decision: the physical platform is a stock Veeniix V995. The
  designed vehicle's gates (7.0 V, six motors, 0.020 N·m) do not carry over
  ([V995 fixture notes](../cad/v995/README.md)).
- **09-26** In-flight failure scenario added next to the release scenario.
  Keeping the healthy motors running changes the impact speed by −0.38 to
  +0.21 m/s depending on the case
  ([#38](https://github.com/500ft/multirotor-recovery-dynamics/pull/38)).
  Scope correction reconciled and the scenario labelled
  ([#37](https://github.com/500ft/multirotor-recovery-dynamics/pull/37)).
- **09-26** Engineering traceability audit and decision index
  ([#39](https://github.com/500ft/multirotor-recovery-dynamics/pull/39)).
- **09-24** Critique corrections, several to the repository's own earlier
  review ([#36](https://github.com/500ft/multirotor-recovery-dynamics/pull/36)).
- **09-24** Paired comparisons. The guard does not merely fail to help: it
  lost 69 of the 76 trials where the two designs differed. The spin-aware
  controller won none of its discordant pairs
  ([#35](https://github.com/500ft/multirotor-recovery-dynamics/pull/35)).
- **09-24** Parachute inflation time modelled: it saves 0 of 2,000 runs in
  every case, and needs about 10.5 m of drop against a tallest case of 6 m
  ([#34](https://github.com/500ft/multirotor-recovery-dynamics/pull/34)).
- **09-22** Literature review: 81 verified references, a claim ledger and a
  novelty assessment ([#26](https://github.com/500ft/multirotor-recovery-dynamics/pull/26)).
- **09-22** V995 identity, capability sheet, parts inventory and bench wiring
  sheet ([#24](https://github.com/500ft/multirotor-recovery-dynamics/pull/24)).
  Claim audit of findings F01–F10 and the bench intake packet
  ([#25](https://github.com/500ft/multirotor-recovery-dynamics/pull/25)).
- **09-22** Study A2 (a spin-aware controller variant) and a registered
  drop-test prediction ([#22](https://github.com/500ft/multirotor-recovery-dynamics/pull/22)).

## Week of 2026-09-14

- **09-16** Survivable-set study: after a partial loss of propulsion, which
  design package gives a survivable landing, judged by a preregistered impact
  criterion ([#21](https://github.com/500ft/multirotor-recovery-dynamics/pull/21)).
- **09-15** Source candidates and a gap inventory for the single-motor bench
  fixture ([#20](https://github.com/500ft/multirotor-recovery-dynamics/pull/20)).

## Week of 2026-09-07

- **09-13** Bench-fixture geometry contract, then tightened twice
  ([#15](https://github.com/500ft/multirotor-recovery-dynamics/pull/15),
  [#16](https://github.com/500ft/multirotor-recovery-dynamics/pull/16),
  [#17](https://github.com/500ft/multirotor-recovery-dynamics/pull/17)).
- **09-10 to 09-12** Sourced bench inputs and fixture requirements; blockers
  made explicit ([#12](https://github.com/500ft/multirotor-recovery-dynamics/pull/12),
  [#14](https://github.com/500ft/multirotor-recovery-dynamics/pull/14)).
- **09-11** README and presentation rewrite
  ([#13](https://github.com/500ft/multirotor-recovery-dynamics/pull/13)).
- **09-09** CAD input register and geometry CI for the motor envelope
  ([#10](https://github.com/500ft/multirotor-recovery-dynamics/pull/10),
  [#11](https://github.com/500ft/multirotor-recovery-dynamics/pull/11)).
- **09-07** Mass numbers reconciled (155 g against 165 g) and gated by tests;
  CAD part list; wire routing table
  ([#8](https://github.com/500ft/multirotor-recovery-dynamics/pull/8),
  [#5](https://github.com/500ft/multirotor-recovery-dynamics/pull/5) to
  [#7](https://github.com/500ft/multirotor-recovery-dynamics/pull/7),
  [#9](https://github.com/500ft/multirotor-recovery-dynamics/pull/9)).
- **09-06** Measured-authority evidence checks hardened
  ([#4](https://github.com/500ft/multirotor-recovery-dynamics/pull/4)).

## Week of 2026-08-31

- **09-04** Mass rollup synced with the committed budget and gated by tests
  ([#1](https://github.com/500ft/multirotor-recovery-dynamics/pull/1),
  [#2](https://github.com/500ft/multirotor-recovery-dynamics/pull/2)).

## Before September

Repository started 2026-05-06 as SelfStabilizingDrone: the 6-DoF release and
recovery model, the component tiers, the Monte Carlo sweeps (4% recovery with
placeholder torque; 300 of 300 with the mixer model and revised controller) and
the guard analysis.
