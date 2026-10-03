# Roadmap

This is the plan for finishing the project. Open questions are tracked in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line pending owner scope choice

**Current step: D3.** The owner must choose whether to close the simulation
study or continue with V995-only bench characterization. Neither choice has
been made, and this result correction does not close the repository.

If bench work is selected, the finish is measured whole-aircraft thrust and
electrical power against recorded transmitter settings and battery state, with
calibration and uncertainty reported. These measurements describe the stock
controller's behaviour on a fixture. Logger development, release trials and a
new aircraft require a separate owner decision.

## Where it stands

- The [README result statements](README.md#simulation-results) have been corrected:
  - the guard's contribution is unresolved because mass, inertia, impact-speed
    limits, tilt limits and controller settings change together;
  - the parachute outcome follows the assumed interval before useful drag;
    the README derives the nominal rest-drop distance from the
    [model parameters](Analysis/survivable_set.py), without claiming a general
    deployment height;
  - the landing verdict checks vertical speed and tilt, omitting lateral
    impact, spin and physical damage criteria;
  - the recovery comparison changes both mixer and controller. Its inputs and
    counts remain in [the stored results](Data/monte_carlo_results.json).
- The historical simulated aircraft was never built. The stock V995 cannot run
  its controller because no usable command or firmware interface is established.
- The bench chain has firmware and host capture code. It has not run on hardware.
- The load-cell end adapter is generated. Cradle and base-plate generators need
  the [measurement worksheet](evidence/v995-fixture-measurements/README.md),
  including the delivered cell's mounting pattern and flight-ready aircraft mass.
- OQ-016 is closed by the [stored scenario comparison](Data/scenario-02/results.json).
  That comparison does not resolve the pending physical scope choice.

## What's left

Decide D3 first. The following work is conditional on selecting V995 bench
characterization; the worksheet remains an optional bench prerequisite while
that choice is pending.

| Step | Who | Done when |
|---|---|---|
| Fill the [27-row unpowered measurement worksheet](evidence/v995-fixture-measurements/README.md) | Owner | Readings committed, including cell identification, aircraft mass and bench dimensions |
| Check cell suitability and complete the fixture | Agent | Actual readings populate the parameter register; fixture geometry and load checks support building it |
| Build and commission the bench chain using [the bring-up procedure](docs/bench-acquisition.md) | Owner | Calibration records cover the needed force range, tare, hysteresis, drift and side loads; stop if uncertainty exceeds the required force resolution |
| Measure whole-aircraft thrust and power | Owner, with agent analysis | Results record transmitter settings, battery state and measurement uncertainty |
| Write up the bench characterization | Agent | Report states the measured scope and limits |

## Outside the authorized work

- Building the historical designed aircraft or switching to a new aircraft.
- Reverse-engineering the stock board (OQ-011).
- A custom recovery controller, logger development or recovery flights.
- Further simulation refinement or experiments before the owner chooses scope.
- Repository closure or archival before an explicit owner decision.
