# Start here — Multirotor Recovery Dynamics

## Choose a path

- **Two-minute review:** [README results](../README.md#simulation-results) →
  [current results](../Analysis/current-results.md) →
  [bench preparation](../cad/bench/fixture-preparation.md).
- **Technical review:** trace one [figure](data-and-figures.md) to its source,
  inspect the [measured-authority contract](specs/measured-authority-gate/),
  then reproduce the relevant check.
- **Contribution:** read [Contributing](../CONTRIBUTING.md), select a bounded
  defect or source correction, and preserve the registered evidence requirements.

## Software checks — Python 3.11

Use the [README installation](../README.md#quick-start), then run from the root:

```sh
python cad/input_requests.py --check
python -m unittest discover -s Analysis/tests -v
```

The full suite is longer than the quickstart; the recorded baseline took about
2.5 minutes in the local environment. Runtime is not a hardware-performance claim.
See [CI](../.github/workflows/ci.yml) for the maintained sequence.

Input-sheet generation cannot fill an unknown dimension or change provenance.
The [canonical register](../cad/bench/parameters.csv), not the derived request
sheet, is where evidence-backed inputs belong.

## Nominal CAD — separate pinned environment

Use [cad/requirements.lock](../cad/requirements.lock), which pins direct
packages but is not a complete transitive/platform lock:

```sh
conda create -n recovery-cad -c conda-forge --strict-channel-priority --file cad/requirements.lock
conda activate recovery-cad
python -m pytest cad/tests -q
```

The [CAD workflow](../.github/workflows/cad-geometry.yml) regenerates and uploads
the nominal envelope for inspection. The [generator](../cad/generate.py) refuses
pending inputs needed by supported geometry; its current motor body is not a
mounting pattern, propeller or assembled fixture.

## Optional simulation regeneration

Use a disposable checkout at a recorded revision because these commands
overwrite generated JSON and figures:

```sh
python -m Analysis.run_release_recovery
python -m Analysis.monte_carlo_recovery
```

Use [the figure guide](data-and-figures.md) to select a smaller calculator or
inspect committed outputs instead. The 4% placeholder result and the 300/300
revised prediction differ in controller behavior as well as authority assumptions;
they are not a controlled causal test of torque alone.

## What the next measurement needs

[Fixture preparation](../cad/bench/fixture-preparation.md) distinguishes vendor
lookups, physical observations and design decisions. The proposed load cell
is not an installed/calibrated component. The stand calibration lever and
vehicle `arm_m` are different quantities.

Freeze the fixture's dimensional/uncertainty contract before modeling or loading
the measurement assembly. Keep the registered 7.0 V bench condition, individual
thrust observations, installed geometry and fixed-controller evaluation distinct.

No instruction here permits powered work. Review [Safety](../Safety/README.md)
and the [propulsion-bench checklist](../Instrumentation/propulsion-bench-safety-checklist.md)
with the responsible operator. The [review index](REVIEW_READY.md) and
[task ledger](SPRINT_TASKS.csv) retain actual completion status.

## September 11 completion correction

Read the [item-by-item correction](COMPLETION_RECONCILIATION.md) before interpreting a prepared protocol, software check, or search export as a completed research gate. It identifies actual deliverables and the remaining measurement, review, or source-reading work separately.
