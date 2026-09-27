# V995 whole-aircraft fixture

**Platform decision (owner, 2026-09-27): the physical platform is fixed as the
stock Veeniix V995** — stock motors, propellers, controller, battery and
transmitter. All future physical work is based on this aircraft.

## This register is separate, on purpose

`cad/bench/parameters.csv` describes the **historical EX1103 / Gemfan
single-motor stand**. It keeps its own gates, its own contract and its own
pending rows. **No value crosses between the two registers.** In particular, do
not transfer to the V995:

| Historical input | Why it does not apply |
| --- | --- |
| 7.0 V acceptance voltage | the V995 runs a 3.7 V 1S pack |
| six-sampled-motor requirement | that is the single-motor stand's sampling rule |
| 0.020 N·m authority threshold | derived from the 225 g full-reserve requirement for the designed vehicle |
| 60 mm assumed arm | the designed vehicle's assumed radius, not a V995 measurement |
| 4.2 N simulated thrust | a four-motor simulation input, not a bench design limit |
| EX1103 / Gemfan geometry | a different motor and propeller |

## Scope of what this measures

Aircraft → retained removable cradle → load-cell loaded end → fixed end → rigid
base → bench restraints. **Direct force**: no pivot or lever ratio; the beam
senses force in bending.

This yields **aggregate axial force on the whole stock aircraft under documented
restrained conditions**. It does **not** establish individual rotor thrust,
independent motor commands, roll/pitch authority, or recovery performance.

## What is generated, and what is not

`generate_fixture.py` builds only `cell_end_adapter` — the plate that bolts to
one end of the load cell. Its footprint follows from the registered hole pattern
plus a declared edge margin.

Deliberately **not** generated, each blocked on a named input:

| Part | Blocked on |
| --- | --- |
| `cradle` | V995 flight-ready mass, rotor coordinates, contact/retention geometry — the aircraft has not been inspected |
| `base_plate` | `stand_anchor_spacing` — no bench/clamp geometry exists |
| `full_assembly` | both of the above, plus the delivered cell revision and signed load cases |

## Evidence status

**No input here is `measured`.** The cell geometry is `candidate_drawing`: the
Adafruit 4540 PDF viewer was unreadable, and the indexed 80 mm image sits under
PID 5231, so it is *candidate geometry for the 4540*, not a verified
delivered-part drawing. Adafruit also lists an older 80 mm 5 kg version, so
product number and capacity alone do not fix the mounting revision.

Edge margin, thickness and hole clearance are `design_choice` and are **not**
derived from any load case. Regenerating this geometry confirms the code
reproduces the register — nothing about a delivered part, a fit, or a calibration.

## Cell selection screening

Whole-aircraft hover force at the **unverified owner estimate** of 50 g is
0.4903 N (per rotor 0.1226 N). Against the exploratory objective
`U ≤ 0.025 · F_ref` = 0.01226 N, treating three 0.03 %FS terms as independent
symmetric rectangular bounds at k = 2:

| Cell | Full scale | 3-term screen U | vs target |
| --- | ---: | ---: | ---: |
| 5 kg (4541) | 49.03 N | 0.02942 N | **2.4× over** |
| 1 kg (4540) *if* 0.03 %FS class | 9.81 N | 0.00588 N | 0.48× (≈2.1× margin) |

**A 1 kg cell must be better than 0.0625 %FS per term** (three-term, k = 2) to
meet the target. No accuracy table was verified for the 4540, so its class is
unknown — the margin above is conditional on it matching the 4541's published
figures. Do not substitute generic TAL220 or 4541 specifications for it.

This is a **datasheet screen, not measured uncertainty**, and neither cell is an
accepted calibrated instrument. Adafruit's "capacity ≥ 2× maximum applied load"
guidance makes ≈4.90 N a preliminary screening ceiling for the 1 kg cell — not a
verified fixture strength rating. Taring does not remove physical dead load.
