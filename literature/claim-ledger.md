# Claim ledger

Every load-bearing claim this repository currently makes, the external evidence
for or against it, and what must change. Claims are quoted or paraphrased from
the committed specs. **A claim with no ledger entry should not be in the repo.**

Confidence is about *our* claim after checking the literature, not about the
cited papers.

---

## A. Novelty and framing

### A1. "Controlled flight after one- and two-rotor loss via thrust reallocation is established" (`design.md` §1)
- **Support:** Mueller & D'Andrea (2014, 2016) A; Sun et al. T-RO (2021) A; Lanzon et al. (2014) C.
- **Understated.** Ke, Cai & Quan (T-RO 2023, A) demonstrate **one, two adjacent, two opposite and three** rotor failures with a *single non-switching passive controller* in **outdoor flight**. Our two_adjacent class is not open in the controls sense.
- **Action:** widen the "known" list; cite Ke et al. and Sun et al. (2020). **Confidence: high** that we were understating prior art.

### A2. "Open: a policy over the post-failure state that selects among actions, with a quantified survivable set that includes recovery delay and authority loss"
- **Support (narrowed but survives):** no verified work maps (h, v_z, ω, delay) to a *choice among actions*, nor publishes a recoverable set *as a function of detection delay*. Closest: Mao et al. (RA-L 2024, B) — a two-action threshold on damage severity only.
- **Contested:** Siotia et al. (Sci. Rep. 2026, B/C) claim in print that the field lacks "an integrated framework that … dynamically transitions between active stabilization and passive descent using altitude-aware decision logic."
- **Nearest method precedents:** Sun & de Visser (2019, B) Monte-Carlo quadrotor safe envelope — same HJ-doesn't-scale reasoning, binary labels, nominal conditions; Yin et al. (2019, A) probabilistic envelope, fixed-wing; Sun et al. (2020, B) post-failure MC recovery, no set estimate.
- **Action:** rewrite §1 to the narrowed wording in `novelty-and-gaps.md`, cite Siotia et al. and state the difference. **Confidence: moderate** — survives, but only as worded there.

### A3. "The mechanism's spin-aware / primary-axis follow-on is our next controls step" (`design-a2.md` §4)
- **Contradicted as *invention*:** the primary-axis relaxed-hover controller is Mueller & D'Andrea's and is **patented** (US 9,856,016 B2 + continuations).
- **Action:** describe A2-follow-on as *adopting* a known controller, with citations. **Confidence: high.**

---

## B. The landing criterion

### B1. "Impact ≤2.0 m/s and tilt ≤30° (bare); ≤2.5 m/s and ≤60° (guarded)" (`design.md` §5, PREREGISTERED-ASSUMED)
- **Cannot rest on injury data:** 165 g at 3 m/s = **0.74 J**; most conservative published yardstick **11 ft-lb = 14.9 J**, itself a *rigid-object equivalence* a frangible airframe clears by a further ~10× (FAA: Phantom 3 needs 130 ft-lb to match). Non-binding by ~27× before frangibility. (A4 2017 A; FAA 2021 A; Svatý et al. 2025 A.)
- **Real anchor for the speed band:** 14 CFR 27.725 (**2.55 m/s**), 27.727 (**3.12 m/s**), 29.725 (**2.0 m/s**), 25.473 (**3.05 / 1.83 m/s**) — Evidence A, binding text, **by analogy** from a different vehicle class and scale.
- **The tilt limit has no published basis at all.** Nearest precedent (Apollo LM gear) is a *coupled envelope*, not a scalar.
- **Action:** re-scope to *vehicle survival*; cite 27.725/27.727 as a labelled analogy; derive tilt from a tip-over calculation on our guard geometry; keep the injury arithmetic as a bounding argument only. **Confidence: high** that the current justification is wrong-footed, **high** that the numeric band is defensible once re-anchored.

### B2. "The guard absorbs energy and tolerates attitude" — `GUARDED_CRITERION` relaxation 2.0 → 2.5 m/s, 30° → 60°
- **No measured support for a speed-tolerance multiplier.** The only measured guard evidence: A4 §4.10 — a stock blade guard prevents skin laceration to ≈1.07 m/s (vs 0.3 m/s unguarded) and **then fails structurally**; Mili et al. (2026, B) — compliant structures cut peak force ~13 % but **increase rebound energy**; kirigami guards −78.2 % peak force at side impact (B).
- **Action:** reframe the guard as *laceration prevention and force reduction with a known failure point*. Flag the 2.5 m/s / 60° relaxation as the unsupported EST it is (OQ-010). **Confidence: high.**

### B3. "Lateral impact velocity is excluded (declared limitation)" (`design.md` §5)
- **Contradicted as a safe simplification:** the literature's criteria are coupled envelopes including horizontal velocity; Mili et al. find **oblique 45° impacts raise peak force 27 %**. For a release-recovery vehicle the tilted, translating corner *is* the design case.
- **Action:** keep the exclusion for now but re-classify from "declared limitation" to "known-wrong simplification, prioritised for removal". **Confidence: high.**

