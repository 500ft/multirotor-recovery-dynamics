# V995 fixture: what must be researched or measured, and what each number decides
Date: 2026-09-27 · Companion to [the fixture research report](v995-fixture-research-2026-09-27.md)

Every item states the quantity, how to obtain it, and **what it blocks**. Ordering is by
consequence, not by convenience. Nothing here is a measurement; these are the measurements and
confirmations that do not yet exist.

All arithmetic below was reproduced independently from the committed screening record. Two
numbers are new and are marked **NEW**.

---

## Tier 0 — decides whether the purchased sensor is usable at all

Do these before any CAD is frozen or any part is printed. If either goes the wrong way, the
fixture geometry is not the thing that needs changing.

### 0.1 Flight-ready mass of the stock V995 — **the single highest-leverage unknown**

| | |
| --- | --- |
| Quantity | Total mass as flown, with battery, guards and any retained cradle interface, in grams |
| How | Kitchen or jeweller's scale, resolution 0.1 g or better, aircraft complete and flight-ready. Record what is and is not installed |
| Status | **Owner estimate of 50 g, unverified.** A search snippet reported 22.3 g, also unverified |

**NEW — why this decides the sensor question.** The declared objective is to resolve 5 % of the
reference force with expanded uncertainty no worse than half that increment, so the target scales
with mass while the cell's screening uncertainty does not.

| flight-ready mass | hover force | target U | 1 kg 5-term screen | verdict |
| --- | --- | --- | --- | --- |
| 22.3 g (snippet) | 0.2187 N | 0.00547 N | 0.00994 N | **FAILS by 1.8×** |
| 30 g | 0.2942 N | 0.00735 N | 0.00994 N | **FAILS by 1.35×** |
| **40.5 g** | 0.3972 N | 0.00993 N | 0.00994 N | **break-even** |
| 50 g (owner estimate) | 0.4903 N | 0.01226 N | 0.00994 N | passes, 19 % margin |
| 70 g | 0.6865 N | 0.01716 N | 0.00994 N | passes, 42 % margin |

Below about **40.5 g the purchased 1 kg cell cannot meet the stated objective** even on borrowed
specifications, before any electronics. The report recommends calibrating the 1 kg cell first;
that recommendation is sound only if the aircraft is heavier than roughly 40 g. Weigh it first.

### 0.2 Thermal stability of the measurement, and the tare cadence it forces

| | |
| --- | --- |
| Quantity | Air and fixture temperature change over a measurement block, in °C; time constant of the cell after handling |
| How | Log temperature beside the cell through a representative block. Record soak time from power-on |
| Status | Not characterised |

**NEW — the size of the problem.** Applying the 4541 zero-temperature drift of 0.3 % FS per 10 °C
as a screen, and comparing with the 0.01226 N target at the 50 g scenario:

| cell | zero drift | drift that consumes the **entire** target |
| --- | --- | --- |
| 1 kg | 0.00294 N/°C | **4.2 °C** |
| 5 kg | 0.01471 N/°C | **0.83 °C** |

A few degrees of room drift spends the whole uncertainty budget. This makes thermal soak and
re-taring first-order requirements, not procedural detail, and it is a second independent reason
to prefer the 1 kg cell. The drift figure is **borrowed from the 5 kg drawing and is not verified
for the purchased part**, which is exactly item 0.3.

### 0.3 Delivered 1 kg cell: revision, drawing and accuracy table

| | |
| --- | --- |
| Quantities | Body length; hole pattern at **both** ends with thread size, pitch and usable depth; longitudinal hole positions; which end is the load end; nonlinearity, hysteresis, repeatability, creep, corner error, sensitivity, zero output, output resistance, temperature coefficients; rated capacity and safe overload |
| How | Measure the delivered part with calipers and thread gauges. Ask Adafruit support for the datasheet matching the shipped revision, quoting the order |
| Status | **No accuracy table verified for the 4540.** Geometry in hand is a candidate drawing under a different product number |

The report is explicit that the indexed text pointed to an 80 mm image under PID 5231 and that
this is candidate geometry, not a verified delivered-part drawing. **Do not substitute the 4541
figures or generic TAL220 specifications.** Every screening number above depends on borrowed
specs and must be re-run once real ones exist.

---

## Tier 1 — numbers required before CAD can be frozen

These are the register rows that currently block geometry. Each needs a measured value, a
tolerance and a datum it is measured from.

### 1.1 Pending in `cad/v995/parameters.csv`

| parameter | unit | how to obtain | what it sets |
| --- | --- | --- | --- |
| `aircraft_capture_width` | mm | Caliper across the body at the chosen capture station, at its widest point within the station | Cradle internal width and wall positions |
| `aircraft_capture_length` | mm | Caliper along the body between the chosen fore and aft limits, clear of rotor arms | Cradle floor length |
| `cradle_wall_height` | mm | From the capture station: height needed to retain laterally without touching arms, motors, guards or wiring | Wall height, and whether the wall enters the rotor inflow |
| `bench_anchor_spacing` | mm | Centre distance of the actual bench anchor points or T-slots | Base plate hole pattern |
| `bench_anchor_hole_diameter` | mm | Fastener diameter plus clearance | Base plate holes |

