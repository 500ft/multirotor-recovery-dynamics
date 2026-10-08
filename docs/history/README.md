# Preserved project history

The [roadmap](../../ROADMAP.md) defines current work. These records retain their
original configurations, assumptions and unresolved findings; their OPEN labels
do not schedule work. Retained evidence stays at its original paths so reproduction links, CAD inputs
and prior source hashes remain usable. Obsolete execution surfaces were deleted
as described below.

| Study or asset | Preserved record |
| --- | --- |
| Previous Crazyflie finish line and phases | [Roadmap before the pivot](https://github.com/500ft/multirotor-recovery-dynamics/blob/aeeccb2a8fee1942e3c0ae0b7d4777f7377fcb7c/ROADMAP.md) |
| Earlier README and historical headline comparisons | [README before the pivot](https://github.com/500ft/multirotor-recovery-dynamics/blob/aeeccb2a8fee1942e3c0ae0b7d4777f7377fcb7c/README.md) |
| NanoBench development replay | [Report](../nanobench-baseline.md), [source/split/results](../../Data/nanobench-baseline/), [configuration register](../../Engineering%20Data/platform_crazyflie.csv) |
| NanoBench timing/configuration qualification | [G1 report](../nanobench-g1.md), [executed output](../../Data/nanobench-g1/); G1 incomplete, final-test files unopened |
| Alternative-data author request | [Unsent draft](../idsia-data-request.txt); no outreach authorization |
| Designed aircraft, never built | [Design report](../../Design%20Report/README.md), [results](../../Analysis/current-results.md#historical-designed-aircraft), [frozen study specifications](../specs/README.md) |
| Historical review and progress | [Review index](../REVIEW_READY.md), [progress log](../SPRINT_PROGRESS.md) |
| V995 fixture and other CAD | [V995 notes](../../cad/v995/README.md), [CAD assets](../../cad/) |
| Calibration and capture assets | [Instrumentation](../../Instrumentation/), [bench acquisition](../bench-acquisition.md), [historical safety procedure](../../Safety/README.md) |
| Older figures and their generators | [Production guide](../data-and-figures.md#historical-designed-aircraft-outputs), [figure manifest](../figure-manifest.json) |

The historical guard comparison changes vehicle properties, controller settings
and landing limits together. Its guard contribution remains unresolved. The
historical landing rule uses vertical speed and tilt, omitting lateral impact,
spin and physical damage. Recovery comparisons that change both mixer and
controller do not isolate either change. The old parachute outcome depends on
its deployment assumptions. These qualifications remain in the linked reports;
none becomes validation of the warning study.

## Cleanup and retention

The owner adopted a dependency roadmap and removal of retired execution surfaces.
The complete [pre-cleanup tree](https://github.com/500ft/multirotor-recovery-dynamics/tree/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b)
retains the exact old sources, task ledgers and rendering code. Historical test
logs that name removed commands describe that revision's tools; use that tree
to replay those administrative checks. They are not current task instructions.

Removed from the working tree:

- CAD work orders, item list, dependency/status ledgers, placement draft and
  duplicated embedded checks: `docs/CAD_PLAN.md`, `CAD_ITEMS.md`, `CAD_TASKS.csv`,
  `CAD_DEPENDENCIES.json`, `CAD_REVIEW_DISPOSITION.md`, `CAD_PLAN_CHECKS.md`.
- The competing `docs/SPRINT_TASKS.csv`, CAD scope and evidence-gap work plans,
  the old measured-authority execution schedule, and the retired engineering and
  procurement roadmaps. Executed correction reports and scientific protocols remain.
- `cad/ledger_validator.py` and its tests, whose sole inputs were those retired
  administrative ledgers. No current geometry or analysis imports them.
- The unused `Analysis/render_state_machine.py` and conceptual project-overview
  SVG. The state JSON, historical diagram and tests remain because the frozen
  drop protocol references the failsafe specification.
- The automatic V995 fixture-regeneration step. It published no retained result;
  the useful CAD source, register, contracts and geometry tests remain available.
  Full-history checkout was needed only for the retired ledger test and was removed.

Retained deliberately:

- QDrone2 code, protocol, result and figure; NanoBench source records, replay,
  timing blockers, frozen split and test excerpt. Final-test files stay unopened.
- Historical guard, parachute, release and scenario execution code, their tests,
  parameter sources and plots. Committed simulation outputs depend on them;
  deleting them would break reproduction. Their scientific qualifications remain.
- CAD generators and measured geometry evidence, pending input registers, fixture
  and calibration checks, bench firmware/capture, safety assets and source licenses.
  Their existence supplies no installed calibration or physical approval.
- Frozen historical control/measurement specifications, numerical registers,
  primary data and completed evidence records. Their old task IDs are provenance,
  while [ROADMAP.md](../../ROADMAP.md) is the sole active plan.
