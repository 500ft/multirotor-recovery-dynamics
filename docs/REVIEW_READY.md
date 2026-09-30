# Partial handoff — software integrity ready for review

## Day-3 preparation — 2026-09-09

Six request-sheet tests cover exact pending-row coverage, a newly added unknown pending row, invalid units, a filled pending value, duplicates and snapshot drift. 29 CAD tests pass. The load-cell choice is sourced and proposed; no fixture geometry, hole pattern or measurement was invented.

Review [DAY3_PLAN.md](https://github.com/500ft/multirotor-recovery-dynamics/blob/935a38b5f4d187669ce2f6d0ceb88ef0a8d79c6c/docs/DAY3_PLAN.md), [deliverable](../cad/bench/fixture-preparation.md), and [commands/evidence](../evidence/task-day3-2026-09-09/README.md). Base: `3658f038f115f0c2d831333eed935b13caf032c0`; new PR branch: `task/day-three-20260909`. No original Owner/External gate is closed. Final source identity is the PR head, reported in its delivery record rather than embedded circularly here.

No guessed motor-hole layout, caliper readings, calibrated thrust, vehicle radius or fixture approval.

## Hosted tooling acceptance — 2026-09-09

DR-CAD-10 is now **done**: hosted geometry and existing CI passed for source
`82a652bd615f17862dbeed326828289b2af73b58`. The uploaded STEP was downloaded, hash-checked,
reimported and checked for one solid and contracted volume. See
[hosted checks and artifact identity](../evidence/review-2026-09-09/hosted-verification.json). This supersedes the
intermediate in-progress statements below. Owner/physical gates remain open.


## Latest follow-up — 2026-09-09

[Day-2 adversarial review](../evidence/review-2026-09-09/README.md) supersedes
the initial completion claim below: DR-CAD-10 is in progress until the installed
geometry workflow runs green. The original patch-only delivery did not meet its
CI acceptance criterion. Input admission, full direct-package version checking,
and STEP round-trip metric checks are hardened with reproduced regressions.

[DR-CAD-10 geometry-tooling handoff](../evidence/task-2026-09-09/README.md) adds a parameter-driven
CadQuery generator, a reviewed geometry contract with 12 fail-closed tests, and a pinned
toolchain. It regenerates model geometry from the register; it is not a fixture design, part or
measurement. Geometry CI runs in [`.github/workflows/cad-geometry.yml`](../.github/workflows/cad-geometry.yml).

## Follow-up — 2026-09-08

[DR-CAD-01 input-register handoff](../evidence/task-2026-09-08/README.md) completes
one planning-input task, not a CAD model. Hardware/metrology owner gates remain
open. Earlier sprint evidence below is historical and unchanged.

Prepared 2026-09-05; software handoff completed 2026-09-06. Physical validation and Owner review remain pending.

## Identity and scope

- Canonical checkout: `/Users/redhose/Developer/research-sprints/2026-09-05/SelfStabilizingDrone`.
- Remote: https://github.com/500ft/SelfStabilizingDrone.git
- Branch: `sprint/evidence-integrity-20260905`.
- Base commit: `45da9be1a9647ce39ae18e3ea2494d965ee827e8`.
- Final commit: this packet's containing commit (reported in the PR; not self-embedded). Original owner checkout remains untouched.
- Candidate gate SHA256: `d8de05fc5c239190f648323a681f934d5b286f9cc4fce3090b2822e3ecf0068e`.
- Candidate test SHA256: `38ebd73ada2a5a842b5adbcb7aea76c732f36653d8d5f7651b9f66730d05ba8e`.
- Artifact: local Python source/CLI and replay evidence, not a registry release or deployment.
- Scope: measured-authority evidence admission and claims; no controller, dynamics, thresholds, estimates, or physical results changed.

Roadmap: [SPRINT_ROADMAP.md](https://github.com/500ft/multirotor-recovery-dynamics/blob/a1d5bf944247e55688d18af85cfe9efab1591b13/docs/SPRINT_ROADMAP.md).
Status authority: [SPRINT_TASKS.csv](SPRINT_TASKS.csv).
Checkpoints: [SPRINT_PROGRESS.md](SPRINT_PROGRESS.md).

## Deliverables and acceptance evidence

| Deliverable | Implementation and evidence |
|---|---|
| Invalid numerics do not PASS or masquerade as physical FAIL | [gate](../Analysis/measured_authority_gate.py), [regressions](../Analysis/tests/test_measured_authority_gate.py), [red/green record](../evidence/sprint-2026-09-05/verification.md) |
| Six sampled motors per grid, unique observations, source hashes, supplied uncertainty | [format/limits](specs/measured-authority-gate/evidence-contract.md), [admission amendment](specs/measured-authority-gate/design.md), evidence-contract unit tests |
| Actual CLI route, strict JSON, explicit synthetic status | [ten-case outputs](../evidence/sprint-2026-09-05/cli-evaluation.json), [predeclared judgments](../evidence/sprint-2026-09-05/evaluation.md), [replay script](../evidence/sprint-2026-09-05/evaluate_candidate.py) |
| Correct research wording | [README](../README.md), [Scenario C](../Analysis/current-results.md): authority AND controller changes; empirical quantile not population confidence |
| Reproducible review packet | [baseline/reproduction](../evidence/sprint-2026-09-05/baseline.md), [final verification](../evidence/sprint-2026-09-05/verification.md), ledger |

## Intentional interface changes

`evaluate_rows(rows, evidence_path=Path(...))` requires a valid source manifest for a verdict. Original three-column-only calls return INCONCLUSIVE. Added IDs and nominal derived uncertainty are documented; nominal torque is reduced by supplied expanded uncertainty once. Missing uncertainty has no zero default.

CLI adds `--manifest`. Exit codes: PASS0, FAIL1, INCONCLUSIVE2, DEVELOPMENT_ONLY3. JSON includes evidence kind, manifest hash, numerical result, sampled motor IDs and static-only scope. The authority/voltage/grid thresholds and962/1,000 recovery gate are unchanged. Inclusive acquisition tolerances handle representational roundoff (up to four ULPs), not an expanded physical operating envelope.

The checker validates supplied consistency. A synthetic-labeled bundle cannot PASS, but falsely relabeling synthetic data measured is not detectable from metadata. The replay deliberately demonstrates this limitation. A reviewer must inspect source data and calibration/derivation quality before accepting a measured result.

## Reproduce

The primary agent independently reran the delegated software checks on2026-09-06:
[actual rerun record](../evidence/sprint-2026-09-05/parent-verification.json).
This is additional software verification, not independent human or physical validation.

From the canonical checkout, with the tested Python3.11 environment/dependencies:

```bash
python -m unittest Analysis.tests.test_measured_authority_gate -v
python -m unittest discover -s Analysis/tests -v
python -m compileall -q Analysis
git diff --check
python -m Analysis.measured_authority_gate --help
python evidence/sprint-2026-09-05/evaluate_candidate.py --output evidence/sprint-2026-09-05/cli-evaluation.json
```

Observed: focused21/21; full86/86 in128.281s; compile/diff/help exit0; scenario runner10/10 matched, exit0. Baseline69/69 in119.355s. The improvement is rejected invalid/incomplete evidence and explicit result boundaries, not a higher test count. No configured lint/typecheck/distribution build was claimed run.

The last command regenerates synthetic output. No physical raw data is present. Source/test hashes and original judgments were recorded before additional CLI cases; all evaluation is developer evidence, not independent validation.

## Incomplete work — three priorities

1. **DR-S02:** Owner supplies actual six-motor roster, raw telemetry, calibrated geometry, uncertainty/derivation review and approved guarded measurement readiness. [Prepared intake](specs/measured-authority-gate/evidence-intake.md) is not completed coordination/approval.
2. A real authority result needs competent source/calibration review; transient-response distributions and fixed-controller recovery evaluation are not produced. No flight or Wave-2 spending authorization follows.
3. **DR-S09:** independent human review/feedback pending. Another agent's rerun is useful verification, not an independent human/hardware study.

Potential portfolio bullet, limited to completed software: “Hardened a preregistered UAV authority gate to reject invalid and untraceable measurement inputs, enforce six-motor source coverage and uncertainty handling, and expose reproducible synthetic-versus-measured evidence boundaries.”

## Ready-to-send review request

“Review SelfStabilizingDrone against docs/SPRINT_ROADMAP.md. Repository: /Users/redhose/Developer/research-sprints/2026-09-05/SelfStabilizingDrone. Base commit: 45da9be1a9647ce39ae18e3ea2494d965ee827e8. Final commit: PR head (see GitHub PR). Review index: docs/REVIEW_READY.md. Incomplete work: DR-S02 actual measurement/calibration/readiness evidence, measured-input recovery evaluation, and DR-S09 independent human feedback. Reproduce the changed behaviors and counterexamples, rerun appropriate checks, and assess the code and evidence independently. Review first; make further changes only if requested.”
