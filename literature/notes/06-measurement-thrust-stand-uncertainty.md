# 06 — Propulsion characterization, thrust stands, measurement uncertainty

Repo artifacts this cluster governs: `docs/bench-acquisition.md` (R2 settings),
the R3 calibration plan and OQ-012, `Analysis/measured_authority_gate.py` and its
`docs/specs/measured-authority-gate/evidence-contract.md`, `cad/bench/*`.

## Headline findings for this repo

1. **Ground effect will corrupt a whole-vehicle bench test unless we design
   against it, and the required clearance is larger than intuition suggests.**
   For a *whole quadrotor* the measured thrust inflation reaches **≈1.4× near
   z/R ≈ 1 and does not settle to 1 until z/R ≈ 5–6** (≈2.5–3 rotor diameters) —
   worse than the single-rotor case because of the **fountain effect** between
   opposing rotors. For the ~50 g V995 that is a few tens of cm in *every*
   direction, including the ceiling. Cheap to buy; must be bought.
2. **"A tare is not a calibration" now has a citation** — VIM 2.39 Note 2:
   calibration must not be confused with *adjustment* of a measuring system,
   "often mistakenly called 'self-calibration'". This is exactly the distinction
   `docs/bench-acquisition.md` §2 (E3) and the R3 plan already make.
3. **Battery sag should be eliminated, not corrected.** Both authoritative
   small-prop benches (Deters et al.; NASA Ames) power the article from a
   **regulated bench supply** and measure supply voltage independently. Our plan's
   "retain voltage as a covariate" is second-best; say so.
4. **Thermal zero drift dominated a professional balance** — NASA Ames saw
   **0.1–0.3 lb** end-of-run z-force drift, well correlated with temperature, and
   fitted a per-channel linear correction. At our 0.49 N hover-equivalent scale
   this effect is not a rounding error; log temperature.
5. **A prop guard is not a duct.** Properly designed shrouds give large gains
   (+94 % thrust at constant power at 16 cm rotor scale); a loose guard ring at
   large tip clearance has no claim to them. The V995's guards must be measured
   both ways on our own bench, never assigned a literature number.
6. **There is no ASTM/ISO/SAE standard test method for sUAS thrust-stand
   characterization.** That absence is itself a defensible statement in our
   uncertainty doctrine — and it means our evidence contract has to carry the
   weight a standard normally would.

## 1. Measurement-uncertainty doctrine

