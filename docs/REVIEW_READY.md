# Review index

What to review, and where each piece of evidence lives. The plan is in the
[roadmap](../ROADMAP.md) and the history in the [progress log](SPRINT_PROGRESS.md).
The earlier, longer version of this index is kept at
[commit 246d163](https://github.com/500ft/multirotor-recovery-dynamics/blob/246d163dcd8ce25242baee585e6ea1d05a53e7f4/docs/REVIEW_READY.md).

Nothing here has had an independent review, and nothing has been measured.

## Review now

1. **The survivable-set results** ([current results](../Analysis/current-results.md),
   [design](specs/survivable-set/design.md)). The guard loses 69 of 76
   discordant paired trials, the parachute needs about 10.5 m, and two adjacent
   rotors out is unrecoverable. Worth checking: the scenario caveat (rotor-out
   cases model a release, not an in-flight failure) and whether the binary
   landing criterion can resolve anything in the primary cells.
2. **The V995 bench chain** ([wiring and bring-up](bench-acquisition.md),
   [firmware](../Instrumentation/firmware/code.py),
   [capture](../Instrumentation/bench_capture.py)). Worth checking: the wiring
   table against the delivered boards before any wire is placed.
3. **The V995 fixture** ([notes](../cad/v995/README.md)). Worth checking:
   whether the 1 kg load cell can resolve the target force at a mass around
   50 g, once the aircraft is weighed.

## Reproduce

Run the [README quick start](../README.md#quick-start). The
[reading guide](START_HERE.md) covers the full analysis suite, study
regeneration and the pinned CadQuery environment.

## Evidence records

| Folder | What it holds |
| --- | --- |
| [v995-fixture-measurements](../evidence/v995-fixture-measurements/README.md) | The 27-row measurement worksheet for the owner (not yet filled) |
| [v995-fixture-research-2026-09-27](../evidence/v995-fixture-research-2026-09-27/README.md) | Source review for the whole-aircraft fixture |
| [week-2026-09-19](../evidence/week-2026-09-19/README.md) | Week of 2026-09-19: claim audit, V995 capability sheet, bench intake packet |
| [task-day4-2026-09-15](../evidence/task-day4-2026-09-15/README.md) | Single-motor fixture source candidates and gap inventory |
| [correction-2026-09-11](../evidence/correction-2026-09-11/README.md) | Correction of what earlier work had and had not finished |
| [presentation-2026-09-10](../evidence/presentation-2026-09-10/README.md) | README presentation checks |
| [review-2026-09-09](../evidence/review-2026-09-09/README.md) | Adversarial review of the CAD tooling |
| [task-2026-09-09](../evidence/task-2026-09-09/README.md) | Geometry CI for the motor envelope |
| [task-day3-2026-09-09](../evidence/task-day3-2026-09-09/README.md) | Sourced bench inputs |
| [task-2026-09-08](../evidence/task-2026-09-08/README.md) | CAD input register |
| [sprint-2026-09-05](../evidence/sprint-2026-09-05/) | First integrity sprint baseline |
