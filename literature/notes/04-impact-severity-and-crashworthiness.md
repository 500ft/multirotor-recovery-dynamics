# 04 — Ground impact severity, injury thresholds, crashworthiness

Repo artifacts this cluster governs: `BARE_CRITERION`, `GUARDED_CRITERION`,
`SENSITIVITY` in `Analysis/survivable_set.py`; `design.md` §5 (the
PREREGISTERED-ASSUMED landing criterion); OQ-010's guarded impact tolerance;
the whole justification for the guard/mechanism.

## Headline findings for this repo

1. **Our landing criterion cannot be justified on human-injury grounds — and
   that is a finding, not a failure.** At 165 g and 3 m/s the vehicle carries
   **0.74 J (0.55 ft-lb)**. The most conservative published human-injury
   yardstick anywhere in the corpus is **11 ft-lb (14.9 J)** — and that is a
   *rigid-object equivalence*, which a frangible airframe clears by a further
   order of magnitude (the FAA's own figure: a Phantom 3 needs **130 ft-lb**
   pre-impact to match a rigid object at 11 ft-lb). We are **~27× below** the
   yardstick in raw KE before frangibility. Injury is not the binding constraint.
2. **But 1.5–3 m/s has a real, citable anchor — from landing-gear
   certification, not injury research.** 14 CFR 27.725 (limit drop, 13 in →
   **2.55 m/s**), 27.727 (reserve energy, 1.5× height → **3.12 m/s**), 29.725
   (8 in → **2.0 m/s**), 25.473 (**3.05 / 1.83 m/s**). Four independent
   regulatory anchors spanning **1.83–3.12 m/s**. Our band is not arbitrary; it
   is the certified design-landing-velocity envelope, **reached by analogy from a
   different vehicle class and scale**. Saying that is far stronger than "assumed".
3. **The tilt limit has no published basis at all.** No sUAS standard specifies
   impact attitude as a pass/fail parameter. It must come from a **tip-over
   calculation on our own guard geometry**, validated by drop test.
4. **A scalar criterion is the wrong shape.** Both 27.725's "greatest probable
   sinking speed" language and the Apollo LM gear criterion are *coupled
   envelopes* over (vertical velocity, horizontal velocity, attitude, attitude
   rate, surface slope). For a release-recovery vehicle the tilted, translating
   corner **is** the design case — exactly the corner a scalar gets wrong.
5. **No crashworthiness standard exists for the vehicle itself.** Verified
   negative result. NIST sUAS test methods cover maneuvering and proficiency, not
   survivability; ASTM F3389/F3322 test the *human* side. A4 flags the adjacent
   gap explicitly: "blade guard standards exist for consumer grade fans but not
   for flight worthy stands."

## 1. ASSURE / FAA ground-collision severity

