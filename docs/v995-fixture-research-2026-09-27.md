# Stock V995 fixture: scope correction and online evidence

Date: 2026-09-27. Status: **source review and quantitative screening; installed acceptance pending**.

The owner has confirmed that the already-purchased **stock Veeniix V995 is the
continuing physical platform**. This fixes platform selection. It does not turn
catalogue data into inspection or calibration results.

## The principal correction

The quoted D1–D6 / T12 / twelve-row blocker list describes the historical
EX1103–Gemfan **single-motor stand**. The repository already distinguishes it from
the V995 **whole-aircraft cradle** in the
[September 21 capability sheet](../evidence/week-2026-09-19/platform-capabilities.md)
and [bench intake scope notice](../evidence/week-2026-09-19/bench-intake-packet.md).
For the V995, start from that capability sheet and
[bench acquisition](bench-acquisition.md), not by filling EX1103 rows with V995
numbers. The historical protocol's 7.0 V, six sampled motors, 0.020 N m threshold
and 4.2 N simulation thrust do not transfer to the stock aircraft.

One-paragraph platform answer: retain the V995's stock motors, propellers,
controller, battery and transmitter; characterize the complete aircraft using
external instrumentation. Use a removable whole-aircraft cradle and direct force
sensing with the purchased Adafruit chain. This produces aggregate axial force
under documented restrained conditions. It does not expose individual rotor
forces, independent motor commands, roll/pitch control authority or recovery
performance. Those would require separately demonstrated observability and a
new experiment definition.

## Online sources inspected through the Chrome extension

