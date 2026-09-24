# 03 — Parachute / ballistic recovery and controlled descent

Repo artifacts this cluster governs: the `parachute` action in
`Analysis/survivable_set.py` (`PARACHUTE_TERMINAL_M_S = 1.8`,
`PARACHUTE_DEPLOY_S = 0.8`, `parachute_impact_speed`); OQ-010's parachute
decision; `design.md` §4 and §1 ("parachute recovery of small UAS is established").

## Headline findings for this repo

0. **Provenance correction, 2026-09-24 (critique C03).** Every landing outcome
   cited in this note from Siotia et al. is a **simulation or hardware-in-the-loop
   result, not a physical drop measurement**; the ParaZero figures are vendor test
   data obtained via a search-engine extract. Nothing here is an independent
   physical validation of any model, and fitting our inflation interval to these
   numbers is **model-to-model calibration**. The evidence grades below already
   said B/C; the prose did not, and now does.

1. **Our parachute action is optimistic by roughly an order of magnitude in
   altitude.** We model 0.8 s deployment to a 1.8 m/s terminal speed and find the
   action worthless below ~3 m and ~40 % effective at 6 m. Measured data on
   *heavier* airframes puts the floor at **10–15 m**: a 900 g Mavic-class vehicle
   loses **11 m on average and 15.9 m worst case** to full canopy (ParaZero,
   vendor test data); a 2 kg UAV has **40 % survivability at 10 m**, "begins to
   operate effectively" at **15 m**, and needs **22–23 m** for complete mitigation
   (Siotia et al. 2026). Our model's 6 m success is not supported by anything
   measured, and our conclusion "the parachute is the only nonzero action for
   two-adjacent loss" rests on it.
2. **No standard gives a numeric minimum altitude, deliberately.** ASTM F3322
   §3.1.27 defines minimum deployable altitude as "airframe/speed dependent and
   certified through testing". **Do not attribute a number to F3322** — a reviewer
   who owns the standard will catch it.
3. **For a sub-250 g vehicle the argument against a parachute is mass, not
   altitude.** The lightest COTS system found is ~185 g — **74 % of the entire
   250 g budget** before canopy, bridle, ejector and independent trigger. This is
   a stronger, cleaner and unrefuted argument than our altitude claim.
4. **A parachute buys a sub-250 g aircraft nothing regulatorily.** It is already
   Part 107 Category 1. ParaZero and Indemnis told the FAA on the record that
   "even when equipped with a parachute, very few unmanned aircraft models will be
   capable of meeting the applicable kinetic energy limitation."
5. **Correction to carry into the repo:** 11 ft-lb and 25 ft-lb are *rigid-object
   injury equivalents*, **not** aircraft kinetic-energy caps. Per ASSURE data in
   the rule itself, a Phantom 3 needs ~130 ft-lb and ~220 ft-lb respectively to
   produce equivalent HIC15 injury.

## 1. Standards