**Also needed and not yet registered:**

- **Capture-station location** along the body, as a distance from a named datum. Every dimension
  above is meaningless without stating where on the aircraft it was taken.
- **Rotor plane height above the capture station**, mm, and **rotor tip radius and coordinates**
  relative to the same datum. These decide cradle wall clearance and airflow interference.
- **Centre-of-mass location** in the capture plane, mm from the datum. An offset centre of mass
  against a single load path produces a moment the cell is not meant to read.
- **Guard outer envelope**, mm, since the guards and not the body may be the widest feature.

### 1.2 Thicknesses currently chosen for printability, not from a load case

`adapter_thickness` 4.0 mm, `cradle_wall_thickness` 3.0 mm, `cradle_floor_thickness` 4.0 mm and
`base_plate_thickness` 6.0 mm are all recorded as design choices explicitly **not derived from a
load case**. To justify them you need:

- **Maximum applied force**, N, including the largest transient, not the hover value.
- **Signed load cases**: the cradle must transmit **uplift as well as downward load** if the
  reaction reverses. State both directions.
- **Off-axis moments**, N·m, from centre-of-mass offset and from any asymmetric thrust.
- **Printed material and orientation**: which filament, which print direction, and the layer
  adhesion strength in the direction the load actually passes. A printed part is not isotropic
  and the weak direction is usually across layers.
- **Fixture stiffness target**, N/mm, so the fixture does not become the compliant element and
  turn a force measurement into a deflection measurement.

### 1.3 Joint and fastener stacks

- **Screw, washer and spacer stack** at each cell end, in mm, and the **usable thread engagement**
  that results. The report lists usable thread depth as unresolved on both drawings.
- **Clearance-hole diameters** for the delivered fasteners.
- **Whether the cell's sensing section is kept free** over its full length. `cell_relief_depth` is
  2.0 mm by choice; the required relief comes from the delivered drawing.

### 1.4 Parasitic load paths — a check, not a number

Cables, guards, restraints and the cradle itself must not create a **parallel force path** around
the cell. This is a yes-or-no inspection with a recorded method, and it invalidates every reading
if it is wrong. Specify how it will be verified, for example by a known dead load applied with and
without cabling dressed.

---

## Tier 2 — required to accept the instrument

None of these can be researched online; all are bench work.

- **Reference loads**: a set of characterised masses spanning the useful range, with their own
  traceability and uncertainty stated. At least five points.
- **Ascending and descending cycles** to expose hysteresis, with held-out points not used to fit
  the calibration.
- **Zero return** after each cycle, and **drift** over a representative block duration.
- **Eccentric-load check**: same load applied at several positions on the cradle, to quantify what
  the corner-error specification means in this installation.
- **Installed expanded uncertainty**, N, combining calibration residuals, drift, hysteresis,
  eccentricity and the acquisition chain, with its coverage factor stated.
- **Acquisition chain limits**: NAU7802 noise-free resolution at the chosen gain and rate, in N
  referred to input; cable microphonics; supply stability. A 24-bit converter does not deliver
  24 usable bits.
- **Useful force range**: the span over which the accepted uncertainty holds. Adafruit's guidance
  of at least twice the maximum applied force gives roughly **4.90 N** as a preliminary screening
  ceiling on the 1 kg cell. That is a screening ceiling, **not** a verified fixture strength
  rating, and taring does not remove physical dead load.

**Acceptance rule to declare in advance:** the instrument is accepted only if the reviewed
expanded uncertainty meets the declared objective **throughout the useful range**, not at one
convenient point.

---

## Tier 3 — needed only for a later torque or per-rotor claim

Deferred deliberately. Aggregate axial force does not establish individual rotor thrust,
independent motor commands, roll or pitch authority, or recovery performance.

- **Measured moment arm**, m, with its own expanded uncertainty.
- **Rotor coordinates** relative to the centre of mass.
- A second sensing axis or a multi-cell arrangement, since one cell in one axis cannot separate
  a moment from a force.

---

## Do not carry these across from the historical stand

The EX1103 and Gemfan single-motor study stays separate. Specifically, do **not** transfer to the
V995: the 7.0 V six-sampled-motor requirement, the 0.020 N·m authority threshold, the 60 mm
assumed radius, the 4.2 N simulated thrust, or the 0.05 mm proposed hub-fit tolerance. Retain the
stock motor and propeller interfaces rather than inventing dimensions for them.

---

## What the objective actually demands, stated once

At the 50 g scenario, and **only** as a scenario:

| quantity | value |
| --- | --- |
| total hover force | 0.4903 N |
| per-rotor share, symmetric | 0.1226 N |
| increment to resolve, 5 % | 0.0245 N |
| target expanded uncertainty | 0.0123 N |
| fraction of 1 kg range used | 5.0 % |
| one rotor lost, as a fraction of total | 25 % |

The last row is worth noting: a whole rotor failing is a 25 % change, which this chain would see
easily. The demanding requirement is the 5 % discrimination, not the gross failure case.