| Source | Established in this session | Limit |
| --- | --- | --- |
| [Veeniix V995](https://www.veeniix.com/drones/V995?product_id=22&title=Drones) | Manufacturer identifies V995, stock transmitter functions, altitude hold, guards, and its official Ruko shop | Specifications and Downloads tabs returned empty content in the inspected DOM; no motor drawing, hub fit, thrust curve or measured mass established |
| [Adafruit PID 4540](https://www.adafruit.com/product/4540) | 1 kg version; product dimensions 80 × 12.7 × 12.7 mm; listed body mass 29 g; linked drawing | Nominal catalogue envelope, not delivered-part inspection |
| [Adafruit PID 4541](https://www.adafruit.com/product/4541) | Current 5 kg version; 75 × 12.7 × 12.7 mm; an older 80 mm 5 kg version appears in the selector | Revision-specific interfaces must not be interchanged |
| Adafruit product instructions | Fix one end and load the other in the marked direction; installed calibration with known weights required; recommend capacity at least twice maximum applied force/weight | Recommendation does not supply off-axis ratings, uncertainty or a fixture structural analysis |

Drawing links located on those product pages:

- [4540 drawing / datasheet](https://cdn-shop.adafruit.com/product-files/4540/Datasheet.pdf).
- [4541 current drawing](https://cdn-shop.adafruit.com/product-files/4541/C14641+C14642+C14643+datasheet.png).

On resuming Chrome, the 4541 image was visually inspected. The 4540 PDF viewer
remained inaccessible. Its indexed text identifies an underlying Adafruit image,
[80 mm drawing](https://cdn-shop.adafruit.com/product-files/5231/Datasheet.png),
which was opened and visually inspected. Because that image is under PID 5231
and the PDF itself could not be checked, its association with 4540 remains
**candidate evidence**, not an accepted delivered-part drawing.

The [Adafruit support response about PID 4540](https://forums.adafruit.com/viewtopic.php?t=181236)
dated July 14, 2021 states that a full load-cell datasheet was unavailable.
The current 4540 product page provides a diagram, without a performance table.
Do not treat the old support response as proof that no later specification could
exist; the finding here is that no matching 4540 accuracy specification was verified.
Google's AI overview supplied generic TAL220 values from a SparkFun document;
those were **not adopted**, because it does not establish the purchased part's identity.

### Interface transcription

| Feature | 4540 / 80 mm candidate image | 4541 current vendor-linked image |
| --- | --- | --- |
| Body | 80 mm long, 12.7 mm wide in top view; product page additionally gives 12.7 mm height | 75 ± 0.15 mm long; 12.7 × 12.7 mm section |
| Holes | Two M4×0.7 THRU at the left end; two M5×0.8 THRU at the right end | Four M4; drawing does not explicitly specify pitch or usable thread depth |
| End-pair pitch | 15 mm at each end | 10 ± 0.15 mm at each end |
| Longitudinal location | Outer holes 5 mm from each end; derived X = 5, 20, 60, 75 mm from the left body end | Inner-hole gap 44 ± 0.15 mm; derived nominal X = 0, 10, 54, 64 mm from the leftmost hole axis |
| Across width | Common longitudinal centerline as drawn | Common longitudinal centerline as drawn |
| Unresolved | No tolerance block, load-end assignment or engagement limits in image; association/revision needs confirmation | No revision/date block, fixed-versus-loaded-end designation, off-axis limits or engagement limits; do not infer an edge offset from a photograph |

Derived coordinates are arithmetic combinations of printed dimensions, not new
independent tolerances. Preserve the dimensional chain and its correlations.
Neither drawing establishes a complete screw/washer/spacer stack or permits
fabrication before matching the delivered cell. The 80 mm and 75 mm interfaces
are not interchangeable.

Source screenshots: [75 mm drawing](../evidence/v995-fixture-research-2026-09-27/adafruit-4541-drawing-browser.png)
and [80 mm candidate drawing](../evidence/v995-fixture-research-2026-09-27/adafruit-80mm-candidate-drawing-browser.png).

### 4541 performance transcription

The vendor-linked Chinese image lists nonlinearity **0.03% FS**, hysteresis
**0.03% FS**, repeatability **0.03% FS**, creep **0.05% FS / 3 min**, and corner
error **0.05% FS**. It also lists sensitivity **1.0 ± 0.1 mV/V**, zero output
**−0.15 ± 0.05 mV/V**, output resistance **1000 ± 10 ohm**, sensitivity temperature
drift **0.03% FS / 10°C** and zero temperature drift **0.3% FS / 10°C**.
The image says capacity 1–10 kg while its filename includes the 5/10/20 kg
product group. Use the product page's 5 kg rating for PID 4541, and do not extend
this table to other purchased versions without identity evidence. It does not
state a safe-overload percentage, rated deflection or off-axis moment limit.

A search-result snippet reported 22.3 g for V995, conflicting with the earlier
owner estimate of approximately 50 g. That snippet is not adopted as a
manufacturer-verified flight-ready mass. Both battery inclusion and the mass of
the actual aircraft remain material. The prior manufacturer battery specification
accepted for planning is recorded in the September 21 inventory; this session
has not reverified it.

## Decisions and the twelve legacy rows

Recommended design basis: **direct force, 1 kg PID 4540 as the initial candidate,
existing NAU7802 → QT Py chain, complete stock aircraft retained**. This is an
engineering recommendation; only the platform choice above is attributed to the
owner. Cell suitability still depends on the load and uncertainty budgets below.

| Legacy register row | Disposition for the stock V995 whole-aircraft fixture |
| --- | --- |
| `motor_mount_pitch_circle` | External cradle does not mount individual motors. Replace this interface requirement with actual cradle contact/retention geometry in a V995-specific contract. |
| `motor_mount_hole_diameter` | Same: not a prerequisite to designing an external cradle; do not invent V995 motor screws. |
| `motor_mount_thread_engagement` | Same: retain factory motor attachment. New cradle and cell joints need their own engagement records. |
| `prop_mount_screw_spacing` | No new prop-to-motor interface is being designed. Retain factory propellers; inspect their condition and clearance. |
| `prop_hub_fit_tolerance` | Preserve the factory mating interface. No new fit class or arbitrary 0.05 mm tolerance is needed for an external cradle. A replacement hub would reopen the fit question. |
| `load_cell_capacity` | Prefer the purchased 1 kg unit for initial low-force characterization: nominal capacity 9.80665 N using standard gravity. This is capacity, not proven usable range or expanded uncertainty. |
| `load_cell_mount_spacing` | Obtain both end interfaces from the matching Adafruit drawing and verify the delivered version. A scalar spacing alone is insufficient. Installed calibration follows construction; it need not prevent preliminary interface research. |
| `stand_anchor_spacing` | Actual bench/clamp geometry remains physical evidence. Alternatively design a new mounting pattern as a declared design choice and verify that its bench interface exists. |
| `stand_calibration_lever` | No external calibration lever in the recommended direct-force route. Record applicability explicitly in a V995 contract; do not enter zero or silently exempt the legacy checker. |
| `authority_arm_measured` | Not needed for aggregate axial force alone. Needed for any later torque model; rotor coordinates relative to a stated origin/CG cannot be inferred from overall body size. |
| `thrust_expanded_uncertainty` | Requires installed reference-load data, residuals, hysteresis, repeatability, drift, alignment and coverage assumptions. A website cannot close it. |
| `arm_expanded_uncertainty` | Deferred with any torque claim; required with the corresponding measured arm geometry when that claim is made. |

Thus the two supposed “closable today” decisions become **retain the factory hub**
and **start with the 1 kg candidate**. They are not grounds to fabricate numeric
fit or calibration evidence. There is no implemented applicability amendment in
this research note, and no legacy register row has been relabelled as measured.

## Concrete topology and schema requirements

Proposed load path: stock aircraft → removable retained cradle → load-cell loaded
end → load-cell fixed end → rigid base → bench restraints. The beam measures force
through bending; “direct force” means no added pivot/lever ratio, not axial
stretching of the beam. Independent guards and cables must not carry unrecorded
force around the sensor. Cradle interference with rotor flow must be assessed.

| Field group | V995 definition / units | Evidence needed before geometry acceptance |
| --- | --- | --- |
| Identity | aircraft configuration, cell PID/revision, cradle revision, serial/label records | Actual parts plus matching drawings |
| Aircraft interface | contact patches, restraint points and rotor swept envelopes; coordinates in mm | Inspection of stock aircraft; no dimensions scaled from product photos |
| Cell interfaces | separate fixed/loaded ends; hole count; XYZ coordinates in mm; thread; usable depth; face datum; tolerances | Matching drawing plus part confirmation |
| Fastener stacks | per-joint screw length, washer/spacer/cradle thickness, engagement, bottoming clearance in mm | Selected hardware and drawings/inspection |
| Datum | datum A: cell fixed mounting face; B/C: specified locating features; sensing direction from cell marking; separate aircraft axes | Coordinates tied to actual geometry; alignment measured by appropriate angular/coordinate inspection |
| Force line | application point and direction, lateral offsets in mm, permitted moments in N m | Drawing load location, allowable off-axis response and installed eccentric-load checks |
| Loads | aircraft/cradle dead loads, preload, positive/negative thrust reactions, cable force, transient allowance; N and N m | Measured masses, justified force envelope and manufacturer limits |
| Anchors | hole/clamp coordinates, edge distances, reactions, stiffness, engagement | Actual bench and restraint design |
| Metrology | force range, discrimination objective, expanded uncertainty in N, coverage, sampling/filter settings | Reference masses, installed calibration, repeat tests and recorded configuration |
| Inspection | per-feature instrument, resolution, datum, repeated observations and acceptance limit | Identified available instruments and accessible features |

No defensible numerical allowable offset follows from nominal cell capacity.
For angular misalignment alone, axial projection error is
`T(1 − cos(theta))`; lateral eccentricity also creates `M = T e` and needs the
cell's moment sensitivity/limits. These are different errors.

With a vertical cradle, one possible sign convention is downward support force:
`R = W_aircraft + W_cradle + preload − T + F_cable + F_transient`.
At stable unchanged dead load, `T = R_props_off − R_props_on`. Confirm polarity
with a reference load. Taring does not remove physical dead load or its effect on
range, stiffness, drift and overload. If the reaction reverses, the joints and
calibration must support that direction; do not assume a loose resting cradle
can measure uplift.

Maximum static thrust is not established by aircraft mass or hover. No online
thrust curve was verified. Retain an explicit `T_max` unknown and use a documented
operating envelope before final load/anchor/clearance calculations. Adafruit's
2× capacity guidance gives a preliminary 1 kg screen of no more than about
4.90 N maximum absolute applied sensor force, and 24.52 N for 5 kg. These are
screens, not permitted motor operating limits or fixture strength ratings.

## Measurement capability: what the arithmetic actually says

For a symmetric hover estimate, `T_total = m g` and `T_rotor = m g / 4`.
At the **unverified 50 g scenario**, total hover is 0.4903 N and per-rotor hover
is **0.1226 N**, not 0.2 N. A 0.2 N rotor force can be a separate scenario, but
is not derived from a 50 g hover mass. The V995 fixture measures the total.

| Force scenario | Force (N) | % of 1 kg capacity | % of 5 kg capacity |
| --- | ---: | ---: | ---: |
| 50 g whole-aircraft hover estimate | 0.4903 | 5.00 | 1.00 |
| 50 g symmetric per-rotor estimate | 0.1226 | 1.25 | 0.25 |
| Quoted per-rotor example | 0.2000 | 2.04 | 0.408 |

Small percentage of full scale alone does **not** establish that uncertainty
exceeds the force. A specification `p %FS` corresponds to an absolute bound
`b = (p/100) F_FS`, whose fraction of the measured force is `b/F`.
Actual `p` values must come from a matching specification. The 4541 values are
transcribed above; corresponding 4540 values remain unverified.

The existing exploratory objective is to distinguish 5% of `F_ref_use`, with
expanded uncertainty no greater than half that increment:
`U_target = 0.025 F_ref_use`. It remains a proposal, not a passed criterion.
At 0.4903 N this is **0.01226 N**, equivalent to **0.125% FS for 1 kg** or
**0.025% FS for 5 kg** for the entire installed uncertainty budget. At a 0.2 N
reference the corresponding limits are 0.005 N, 0.05099% FS and 0.01020% FS.

For explicitly bounded independent rectangular errors `b_i`, a preliminary
standard uncertainty screen is `u_i = b_i/sqrt(3)` and
`U = k sqrt(sum(u_i^2) + other variance terms)`. Independence, the distributions
and a coverage factor near 2 need justification. Do not double-count a combined
accuracy specification and the same constituent errors, or mistake a worst-case
bound for a standard uncertainty. Installed calibration must also include the
reference, fit residuals, noise at the declared bandwidth, hysteresis, zero
return, drift, alignment, eccentric loading, cables and dead-load subtraction.
Propwash/cradle effects are experimental biases requiring separate assessment.

### Quantitative 5 kg screening result

Using `F_FS = 5 × 9.80665 = 49.03325 N`, each 0.03% FS term corresponds to
**0.014710 N**. For a preliminary Type-B screen only, interpret each as a
symmetric bound with an independent rectangular distribution and use `k = 2`.
For nonlinearity, hysteresis and repeatability together:

`U_screen = 2 sqrt(3 × (0.0003 F_FS / sqrt(3))²) = 0.029420 N`.

That is **6.0%** of the 50 g scenario's 0.4903 N force, and **2.4 times** its
0.01226 N target. The three absolute bounds summed conservatively are 0.04413 N,
or 9.0% of that force. Adding the published creep and corner-error terms under
the same independence assumptions would give about **0.04968 N (10.13%)**.
Do not add these blindly to calibration residuals covering the same mechanisms.

This is a specified-error screening model, not a calibrated lower bound on the
actual cell's achievable uncertainty. It already exceeds the target before
reference-load uncertainty, electronics, drift and fixture effects are included.
The 5 kg cell therefore **does not demonstrate compliance from its published
specifications** and is not the preferred precision instrument for this task.
It may still serve coarse measurements or pass a carefully justified local
calibration; this calculation does not prove physical impossibility.

Unrounded inputs, assumptions and results are retained in
[screening-calculation.json](../evidence/v995-fixture-research-2026-09-27/screening-calculation.json).

The zero-temperature coefficient corresponds to **0.01471 N per °C** for this
5 kg version, illustrating why temperature stability and nearby zero checks
matter. Sensitivity coefficient, excitation and ADC settings also need review;
the present drawing does not establish recommended excitation limits. Keep the
existing 2.4 V excitation proposal provisional rather than declaring it validated.

**1 kg verdict:** choose it as the initial calibration candidate, not as an
accepted instrument. For the 50 g force scenario its entire installed expanded
uncertainty must be no more than **0.125% FS = 0.01226 N**, equivalent to about
1.25 g of force. If three independent rectangular component bounds alone shared
that whole budget equally, each would need to be ≤0.0625% FS; actual allocations
must be smaller to leave room for the rest of the chain. No verified 4540 table
currently establishes those bounds. Importing 4541 or generic TAL220 values
would conceal that gap.

Before a powered experiment, qualify the 1 kg cell in its actual mounting and
load direction, at the actual cradle/preload operating point. A candidate low-force
reference sequence is 0, 5, 10, 20, 50 and 100 g equivalent increments, provided
it spans the intended experiment and remains within the established load budget.
Use characterized reference masses, repeated ascending/descending cycles,
independent holdout loads, zero returns, three-minute holds, temperature records
and eccentric-load trials. Match the eventual 80 SPS/filtering configuration and
also characterize the proposed 10 SPS static alternative. Establish noise and
uncertainty at the averaging interval actually reported; do not count correlated
samples as independent. Subtractive thrust measurements require the covariance
of the props-off and props-on readings, not an assumed zero contribution.

Accept only after the reviewed installed uncertainty meets
`U ≤ 0.025 F_ref_use` throughout the declared useful range. That target is still
exploratory and must be tied to the actual experiment; online research has not
closed the calibration row or established maximum motor thrust.

## Gate and critical-path answer

- C1 Phidgets 3132_0 remains a historical candidate, not an assertion that it was
  purchased. It is the wrong source for a V995 cradle drawing, but should not be
  silently rewritten as an Adafruit part under the same historical identity.
- The five `vendor_nominal` register inputs are EX1103/Gemfan values. Confirming
  them on the V995 is impossible: they describe different components. Preserve
  that historical record and author the V995 interface/acceptance contract.
- D1–D6 do not become accepted reviews from internet searches. For V995, use the
  direct-force recommendation, identify the 1 kg candidate and delivered
  revision, define the cradle/interfaces and metrology objective, then review
  that packet. Legacy D3 motor-hub design is outside this fixture boundary.
- Updated sequence: **stock platform fixed → source/drawing review → explicit
  whole-aircraft force objective and cell candidate → inspect cradle/cell/bench
  interfaces → freeze numerical geometry and load criteria → model/build →
  installed calibration and uncertainty → aggregate-force experiment**.
  Calibration can be planned now; it cannot be completed online. The historical
  T12 and release checker remain unchanged and cannot certify this new fixture.

No powered tests, CAD release, task-completion claims, fabricated measurements
or attributed review approvals are included in this document.
