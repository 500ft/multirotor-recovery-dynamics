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

## What the cradle and base plate still need

Both generators are **written, tested and wired in**. They are skipped today
because five register rows are pending — not because the geometry is unknown.
Populate the rows and the parts build on the next run, with the same oracle and
STEP round-trip checks as the adapter.

### Cradle — 3 measurements, all on the aircraft you own

| Row | What to measure | How |
| --- | --- | --- |
| `aircraft_capture_width` | outer body width at the station the cradle grips — **not** the rotor-tip span | calipers at a recorded datum; take three independently repositioned readings and save all three |
| `aircraft_capture_length` | body length the cradle floor spans, chosen to sit between rotor arms without fouling the guards | record which features bound the chosen station |
| `cradle_wall_height` | wall height that retains the airframe laterally without reaching the rotor plane | derive from measured body height and rotor-plane offset; justify against rotor clearance, do not pick for convenience |

Already registered as `design_choice`: wall thickness 3.0 mm, floor thickness
4.0 mm. Neither is derived from a load case.

**Design intent already encoded.** The cradle is a U-channel, not a gravity
pocket, because the reaction can reverse — the fixture has to transmit **uplift
as well as downward load**. It bolts to the cell's loaded end on the registered
hole pattern, and the generator refuses a floor too short for that pattern.

### Base plate — 2 measurements, both on the bench

| Row | What to measure | How |
| --- | --- | --- |
| `bench_anchor_spacing` | centre distance between the two anchor points the plate bolts to | measure the actual bench/clamp pattern, or design and verify a new mounting interface |
| `bench_anchor_hole_diameter` | clearance for the anchor fastener | follows from the chosen anchor hardware |

Already registered as `design_choice`: plate thickness 6.0 mm, relief depth
2.0 mm.

**Design intent already encoded.** The plate carries a **relief pocket** between
the cell pattern and the anchors, so the cell's sensing section stays free to
deform. Without it the plate becomes a parallel force path around the cell and
the measurement is invalid. The generator fails closed if the pocket would breach
the plate, if a hole would fall off the plate, or if there is no room for the
pocket once fastener land is allowed for.

### What is still *not* covered by these five rows

- **Signed load cases and off-axis moments.** Every thickness above is a
  printability choice. No stress or deflection check exists, so none of these
  parts is structurally justified — only geometrically defined.
- **Rotor-airflow interference.** The cradle's effect on the flow it sits in is
  unassessed; see the ground-effect and recirculation notes in
  `literature/notes/06`.
- **Cable and restraint routing**, which must not create a parallel force path
  alongside the cell.
- **Delivered cell revision** (OQ-017) — the bolt pattern is `candidate_drawing`.

Closing the five rows makes the parts *buildable*. It does not make them
*accepted*.
