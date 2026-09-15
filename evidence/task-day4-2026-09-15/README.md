# Day-4 implementation slice — evidence record (T00/T18)

Baseline: plan revision `a31a0de` on `docs/day4-plan-revision-20260914`
(implementation baseline `358872c` on `main`). Working tree: fresh clone of this
branch; no other local modifications. Delivered slice: T00 (this record), T01
([source-candidates.md](../../cad/bench/source-candidates.md)), T11 gap inventory
([fixture-definition.md](../../cad/bench/fixture-definition.md)). All D1–D6
decisions were pending at execution time, so no decision-gated step (T02–T10,
T12–T17) ran; no register value, evidence state, route file, task status or frozen
threshold changed.

Environment: Python 3.13.7 (system CPython), NumPy 2.5.3, Matplotlib 3.11.2.
This is not the pinned CAD environment; see the geometry row below.

## Commands and observed results — 2026-09-15

| Command | Observed |
| --- | --- |
| `python3 cad/input_requests.py --check` | exit 0; "consistent; no inputs accepted or measured" |
| `python3 cad/fixture_contract.py --check` | exit 0; "current: 2 evaluable, 10 pending" |
| `python3 cad/fixture_contract.py --release` | exit 2; `REFUSED INPUTS_INCOMPLETE`, 10 pending clauses + 11 pending rows (expected refusal, captured not suppressed) |
| `python3 cad/ledger_validator.py live` | exit 0; "PASS live: 13 tasks … 9 invalid mutations rejected; links OK" |
| `python3 -m unittest discover -s Analysis/tests` | exit 0; **Ran 91 tests**, OK, 138.9 s |
| `python3 -m pytest cad/tests tools --ignore=cad/tests/test_geometry.py -q` | exit 0; 34 passed |
| `python3 tools/check_presentation.py . "Multirotor Recovery Dynamics" multirotor-recovery-dynamics` | exit 0; issues: `[]`, 5 files, 62 local links |
| `python3 tools/test_presentation.py` | exit 0; OK |
| `git diff --check` | exit 0 |

Geometry/STEP tests (`cad/tests/test_geometry.py`) require the pinned
`cad/requirements.lock` environment (CadQuery), not present locally; this branch
touches `cad/**`, so the hosted `CAD geometry` workflow runs on the PR and its
result is recorded there — see the PR checks for the head commit.

Source access for T01 (fetched 2026-09-15): Phidgets 3132_0 product page and
mechanical drawing PDF Rev 1 (2025-06-10) — accessible, dimensions transcribed into
the candidate packet with printed/derived marked; Happymodel EX1103 page —
accessible, mounting pattern confirmed absent; BetaFPV/Flywoo Gemfan 2023 listings —
accessible, hub nominals only. No dimension was inferred from photographs; no
delivered part was identified or inspected.
