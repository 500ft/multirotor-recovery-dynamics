# Start here — Multirotor Recovery Dynamics

The [README](../README.md) is the overview and the [roadmap](../ROADMAP.md) is
the plan. This guide is for reading the work quickly or rerunning it.

## Reading paths

| If you have | Read |
| --- | --- |
| Two minutes | [README results](../README.md#simulation-results), then [current results](../Analysis/current-results.md) |
| Half an hour | The [survivable-set design](specs/survivable-set/design.md), then one figure traced through [data and figures](data-and-figures.md) |
| A review to do | The [review index](REVIEW_READY.md) |
| Hardware to set up | [V995 fixture notes](../cad/v995/README.md), the [measurement worksheet](../evidence/v995-fixture-measurements/README.md) and the [bench wiring and bring-up](bench-acquisition.md) |

## Two vehicles, kept apart

The simulation work used a designed 130–165 g vehicle (EX1103 motors, Kakute H7
flight controller, 2S battery). It was never built. Its numbers live in
`Engineering Data/`, `cad/bench/` and the analysis code, with its own gates
(7.0 V, six motors, 0.020 N·m).

The physical platform since 2026-09-27 is a stock Veeniix V995, about 50 g.
It has its own register in `cad/v995/` and no values are copied from the
designed vehicle. Its first measured values will go into a new
`Engineering Data/platform_v995.csv`.

## Software checks — Python 3.11

Set up as in the [README](../README.md#quick-start), then from the repository
root:

```sh
python cad/input_requests.py --check
python -m unittest discover -s Analysis/tests -v
python -m unittest discover -s Instrumentation/tests -v
```

The full analysis suite takes a few minutes. [CI](../.github/workflows/ci.yml)
runs the same sequence. Real inputs belong in the parameter registers
([designed vehicle](../cad/bench/parameters.csv), [V995](../cad/v995/parameters.csv)),
never in the derived request sheet.

## CAD — pinned environment

The pins in [cad/requirements.lock](../cad/requirements.lock) cover direct
packages only, not the whole dependency tree:

```sh
conda create -n recovery-cad -c conda-forge --strict-channel-priority --file cad/requirements.lock
conda activate recovery-cad
python -m pytest cad/tests -q
```

The [CAD workflow](../.github/workflows/cad-geometry.yml) regenerates the
geometry and uploads it for inspection. For the V995, only the load-cell end
adapter builds today; the cradle and base plate build once the worksheet is
filled.

## Regenerating the simulations

These overwrite the committed JSON and figures, so use a spare checkout at a
recorded revision:

```sh
python -m Analysis.run_release_recovery
python -m Analysis.monte_carlo_recovery
```

[Data and figures](data-and-figures.md) lists smaller single-study commands.
The 4% placeholder result and the 300 of 300 mixer prediction differ in
controller as well as torque, so they are not a controlled test of torque
alone.

## Before any powered work

Nothing in this guide authorises powering anything. Go through
[Safety](../Safety/README.md) and the
[bench checklist](../Instrumentation/propulsion-bench-safety-checklist.md)
with the person responsible, and start the bench bring-up with the power-off
continuity check in [bench-acquisition.md](bench-acquisition.md).

The September 11 [completion correction](COMPLETION_RECONCILIATION.md)
explains which early deliverables were preparation rather than finished work.