| Ref | A/E | Key content |
| --- | --- | --- |
| **JCGM 100:2008 (GUM)**, *Evaluation of measurement data — Guide to the expression of uncertainty in measurement*, BIPM, [10.59161/jcgm100-2008e](https://doi.org/10.59161/jcgm100-2008e) | 3 / A | Designation verified. Type A (statistical) vs Type B; law of propagation **including covariance terms for correlated inputs**; expanded uncertainty U = k·u_c. |
| JCGM 101:2008 (MC propagation), 102:2011, 104:2009 | 2 / A | Use Monte Carlo propagation when the model is nonlinear or inputs non-Gaussian — relevant to propagating through a nonlinear ADC/calibration fit. |
| **JCGM 200:2012 (VIM)**, entry **2.39 "calibration"** | 3 / A | Calibration is a two-step relation from standards-with-uncertainty to indications-with-uncertainty. **Note 2: not to be confused with adjustment ("self-calibration") or with verification.** The citable basis for "a tare is not a calibration" and "ADC internal calibration ≠ force calibration". |
| Taylor & Kuyatt, **NIST TN 1297** (1994) | 3 / A | US restatement: Type A/B, combined and expanded uncertainty, reporting rules. |
| Possolo, **NIST TN 1900** (2015), [10.6028/NIST.TN.1900](https://doi.org/10.6028/NIST.TN.1900) | 3 / A | Supplements TN 1297; bottom-up vs top-down budgets. **The practical one to follow for a small bench.** |
| **ILAC-P14:09/2020**, *Policy for Measurement Uncertainty in Calibration* | 3 / A | Reporting: **y ± U**, state **k** and that coverage ≈95 %, and give **U to at most two significant digits** with the result rounded to match. |
| ASME PTC 19.1-2018 (R2024), *Test Uncertainty* | 2 / A | Engineering-test framing; classifies by effect *and* by quantification process. Paywalled — **no clause citations**. |

**Doctrine for stating our calibration result** (this is what R3.8 should emit):

1. A calibration is a *relation* with uncertainty on both sides (VIM 2.39);
   zeroing the NAU7802 is **adjustment**.
2. Budget = Type A (repeat loadings, scatter) + Type B (mass-standard uncertainty,
   resolution, hysteresis, creep, temperature, off-axis), combined **with
   covariances where components share a source**.
3. Report **y ± U**, U = k·u_c, state k and coverage (k = 2 ≈ 95 %), **U to ≤2
   significant digits**.
4. State traceability of reference masses and the conditions (temperature,
   orientation, load direction) under which the relation holds.
5. **Copy the worked template**: Russell et al. (2016) form a 4-term RSS budget —
   relative calibration error, hysteresis, repeatability (2σ of returning static
   points), and unsteadiness (2σ/√N) — quoted at 95 %.

## 2. Load-cell metrology

| Ref | A/E | Key content |
| --- | --- | --- |
| **OIML R 60-1:2021 (E)**, *Metrological regulation for load cells — Part 1* (Parts 2 and 3: test procedures, report format) | 3 / A | Designation verified. Defines **creep**, **hysteresis error**, **minimum dead load output return (DR)**, temperature effect on min-dead-load output and on sensitivity, barometric and humidity effects. Limits: creep after 30 min at 90–100 % E_max ≤ 0.7·\|MPE\|, 20→30 min drift ≤ 0.15·\|MPE\|; DR ≤ 0.5 v; performance over **−10 °C to +40 °C**; output change ≤ v_min per 1 kPa; repeatability = max spread over 3–5 identical applications ≤ \|MPE\|. Cites OIML G 1-100 (= GUM) for expanded uncertainty. |
| ASTM E74-18e1, *Calibration and verification of force-measuring instruments* | 2 / A | Multiple runs, least-squares fit to 5th order, uncertainty from residuals. Paywalled. |
| ISO 376:2011, *Calibration of force-proving instruments* | 2 / B | International counterpart; 2nd–3rd order fits. **E74 and ISO 376 are not interchangeable.** |
| Vishay Micro-Measurements **TN-504-1**, *Strain gage thermal output and gage factor variation with temperature* | 2 / C | Thermal output ("apparent strain") from CTE mismatch between foil and flexure — the physical mechanism behind our zero and span drift. **Log bench temperature alongside grams.** |

**Practical consequence.** OIML classes are stated in verification intervals *v*,
not "% FS", so a hobby-cell "0.05 % FS" number is not comparable to an OIML class.
We will have no certificate for the Adafruit cells, so we must **measure our own
creep, hysteresis and temperature coefficients using R 60-1's test definitions as
the protocol**, then carry them as Type B components. That is a concrete addition
to the R3 plan.

## 3. Small-propeller / low-Reynolds performance

| Ref | A/E | Key content |
| --- | --- | --- |
| Brandt & Selig (2011), *Propeller performance data at low Reynolds numbers*, AIAA 2011-1255, [10.2514/6.2011-1255](https://doi.org/10.2514/6.2011-1255) | 3 / A | 79 propellers; Re at 0.75R ≈ 50 000–100 000 for small UAV props. Foundational dataset. |
| **UIUC Propeller Data Site** (Selig et al.), Vols 1–4 | 3 / A | Open wind-tunnel C_T, C_P, η vs J and RPM including static. **The reference to sanity-check any home bench against.** |
| Deters, Ananda & Selig (2014), *Reynolds number effects on the performance of small-scale propellers*, AIAA 2014-2151, [10.2514/6.2014-2151](https://doi.org/10.2514/6.2014-2151) | 3 / A | 27 COTS + 4 printed props, **2.25–9 in** — our size class. Performance improves with Re. |
| **Deters, Kleinke & Selig (2017)**, *Static testing of propulsion elements for small multirotor UAVs*, AIAA 2017-3743, [10.2514/6.2017-3743](https://doi.org/10.2514/6.2017-3743) | 3 / A | Ten prop pairs from four popular quadrotors, Re < 200 000, **static only** — the closest published analogue to our bench. |
| Dantsker, Caccamo, Deters & Selig (2022), *Performance testing of APC electric fixed-blade UAV propellers*, AIAA 2022-4020 | 2 / A | UIUC Vol. 4 — the experimental check on APC's numbers. |
| APC Propellers, *Performance Data* | 2 / C | **Generated by proprietary analysis software from measured geometry, not wind-tunnel measurement.** Treat as prediction. |

## 4. Thrust-stand design and the recirculation/ground-effect trap

| Ref | A/E | Key content |
| --- | --- | --- |
| **Russell, Jung, Willink & Glasner (2016)**, *Wind tunnel and hover performance test results for multicopter UAS vehicles*, AHS 72nd Forum, NASA NTRS 20160007399 | 3 / A | Five COTS multicopters. Rotors ~6 ft from tunnel walls → "potential for recirculating air to affect the measurements… **The effects of recirculation for the hover tests in the tunnel have yet to be quantified**"; lab sting stand ~30 ft from walls considered safe. **Thermal zero drift dominated**: final static z-force **0.1–0.3 lb** below initial, correlated with temperature, corrected by a fitted per-channel linear term. Check loads run **increasing and decreasing** before and after; max hysteresis 0.021 lb; calibration-slope error ±0.020·F_x. Uncertainty = RSS of calibration error, hysteresis, repeatability (2σ), unsteadiness (2σ/√N, N = 30 720 at 1024 Hz × 30 s). |
| Deters, Ananda & Selig (2014), rig description | 3 / A | **The only hard clearance number verified in a peer-reviewed source**: sting long enough that props sit **>1.5 diameters from the fairing**. Also: T-pendulum balance on flexural pivots; **load cell matched to the load** (2.2 lb cell for props ≤5.5 in); 10 selectable mounting positions so each test uses the cell's full range; **preload weight keeps the cell in tension at all times**; NACA 0025 fairing encloses sting, torque cell and wiring to keep them out of the slipstream. |
| Deters, Kleinke & Selig (2017), §III | 3 / A | Static balance run **outside** the tunnel; torque cell moved behind the motor to cut sting-weight moment; calibration by **dead weights over a low-friction pulley, loading and unloading** (hysteresis checked in the calibration itself), repeated regularly, with **slope changes typically ≤1 %** — a usable recalibration-cadence criterion. **Regulated bench supply (not a battery)**, voltage separately verified by DMM. |
| **Sanchez-Cuevas, Heredia & Ollero (2017)**, *Characterization of the aerodynamic ground effect and its influence in multirotor control*, Int. J. Aerospace Eng. 2017:1823056, [10.1155/2017/1823056](https://doi.org/10.1155/2017/1823056) | 3 / A | Single rotor: **T_IGE/T_OGE = 1/(1 − (R/4z)²)**, validated on two multirotors; inflation ~**1.2×** at small z/R, essentially gone by **z/R ≈ 4**. **Whole quadrotor is far worse**: measured ratio ≈**1.4× near z/R ≈ 1**, not settling to 1 until **z/R ≈ 5–6**, attributed to the **fountain effect** (opposing-rotor downwash meeting under the body), supported by CFD. **Partial ground effect produces a pure moment disturbance** — on our bench that appears as an apparent pitch/roll bias, not just a thrust bias. |
| Cheeseman & Bennett (1955), ARC R&M 3021 | 1 / A | The classical ground-effect reference; cite as provenance only. |

**Bench rules this generates for `docs/bench-acquisition.md` §5 / R3:**

1. Clearance in **rotor-diameter units, in every direction including the ceiling**:
   ≥2.5–3 diameters for a whole vehicle (from z/R ≈ 5–6), ≥2 for a single rotor.
2. Keep the rig out of the slipstream; whatever remains ≥1.5 prop diameters away.
3. **Prove the absence of the artifact**: sweep stand height / wall distance at
   fixed commanded RPM and show the thrust curve has gone flat before quoting a
   number. Russell et al. explicitly *did not* do this — it is the one acceptable
   way to claim out-of-ground-effect conditions on a preregistered gate, and it
   would be a small genuine contribution.
4. **Bracket every run with a zero-load static point and log temperature**, then
   separate thermal drift from aerodynamic bias before blaming either.
5. Match the cell to the load and keep it preloaded in tension.

## 5. Propulsion characterization: what our chain can and cannot claim

| Ref | A/E | Key content |
| --- | --- | --- |
| Leishman (2006), *Principles of Helicopter Aerodynamics*, 2nd ed., CUP, ISBN 0-521-85860-7, §2.8 | 3 / B | **Figure of Merit** = ideal hover power / actual hover power — the dimensionless, scale-fair static efficiency. |
| Deters, Kleinke & Selig (2017) | 3 / A | Reduction path: P = 2πnQ from measured torque; C_T = T/(ρn²D⁴), C_P = P/(ρn³D⁵); Re at 0.75R via Sutherland; density from measured ambient p, T. **Shaft power (torque) and electrical power measured separately** — that separation is what attributes losses to ESC/motor vs rotor. |
| Tyto Robotics (RCbenchmark), *Recommended propeller setup for thrust tests* (2025) | 2 / D | "Testing with the thrust in the other direction can create a **3–20 % difference** in your results due to airflow interaction with the fixture" — upstream obstruction costs less than downstream. **Vendor grade, no data shown; treat as a hypothesis to test on our own bench.** |

**Consequence for our claims.** The INA260 gives the **electrical** side only.
Without a torque measurement we can compute **thrust per electrical watt (N/W)**
but **not Figure of Merit**. Also: propulsive efficiency η = TV/P is *identically
zero* in static test (V = 0), so it is not a meaningful static metric — quoting
N/W as "efficiency" across different props is the standard error, and our plan's
existing note on this is correct. N/W scales with disk loading, so it is only
comparable between rotors of the same diameter.

## 6. Ducted / shrouded rotors — and why the V995's guards are not ducts

| Ref | A/E | Key content |
| --- | --- | --- |
| **Pereira (2008)**, *Hover and wind-tunnel testing of shrouded rotors for improved micro air vehicle design*, PhD, Univ. Maryland (also Pereira & Chopra, JAHS 54(1), 2009) | 3 / A | 17 shrouded-rotor models at **16 cm rotor diameter** — our scale. vs open rotor: **up to +94 % thrust at equal power**, or **−62 % power at equal thrust**. Gains exceed momentum theory because the shroud also cuts non-ideal rotor losses. Depends on diffuser angle/length, **inlet lip radius**, and **tip clearance**. |
| Li, Yonezawa & Liu (2021), *Effect of ducted multi-propeller configuration on aerodynamic performance in quadrotor drone*, Drones 5(3) 101, [10.3390/drones5030101](https://doi.org/10.3390/drones5030101) | 2 / C | **CFD only, no experimental validation.** Ducted vs non-ducted: +7.0 % lift/+9.7 % FM (basic spacing) up to +24.5 % lift/+38.1 % FM optimized. Tip-distance interference degrades at small spacing; height offset helps. |
| Hein & Chopra (2007), *Hover performance of a micro air vehicle: rotors at low Reynolds number*, JAHS 52(3) 254–262, [10.4050/JAHS.52.254](https://doi.org/10.4050/JAHS.52.254) | 2 / B | Open-rotor MAV-scale baseline for FoM comparison. |

**Rule for the repo:** the V995's guard rings are large-tip-clearance ducts at
best. **Measure with and without guards on our own bench**; import no number from
the shrouded-rotor literature. This also matters for the `mechanism` action's
mass/inertia credit in OQ-010 — if the guard is aerodynamically active, removing
it changes thrust as well as mass.

## 7. Gaps (report as absences)

- **No ASTM/ISO/SAE standard test method for sUAS propulsion bench
  characterization.** ASTM F38 covers airworthiness, operations and operator
  qualification; nothing on thrust-stand characterization. Do not cite a standard
  here — there isn't one.
- **No published quantitative correction for recirculation in a small restrained
  multirotor bench test** — Russell et al. explicitly leave it unquantified. Our
  height/wall sweep would be a genuine small contribution.
- **No verifiable published guidance on battery-sag correction in thrust testing** —
  the citable practice is to eliminate it with a regulated supply.

## Unverified — do not cite until confirmed

- "At least 2–3 propeller diameters of clearance in all directions" attributed to
  Tyto Robotics — **that sentence is not on the fetched Tyto pages.** Do not cite
  it to them; cite the z/R ≈ 5–6 result from Sanchez-Cuevas et al. instead
  (which happens to agree).
- Search-summary claims about a 15×10×3.5 m hover facility, OGE at 1.5 rotor
  diameters, ground plane at 2× rotor diameter, +7 % thrust at half a diameter —
  each needs its own primary source.
- "Duct increases thrust by 4 %" (ducted counterrotating UAV propeller noise
  study) — search summary only.
- Deters' PhD dissertation (Illinois IDEALS 49658, 2014) likely contains
  component-level u(C_T), u(C_P) at low thrust — **our main risk at 50 g scale.**
  Worth pulling directly.
- ASME PTC 19.1, ASTM E74, ISO 376 clause contents — designations/years/scopes
  verified, bodies paywalled. **No clause numbers from these.**