| Ref | A/E | Key content |
| --- | --- | --- |
| **ASTM F3322-22**, *Standard Specification for sUAS Parachutes*, [10.1520/F3322-22](https://doi.org/10.1520/F3322-22) (F38.01; also F3322-24a, [10.1520/F3322-24A](https://doi.org/10.1520/F3322-24A)) | 3 / A | §1.1 lessen impact energy on loss of stable flight; §1.1.1 supports CAA permission to fly over people; §1.1.2 partial compliance may not be claimed. **§3.1.27 MDA** = altitude from failure to stabilized descent, "airframe/speed dependent and certified through testing in Section 6" — **no numeric value**. §3.1.40 stabilized descent = within 10 % of specified fall speed. §3.1.13 KE = ½mv² (formula only, **no threshold**). **§3.1.8–9 CNMF / CNMF+1**: failure injection defined by adjacent motors killed — 4-rotor: 1 motor = CNMF, **2 adjacent = CNMF+1**. Directly parallel to our failure classes. §5.1.3 permits parachute **combined with airbags**. |
| **EASA MOC Light-UAS.2512-01** (2023), *Means of compliance with SORA M2 (medium robustness)* | 3 / A | **The most useful document for the minimum-altitude question.** MDA construction: *greatest altitude loss recorded across all deployment tests + 2 × full parachute assembly length*, measured from power cut to stable descent speed, at MTOM, for multirotors **at both hover and maximum forward speed**; **+3 s of free-fall distance if manually activated**. ≥30 successful activation tests. Descent rate + wind must vector-sum ≤10 m/s (≤25 kg). Alternative non-parachute route: max impact energy **<175 J**. |
| ASTM F3389/F3389M-21, *Assessing the Safety of Small Unmanned Aircraft Impacts* | 2 / A(designation) | Blunt-force head/neck injury for sUA <55 lbf, derived from ASSURE. Companion to F3322. |
| CEN EN 4709-006:2026, *Means to terminate flight* | 2 / D | Catalogue entry only, clause text unseen. *(Note: prEN 4709-004 is lighting, not parachutes — a common miscitation.)* |

## 2. Deployment altitude and latency — the measured numbers

| Ref | A/E | Verified numbers |
| --- | --- | --- |
| **Siotia, Shankar, Nair & Nair (2026)**, *Enhancing UAV survivability through real-time stall detection and parachute assisted recovery*, Sci. Reports 16:18189, [10.1038/s41598-026-47045-0](https://doi.org/10.1038/s41598-026-47045-0) | 3 / A (HIL + sim, **no free-flight drops**) | 2 kg UAV. **Deployment 0.8 s.** At **10 m**: fall time ≈1.43 s ≈ deployment time → canopy only partially inflates; impact 9.1 m/s with chute vs 14.8 m/s without; **40 % survivability**. **15 m** = "begins to operate effectively"; **22–23 m** for complete mitigation. Terminal velocity model v_t = √(2mg/(C_d A ρ)) ≈ 5 m/s at C_d 1.2, A 1.5 m². Emergency response triggered **within 1.1 s** of stall confirmation. At 25 m: 22.2 → 3.2 m/s, 95 % survival. Authors conclude low-altitude mitigation is needed **below 15 m**. |
| ParaZero SafeAir (Mavic-class ~900 g), vendor knowledge base | 3 / C | **11 m (36.1 ft) average altitude loss to full canopy; 15.9 m (52.2 ft) worst case; 3.7 m/s average descent rate.** Published MFA = worst loss + 2× cord length (the EASA rule). ⚠️ Obtained via an indexed extract of a Cloudflare-blocked page — re-confirm against the current manual before citing in a paper. |
| Farajijalal, Eslamiat, Avineni, Hettel & Lindsay (2025), *Safety systems for emergency landing of civilian UAVs — a comprehensive review*, Drones 9(2) 141, [10.3390/drones9020141](https://doi.org/10.3390/drones9020141) | 3 / B | Survey of parachutes, nets, airbags, landing gear, aerodynamic recovery; concludes **hybrid/multi-method recovery covers more of the emergency envelope than any single method** — support for our multi-action policy framing. |

**Our deployment constant is defensible; our terminal speed and the resulting
altitude floor are not.** 0.8 s matches Siotia et al. exactly. But their 2 kg
vehicle still fails at 10 m *because 0.8 s of free fall is ~3 m and the canopy is
not inflated*. Our model treats deployment as a delay followed by an instantly
effective drag device — the inflation transient is missing, and that is precisely
what kills low-altitude deployment.

## 3. Canopy sizing and descent modelling

- ASTM F3322-22 §5.4: sizing chain from nominal diameter D₀ = √(S₀/π), with
  MDSL/opening-shock coupling in §5.3 (MDSL = ½ weakest component break strength,
  and ≥ max opening force at max deployment velocity).
- Siotia et al. (2026): quadratic-drag terminal velocity with a worked parameter set.
- EASA M2 MoC: converts descent rate into an operational envelope
  (OL#1 Wind_max = √(10² − descent_rate²)) rather than a design target.
- **Gap: no peer-reviewed canopy-sizing or inflation-dynamics study for sub-250 g
  canopies.** Everything credible sits at ≥900 g. Classical inflation theory
  (Knacke) is the obvious next source and was not checked in this pass.

## 4. Part 107, the 250 g threshold, and the energy criteria

| Ref | A/E | Key content |
| --- | --- | --- |
| **FAA (2021)**, *Operation of Small Unmanned Aircraft Systems Over People*, final rule, 86 FR 4314 | 3 / A | **Category 1** (§107.110): ≤0.55 lb (**250 g**) on takeoff and throughout, no exposed rotating parts that could lacerate skin. **Category 2** (§107.120): ≤**11 ft-lb** rigid-object-equivalent injury. **Category 3** (§107.130): **25 ft-lb**. Rationale for 11 ft-lb "considers variations for all parts of the body for both adults and children… standing, sitting, and prone." **Deployable devices**: the FAA "did not consider the use of a deployable device in the FAA-provided means of compliance," does not prohibit one, and it "is not required"; ParaZero and Indemnis commented that **even with a parachute, very few models can meet the KE limitation**. F3322-18 cited in fn. 54. |
| **la Cour-Harbo (2017)**, *Mass threshold for "harmless" drones*, IJMAV 9(2) 77–92, [10.1177/1756829317691991](https://doi.org/10.1177/1756829317691991) | 3 / B | **The origin of 250 g as a defended figure** — the mass below which expected fatality rate is equivalent to manned aviation. |
| Arterburn, Ewing, Prabhu, Zhu & Francis (2017), *FAA UAS COE Task A4: UAS Ground Collision Severity Evaluation*, ASSURE/UAH | 3 / B | Traces **11 ft-lb** to **RCC Standard 321-07** and AFSPCMAN 91-710 as an inert-debris critical-injury threshold ("very conservative"); NAVAIR's competing **15 ft-lb** skull-fracture threshold from a cadaver study (Raymond et al., J. Biomech. 42:2479–2485, 2009). §5.5 warns ballistic inert-mass models are a poor proxy — "UAS platforms do not typically break up into small 2 lbs pieces with purely ballistic trajectories." |
| Campolettano et al. (2017), *Ranges of injury risk associated with impact from UAS*, Ann. Biomed. Eng. 45(12) 2733–2741, [10.1007/s10439-017-1921-6](https://doi.org/10.1007/s10439-017-1921-6) | 2 / A | 1.2–11 kg; max AIS 3+ risk 11.6 % in live flight tests, >50 % in some falling-impact tests. The basis for EASA's lethality estimate. |

**The critical correction.** Per the rule's own ASSURE data, a Phantom 3 must
reach **~130 ft-lb** pre-impact KE to produce HIC15 injury equivalent to a rigid
object at 11 ft-lb, and **~220 ft-lb** to match 25 ft-lb. Never quote 11/25 ft-lb
as drone kinetic-energy caps.

## 5. Alternatives at low altitude — where our mechanism belongs

| Ref | A/E | Key finding |
| --- | --- | --- |
| *Development of chemical reaction airbag safety system for multi-rotor UAV…*, Drones (2026) 10(3) 199, [10.3390/drones10030199](https://doi.org/10.3390/drones10030199) | 3 / B | Chemically inflated airbag, faster than compressed gas: **impact force 4638.8 N → 1562.76 N (≈66 % reduction)**, inflation "within a fraction of a second". ⚠️ **Author list not resolved — get it before citing.** |
| **Mili, Catar, Gérard, Tabiai & St-Onge (2026)**, *From bench to flight: translating drone impact tests into operational safety limits*, arXiv [2602.05922](https://arxiv.org/abs/2602.05922) | 2 / B | Drones launched at 3–4 m/s into instrumented walls, 1000 fps. **410 g DJI Avata: 230.4 ± 27.3 N peak; 250 g bamboo Cognifly: 84.4 ± 3.3 N — mass dominates.** No configuration met the 65 N face-impact threshold (ISO/TS 15066). **Compliant TPU joints cut peak force ~13 % but increased rebound energy** — an explicit compliance-vs-restitution trade-off. Oblique 45° impacts raised peak force 27 %. **Directly relevant to arguing guards as energy absorbers.** |
| *Origami and kirigami structure for impact energy absorption: its application to drone guards*, Sensors (2023) 23(4) 2150, [10.3390/s23042150](https://doi.org/10.3390/s23042150) | 2 / B | SMA-actuated deformable guards: **78.2 % reduction in maximum impact force at side impact**. |
| de la Torre-Vanegas, Soriano-Garcia, Becerra & Mercado-Ravell (2025), *Vision-based risk aware emergency landing for UAVs in complex urban environments*, arXiv [2505.20423](https://arxiv.org/abs/2505.20423) | 2 / B | Pixel-level semantic risk map → landing-zone selection with **altitude-dependent safety thresholds**; >90 % success. Best hit for emergency landing site selection — a possible future action in our policy. |

## 6. Required changes to the repo

1. **Re-specify the parachute action** (OQ-010): either model inflation explicitly
   (drag ramping over the deployment interval, not a step) or raise the effective
   deployment altitude to match the 10–15 m measured floor. Re-run the sweep. The
   current "parachute is the only nonzero action for two-adjacent" conclusion is
   *directionally* supported (it is the only action that works at all) but its
   quantitative cells at 3 m and 6 m are not credible.
2. **Replace the altitude argument with the mass argument** for a sub-250 g
   parachute, and cite the lightest COTS mass plus the Category 1 point.
3. **Restate `design.md` §1**: "parachute recovery of small UAS is established"
   is true for ≥900 g airframes with a 10–15 m floor; it is **not** established at
   sub-250 g, where no product or study was found.
4. **Add the guard-as-absorber literature** to justify the mechanism at all —
   Mili et al. (2026) and the kirigami guard paper are the only measured
   energy-absorption numbers available, and they support a *force-reduction*
   framing rather than our current impact-speed-tolerance framing.

## Unverified — do not cite until confirmed

- "F3322 requires 45 test flights; -24a raises it to 49" — consistent across
  multiple vendor sources, but **Section 6 of the standard was never seen**
  (preview cuts off at §5.4). Buy the standard before citing a test count.
- Any descent-rate or impact-energy **pass/fail threshold** in F3322 — §3.1.13
  gives the formula; no threshold value was found. Inference, not verification.
- ParaZero's 11 m / 15.9 m / 3.7 m/s (search-engine extract, not the page).
- "Minimum deployment altitude 20–50 m / 25–40 m / 15–30 m" — vendor marketing
  and SEO content only. **Do not cite.**
- Authors of the Drones 10(3) 199 airbag paper.
- Full text of la Cour-Harbo (2017) — verified by DOI/abstract only (403).
- ASSURE Ground Collision Severity Phase II Annex A p.113 (cited by EASA for the
  11 kg @ 10 m/s → 25 % lethality figure) — not opened.
- **Edition trap:** MDA is §3.1.24 in F3322-18 but §3.1.27 in F3322-22, and the
  EASA MoC still points at the -18 numbering. Cite the edition actually read.