---

## C. The parachute action

### C1. "v_t = 1.8 m/s, deploy 0.8 s" and the resulting per-cell numbers
- **Deployment time supported:** Siotia et al. (2026, A) measure exactly 0.8 s.
- **Terminal speed and altitude floor contradicted:** measured floors are **10–15 m** (2 kg: 40 % survivability at 10 m, "effective" at 15 m, complete at 22–23 m; 900 g Mavic-class: **11 m average, 15.9 m worst-case** altitude loss to full canopy). A4 separately states **18.0 ft/s = 5.49 m/s** is the lowest *reliable* parachute descent rate — 3× our modelled 1.8 m/s.
- **Root cause in our model:** we treat deployment as a delay followed by an instantly effective drag device. The **inflation transient is missing**, and that is exactly what kills low-altitude deployment.
- **Action (OQ-010):** model inflation explicitly or raise the effective floor; re-run. The qualitative conclusion ("only nonzero action for two_adjacent") is directionally safe; the 3 m and 6 m cells are not credible. **Confidence: high.**

### C2. "Parachute recovery of small UAS is established" (`design.md` §1)
- **True for ≥900 g**; **not established at sub-250 g** — no product, standard clause or study found. Lightest COTS system ≈185 g = **74 % of a 250 g budget** before canopy, bridle, ejector and trigger.
- **Action:** replace the altitude argument with the **mass** argument, and note that a sub-250 g aircraft is already Part 107 Category 1 — ParaZero and Indemnis told the FAA on record that even with a parachute "very few unmanned aircraft models will be capable of meeting the applicable kinetic energy limitation." **Confidence: high.**

---

## D. Allocation and control

### D1. "Cascaded torque-priority allocation" (`failure_allocation.py`, `design-a2.md` §2)
- **It has a name:** **redistributed pseudo-inverse** (Virnig & Bodden 1994, B), cascaded-generalized-inverse lineage (Bordignon & Durham 1995, A).
- **Its quality is bounded by literature:** Härkegård (2002, B) — RPI methods "only deliver approximate and sometimes unreliable solutions"; active-set reaches the optimum at comparable runtime. QP allocation redistributes automatically (Härkegård 2004, A).
- **Attitude priority is supported:** Faessler et al. (2017, A) prioritise roll/pitch, then collective, then yaw — exactly our ordering; PX4 airmode is the deployed form.
- **Action:** rename and cite; justify on compute cost; record active-set/SLS/QP as the honest upgrade path. **Confidence: high.**

### D2. `TORQUE_PRIORITY = 10.0` weighting a newton residual against a newton-metre residual
- **No citable basis exists.** Literature offers: weight-as-tuning-knob (Johansen & Fossen 2013 A; Härkegård 2004 A), normalise-to-actuator-limits (Cuniato et al. 2024, C), or the warning that aggressive weighting **degrades conditioning** and is why SLS *stages* objectives instead (Hafner et al. 2025, A).
- **Action:** normalise both residuals by reference force/moment scales, or stage them; re-run the paired comparison. Whichever we choose is **a contribution to document, not a citation to borrow.** Already flagged as F06. **Confidence: high.**

### D3. Detection delay cells of 0.11 s and 0.30 s
- **0.11 s is inside the published envelope** (20–130 ms; KF residual detector 30–130 ms over 26 real propeller ejections, C; L1 multiple-model 45 ms, A; motor-speed FDD 28 ms / takeoff threshold 20 ms / thrust-loss 184 ms, C).
- **0.30 s is beyond any published detection latency** — a deliberate stress case, not a representative one.
- **Unmodelled coupling:** detection delay (20–184 ms) and brushed motor lag (**≈72 ms**, Crazyflie 2.1, B) are the same order; we treat spool-up and detection as independent additive latencies.
- **Our framing is ahead of the literature:** no source reports detection latency as a *distribution*. Claim the framing, don't cite a number as if it were one. **Confidence: high.**

---

## E. Statistics

### E1. "Mechanism lower bound vs reallocation upper bound" (`kill_criterion`)
- **Sidedness mislabelled:** a 95 % lower combined with a 95 % upper is a **90 % central** construction (Brown, Cai & DasGupta 2001 A; Meeker et al. 2017 B; ICH E9 convention B). Keep the preregistered rule; **relabel it**.
- **Design error:** the comparison should be **paired**. Our seeds include the action index, so mechanism and realloc draw *different* vehicles. Correct analysis is McNemar (mid-p preferred; Fagerland et al. 2013 A) with Tango's (1998, A) score interval for the paired risk difference.
- **Action:** pair the draws (already in the W05 plan — now a **correctness requirement**, not an optimisation), then re-analyse. **Confidence: high.**

