# Roadmap

This is the plan for finishing the project. Open questions are tracked in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line (owner decision, 2026-10-04)

The platform is the Bitcraze Crazyflie. The project finishes as a model study
checked against public flight data:

1. A rigid-body and rotor model of the Crazyflie 2.1, identified on training
   flights from the public [NanoBench dataset](https://github.com/syediu/nanobench-iros2026)
   and checked on held-out whole flights.
2. A tumble-recovery controller written as a Crazyflie firmware module and
   tested in software-in-the-loop with [CrazySim](https://github.com/gtfactslab/CrazySim).
   Landing is judged on vertical and horizontal speed, tilt and impact energy.
3. A design study over propeller, frame size, battery and payload, with inertia
   taken from CAD mass properties and a sensitivity analysis.

NanoBench has hover, excitation and tracking flights, with no tumbling. The
model is validated in normal flight; recovery results are model predictions
until flown. Flight tests on a Crazyflie 2.1+ are a separate, later decision
that needs a purchase and the release-test safety plan.

## Where it stands

- The documented values, each with its source, are in the
  [platform register](Engineering%20Data/platform_crazyflie.csv). None is
  measured by this project. Two published thrust maps disagree (OQ-019).
- NanoBench's vehicle flew at a measured 40.85 g with markers and a charging
  deck, above the 27 g stock mass. Validation uses that configuration.
- The V995 is retired: its main chips are unmarked and no programming route was
  found (OQ-011). Its CAD and worksheet are kept as history.
- The [simulation results in the README](README.md#simulation-results) are for
  the historical designed aircraft, which was never built.
- The bench chain is untested hardware, kept for per-motor thrust measurement
  if a Crazyflie is bought.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Record the platform decision and the documented parameter register | Agent | Merged |
| 2 | Load NanoBench and replay its recorded motor commands through the existing rigid-body model with the documented parameters | Agent | Open-loop prediction error per flight committed. **Current step** |
| 3 | Identify mass-property and rotor parameters on training flights, with mass fixed at the measured 40.85 g; check on held-out whole flights (OQ-018, OQ-019) | Agent | Held-out error table; identified values added to the register |
| 4 | Set up CrazySim and record the stock firmware's response to a release with tumble (OQ-021) | Agent | Stock behaviour recorded |
| 5 | Write and test a recovery controller as a firmware module in CrazySim; add horizontal speed and impact energy to the landing verdict | Owner and agent | Recovery envelope in software-in-the-loop |
| 6 | CAD envelope from Bitcraze's published files (board outline, motor mounts, propeller and motor mockups); model the design variants | Owner | Variant mass properties committed |
| 7 | Design study: screening (Morris), then variance-based sensitivity (Sobol), over propeller, frame, battery and payload | Agent | Sensitivity results and trade-off plot |
| 8 | Write up, then decide whether to buy a Crazyflie 2.1+ for flight tests (OQ-020) | Agent, then owner | Report merged; purchase decision recorded |

## Decision points

| Gate | After step | Continue if | Otherwise |
|---|---|---|---|
| G1 | 2 | The documented thrust model is close enough for identification to correct | Narrow the scope to attitude dynamics |
| G2 | 3 | Held-out error is comparable to NanoBench's published system-identification baselines | Revise the model structure first |
| G3 | 4 | CrazySim runs on an available machine or in CI | Port the firmware logic into the Python simulation |
| G4 | 5 | The controller recovers across the target envelope in software-in-the-loop | Report a negative result with the reasons |
| G5 | 8 | A specific prediction is worth testing and the release safety plan is ready | Finish as a model study |

## After a purchase (not scheduled)

Per-motor thrust on the bench chain (worksheet load-cell and bench rows),
bifilar-pendulum inertia, then low releases over a net: stock firmware first,
then the recovery module, compared with the registered prediction.

## Not in this version

- Flight tests or any purchase, until step 8.
- The V995 bench study and fixture.
- Building the historical designed aircraft (EX1103 motors, Kakute H7).
- Rotor-out and parachute studies on the Crazyflie.
