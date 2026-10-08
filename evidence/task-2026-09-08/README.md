# DR-CAD-01 verification — 2026-09-08

Base: `afa39bba17e18062831f462e339eb14b0135f619`. Candidate identity is the
containing PR head; no physical specimen, geometry export or measurement is claimed.

Deliverables: [25-row register](../../cad/bench/parameters.csv),
[source and coordinate decisions](../../cad/bench/design-inputs.md), and
[consistency test](../../Analysis/tests/test_bench_inputs.py).
The authoritative status remains [CAD_TASKS.csv](https://github.com/500ft/multirotor-recovery-dynamics/blob/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b/docs/CAD_TASKS.csv).
The earlier sprint ledger is byte-preserved. Missing fits remain blank/pending;
completing the input inventory does not authorize fabrication or motor operation.

## Reproduction and observed evidence

Runtime: Python 3.11.8 (`/Users/redhose/ENTER/bin/python`). Commands run from the
repository root unless stated otherwise. The pristine baseline was checked in a
detached worktree at `/private/tmp/daily-baseline-20260908-SelfStabilizingDrone`
after the documentation draft existed, without copying candidate changes there.

| Command | Observed result |
| --- | --- |
| `python -m unittest discover -s Analysis/tests -q` at base | Exit 0; 90 tests, 120.307 s |
| Same command at candidate | Exit 0; 91 tests, 119.223 s |
| `python -m unittest Analysis.tests.test_bench_inputs -v` | Exit 0; one new consistency test |

The test checks source availability, evidence states, units, explicit missing
values and agreement with the frozen collective grid and authority threshold.
It is not a geometry, manufacturer-accuracy or hardware safety test. Vendor pages
and applicability caveats are linked in the input decisions. No dimensions from
the electrical UART map were promoted to mounting dimensions.

Final follow-up: repository and bench-input checks passed (11 tests, exit 0);
[captured outputs](checks.json). The embedded CAD validator passed (12 tasks,
four rejected invalid mutations, dependency/link/sprint preservation PASS).

Before accepting this PR, also run the embedded Python validator in
[CAD_PLAN_CHECKS.md](https://github.com/500ft/multirotor-recovery-dynamics/blob/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b/docs/CAD_PLAN_CHECKS.md), then `git diff --check`.
That validator checks dependencies, evidence links and historical sprint-ledger
preservation; it does not turn owner readiness into a completed gate.

Next: DR-CAD-02 owner fit/metrology/containment inputs, and independently
DR-CAD-10 geometry tooling. No complete vehicle packaging is required for the bench.
