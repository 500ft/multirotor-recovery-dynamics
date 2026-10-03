# Multirotor Recovery Dynamics

Can a small drone that is thrown, dropped or loses a motor get itself level
again before it hits the ground? This repository models that recovery in
simulation. The owner has yet to choose whether to close the simulation study
or continue with bench characterization of the stock Veeniix V995 micro-quad.

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
other inputs came from estimates and catalog specifications. The available
physical aircraft is a stock V995 with its original board and transmitter. It
cannot run the simulated controller: no usable command or firmware interface
has been established. Its flight-ready mass still needs to be weighed.

## Simulation results

All of these use estimated inputs. None has been checked against hardware.

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
  have not run on hardware yet. [Wiring and bring-up](docs/bench-acquisition.md).
- **CAD.** The load-cell end adapter is generated and checked. The cradle that
  holds the whole V995 on the load cell, and the base plate under it, have
  working generators waiting on the [measurement worksheet](evidence/v995-fixture-measurements/README.md).
  It has 15 load-cell rows, 7 aircraft rows and 5 bench rows. Those readings
  supply five pending CAD parameters and confirm the delivered cell's mounting
  pattern. [V995 fixture](cad/v995/README.md).

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

The owner must choose between closing the simulation study and V995-only bench
characterization (D3). If bench work is selected, the
[27-row measurement worksheet](evidence/v995-fixture-measurements/README.md)
remains its unpowered prerequisite. It covers the delivered load cell, aircraft
mass and geometry, and bench dimensions. See the [roadmap](ROADMAP.md) for the
pending scope choice. Logger development, release trials and a new aircraft
are not authorized by this correction.

## Safety and limits

**Do not attempt recovery flights from the current state of this repository.**
Work through the [bench checklist](Instrumentation/propulsion-bench-safety-checklist.md)
and [operating constraints](Safety/README.md) first.

- Mass properties, propulsion, guard response and recovery have not been
  measured. A passing test or a good simulated sweep does not change that.

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
