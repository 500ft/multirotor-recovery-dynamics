# V995 bench: what still needs hard numbers

Every value the whole-aircraft fixture and its measurement objective depend on, what kind of number each
one is, how to get it, and what it unblocks. Companion to
[`v995-fixture-research-2026-09-27.md`](v995-fixture-research-2026-09-27.md), which establishes the
platform change and the load-cell findings. This file is the work list that follows from it.

Nothing here is a measurement. Every number below is either an input that does not exist yet, or a
screening figure computed from an unverified input and labelled as such.

---

## 0. The measurement that decides whether the objective is achievable at all

**Flight-ready mass of the stock V995, as it will sit in the cradle.** Everything else is downstream.

The exploratory objective is to resolve 5% of a reference force with expanded uncertainty no worse than
half that increment, `U_target = 0.025 · m · g`. Because the target scales with mass, a lighter aircraft
makes the same instrument worse, not better. The mass is currently an owner estimate of 50 g, with a
search snippet suggesting 22.3 g and no manufacturer-verified figure.

Screening the 1 kg cell against that objective, using the 4541's published percentages as a placeholder
because **no accuracy table has been verified for the purchased 4540**:

| mass | reference force | `U_target` | 3-term screen | 5-term screen |
|--:|--:|--:|--:|--:|
| 22.3 g (snippet) | 0.2187 N | 0.00547 N | 1.08× | **1.82× FAIL** |
| 40 g | 0.3923 N | 0.00981 N | 0.60× | **1.01× FAIL** |
| 50 g (owner estimate) | 0.4903 N | 0.01226 N | 0.48× | 0.81× marginal |
| 80 g | 0.7845 N | 0.01961 N | 0.30× | 0.51× |

3-term = nonlinearity, hysteresis, repeatability. 5-term adds creep and corner error. Independent
rectangular bounds, `u = b/√3`, `k = 2`.

**Breakeven is 40.5 g on the 5-term screen and 24.0 g on the 3-term screen.** Below those the datasheet
alone exhausts the entire budget, before electronics, alignment, drift, dead-load subtraction, cable
forces or propwash are counted at all.

Two consequences worth facing before any CAD is cut:

- At the owner's own 50 g estimate the five datasheet terms already consume **81%** of the total permitted
  uncertainty. That is not a comfortable instrument for this objective; it is one that has to be near
  perfect everywhere else.
- The 5 kg cell fails on the 3-term screen at 2.40× and is not a candidate for this objective on published
  specifications. That confirms the report's recommendation, and the 1 kg result shows the recommendation
  is necessary but may not be sufficient.

*Get it:* scale with resolution ≤ 0.1 g and a stated calibration, aircraft in flight-ready configuration
with battery installed. Record three repositioned readings and the configuration. *Unblocks:* the
feasibility of the entire objective, the load cases, the capacity screen, and whether the target should be
renegotiated before hardware is built.

---

## A. Aircraft measurements — these block CAD directly

Five register rows in [`cad/v995/parameters.csv`](../cad/v995/parameters.csv) are `pending` with **empty
values**. The generator cannot produce a cradle or base plate until they exist.

| # | parameter | what to measure | acceptance |
|--:|---|---|---|
| A1 | `aircraft_capture_width` | Outer body width at the chosen capture station, across the axis the cradle grips. **Not** the rotor-tip span. | Calipers at a recorded station; record the datum and three repositioned readings |
| A2 | `aircraft_capture_length` | Body length the cradle floor spans, chosen to sit between rotor arms without fouling guards | Record which features bound the chosen station |
| A3 | `cradle_wall_height` | Derived from measured body height and rotor-plane offset | Must be justified against rotor clearance, never chosen for convenience |
| A4 | `bench_anchor_spacing` | Centre distance between the two bench anchor points | Measure the actual bench/clamp pattern, or design and verify a new interface |
| A5 | `bench_anchor_hole_diameter` | Clearance for the chosen anchor fastener | Follows from the hardware once A4 exists |

Also needed for the cradle, not yet in the register:

| # | quantity | why |
|--:|---|---|
| A6 | Rotor swept envelope: rotor plane height above the capture station, and tip radius | Sets the clearance the cradle must not violate. The cradle must not enter the swept disc or materially disturb its inflow |
| A7 | Body height at the capture station | A3 cannot be derived without it |
| A8 | Guard and cable exit locations | A guard or cable that touches the base creates a parallel force path around the sensor and silently invalidates every reading |
| A9 | Centre-of-mass location relative to the capture station | Sets the eccentricity `e`, hence the moment `M = T·e` the cell sees off-axis |

---

## B. Hardware measurements — the delivered parts

| # | quantity | why it matters | acceptance |
|--:|---|---|---|
| B1 | Delivered 4540 hole pattern: count, coordinates, **thread designation** (resolves the chosen 4.5 mm `cell_end_hole_diameter` clearance), both end interfaces | The register currently carries `cell_end_hole_spacing = 15.0 mm` from an **80 mm candidate image under a different product ID**, not a verified 4540 drawing | Measure the delivered part *and* obtain its own drawing revision. A single spacing is not enough — fixed and loaded ends differ |
| B2 | Usable thread depth at each hole | Determines screw length and whether a fastener bottoms out and preloads the beam | Inspection plus the drawing |
| B3 | Which end is the loaded end | Reversing it makes the reading meaningless | Cell marking plus drawing; confirm with a known reference load |
| B4 | Body section actually delivered — the register's `cell_body_width` 12.7 mm is `candidate_drawing`, taken from the product page and the 5231 image, not the delivered part | Sets the adapter footprint | Calipers on the delivered cell |
| B5 | Full-scale deflection of the sensing section | `cell_relief_depth` is a guessed 2.0 mm pocket. If the beam touches the base plate the measurement is destroyed | Datasheet or measured under a reference load |
| B6 | Cradle mass | Enters the dead load and the range/drift budget. Taring does not remove physical dead load | Scale, after the cradle exists |
| B7 | Fastener stack per joint: screw length, washer and spacer thicknesses, resulting engagement | Engagement checks cannot be done without it | Selected hardware |

