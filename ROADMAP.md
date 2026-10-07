# Roadmap

## Finish line

Test whether a maneuver-specific warning predicts failure to complete recovery
within an available height on unseen packs, payloads and guard conditions.
Compare with voltage, sag-history and load baselines at a matched false-alarm
rate, including useful warning lead time. Define the maneuver, completion rule,
false-alarm burden and useful lead time before a final evaluation.

The owner [adopted the successor question](docs/decisions/maneuver-warning-v2.md)
and the first public component-data task. This is the current plan. The actual
physical platform and test authorization remain undecided; the previous
Crazyflie choice does not select the warning-study aircraft.

## Current step

Completed the licensed [QDrone2 development response summary](docs/qdrone-response.md).
The executed [result](Data/qdrone-response/results.json) pairs continuous
altitude-response errors with precommand voltage under the original MPC.
The [protocol](Data/qdrone-response/protocol.json) was committed before
calculation. The incomplete ending stays in the result. No warning model was
fitted and no binary recovery outcome was assigned.

Public component qualification is complete for this selected recording. It
cannot settle the finish line: independent pack identities, recovery outcomes
and withheld-condition evidence are missing. No further data campaign starts
under this task. Owner action: resolve [M2–M4](OPEN_QUESTIONS.md#pending-owner-decisions),
including access/platform, maneuver completion and facility responsibility,
before physical-study design or acquisition.

## Remaining work and decision gates

| Gate | Required evidence or decision | Current status |
| --- | --- | --- |
| MR-1 | Adopt the warning question and public component-data qualification | Adopted for this software task; executed result linked above |
| Data qualification | Licensed data, units, controller, timestamps, continuous endpoint and independent run structure | Selected QDrone2 recording qualified for descriptive response only; independent pack/run count unknown |
| MR-2 | Owner supplies access/funding direction, actual aircraft, maneuver/height/completion rule and safety owner | Pending M2–M4; no aircraft switch or physical work inferred |
| Outcome qualification | Independent observed recoveries/failures and command/state timing for the chosen configuration | Missing; ordinary altitude steps and observed motor RPM cannot supply these labels |
| Warning comparison | Freeze processing, warning metrics and whole-pack/condition splits; compare voltage, sag-history and load baselines at matched false-alarm burden | Deferred until suitable outcomes and scope approval exist; no new full research campaign authorized |
| G5 purchase approval | Owner approves exact configuration, budget, useful registered prediction and staged safety/measurement plan | Required before purchase; no paid compute or hardware order authorized |

A warning result needs independent physical completion outcomes. Test withheld
packs and payload/guard conditions without learning processing from their
outcomes. Keep voltage, demand and elapsed-time confounding visible; agreement
on component data alone cannot validate a recovery boundary. Report unsuccessful
cases and uncertainty at the independent run/pack level.

## Preserved scientific gates

The prior [NanoBench G1 qualification](docs/nanobench-g1.md) still lacks raw
collection timing and deployed settings. No G1 pass or G2 final evaluation is
recorded. Keep the [whole-flight split](Data/nanobench-baseline/split.json),
original development outputs and final-test files unchanged and unopened.
Reopening identification requires a separate authorized task that resolves
those prerequisites before using any held-out outcomes.

[NeuroBEM](https://rpg.ifi.uzh.ch/neuro_bem/Readme.html) remains a candidate. Its
processed grid does not establish native sensor bandwidth, and observed RPM
is not available maximum thrust. Reuse permission and causal timing need
qualification before derived analysis. The existing author request remains
[unsent](docs/idsia-data-request.txt). QDrone2, NeuroBEM and NanoBench describe
different vehicles and must remain separate.

## Cost, safety and publication

Use existing machines and the public source files needed for the declared
software task. No purchase, external outreach, physical experiment or paid
compute is authorized. The owner retains physical access, funding, platform,
maneuver and publication decisions. A reviewable repository result PR is
within this task; merging and external publication are separate decisions.

Before any powered work, replace the historical [safety procedure](Safety/README.md)
with one reviewed for the actual aircraft and facility, including containment,
independent disarm, instrumentation and abort responsibility. Existing CAD and
bench files do not establish physical readiness.

## Prior work

The [history index](docs/history/README.md) preserves the earlier roadmap,
reports, simulations, figures, NanoBench replay and useful CAD/calibration
assets. Old recovery outcomes remain results for their original assumptions.
Controller development, identification, the old V995 fixture, parachutes and
fabrication are outside this task. Numerical results live in their result
files; the [register guide](Engineering%20Data/README.md) keeps input sources
separate by configuration.
