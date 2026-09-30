# Roadmap

This is the plan for finishing the project. Open questions are tracked in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line (proposed, owner to confirm)

The physical platform changed on 2026-09-27 to a stock Veeniix V995, and no
finish line has been set for it since. This one follows the owner's two
existing decisions: measure the whole aircraft on a load-cell cradle, and make
the first PCB an airborne sensor/logger that leaves the stock flight controller
in place.

The project is finished when:

1. the V995's thrust and electrical power against throttle have been measured
   on the bench;
2. the airborne logger has recorded the stock V995's angular rates and
   acceleration through a few controlled releases, showing what the stock
   controller actually does; and
3. both are compared with the recovery model and written up, together with the
   simulation study already in the repository.

Recovery with a custom controller is not part of this version. The stock
board has no known command or telemetry interface (OQ-011), so there is
nothing to run a controller on.

## Where it stands (2026-09-30)

- The simulation study is complete on estimated inputs. The headline findings
  are in [Analysis/current-results.md](Analysis/current-results.md):
  - a guard on the airframe does not help; in paired trials it lost 69 of
    the 76 cases where the two designs differed;
  - a parachute never opens in time below about 10.5 m;
  - with two adjacent rotors out, nothing survives in any tested case.
- The bench chain (QT Py RP2040, NAU7802 load-cell amplifier, INA260 power
  monitor, LIS3DH accelerometer) has firmware and host capture code. It has not
  run on hardware.
- CAD: the load-cell end adapter is generated. The cradle and base-plate
  generators are written and tested, and are waiting on five measurements.
- The aircraft's mass is an owner estimate of about 50 g. It decides whether
  the purchased 1 kg load cell can resolve the forces involved at all.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Fill the [measurement worksheet](evidence/v995-fixture-measurements/README.md): 27 rows in one unpowered bench session. That covers the delivered load cell (15 rows, which also settles OQ-017), the aircraft including its flight-ready mass (7 rows) and the bench (5 rows) | Owner | Worksheet committed; the agent then fills `cad/v995/parameters.csv` and starts `Engineering Data/platform_v995.csv` for the mass. **Current step.** |
| 2 | Decide whether the 1 kg cell is good enough at the measured mass | Agent | Screening updated with the real mass |
| 3 | Generate the cradle and base plate, check them against the oracle, export STEP | Agent | Parts accepted |
| 4 | Print the parts, wire the bench chain, and do the bring-up in [docs/bench-acquisition.md](docs/bench-acquisition.md), starting with the power-off continuity check. Calibrate with known masses | Owner | Calibration record committed |
| 5 | Throttle sweep on the cradle with the stock transmitter | Owner, with agent analysis | Thrust and power against throttle committed |
| 6 | Design the airborne logger PCB within the mass the V995 can carry | Agent designs, owner builds | Board logs rates and acceleration on the bench |
| 7 | A few controlled releases with the logger fitted, inside the safety limits in [Safety/README.md](Safety/README.md) | Owner | Logs committed |
| 8 | Compare both measurements with the model and write up the study | Agent | Report merged |

## Not in this version

- The historical designed vehicle (EX1103 motors, Kakute H7, 7.0 V). Its
  plan and gates are kept in the repository but are not being built.
- Reverse-engineering the stock board (OQ-011).
- A custom recovery controller or recovery flights.
- Further simulation refinement before measured inputs exist.