---

## C. Documentary confirmations — a supplier answer, not a measurement

| # | item | current state |
|--:|---|---|
| C1 | **4540 accuracy specification**: nonlinearity, hysteresis, repeatability, creep, corner error, sensitivity, zero offset, temperature drifts | **None verified.** A 2021 Adafruit forum reply said no full datasheet existed. Every number in section 0 for the 1 kg cell borrows the 4541 table and is therefore a placeholder. Ask Adafruit directly for the delivered revision's specification |
| C2 | 4540 drawing revision matching the delivered part | Chrome could not read the 4540 PDF; the indexed geometry came from PID 5231. Adafruit also lists an older 80 mm version, so product number and capacity do not identify the mounting revision |
| C3 | Cell moment/off-axis limits and moment sensitivity | Needed to convert eccentricity into an error and to check the joint is not overloaded. Not established |
| C4 | Cell overload rating, safe and ultimate | Needed for the transient allowance. Adafruit's 2× guidance gives a preliminary 4.90 N screen for 1 kg — a screen, not a rating |
| C5 | NAU7802 noise at the declared output rate and filter setting | The electronics term is currently absent from the budget entirely, and section 0 shows there is almost no room for it |

**Do not substitute TAL220 or SparkFun specifications, or the 4541 table, for the purchased 4540.** They
are different parts, and section 0 shows the conclusion is sensitive to exactly these numbers.

---

## D. Load cases — the numbers that turn `design_choice` into engineering

Seven register rows are `design_choice`: `adapter_edge_margin`, `adapter_thickness`,
`cradle_wall_thickness`, `cradle_floor_thickness`, `base_plate_thickness`, `cell_relief_depth` and
`cell_end_hole_diameter`. Each says in its own source field that it is **not derived from a load case**
(the last is a chosen clearance, resolved by B1 rather than by a load case). They cannot be justified
until these exist.

| # | quantity | note |
|--:|---|---|
| D1 | `T_max`, maximum static thrust of the stock aircraft | **Not established by mass or hover.** No thrust curve verified. Keep it an explicit unknown and declare an operating envelope instead of guessing |
| D2 | Signed load cases | `R = W_aircraft + W_cradle + preload − T + F_cable + F_transient`. If the reaction reverses, the joints and the calibration must support uplift. A loose resting cradle cannot measure it |
| D3 | Transient allowance | Spin-up and stop are not the hover case |
| D4 | Preload from the fastener stack | Enters the dead load and the zero |
| D5 | Cable force and stiffness | An untracked parallel path. Must be bounded or routed to not carry load |
| D6 | Base-plate deflection budget | `base_plate_thickness` is currently "chosen for stiffness under handling" with no stiffness requirement to check against |
| D7 | Anchor reactions and edge distances | Follows from D2 and A4 |

---

## E. Metrology — the campaign that makes it an instrument

None of this can start before the fixture exists, but the numbers should be declared first so the
acceptance criterion is not written after seeing the result.

| # | quantity |
|--:|---|
| E1 | Characterised reference masses spanning the useful range, with their own traceability |
| E2 | Declared useful force range and the discrimination objective inside it |
| E3 | Ascending and descending cycles, with holdout points not used for the fit |
| E4 | Zero return and drift over a stated hold time |
| E5 | Eccentric-load check at the actual `e` from A9 |
| E6 | Installed noise at the declared bandwidth and filter setting |
| E7 | Fit residuals and the full expanded-uncertainty budget with coverage factor |
| E8 | Propwash and cradle-interference bias, assessed separately as an experimental bias, not folded into instrument uncertainty |

**Acceptance:** accept the instrument only if the reviewed expanded uncertainty meets the declared
objective across the whole useful range. On the evidence in section 0, decide *before* building whether
that objective is the right one, because it may not be reachable with this cell at this aircraft mass.

---

## Order of work

1. **Weigh the aircraft** (section 0). It is one measurement and it determines whether the objective
   survives. Do it before anything is cut.
2. **Ask Adafruit for the 4540 specification and drawing revision** (C1, C2). It is an email, and every
   feasibility number currently borrows the wrong part's table.
3. **Inspect aircraft and bench** (A1–A9, B1–B5). This clears the five `pending` register rows and
   unblocks the cradle and base plate.
4. **Declare the load cases and the uncertainty objective** (D1–D7, E2) before freezing geometry, so the
   `design_choice` thicknesses become derived rather than assumed.
5. **Freeze, model, build.**
6. **Calibrate and accept, or reject** (E1–E8).

Steps 1 and 2 cost almost nothing and can both invalidate the current plan. Everything after step 3 is
wasted if step 1 comes back at 22 g.

## What must not be carried over

The historical EX1103/Gemfan single-motor stand is a different platform. Do not transfer its 7.0 V
six-sampled-motor requirement, its 0.020 N·m authority threshold, its 60 mm assumed radius, or its 4.2 N
simulated thrust to the stock V995. The twelve legacy register rows are dispositioned in the research
report; that historical contract stays separate and still reports its own 2 evaluable and 10 pending
clauses.