### E2. "H-A2.1 not supported" / "the mechanism did not beat the baseline"
- **Not equivalence.** Altman & Bland (1995, A): absence of evidence is not evidence of absence. Overlapping CP intervals are especially weak since conservatism widens both.
- **Needs a preregistered margin δ** to become testable (Piaggio et al. 2012 A; Schuirmann 1987 A; Lakens 2017 A; Tango 1998 A for paired binary).
- **Action:** report exactly one of superiority / non-inferiority (δ named) / **inconclusive with achieved n and detectable effect size**. Our current statements are the third. **Confidence: high.**

### E3. Using Clopper–Pearson at all
- **Criticised but defensible.** Brown, Cai & DasGupta (2001, A) call it "wastefully conservative"; Agresti & Coull (1998, A) prefer approximate intervals; Thulin (2014, A) quantifies the sample-size cost.
- **Our direction is favourable:** a conservative *lower* bound on P(survivable landing) errs toward understating survivability, and our grid lands near p = 0 and p = 1 constantly, where Wald degenerates. The rule of three (Hanley & Lippman-Hand 1983, A) *is* our zero-count bound.
- **Gap:** per-cell 95 % intervals over K cells are **not** 95 % simultaneous; our specs say nothing. Preregister "per-cell, no simultaneity claimed" or adjust. **Confidence: high.**

### E4. Per-cell Monte Carlo instead of an exact reachable set
- **Supported:** HJ reachability is capped at ~4–5 states by the curse of dimensionality (Bansal et al. 2017, B); Sun & de Visser (2019, B) make exactly this substitution for a quadrotor safe envelope. Kalra & Paddock (2016, B) for why per-cell resolvable bounds beat a global trial count.
- **Action:** cite these as the method's justification. **Confidence: high.**

---

## F. Measurement and bench

### F1. "A tare removes an offset from the data, not physical load" / "ADC internal calibration is not calibration in newtons"
- **Supported verbatim:** VIM 2.39 Note 2 — calibration must not be confused with *adjustment*, "often mistakenly called 'self-calibration'". **Confidence: high.** No change needed; add the citation.

### F2. Whole-drone restrained thrust test on a bench
- **At risk from ground effect:** whole-vehicle thrust inflation ≈**1.4× near z/R ≈ 1**, not settled until **z/R ≈ 5–6** (≈2.5–3 rotor diameters), due to the **fountain effect**; partial ground effect appears as a **moment** bias (Sanchez-Cuevas et al. 2017, A). NASA Ames left tunnel recirculation **explicitly unquantified** (2016, A).
- **Action:** specify clearance in rotor-diameter units in every direction incl. ceiling; **prove absence by a height/wall sweep** at fixed commanded RPM. That sweep would be a small genuine contribution. **Confidence: high.**

### F3. "Retain voltage as a covariate" for battery sag (R5.3)
- **Second-best.** Both authoritative benches (Deters et al. 2017 A; Russell et al. 2016 A) **eliminate** sag with a regulated supply and verify voltage independently. No published sag-correction guidance was found.
- **Action:** prefer a regulated supply; keep the covariate only for on-pack tests. **Confidence: high.**

### F4. Implicit assumption that guards are aerodynamically neutral
- **Contradicted:** guards increased Phantom 3 **vertical flat-plate drag area by 42 %** (A4, A). Properly designed shrouds give up to **+94 % thrust at equal power** at 16 cm rotor scale (Pereira 2008, A) — but **a guard is not a duct**.
- **Action:** measure the V995 with and without guards; import no literature number. This also affects the OQ-010 mechanism mass/inertia credit — if the guard is aerodynamically active, removing it changes thrust too. **Confidence: high.**

### F5. Thermal drift in the force chain
- **Non-trivial at our scale:** a professional balance showed **0.1–0.3 lb** end-of-run z-force drift correlated with temperature, corrected by a fitted per-channel linear term (Russell et al. 2016, A); mechanism is strain-gauge thermal output (Vishay TN-504-1, C).
- **Action:** bracket every run with a zero-load static point and **log bench temperature**; add creep/hysteresis/temperature measurement per OIML R 60-1 definitions as Type B components. **Confidence: high.**

---

## G. Platform (V995)

### G1. "Brushed motors inferred from two-wire leads" (`platform-capabilities.md`)
- **Consistent with literature scale:** Crazyflie 2.1 (27 g, brushed) motor time constant **≈0.072 s** (Eschmann et al. 2024, B) — the closest published analogue to a ~50 g brushed toy quad.
- **Action:** treat ≈70 ms as the EST motor lag for V995 modelling *if* brushed is confirmed; do not use brushless numbers. **Confidence: moderate** (analogue, not measurement).

### G2. Sub-250 g rotor-loss work is an open lane
- **Verified negative result:** no paper demonstrates rotor-loss FTC on a sub-250 g quadrotor. The reason is physical: post-failure spin rate rises as inertia falls; it already exceeds sensing limits at full scale (>20 rad/s blurs frame cameras, Sun et al. 2021 A; Yeom et al. 2024 B modify rotational drag mechanically to stay inside sensing constraints).
- **Action:** state as "no published flight demonstration at sub-250 g that we could find", never "no one has considered it". Note it corroborates our own gyro-limited envelope. **Confidence: high.**
