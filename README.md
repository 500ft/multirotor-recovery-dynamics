# Multirotor Recovery Dynamics

A simulation-first study of Crazyflie tumble recovery. A baseline replay of
public flights shows substantial angular-rate error in documented motor models.
The next step establishes what can be identified before fitting a model.

[![CI](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml)
![Evidence: development replay](https://img.shields.io/badge/evidence-development_replay-475569)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e)](LICENSE)

[Current work](#current-work) · [Roadmap](ROADMAP.md) ·
[Historical results](#simulation-results) · [Quick start](#quick-start)

## Current work

The owner selected the Crazyflie family. The
[parameter register](Engineering%20Data/platform_crazyflie.csv) separates the
instrumented NanoBench aircraft, stock hardware specifications and published
model defaults. The [register guide](Engineering%20Data/README.md) explains the
firmware's motor-voltage thrust curves and command limits.

[NanoBench](https://github.com/syediu/nanobench-iros2026) supplies recorded motor
commands, motion-capture state and onboard telemetry. The
[executed replay](docs/nanobench-baseline.md) compares documented force and angular
dynamics, short open-loop predictions and persistence on development flights.
[Per-flight errors](Data/nanobench-baseline/development-errors.csv) and the
[result figure](Figures/nanobench-baseline.png) report the outcome. Whole-flight
splits were committed before comparison; final-test predictions remain unexamined.

After identification, the study will compare stock and recovery firmware in
CrazySim and examine feasible design variants. No purchase is authorized before
the owner's final decision. The V995 fixture and the earlier designed-aircraft
simulation are historical work.

## Limits

NanoBench covers ordinary flight and contains no tumble-recovery trials.
Agreement there supports only the tested configuration and operating range.
Recovery, design-variant performance and damage tolerance require separate
physical evidence. Historical results below belong to a different aircraft.

## Simulation results

Historical results are retained here for reproduction.

These results are for the historical designed aircraft (about 130–165 g, never
built). All of them use estimated inputs, and none has been checked against
hardware.

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

The historical [landing verdict](Analysis/survivable_set.py) uses impact vertical speed and
tilt only. It omits lateral impact speed, spin and physical damage criteria, so
passing it does not establish crash survival.

The rotor-out results above use a release/startup scenario that cuts all four
motors during detection and startup. A new comparison ran 7,200 trajectories
with the healthy motors held at their previous thrust after a fault. All 8
primary comparisons distinguish the scenarios. Losing one rotor gets worse by
18 to 53 percentage points of landing pass rate, while losing two opposite
rotors improves by 9 to 16 points and reduced authority on all motors by 38 to
41 points. These results use the historical estimated aircraft. See the [new scenario results](Analysis/current-results.md#scenario-comparison-with-selected-cases).

## Existing bench software and historical CAD

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

The [roadmap](ROADMAP.md#current-step) leaves G1 incomplete for dynamic
identification. Resolve the replay's configuration and timing limits and assess
usable excitation before selecting identifiable parameters and acceptance
tolerances. Compiled-firmware comparison and a purchase decision remain later work.

## Safety

Simulation work authorizes no powered test. The [safety plan](Safety/README.md)
must be revised for the chosen aircraft, instrumentation and facility before
hardware testing. The existing [bench checklist](Instrumentation/propulsion-bench-safety-checklist.md)
is retained for future calibration work.

## Documentation

| Document | What it covers |
| --- | --- |
| [Reading guide](docs/START_HERE.md) | Short review or full reproduction |
| [Current results](Analysis/current-results.md) | Current Crazyflie status and historical simulation results |
| [Historical survivable-set design](docs/specs/survivable-set/design.md) | The paired study behind the guard and parachute results |
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
