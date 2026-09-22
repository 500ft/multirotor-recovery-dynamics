# Week of 2026-09-19 — evidence record (Day 1: W01 + W07 intake)

Baseline: `main` = `eb5cf95` (#21 merged); candidate `study/survivable-set-a2` =
`03d6b49` (#22 open, CI green on that head, base retargeted to `main` 2026-09-19 —
not merged). This branch `week/2026-09-19-day1` stacks on `03d6b49`. Working tree
was clean before Day-1 edits.

Environment: Python 3.11.8 (`~/ENTER/bin/python3`), NumPy 2.1.1, Matplotlib 3.10.1.
Differs from the #22 local evidence (3.13.7 / 2.5.3) and matches CI's 3.11; suite
results agree. Not the pinned CadQuery environment (geometry tests skipped).

## Commands and observed results — 2026-09-19, at `03d6b49` before edits

| Command | Observed |
| --- | --- |
| `python3 -m unittest discover -s Analysis/tests` | exit 0; **Ran 129 tests**, OK, 158.6 s |
| `python3 -m pytest cad/tests tools --ignore=cad/tests/test_geometry.py -q` | exit 0; 34 passed |
| `python3 cad/input_requests.py --check` | exit 0; "consistent; no inputs accepted or measured" |
| `python3 cad/fixture_contract.py --check` | exit 0; "2 evaluable, 10 pending" |
| `python3 cad/fixture_contract.py --release` | **exit 2**; `REFUSED INPUTS_INCOMPLETE` (expected refusal, captured not suppressed) |
| `python3 cad/ledger_validator.py live` | exit 0; "PASS live: 13 tasks … 9 invalid mutations rejected; links OK" |
| `python3 tools/check_presentation.py . "Multirotor Recovery Dynamics" multirotor-recovery-dynamics` | exit 0; issues `[]`, 69 local links |
| `python3 tools/test_presentation.py` | exit 0; OK |
| `git diff --check` | exit 0 |

## Runtime counterexamples recorded (see review F-table)

| Finding | Reproduction | Result |
| --- | --- | --- |
| F03 | detached worktree of `03d6b49`, `python3 -m Analysis.run_survivable_set --quick --workers 6` | `Data/survivable_set_results.json` primary `n` 300 → 30; both JSONs modified; worktree removed, main checkout untouched |
| F09 | `kill_criterion([])` | returned `"KILL: …"`, `mechanism_justified=False` |
| F06 | `MotorAllocation(two_adjacent, 0.06, 4.2, 0.004).max_collective(4.2)` | 2.104 N at lstsq direction `[0.499, 0.499]` producing 0.0424 N·m roll — not a balanced trim |
| F07 | `math.comb` binomial, p₀ = 0.05^(1/30) | P(≥1 of 10) 0.631597; P(≥3) 0.061901; P(≥4) 0.010705 |
| F04 | bound at dt = 5e-4 | Δv ≤ 0.0049 m/s; Δh ≤ 3.9 mm at 7.8 m/s |

## After Day-1 edits

| Command | Observed |
| --- | --- |
| `python3 -m unittest Analysis.tests.test_survivable_set Analysis.tests.test_failure_allocation` | exit 0; 41 tests OK (4 new: F09 ×2, F03 ×1, expected_pairs ×1) |
| `python3 -m Analysis.run_survivable_set --smoke --workers 4` | exit 0; "smoke OK: 10 merged rows, 8 policy rows" |
| `python3 -m Analysis.run_survivable_set --quick --output-dir <repo>/Data/x` | exit 1; "refusing --quick output under tracked …/Data" |
| full suite + presentation checks | see PR CI |

No sweep was run against tracked outputs. `Data/` and `Figures/` are byte-identical
to `03d6b49`.

## W07 status

Intake packet and raw-observation templates prepared
([`bench-intake-packet.md`](bench-intake-packet.md), two CSVs). No inventory,
layout or interface observation exists yet — each awaits the person at the bench.
Every `input-requests.csv` row remains `pending` (12 rows).

## 2026-09-21 — R1 platform identity (hardware-revision plan supersedes W02–W08)

Owner photos of 2026-09-20 (purchase list P1/P2; exposed V995 electronics P3) change
the test article and the bench chain; the simulation schedule in the Day-1 review
becomes a backlog. Delivered on this branch:

| File | Content | State of its contents |
| --- | --- | --- |
| [`hardware-inventory.csv`](hardware-inventory.csv) | 17 rows: V995 + battery/charger, ten purchased items, four `UNKNOWN` bench needs | `PURCHASE_REPORTED` / `OWNER_IDENTIFIED` / `MANUFACTURER_SPECIFICATION` / `UNKNOWN` — nothing `INSPECTED` |
| [`platform-capabilities.md`](platform-capabilities.md) | two platform identities kept apart; capability table; first measured question; B01–B04 status; recorded decisions | planning record |
| [`../../docs/bench-acquisition.md`](../../docs/bench-acquisition.md) | E1–E6 connection table, proposed settings, bring-up order | proposed topology, every row unverified |
| `OPEN_QUESTIONS.md` OQ-011, OQ-012 | board access; load-cell selection/resolution | open |

P3 was viewed directly (converted to JPEG in a scratch directory, not committed):
four ducted three-blade rotors, two-wire motor leads, JST-style battery lead, one
square IC + metal can, `CLK` pad group near the switch end, foam pad removed. P1/P2
were **not** opened here; their product rows come from the plan's transcription and
contain no payment or shipping details.

Checks run at this revision: `python3 tools/check_presentation.py …` and
`tools/test_presentation.py` (see PR CI); no analysis code changed, so the
Analysis suite is unchanged from Day 1 (133 OK).

Next owner returns (blocking R2 bench work): B01 photos; V995 flight-ready mass on a
scale, connector polarity, rotor centres with a datum; which `UNKNOWN` inventory
rows are on hand. Next Claude slice: `firmware/bench_logger/` (CircuitPython) +
`Analysis/capture_bench.py` with no-overwrite runs, then R3 calibration analysis.
