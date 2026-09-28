# V995 fixture measurement worksheet

Fill [`measurement-worksheet.csv`](measurement-worksheet.csv) and the five pending
register rows in `cad/v995/parameters.csv` can be populated, after which the
cradle and base plate build on the next generator run.

**27 rows, one bench session.** Everything is on parts you already own; nothing
here needs a purchase, and nothing needs the aircraft powered.

## Rules that make the readings usable

- **Three independently repositioned readings** where the `repeats` column says
  3. Remove the calipers and re-seat them between readings. Save all three — the
  spread is the evidence, a mean alone is not.
- **Record the datum and station** you measured from. A width without a station
  cannot be checked later.
- **Do not infer a thread from a caliper diameter.** Gauge it, or read it off a
  drawing. A measured major diameter does not give pitch.
- **Leave a row blank rather than estimate it.** A blank keeps the part
  fail-closed; a guess silently becomes a design input.
- Record the instrument and its resolution. Resolution is not uncertainty, but
  without it the reading cannot be bounded at all.

## What each group unblocks

| Group | Rows | Unblocks |
| --- | ---: | --- |
| `load_cell` | 15 | **OQ-017** — moves the bolt pattern off `candidate_drawing`; decides which drawing actually applies to your part |
| `aircraft` | 7 | the **cradle** (`aircraft_capture_width`, `aircraft_capture_length`, `cradle_wall_height`) and replaces the unverified 50 g mass estimate |
| `bench` | 5 | the **base plate** (`bench_anchor_spacing`, `bench_anchor_hole_diameter`) and the ground-effect clearance assessment |

## Two rows that matter more than the rest

**LC-14, which end is the loaded end.** Getting this wrong inverts the fixture:
the cradle would bolt to the fixed end and the measurement would be meaningless.
It is usually an arrow or a label on the body.

**AC-06, flight-ready mass on a scale.** Everything downstream scales from it —
the force range, the cell selection screen, the uncertainty target. It is
currently an unverified estimate of 50 g, and a search snippet suggested 22.3 g,
which would change the conclusion materially. This single reading is the highest
-leverage number in the list.

## Derived, not measured

`cradle_wall_height` is **derived** from AC-03, AC-04 and AC-05 — body height
with clearance to the rotor plane *and* to the guard lower edge, whichever is
more restrictive. Record the three inputs; the derivation and its justification
belong in the register, not in a tape measure.

## What this does not close

Filling every row makes the parts **buildable, not accepted**. Still outstanding
afterwards: signed load cases and off-axis moments, a stress or deflection check
on any of these parts, rotor-airflow interference from the cradle, cable and
restraint routing that must not form a parallel force path, and installed
calibration of the cell (OQ-012).
