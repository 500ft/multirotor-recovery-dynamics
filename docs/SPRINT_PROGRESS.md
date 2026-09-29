# Sprint progress — SelfStabilizingDrone

## 2026-09-11 — evidence-gap correction

The [current correction](COMPLETION_RECONCILIATION.md) supersedes any interpretation that earlier preparation closed a physical, approval, or source-review gate. Work is on `fix/evidence-gaps-20260911` from current renamed main; historical entries below retain their original dates and PR snapshots. The original day-3 and presentation PRs are now merged, but this correction is a new reviewable change, not an asserted merge or publication.

Each omitted or incomplete recommendation is accounted for separately in the current correction and existing task ledgers. No owner signature, measurement, PI conversation, imagery judgment, disclosure approval or independent review was fabricated. Exact tests, scope and next inputs are linked from the correction record; actual delivery state is established by its PR.

## Day-3 work — 2026-09-09

Delivery update: the preparation was committed as 500ft and pushed; [day-3 PR](https://github.com/500ft/SelfStabilizingDrone/pull/12) is open against main. Initial implementation source: `7b13fa1d314e711fe5ff298cb42c32ef400359ca` (later review/documentation commits are visible in the PR). This supersedes the pre-push stopping state below. Original day-1/day-2 PRs are merged; this new PR is not merged. Resume from the named unresolved project gates in [DAY3_PLAN.md](https://github.com/500ft/multirotor-recovery-dynamics/blob/935a38b5f4d187669ce2f6d0ceb88ef0a8d79c6c/docs/DAY3_PLAN.md), not from the already completed push step.

Both reviewed PR layers merged into main; new work starts from `3658f038f115f0c2d831333eed935b13caf032c0` on `task/day-three-20260909`. Six request-sheet tests cover exact pending-row coverage, a newly added unknown pending row, invalid units, a filled pending value, duplicates and snapshot drift. 29 CAD tests pass. The load-cell choice is sourced and proposed; no fixture geometry, hole pattern or measurement was invented.

The [evidence record](../evidence/task-day3-2026-09-09/README.md) contains checks and limits. All 91 existing analysis tests passed in 143.964 seconds, alongside 29 CAD tests. Work is locally verified and not yet recorded here as pushed/merged. Current edits belong to this task; original checkouts were preserved. Next: commit the bounded change and open the new PR; preserve all stated external gates.

## Hosted tooling acceptance — 2026-09-09

DR-CAD-10 is now **done**: hosted geometry and existing CI passed for source
`82a652bd615f17862dbeed326828289b2af73b58`. The uploaded STEP was downloaded, hash-checked,
reimported and checked for one solid and contracted volume. See
[hosted checks and artifact identity](../evidence/review-2026-09-09/hosted-verification.json). This supersedes the
intermediate in-progress statements below. Owner/physical gates remain open.


## 2026-09-09 — adversarial CAD review amendment

The original day-2 completion statement below was premature: a proposed workflow
is not running CI. DR-CAD-10 is now `in_progress` pending a green hosted CAD job.
The workflow is installed and existing CI also targets day-1 stack bases. Current
authentication includes workflow permission; the old restriction is historical.

Baseline 12 CAD tests passed. Eleven regression cases then failed on the
original implementation: nonfinite numeric inputs, populated pending/blank states,
duplicate parameter rows, three unchecked dependency versions, and two undetected
STEP round-trip metric changes. Minimal fixes produce 23 passing CAD tests.
The direct-package constraints are not a platform/transitive build lock.
See [review evidence](../evidence/review-2026-09-09/README.md).
Owner gates, recorded dimensions, registered thresholds, original model exports,
and the historical sprint ledger are unchanged. No fabrication or measurement.
Next action: push the amended PR, observe both hosted jobs, then close only the
tooling task if its installed geometry job passes.

## 2026-09-09 — DR-CAD-10 code-CAD regeneration and geometry tests (historical initial handoff)

Completed the day-2 CAD tooling task. CadQuery is installed in an isolated environment and
pinned in [`cad/requirements.lock`](../cad/requirements.lock) only after a STEP export/reimport
smoke test. [`cad/generate.py`](../cad/generate.py) regenerates the `motor_envelope` family from
the registered parameters and refuses anything missing, pending, mis-united or invalid;
[12 tests](../cad/tests/test_geometry.py) hold it to [`cad/contract.json`](../cad/contract.json)
and prove failure on every bad-input class the task names. Geometry CI is shipped as an
appliable patch under `ci-proposed/` because the PR token lacks workflow scope. No CAD model of a
fixture, no physical part and no owner approval; owner gates are unchanged. Sole status is in
[CAD_TASKS.csv](CAD_TASKS.csv). [Verification](../evidence/task-2026-09-09/README.md).
Branch `task/priority-two-20260909`, stacked on the day-1 branch.
Next check: `python -m pytest cad/tests -q`.

## 2026-09-08 — DR-CAD-01 input register

Completed the existing highest-priority ready CAD-input task; its sole status is
in [CAD_TASKS.csv](CAD_TASKS.csv), not a duplicate sprint row. Historical sprint
CSV remains byte-preserved. [Inputs](../cad/bench/design-inputs.md) and
[verification](../evidence/task-2026-09-08/README.md) distinguish design/vendor
values from unavailable fit/measurement inputs. No CAD model, physical test or
owner approval. DR-CAD-10 is now ready for a later software tooling task; owner
interface approval still blocks real geometry acceptance and fabrication.
Branch `task/priority-one-20260908`; PR records committed/pushed identity.
Next check: `python -m unittest Analysis.tests.test_bench_inputs -v`.

## 2026-09-06 — Reviewer-driven CAD amendment

This entry supersedes the earlier CAD allocation and readiness wording. The same CAD PR is now draft, pending the owner planning-ledger placement decision. [Review disposition](CAD_REVIEW_DISPOSITION.md) records that block; [CAD_PLAN.md](CAD_PLAN.md) and [CAD_TASKS.csv](CAD_TASKS.csv) contain revised priorities, separate tooling estimates and explicit parked work. No CAD model or new measurement was produced. Original integrity-sprint tasks/evidence remain unchanged. Next work is limited to active input-register tasks and unresolved owner decisions, not the parked portfolio-wide CAD program.

## 2026-09-06 — CAD task amendment

Added [individual CAD work orders](CAD_PLAN.md) and [CAD_TASKS.csv](CAD_TASKS.csv), separating component modeling, fixtures, inspection and release deliverables. This is planning only: no CAD or physical task is complete. The original sprint ledger and evidence are unchanged. CAD branch: `plan/cad-tasks-20260906`; the PR supplies the committed source identity. Next CAD action: the first input-register task in the CAD ledger; owner-gated successors remain blocked. Verification of this amendment is recorded in [CAD_PLAN_CHECKS.md](CAD_PLAN_CHECKS.md).

Task status authority: [SPRINT_TASKS.csv](SPRINT_TASKS.csv).

## 2026-09-05 — preparation and baseline

- Isolated checkout `/Users/redhose/Developer/research-sprints/2026-09-05/SelfStabilizingDrone`; branch `sprint/evidence-integrity-20260905`, base `45da9be1a9647ce39ae18e3ea2494d965ee827e8`; initially clean.
- Read execute-and-test and quality-gates instructions; found unittest in CI, no configured lint/typecheck/build.
- Reproduced positive-infinite torque PASS using all 30 grid rows. This is a product defect, not a dependency error.
- Full baseline suite completed: 69 tests in 119.355s, exit 0. NumPy 2.1.1 and Matplotlib 3.10.1 observed.
- Proposed six-day 30h roadmap saved. No behavior changed; waiting for parent to present the roadmap and authorize implementation continuation.
- Owner measurement evidence and facility readiness remain absent. Preparing requirements is not measurement, outreach, or approval.
- Next action: write failing regression when parent gives GO.
- At preparation checkpoint no commit/push; only sprint records were new.

## 2026-09-05 to 2026-09-06 — authorized implementation and partial handoff

- Parent presented roadmaps and gave GO. Rechecked the isolated checkout on
  September 6: same branch/base, only this sprint's changes; no original-owner
  checkout edits.
- DR-S03/S04: test-first finite/sign validation, unique observation IDs,
  six-motor coverage per grid, hashed raw/derived/calibration/uncertainty/
  derivation artifacts, declared reviewer/coverage, uncertainty subtraction.
  Synthetic-labeled data returns DEVELOPMENT_ONLY; caller-provided labels and
  review strings do not authenticate physical data.
- DR-S05: corrected Scenario C's joint authority/controller interpretation;
  static authority and empirical quantiles no longer imply dynamic validation
  or confidence-qualified population coverage. Preserved 0.020 N·m and
  962/1,000 requirements.
- DR-S06: real module CLI tested; exit 0 PASS, 1 FAIL, 2 INCONCLUSIVE, 3
  DEVELOPMENT_ONLY; strict JSON output; old three-column input is now
  intentionally INCONCLUSIVE. Input format and owner intake are documented.
- DR-S07: froze code/test hashes and ten expected synthetic CLI judgments
  before executing the additional scenario script; 10/10 matched, exit 0.
  This is developer evidence, not independent or physical evaluation. Earlier
  acquisition-tolerance endpoint failure was fixed test-first and retained as
  development material. No physical gate or general accuracy claim follows.
- Final full suite: 86 tests in 128.281s, exit 0. Focused suite21/21; compile,
  diff check, and Markdown links passed. Detailed commands/results:
  [verification](../evidence/sprint-2026-09-05/verification.md).
- DR-S08: review packet assembled. DR-S02 and DR-S09 remain blocked on actual
  Owner evidence/readiness and human feedback. No outreach, procurement,
  hardware operation, scheduling, commit, push, publication, or deployment.
- The 30 hours are planned workload estimates, not a claim that 30 clock hours
  elapsed in this session. Agent-owned bounded software deliverables completed;
  hardware/data/reviewer lead times are not compressed.
- HEAD remains `45da9be1a9647ce39ae18e3ea2494d965ee827e8`; branch
  `sprint/evidence-integrity-20260905`. Eight tracked source/docs files modified
  plus new sprint/evidence/contract documents. Candidate explicitly uncommitted.
- Next Agent action: parent independently runs
  `python -m unittest discover -s Analysis/tests -v` from this checkout and
  reviews `docs/REVIEW_READY.md`. Next Owner task: DR-S02 evidence intake;
  no further measured-result work until that dependency is genuinely supplied.
