# Multirotor Recovery Dynamics

Can a small drone that is thrown, dropped or loses a motor get itself level
again before it hits the ground? This repository models that recovery in
simulation. The platform is now the Bitcraze Crazyflie, a 27–29 g nano-quad
whose parameters and firmware are published and whose real flights are in a
public motion-capture dataset, so the model can be checked against real flights
before any hardware is bought.

[![CI](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml)
![Evidence: simulation and nominal CAD](https://img.shields.io/badge/evidence-simulation_%2B_nominal_CAD-475569)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e)](LICENSE)

[Results](#simulation-results) · [Roadmap](ROADMAP.md) ·
[Quick start](#quick-start) · [Safety](#safety-and-limits)

![Simulated altitude loss and recoverable tumble rate across component tiers](Figures/release_recovery_envelope.png)

*Simulated altitude lost against initial tumble rate, by component tier, with
estimated inputs. [Figure provenance](docs/data-and-figures.md).*

## About

Recovery depends on several things at once: how fast the drone detects the
fall, how much torque the motors can produce, the battery's state, where the
mass sits, and what any guard adds. A controller that looks good in one
nominal case can still fail across realistic variation, so the model runs
Monte Carlo sweeps over those variations and judges each case against a
declared landing criterion.

The historical simulated aircraft was never built. Its mass, propulsion and
other inputs came from estimates and catalog specifications.

The platform is now the Crazyflie. Its documented values, each with its source,
are in the [platform register](Engineering%20Data/platform_crazyflie.csv). The
public [NanoBench dataset](https://github.com/syediu/nanobench-iros2026) holds
172 motion-capture flights of a Crazyflie 2.1, flown at a measured 40.85 g with
markers and a charging deck. The stock V995 is retired: its main chips are
unmarked and no programming route was found.

## Simulation results

These results are for the historical designed aircraft (about 130–165 g, never
built). All of them use estimated inputs, and none has been checked against
hardware. They are not Crazyflie results.

| Question | Result |
| --- | --- |
| Does the vehicle recover with the placeholder torque estimate? | 4% of trials at a 2 rad/s tumble, once part tolerances are included |
| With a four-motor mixer model and a revised controller? | 300/300 across the three reported tumble rates, with assumed arm length and datasheet thrust |
| Does a guard around the airframe help recovery? | Guard contribution unresolved: the variants change mass, inertia, impact-speed limits, tilt limits and controller settings together |
| Does a parachute help at these heights? | No landing passes in the stored sweep; the assumed delay before useful drag exceeds the available fall time |
| One rotor out? | Landing passes depend on the release/startup case; see the [stored outcomes](Data/survivable_set_results.json) |
| Two adjacent rotors out? | No landing passes in the tested release/startup cases |

The [stored recovery results](Data/monte_carlo_results.json) give the placeholder
percentage at 2 rad/s and the mixer total across 1, 2 and 3 rad/s. Both the
mixer model and controller changed, so this comparison does not isolate the
mixer's contribution.

The [guard comparison](Analysis/survivable_set.py) changes the vehicle and
landing thresholds together with the controller's minimum thrust while inverted.
Paired trials therefore compare complete configurations; they do not establish
the guard's separate contribution.

The [parachute model](Analysis/survivable_set.py) assumes a nominal 0.8 s
before deployment and 0.6 s of inflation with no useful drag. For a drop from
rest, the ballistic distance over that 1.4 s is `g * t² / 2 ≈ 9.6 m`, already
beyond the tested maximum of 6 m. This explains the
[stored parachute outcomes](Data/survivable_set_results.json) under those timing
assumptions. It is not a general minimum height for other parachutes or arbitrary
initial velocities.

The [landing verdict](Analysis/survivable_set.py) uses impact vertical speed and
tilt only. It omits lateral impact speed, spin and physical damage criteria, so
passing it does not establish crash survival.

The rotor-out results above use a release/startup scenario that cuts all four
motors during detection and startup. A new comparison ran 7,200 trajectories
with the healthy motors held at their previous thrust after a fault. All 8
primary comparisons distinguish the scenarios. Losing one rotor gets worse by
18 to 53 percentage points of landing pass rate, while losing two opposite
rotors improves by 9 to 16 points and reduced authority on all motors by 38 to
41 points. These results use the historical estimated aircraft. See the [new scenario results](Analysis/current-results.md#scenario-comparison-with-selected-cases).

## Hardware so far

- **Bench chain.** A QT Py RP2040 reads a load cell through an NAU7802
  amplifier, plus an INA260 power monitor and an LIS3DH accelerometer. Firmware
  and host capture code are written and tested on synthetic serial output. They
  have not run on hardware yet. The chain is kept for per-motor thrust
  measurements if a Crazyflie is bought. [Wiring and bring-up](docs/bench-acquisition.md).
- **Retired V995 fixture.** The [V995 cradle generators](cad/v995/README.md) and
  [measurement worksheet](evidence/v995-fixture-measurements/README.md) are kept
  as history. The worksheet's 15 load-cell rows and 5 bench rows still describe
  the bench.

## Quick start

Python 3.11, the CI version. No hardware or CAD install is needed.

```sh
git clone https://github.com/500ft/multirotor-recovery-dynamics.git
cd multirotor-recovery-dynamics
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python cad/input_requests.py --check
python -m unittest Analysis.tests.test_bench_inputs Analysis.tests.test_results_numbers -v
```

Both test modules should report `OK`, and pending inputs stay pending. The
[reading guide](docs/START_HERE.md) covers the full analysis suite, study
regeneration and the pinned CadQuery environment.

## What's next

Replay NanoBench's recorded motor commands through the existing rigid-body
model with the documented parameters, and report the open-loop error per
flight. Then identify the parameters on training flights and check them on
held-out flights. The [roadmap](ROADMAP.md) has the full sequence, ending with
a recovery controller tested on the real firmware in simulation and a design
study. Buying a Crazyflie for flight tests is a later decision.

## Safety and limits

**Do not attempt recovery flights from the current state of this repository.**
Work through the [bench checklist](Instrumentation/propulsion-bench-safety-checklist.md)
and [operating constraints](Safety/README.md) first.

- Mass properties, propulsion, guard response and recovery have not been
  measured. A passing test or a good simulated sweep does not change that.
- NanoBench covers hover, excitation and trajectory tracking, with no tumbling.
  A model validated on it is validated in normal flight; recovery results stay
  model predictions until flown.

## Documentation

| Document | What it covers |
| --- | --- |
| [Reading guide](docs/START_HERE.md) | Short review or full reproduction |
| [Current results](Analysis/current-results.md) | Mass, guard, recovery and Monte Carlo results in full |
| [Survivable-set design](docs/specs/survivable-set/design.md) | The paired study behind the guard and parachute results |
| [Literature review](literature/README.md) | What is established, what is open, and which claims the sources contradict |
| [Engineering audit](docs/ENGINEERING_AUDIT.md) · [traceability](docs/TRACEABILITY.md) | Which numbers are derived and which are assumed |
| [Data and figures](docs/data-and-figures.md) | Inputs and code for each plot |
| [Open questions](OPEN_QUESTIONS.md) | Decisions still needed |
| [State machine](Controls/state_machine.json) | Controller states and transitions |

```text
Analysis/          models, gates, tests and result write-ups
Controls/          state machine and interfaces
Engineering Data/  parameter budgets, requirements and failure analysis
cad/               geometry generators, input registers and checks
Instrumentation/   bench firmware, capture code and safety checklist
Safety/            release-rig planning and operating limits
Figures/           simulation figures and diagrams
docs/              specifications and guides
```

## Contributing and license

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing an input, controller or
result. Report problems in
[issues](https://github.com/500ft/multirotor-recovery-dynamics/issues/new/choose)
with the command, revision and what you saw.

Code is [MIT licensed](LICENSE); third-party sources keep their own terms. Cite
the repository revision and the model or result used. The project was first
called SelfStabilizingDrone ([identity note](docs/REPOSITORY_IDENTITY.md)).