| Ref | A/E | Key content |
| --- | --- | --- |
| **Arterburn, Ewing, Prabhu, Zhu & Francis (2017)**, *FAA UAS COE Task A4: UAS Ground Collision Severity Evaluation, Rev. 2*, UAH/Kansas/MSU/ERAU | 3 / A | Metrics: AIS, HIC15/36, Viscous Criterion, Blunt Criterion, FMVSS 208 loads on a Hybrid III 50th-pct male. §5.2: HIC and VC "require complex finite element modeling… **no recommended standards** for the conduct of this modeling" → A4 substitutes an impact-KE ↔ peak head-g correlation. **Thresholds**: RCC/AFSPCMAN critical-injury floor **11 ft-lb**; NAVAIR skull fracture **15 ft-lb**; RCC 10 % POF head **38 ft-lb (51 J)**, thorax **28 ft-lb (36 J)**, abdomen/limbs **60 ft-lb (81 J)**; 50 % POF head **60 ft-lb**; 90 % POF head **87 ft-lb**. Area-weighted 10 % POF: standing **49**, sitting **45**, rock concert **38 ft-lb**. Skull-fracture onset **198 g**. **Phantom 3 needs 181 ft-lb (linear) / 128 ft-lb (3σ) to reach 198 g** — vs **≈23 ft-lb for a steel or wood block of identical mass** (99 % P(AIS≥2) vs <0.10 %). |
| Same, terminal-velocity data | 3 / A | **Multirotor terminal KE = 64.7 ft-lb per lb MGTOW** (<4.4 lb). Phantom 2 measured free fall **≈19 m/s**, flight-test Cd 1.07 (CFD within 1 %). Phantom 3 Cd,vert **0.9313** bare vs **1.124 guarded**; **guards increase vertical flat-plate drag area 42 %** (lateral 19.6 %). **Blades stop windmilling almost immediately** after power loss; stationary blades ≈**40 %** of vertical drag. |
| Same, §4.10 laceration | 3 / A | Syndaver skin (4 N puncture). **With the stock blade guard, no laceration until 3.5 ft/s (≈1.07 m/s), at which point the guard itself failed** by support buckling/fracture; carbon and reinforced-plastic props **cut through** the guard. **Without guards, laceration at 1 ft/s (0.3 m/s).** Named standards: EN 71-1:2014, EC Type Approval Protocol No. 3. |
| **Arterburn, Olivares, Bolte, Prabhu & Duma (2019)**, *Task A14: UAS Ground Collision Severity Evaluation 2017–2019*, FAA | 3 / A | Seven multirotors, five fixed wings, wood/foam blocks, plus PMHS work. **The 198 g criterion = only 9 % probability of AIS≥2 skull fracture** on the Mertz (2016) curve — "overly conservative relative to the PMHS testing." Automotive metrics re-normalised to the Micro-UAS ARC's **30 % probability of AIS≥3** (FMVSS 208 Nij = 1.0 is 22 %; shifted value **Nij ≈ 1.21**). States plainly that **PMHS-derived risk curves for sUAS impacts are still needed** — the curves in use are borrowed from automotive crash. |
| FAA Micro-UAS ARC (2016), *ARC Recommendations Final Report* | 2 / B | Allowable AIS≥3 rates: **Category 2 = 1 %**, **Categories 3 and 4 = 30 %**. Recommended **impact energy density** (KE per contact area) with values set by consensus standards. Flagged blade laceration as needing research. |

## 2. Where 11 and 25 ft-lb actually come from — the correction

| Ref | A/E | Verbatim content |
| --- | --- | --- |
| **14 CFR 107.120(a)** (Category 2) | 3 / A | "Will not cause injury to a human being that is equivalent to or greater than the severity of injury caused by a transfer of **11 foot-pounds of kinetic energy upon impact from a rigid object**"; no exposed rotating parts that would lacerate skin; no safety defects. |
| **14 CFR 107.130(a)** (Category 3) | 3 / A | Identical construction at **25 foot-pounds**. |
| **14 CFR 107.110** (Category 1) | 3 / A | **≤0.55 lb (250 g)** on takeoff and throughout, and **no exposed rotating parts that would lacerate human skin**. |
| **FAA (2021)**, *Operation of sUAS Over People*, Final Rule preamble, 86 FR | 3 / A | Limits based on "the **Range Commanders Council's Common Risk Criteria Standards for National Test Ranges**" and commercial space regulations, which "are based on impacts from **inert debris and other types of rigid objects and assume these rigid objects transfer all their kinetic energy**." To match a rigid object at 11 ft-lb a Phantom 3 needs **130 ft-lb**; at 25 ft-lb, **220 ft-lb**. |

**Three consequences the repo must carry:** (i) 11/25 ft-lb are **injury-severity
yardsticks, not drone KE caps**; (ii) they originate in **range-safety debris
criteria** (RCC 321 / AFSPCMAN 91-710, tracing to Feinstein and Janser fragment
studies), not drone research; (iii) the equivalence is **enormously favourable**
to real, frangible drones (~8.8–11×).

## 3. HIC and blunt trauma — valid, but unbinding and unvalidated at our scale

