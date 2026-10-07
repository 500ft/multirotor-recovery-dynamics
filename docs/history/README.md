# Preserved project history

The [roadmap](../../ROADMAP.md) defines current work. These records retain their
original configurations, assumptions and unresolved findings; their OPEN labels
do not schedule work. Files stay at their original paths so reproduction links,
CAD inputs and prior source hashes remain usable.

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
