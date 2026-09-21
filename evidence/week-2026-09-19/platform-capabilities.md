# Platform identities and capability sheet (R1, 2026-09-21)

Sources: owner photos P1/P2 (purchase list, 2026-09-20), P3 (`IMG_3883.HEIC`,
exposed V995 electronics), owner statements 2026-09-20/21, the V995 board-research
note (2026-09-21) and the hardware-revision plan (2026-09-20/21). Nothing here is
a measurement. States used: `OWNER_IDENTIFIED`, `OWNER_ESTIMATE`,
`MANUFACTURER_SPECIFICATION`, `PURCHASE_REPORTED`, `INSPECTED`, `FUNCTION_CHECKED`,
`CALIBRATED`, `UNKNOWN` — never interchangeable.

## 1. Two platforms, kept apart (R1.5)

| | Historical designed micro-UAV | Actual demonstrator |
| --- | --- | --- |
| Identity | EX1103 11000KV / Gemfan 2023-3 / GNB 2S / Kakute H7 Mini / ArduPilot, ~130–165 g class | **Veeniix V995**, ~50 g (`OWNER_ESTIMATE`), stock board, stock remote |
| Where its numbers live | `Engineering Data/*.csv`, `Analysis/sim_release_recovery.py` tiers, `Data/*.json`, `cad/bench/parameters.csv` | nowhere in `Analysis/` or `Engineering Data/` yet — **by rule**: no V995 value enters a parameter file until it is `INSPECTED`/`CALIBRATED` with a source |
| Gates that apply | EST-REC-007 measured-authority gate, DR-CAD-12 fixture contract, DR-SS-01/02/03 | none inherited; each V995 experiment states its own objective (R6.4) |
| Fixture | single-motor thrust stand, Phidgets 3132_0 candidate, D1–D6 pending | whole-drone cradle on an Adafruit 1 kg / 5 kg cell — different interfaces, own evidence |

Smallest config mechanism: none is needed this week. The V995 has no measured
parameter to hold, so a profile file would be a container for `UNKNOWN`s. When the
first measured quantity exists (R5.6), it goes into a new `Engineering Data/
platform_v995.csv` with `platform_id`, `value`, `state`, `source` — the same row
shape as `mass_budget.csv` — and `Analysis/` reads it only through an explicit
`platform` argument. `Analysis/hardware_resources.py` validates the Kakute map only;
its PASS says nothing about the V995 PCB.

## 2. Capability table (R1.4)

| Capability | Status | Evidence | What would change it |
| --- | --- | --- | --- |
| Stock manual control (transmitter) | `documented` (manufacturer functions: altitude hold, headless, auto maneuvers) | S12 product page | owner flight check → `tested` |
| Telemetry readout | `unknown` | no interface identified; `CLK` pads are a lead, not a port | B01 photos → B02 datasheet match → B03 continuity map |
| Command input (external) | `unknown` | no SDK/API on manufacturer downloads page | same as above; read-only telemetry and command authority are separate |
| Firmware source / flashing | `unknown` | no verified MCU identity, schematic or firmware image found (board note D) | readable chip markings |
| Per-motor command | `unavailable` (stock) | brushed two-wire leads (inference); no driver access | controller replacement — a vehicle revision, not a sensor install |
| Emergency stop behavior | `unknown` | not observed | owner records stock behavior on signal loss / switch |
| Angular rate / attitude observability | `unresolved` | LIS3DH is specific force only; no gyro purchased; stock IMU inaccessible | stock telemetry access, or a justified IMU addition after mass/CG review |
| Aggregate axial force + electrical power on the bench | `plausible` | purchased chain; nothing wired | R2 bring-up + R3 calibration |

## 3. First measured question (R1.6)

**Can the acquisition chain (1 kg cell → NAU7802 → QT Py; INA260) resolve
repeatable axial force and electrical power under documented static/steady bench
conditions?** Planning scale only: hover-equivalent weight ≈ 0.050 kg × 9.80665 ≈
0.49 N ≈ 5 % of the 1 kg cell range, so the question is demonstrated low-force
resolution, not overload capacity. The proposed discrimination target (5 % of
F_ref_use, expanded uncertainty ≤ half of that: ≈ 0.012 N at 0.49 N) is an
*exploratory* target; it is not a repo release threshold and stays undecided until
F_ref_use and an uncertainty budget exist (R3.7).

Conditional next: what the complete stock drone produces under repeatable operator
commands in a reviewed restraint (R5 branch A), and whether a logger package is
plausible by mass/CG. Later: whether any accessible controller can execute an
intervention. The first two remain useful if the third stays inaccessible.

## 4. Board investigation status (B01–B04)

| Task | Owner/Agent | Status | Note |
| --- | --- | --- | --- |
| B01 sharp close-ups: central IC, pad group, edge marking, underside | owner, ~15 min | **pending** | transcribe every IC line exactly, `?` for unreadable; keep prop/motor/wire positions recorded |
| B02 datasheet match of exact markings | Claude, ~30 min | blocked on B01 | separate MCU / RF / inertial / pressure / regulator / drivers; bounded search |
| B03 power-off continuity map (GND, battery in, pads, identified pins) | owner + review | blocked on B02 | observations ≠ inferred nets; no programmer attached on the strength of "CLK" |
| B04 capability decision | Claude, ~15 min | blocked on B03 | if unresolved, finish the independent logger and name the blocking chip/net |

Documentary leads retained, none proven: U46C-022 manual association → UDIRC
Firefly U46C / CML `UDI-I22-07` receiver board (possible related platform); FCC ID
`2BBLM-V995` (no internal-photo exhibit obtained); `IC 33721-V995`.

## 5. Decisions recorded

- Charger and flight-battery specifications accepted from the manufacturer for
  planning (owner, 2026-09-21); no re-verification task. Charger input is never
  an accessory rail source (E6).
- Development path for this week: **independent instrumentation** (path 1). Stock
  control preserved; nothing attached to the drone's power until connector
  polarity, accessible rail, current budget and grounding are known.
- CAD/FEA for any V995 cradle or mount follows the owner-designated briefing
  `500ft/engineering-audit/docs/cad_agent_briefing.md` (blob `530550e2`, read
  2026-09-21 by the planning assistant; re-read before the first CAD task):
  parameters from `cad/bench/parameters.csv` → versioned JSON job input; an
  independent geometry oracle before authoring; a parameter re-drive check; a STEP
  round-trip with stated tolerance. No CAD task is open this week.

## 6. Owner returns needed before R2 bench work

1. B01 photos (above).
2. R1.3: V995 label/revision, connector polarity, flight-ready mass **with**
   battery on a scale, body axes and rotor-center locations with a datum, and the
   mass of any proposed sensor/wire/mount package weighed separately.
3. Confirm which `UNKNOWN` rows of `hardware-inventory.csv` are on hand: USB data
   cable, reference masses, caliper, multimeter / current-limited supply.