| Ref | A/E | Key content |
| --- | --- | --- |
| **Svatý, Vrtal, Mičunek, Kohout, Nouzovský, Frydrýn, Blodek & Kocián (2025)**, *Impact analysis assessment of UAS collision with a human body*, PLOS ONE 20(3) e0320073, [10.1371/journal.pone.0320073](https://doi.org/10.1371/journal.pone.0320073) | 3 / A | **The single most relevant published source for the sub-250 g regime.** 49 impact tests, 19 UAS types, **~20 g to >1 kg** (explicitly including the 250 g boundary; DJI Spark and Mini named), **7–24 m/s**, **1–280 J**. Vertical drop rig 5–37 m, Hybrid III 50th-pct ATD, five cameras at **500–2000 fps**, 27-channel DAQ. **Central conclusion: KE models show "limitations of their predictive ability for deformable and frangible structures"; HIC15 exhibits an asymptotic trend with increasing KE** — energy transmitted decreases proportionally as KE rises, because the airframe deforms and fractures. **Structural fragility is itself the mitigation.** |
| Campolettano, Bland, Gellner, Sproule, Rowson, Tyson, Duma & Rowson (2017), *Ranges of injury risk associated with impact from UAS*, Ann. Biomed. Eng. 45(12) 2733–2741, [10.1007/s10439-017-1921-6](https://doi.org/10.1007/s10439-017-1921-6) | 2 / B | **1.2–11 kg only — 7× our vehicle.** Max AIS 3+ risk 11.6 % in live flight, >50 % in several falling-impact tests; risk rises with mass. Designs that "redirect the UAS away from the head or deform upon impact transfer less energy." |
| Eppinger, Sun, Bandak et al. (1999/2000), NHTSA — source of HIC15 thresholds and AIS risk curves used by A4/A14 | 2 / A | Cited inside A4; the automotive provenance of every injury curve in this field. |
| Versace (1971), SAE 710881 — origin of HIC; Lau & Viano (1985) — origin of VC | 1 / B | Provenance only. |
| Magister (2010), *The small unmanned aircraft blunt criterion based injury potential estimation*, Safety Science 48(10) 1313–1320, [10.1016/j.ssci.2010.04.012](https://doi.org/10.1016/j.ssci.2010.04.012) | 3 / C | Citation verified; **paywalled, no numbers extracted.** |

**Verdict on HIC at 165 g:** not invalidated, simply **unbinding and
unvalidated** there. A4 says HIC/VC need FE modelling with "no recommended
standards"; A14 shows the 198 g criterion is over-conservative against PMHS;
Svatý et al. show the KE→HIC relation saturates for light frangible drones;
Campolettano's tested range stops at 1.2 kg. **It must not be the basis for our
landing criterion.**

## 4. The 250 g line itself

| Ref | A/E | Key content |
| --- | --- | --- |
| la Cour-Harbo (2017), *Mass threshold for "harmless" drones*, IJMAV 9(2) 77–92, [10.1177/1756829317691991](https://doi.org/10.1177/1756829317691991) | 3 / C | **250 g** from P(crash) × P(hit a person) × P(fatality \| impact) reaching an expected fatality rate equivalent to manned aviation. Author explicitly warns it rests on "numerous assumptions". *(Abstract verified; PDF 403-blocked.)* |
| la Cour-Harbo (2018), *Quantifying risk of ground impact fatalities for small unmanned aircraft*, JIRS, [10.1007/s10846-018-0853-1](https://doi.org/10.1007/s10846-018-0853-1) | 2 / C | Citation verified, not read. |
| Koh, Low, Li, Zhao, Deng, Tan et al. (2018), *Weight threshold estimation of falling UAVs based on impact energy*, Transp. Res. C 93 228–255, [10.1016/j.trc.2018.04.021](https://doi.org/10.1016/j.trc.2018.04.021) | 3 / C | Citation verified; paywalled. |

## 5. Vehicle crashworthiness — verified negative result

**No published standard, certification basis or consensus test protocol defines a
damage threshold, impact-speed limit or pass/fail criterion for the survival of a
small multirotor airframe on ground impact.** The academic work each invents its
own ad-hoc drop protocol:

| Ref | A/E | Key content |
| --- | --- | --- |
| Ferrentino, Wu, Nuzzo, Girardi, Brancart & Vanderborght (2026), *A visco-hyperelastic lattice-based arm structure to improve UAV collision resilience*, Drones 10(9) 698, [10.3390/drones10090698](https://doi.org/10.3390/drones10090698) | 3 / B | Soft continuum-lattice arms tuned for controlled buckling; FE validated to MAE 6.7 % quasi-static / 12.1 % dynamic; drop tests give **up to +99 % specific energy absorption and −65 % peak impact force** vs bulk material; **thrust loss 0.42 ± 0.26 %**. *(Abstract verified; MDPI page 403.)* |
| Pham, Eschmann, Zhou, Olarte, Loianno & Ho (2026), *HoLoArm: deformable arms for collision-tolerant quadrotor flight*, IEEE RA-L 11(3) 3582–3589, arXiv [2605.25790](https://arxiv.org/abs/2605.25790) | 2 / B | Survives collisions **up to 7.6 m/s**; 540 g payload; recovery 0.3–0.6 s. |
| Liu & Karydis (2021), *Toward impact-resilient quadrotor design…*, ICRA, arXiv [2011.02061](https://arxiv.org/abs/2011.02061) | 2 / B | Impact-resilient design + recovery control to sustain flight after collisions. |
| NIST Standard Test Methods for sUAS (Jacoff et al.; ASTM E54.09; NFPA 2400) | 1 / B | **Negative finding: these cover maneuvering, payload and proficiency — there is no crashworthiness or survivable-landing drop test.** |

## 6. Terminal velocity in uncontrolled descent

| Ref | A/E | Key content |
| --- | --- | --- |
| ASSURE A4 (above) | 3 / A | 64.7 ft-lb per lb MGTOW; Phantom 2 ≈19 m/s measured; guards +42 % vertical drag area. |
| Hammer, Quitter, Mayntz, Bauschat, Dahmann & Götten (2023), *Free fall drag estimation of small-scale multirotor UAS using CFD and wind tunnel experiments*, CEAS Aeronautical J. 15(2) 269–282, [10.1007/s13272-023-00702-w](https://doi.org/10.1007/s13272-023-00702-w) | 3 / B | URANS validated against wind tunnel. **Free-spinning propellers may increase drag up to 110 %**; **increasing fuselage pitch angle lowers drag 40–85 %**. ⚠️ **Contradicts A4's observation that blades stop windmilling** — reconcilable (braked ESC vs freewheeling), but **we must check our own hardware rather than assume**. |

**Derived for our 165 g vehicle** (our arithmetic, flagged as such): A4's fit →
0.3638 lb × 64.7 ≈ **23.5 ft-lb ≈ 31.9 J** → **v_term ≈ 19.7 m/s**, consistent
with A4's measured ~19 m/s and the EU C0 19 m/s speed cap. Guards would reduce it
(+42 % drag area → roughly −16 % terminal velocity). **Caveat: 0.36 lb is at the
extreme low end of A4's <4.4 lb fit — an extrapolation, to be replaced by our own
measured power-off descent rate, which A4 §5.1 calls "a straight forward task".**

## 7. The anchor for 1.5–3 m/s: landing-gear certification

| Source (verbatim) | Value | Impact speed |
| --- | --- | --- |
| **14 CFR 27.725** (normal-category rotorcraft, **limit drop test**): free drop of "13 inches from the lowest point of the landing gear to the ground" (or lesser height ≥8 in matching "the greatest probable sinking speed likely to occur at ground contact in normal power-off landings") | 0.330 m | **≈2.55 m/s** |
| **14 CFR 27.727** (**reserve energy absorption drop test**): "The drop height must be 1.5 times that specified in §27.725(a)" | 0.495 m | **≈3.12 m/s** |
| **14 CFR 29.725** (transport rotorcraft) | 0.203 m | **≈2.0 m/s** |
| **14 CFR 25.473** (transport airplanes): "limit descent velocity of 10 fps at the design landing weight" and "6 fps at the design take-off weight" | — | **3.05 / 1.83 m/s** |

Aboutness 2 (analogy) / Evidence A (binding regulatory text). Speeds computed as
√(2gh) from the quoted drop heights.

**How to state it honestly:** our 1.5–3 m/s band is **not arbitrary** — it spans
the certified design-landing-velocity envelope across four independent regulatory
anchors (1.83–3.12 m/s). It is an **argument by analogy from a different vehicle
class at a different scale**, and must be labelled as such. That is materially
stronger than "PREREGISTERED-ASSUMED".

**The tilt limit has no published basis.** The nearest precedent is the Apollo LM
landing-gear criterion — instructive because it is *not* a scalar: a coupled
envelope over slope, obstacle height, vertical and horizontal velocity, attitude
and attitude rate. *(NASA NTRS 19720018253 — retrieved via search summary only;
numbers must be confirmed before citing.)*

## 8. What a rigorous criterion would be, in order of cost

1. **Re-scope "survivable landing" to vehicle survival, not injury**, and say why:
   injury is non-binding at 165 g with guards. The criterion then needs no injury
   literature at all.
2. **Derive the limit from a drop test of the actual vehicle**, borrowing the
   **27.725/27.727 structure**: a *limit* drop (no permanent deformation, remains
   airworthy) plus a *reserve energy* drop at **1.5× the height** (may deform,
   must not collapse). Instrument with the onboard IMU plus high-speed video —
   Svatý et al. used 500–2000 fps for exactly this event class.
3. **Express the criterion as an envelope, not a scalar**: (vertical velocity,
   horizontal velocity, attitude, attitude rate, ground slope). Our current
   criterion also **excludes lateral velocity entirely** (`design.md` §5 declares
   this) — the literature says that is precisely the wrong simplification for a
   tilted, translating touchdown.
4. **Get the tilt limit from geometry + a tip-over calculation** (CG projection
   leaving the support polygon), then validate on the same rig. That converts
   tilt from assumption to derived quantity with one measurement.
5. **Anchor terminal velocity empirically** — measure power-off descent rate; the
   guarded Cd differs measurably (+42 % drag area on a Phantom 3).
6. **Keep the injury numbers as a bounding argument only**: "at 3 m/s this vehicle
   carries 0.74 J, versus the most conservative published human-injury yardstick
   of 14.9 J — itself a rigid-object equivalence a frangible airframe clears by a
   further order of magnitude." A strong, fully-cited safety argument; not a
   landing criterion.

## 9. Bonus finding for the guard/mechanism justification

A4's laceration testing is the **only measured evidence found for what a prop
guard actually buys**: it prevents skin laceration up to ≈1.07 m/s impact (vs
0.3 m/s unguarded) and **then fails structurally**. Combined with Mili et al.
(cluster 03) — compliant structures cut peak force ~13 % but **increase rebound
energy** — the honest framing of our guard is **laceration prevention and
force reduction with a known failure point**, not an impact-speed tolerance
multiplier. `GUARDED_CRITERION`'s relaxation from 2.0 → 2.5 m/s has no measured
support and should be flagged as the EST it is (OQ-010).

## Unverified — do not cite until confirmed

- **ASTM F3389 Method A = 54 ft-lbf impact-KE cap** — standards-distributor
  abstract only; standard is paywalled.
- ASTM F3322 numeric descent-rate requirement — never seen. *(A4's separate
  **18.0 ft/s = 5.49 m/s** minimum reliable parachute descent rate **is** verified
  from A4 text — note this **contradicts our 1.8 m/s model terminal speed**; see
  cluster 03.)*
- FAA UAS **Registration** Task Force ARC (Nov 2015) and the **80 J** MITRE
  lethality limit behind the US 250 g line — the FAA URL serves the Micro-UAS ARC
  report instead. Find the real RTF ARC PDF.
- EU 2019/945 Class C0 "19 m/s max speed" — consistent across secondary sources;
  EUR-Lex Annex Part 1 not read.
- Ferrentino et al. specific test numbers (670 g, 1/1.5/3 m drops, 16.69–23.99 N
  vs 11.65–16.52 N) — a search summary appears to **conflate** the Ferrentino and
  HoLoArm papers. Read both PDFs first.
- Apollo LM gear criterion numbers (6° slope, 24-in obstacles, 10 ft/s, 7 ft/s at
  ≤4 ft/s horizontal, ±6°, ≤2°/s) — search summary of NTRS 19720018253.
- Magister (2010), Koh et al. (2018), la Cour-Harbo (2017/2018), Campolettano
  et al. (2017) — citations and abstracts verified, **internal numbers are not**.
- Eppinger et al. HIC15 threshold table by ATD size (A4 Table 6) — an image in the
  A4 PDF that could not be read.
