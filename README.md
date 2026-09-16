# Multirotor Recovery Dynamics

Model the conditions under which a protected micro-UAV could recover attitude
after release—and identify the measurements needed to test that prediction.

[![CI](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/multirotor-recovery-dynamics/actions/workflows/ci.yml)
![Evidence: simulation and nominal CAD](https://img.shields.io/badge/evidence-simulation_%2B_nominal_CAD-475569)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e)](LICENSE)

[Start here](docs/START_HERE.md) · [Evidence](#evidence-snapshot) · [Quick start](#quick-start) · [Documentation](#documentation) · [Safety](#safety-and-limits)

![Conceptual sequence from simulated release to pending propulsion measurements and a new fixed-controller recovery evaluation](docs/media/project-overview.svg)

*Conceptual engineering sequence, not a flight demonstration. Measured propulsion
authority and physical recovery remain pending.*

## About

Midair recovery is a coupled engineering problem: release detection, available
torque, descent, battery state, mass distribution and guard loads must agree.
A plausible controller alone is not evidence that the vehicle can recover.

This repository links those constraints through executable dynamics, structured
engineering inputs, regression tests and explicit stop/go gates. It includes
nominal motor-envelope CAD and bench preparation—not a finished recovery vehicle.

## Evidence snapshot

| Work product | What exists | Boundary |
| --- | --- | --- |
| Release and recovery models | [Dynamics, uncertainty and gate results](Analysis/current-results.md) | Simulation with estimated or catalog-derived inputs |
| Negative feasibility finding | Placeholder-torque Monte Carlo recovers 4.0% in the reported as-toleranced case | A failed modeled gate, not a physical failure rate |
| Revised prediction | Assumed four-motor mixer **and revised controller** recover 300/300 in the reported sweep | Not an isolated torque intervention or hardware validation |
| Nominal geometry | [Motor-envelope generator](cad/generate.py) and [geometry contract](cad/contract.json) | No guessed mount pattern, shaft or propulsion fixture |
| Bench preparation | [Input requests](cad/bench/input-requests.csv) and [fixture requirements](cad/bench/fixture-preparation.md) | Vendor proposals are not measurements or purchased parts |
| Measured-authority gate | [Registered evidence contract](docs/specs/measured-authority-gate/) | Actual thrust, installed geometry and recovery evaluation pending |
| Survivable-set study (A/B) | [Preregistration](docs/specs/survivable-set/design.md), motor-failure allocation, policy map with exact bounds | Simulation on EST action inputs (OQ-010); no hardware claim until the bench and drop gates run |

![Simulated altitude loss and recoverable tumble rate across component tiers](Figures/release_recovery_envelope.png)

*Simulation output with estimated/catalog inputs. The [result summary](Analysis/current-results.md)
and [figure provenance](docs/data-and-figures.md) explain the assumptions.
No recovery-flight or static-thrust measurements are shown.*

## Quick start

Use **Python 3.11**, matching CI. This bounded first check needs no hardware,
CAD installation or regenerated study outputs.

```sh
git clone https://github.com/500ft/multirotor-recovery-dynamics.git
cd multirotor-recovery-dynamics
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python cad/input_requests.py --check
python -m unittest Analysis.tests.test_bench_inputs Analysis.tests.test_results_numbers -v
```

Expected: the derived input-request sheet is consistent and both test modules
report `OK`. Pending values remain pending. These checks establish register
and documented-number consistency, not physical readiness.

The [reading guide](docs/START_HERE.md) separates the complete analysis suite,
optional study regeneration and pinned CadQuery environment.

## Documentation

| Start with | Use it to |
| --- | --- |
| [Reading guide](docs/START_HERE.md) | Choose a short review or a technical reproduction |
| [Current results](Analysis/current-results.md) | Inspect mass, guard, recovery and Monte Carlo conclusions |
| [Data and figures](docs/data-and-figures.md) | Trace plots to inputs, code and evidence states |
| [Measured-authority contract](docs/specs/measured-authority-gate/) | Understand what the next measurement must establish |
| [Fixture preparation](cad/bench/fixture-preparation.md) | Review load-cell proposal, interfaces and metrology |
| [CAD inventory](docs/CAD_ITEMS.md) | Separate planned assemblies from existing nominal geometry |
| [State machine](Controls/state_machine.json) | Inspect authoritative controller states and guards |
| [Bench safety checklist](Instrumentation/propulsion-bench-safety-checklist.md) | Review prerequisites before any powered work |
| [Review index](docs/REVIEW_READY.md) | Find checks, counterexamples and unresolved gates |

```text
Analysis/          models, acceptance gates, tests and result interpretation
Controls/          authoritative state machine and interfaces
Engineering Data/  parameter budgets, requirements and failure analysis
cad/               nominal geometry, input registers and geometry checks
Instrumentation/   proposed bench measurements and safety checklist
Safety/            release-rig planning and operating constraints
Figures/           existing simulation figures and engineering diagrams
docs/              contracts, source lineage and reviewer guides
```

## Next engineering gate

Prioritize the **single-motor propulsion bench**, not vehicle packaging.
Resolve source-backed mounting interfaces, fixture geometry, calibration and
installed lever-arm measurements before admitting thrust data at the registered
7.0 V condition. Vendor data at a different voltage/propeller is not that result.

The [fixture preparation](cad/bench/fixture-preparation.md) recommends a candidate
load cell and a metal load path, with reasons and unresolved inputs. It does
not authorize purchasing, assembly or operation. Measured static authority
would then feed a new fixed-controller evaluation; it would not itself validate
recovery in flight.

## Safety and limits

**Do not attempt recovery flight from the current repository state.** The
[bench checklist](Instrumentation/propulsion-bench-safety-checklist.md),
[operating constraints](Safety/README.md) and registered gates come first.

Mass properties, real propulsion authority, guard response and physical
recovery have not been measured here. A successful nominal STEP export,
a software test or a favorable simulated sweep cannot close those gaps.

## Contributing and license

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing an input, controller or
generated result. Report commands, source revision, evidence category and
counterexamples in [issues](https://github.com/500ft/multirotor-recovery-dynamics/issues/new/choose).

Repository code is [MIT licensed](LICENSE); third-party sources retain their
own terms. Cite the exact repository revision and the specific model or result
used. [Identity and presentation notes](docs/REPOSITORY_IDENTITY.md) explain the
rename; no paper title, frozen gate or software API is changed by it.
