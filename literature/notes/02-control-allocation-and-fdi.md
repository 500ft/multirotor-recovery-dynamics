# 02 — Control allocation under failure/saturation, and fault detection

Repo artifacts this cluster governs: `Analysis/failure_allocation.py`,
the `spin_aware`/airmode logic in `Analysis/sim_release_recovery.py`, the
`delay` state coordinate in `docs/specs/survivable-set/design.md` §2.

## Headline finding for this repo

**Our allocator is a named, 30-year-old method, and the literature calls it
suboptimal.** `MotorAllocation.apply()` — pseudo-inverse solve, clamp the
saturated motors, drop their columns, re-solve the free ones with a priority
weighting — is the **redistributed pseudo-inverse (RPI)** of Virnig & Bodden
(1994), in the cascaded-generalized-inverse lineage of Bordignon & Durham
(1995). Härkegård (2002) states directly that RPI-type methods "only deliver
approximate and sometimes unreliable solutions" while an active-set solver
reaches the true optimum at comparable runtime.

Consequences, in order of importance:

1. `design-a2.md` §2 should name the method (RPI with attitude-priority
   reweighting), cite the 1994/1995 origin, and justify it on implementation
   cost — **not** present it as a repo invention. Action: amend the spec.
2. The honest upgrade path is an active-set / sequential-least-squares solver
   (Härkegård 2002, 2004; Hafner et al. 2025) or a one-shot QP where
   redistribution falls out automatically (Härkegård 2004). This is a concrete,
   citable alternative to "tune the allocator further".
3. `TORQUE_PRIORITY = 10.0` weights a newton residual against a newton-metre
   residual. No source prescribes a dimensional rule for this; see §3 below.

## 1. Allocation fundamentals

| Ref | Aboutness / Evidence | Why it matters here |
| --- | --- | --- |
| Johansen & Fossen (2013), *Control allocation — A survey*, Automatica 49(5) 1087–1103, [10.1016/j.automatica.2013.01.035](https://doi.org/10.1016/j.automatica.2013.01.035) | 3 / A | The canonical survey; legitimises the allocation layer and taxonomises pseudo-inverse, null-space, direct, LP, QP and dynamic methods. |
| Durham (1993), *Constrained control allocation*, JGCD 16(4) 717–725, [10.2514/3.21072](https://doi.org/10.2514/3.21072) | 3 / A | Origin of direct allocation and the **attainable moment set**: no generalized inverse reaches the whole attainable set once effectors are constrained. This is *why* a pseudo-inverse fails after rotor loss. |
| Bordignon & Durham (1995), *Closed-form solutions to constrained control allocation*, JGCD 18(5) 1000–1007, [10.2514/3.21497](https://doi.org/10.2514/3.21497) | 3 / A | Cascaded generalized inverse lineage — the family our `apply()` belongs to. |
| Virnig & Bodden (1994), *Multivariable control allocation and control law conditioning when control effectors limit*, AIAA GNC, [10.2514/6.1994-3609](https://doi.org/10.2514/6.1994-3609) | 3 / B | **The RPI original.** Cite this for our two-pass scheme. |
| Bodson (2002), *Evaluation of optimization methods for control allocation*, JGCD 25(4) 703–711, [10.2514/2.4937](https://doi.org/10.2514/2.4937) | 3 / A | LP/QP/fixed-point comparison; optimization-based allocation is real-time feasible. |
| Härkegård (2002), *Efficient active set algorithms for … aircraft control allocation*, IEEE CDC, [10.1109/CDC.2002.1184694](https://doi.org/10.1109/CDC.2002.1184694) | 3 / B | States RPI is approximate/unreliable; active set is optimal at similar cost. **The citation that bounds our method's quality claim.** |
| Härkegård (2004), *Dynamic control allocation using constrained quadratic programming*, JGCD 27(6) 1028–1034, [10.2514/1.11607](https://doi.org/10.2514/1.11607) | 3 / A | QP allocation redistributes automatically on saturation — no hand-rolled loop needed. |
| Kirchengast, Steinberger & Horn (2018), *Control allocation under actuator saturation: an experimental evaluation*, IFAC-PapersOnLine 51(25) 48–54, [10.1016/j.ifacol.2018.11.080](https://doi.org/10.1016/j.ifacol.2018.11.080) | 3 / B | Experimental comparison on a rig emulating **quadrotor rotational dynamics** in the multiple-active-constraint regime — the closest published benchmark to our case. |
| Hafner, Myschik & Holzapfel (2025), *Accelerating sequential least squares active set control allocation*, Control Eng. Practice 166, 106621, [10.1016/j.conengprac.2025.106621](https://doi.org/10.1016/j.conengprac.2025.106621) | 3 / A | Modern SLS-vs-WLS tradeoff and the weighting/conditioning hazard (§3). |
| Miller & Pei (2025), *A comparison of control allocation methods in the presence of parametric model uncertainty*, AIAA SciTech, NASA NTRS [20240014917](https://ntrs.nasa.gov/citations/20240014917) | 2 / C | Convex-optimization allocators outperform generalized inverses under effectiveness-matrix uncertainty — and a partially-failed rotor *is* that uncertainty (our `partial_authority` class). |

## 2. Multirotor-specific: attitude priority and rotor-loss allocation

| Ref | A/E | Why it matters here |
| --- | --- | --- |
| Faessler, Falanga & Scaramuzza (2017), *Thrust mixing, saturation, and body-rate control…*, IEEE RA-L 2(2) 476–482, [10.1109/LRA.2016.2640362](https://doi.org/10.1109/LRA.2016.2640362) | 3 / A | **Peer-reviewed anchor for attitude-priority desaturation**: roll/pitch first, then collective, then yaw. Our airmode reserve and `TORQUE_PRIORITY` implement this ordering. |
| Smeur, Höppener & de Wagter (2017), *Prioritized control allocation for quadrotors subject to saturation*, IMAV 2017, 37–43, [imavs.org/papers/2017/6.pdf](https://www.imavs.org/papers/2017/6.pdf) | 3 / B | Lexicographic/staged priority for INDI-controlled quadrotors. No DOI — cite by stable URL. |
| Mueller & D'Andrea (2016), *Relaxed hover solutions for multicopters*, IJRR 35(8) 873–889, [10.1177/0278364915596233](https://doi.org/10.1177/0278364915596233) | 3 / A | Post-rotor-loss equilibrium is a **spin about a body-fixed axis with yaw sacrificed** — the theoretical basis for our reduced-attitude allocation (yaw command dropped). |
| Sun, Sijbers, Wang & de Visser (2018), *High-speed flight of quadrotor despite loss of single rotor*, IEEE RA-L 3(4) 3201–3207, [10.1109/LRA.2018.2851028](https://doi.org/10.1109/LRA.2018.2851028) | 3 / A | Sensor-based reconfiguration reduces model dependence; flight-validated. |
| Sun, Wang, Chu & de Visser (2021), *Incremental nonlinear FTC of a quadrotor with complete loss of two opposing rotors*, IEEE T-RO 37(1) 116–130, [10.1109/TRO.2020.3010626](https://doi.org/10.1109/TRO.2020.3010626), arXiv [2002.07837](https://arxiv.org/abs/2002.07837) | 3 / A | **Our `two_opposite` class, solved and wind-tunnel validated.** Directly bounds what we may claim as open. |
| Lu & van Kampen (2015), *Active FTC for quadrotors subjected to a complete rotor failure*, IROS, [10.1109/IROS.2015.7354046](https://doi.org/10.1109/IROS.2015.7354046) | 3 / B | Canonical active FTC (detect → reconfigure); the architecture in which a detection delay exists at all. |
| Nan, Sun, Foehn & Scaramuzza (2022), *Nonlinear MPC for quadrotor fault-tolerant control*, IEEE RA-L 7(2) 5047–5054, [10.1109/LRA.2022.3154033](https://doi.org/10.1109/LRA.2022.3154033), arXiv [2109.12886](https://arxiv.org/abs/2109.12886) | 3 / A | NMPC folds allocation + constraints into one optimisation — "let the optimiser redistribute". |
| PX4, *Control Allocation (Mixing)*, [docs.px4.io](https://docs.px4.io/main/en/concept/control_allocation) | 3 / D | Deployed airmode: raise/lower total thrust to preserve roll/pitch authority; desaturation slides along a thrust-axis vector without changing angular acceleration. Grey lit, but it is what real vehicles run. |

## 3. The N vs N·m weighting problem — an open gap, not a citation

No source found prescribes a dimensional rule for weighting a force residual
against a moment residual. The literature offers three positions:

- **Weight as a tuning knob** (Johansen & Fossen 2013; Härkegård 2004) — a
  positive-definite weighting matrix, chosen by design, no consistency rule.
- **Normalise to actuator limits instead of tuning** — Cuniato et al. (2024),
  arXiv [2412.16107](https://arxiv.org/abs/2412.16107) (aboutness 2, evidence C),
  explicitly motivated by avoiding heuristic weight tuning: scale actuator
  ranges to [−1, 1] before allocating.
- **The weighting is numerically hazardous** — Hafner et al. (2025): strongly
  prioritising one objective by shrinking a weight degrades the condition number
  of the combined matrix (single-precision failures), which is why SLS *stages*
  objectives instead of weighting them against each other.

**Repo implication.** `TORQUE_PRIORITY = 10.0` is a unit-bound heuristic with no
citable basis, exactly as `review-2026-09-19.md` F06 already flagged. Either
normalise both residuals by reference force/moment scales (Cuniato-style) and
re-run the paired comparison, or stage the objectives (SLS). Whichever we pick is
a **contribution to document, not a citation to borrow.**

## 4. Fault detection and isolation — and what a detection delay really costs

| Ref | A/E | Why it matters here |
| --- | --- | --- |
| Fourlas & Karras (2021), *A survey on fault diagnosis and FTC methods for UAVs*, Machines 9(9) 197, [10.3390/machines9090197](https://doi.org/10.3390/machines9090197) | 3 / A | Best recent UAV FDD+FTC survey, organised by subsystem. |
| Zhang & Jiang (2008), *Bibliographical review on reconfigurable FTC systems*, Annual Reviews in Control 32(2) 229–252, [10.1016/j.arcontrol.2008.03.008](https://doi.org/10.1016/j.arcontrol.2008.03.008) | 2 / A | Passive vs active FTC taxonomy: **a detection delay exists only in active FTC.** Frames why delay is a state coordinate for us. |
| Avram, Zhang & Muse (2017), *Quadrotor actuator fault diagnosis and accommodation using nonlinear adaptive estimators*, IEEE T-CST 25(6) 2219–2226 | 3 / A | Detection estimator + isolation bank with adaptive thresholds; real-time experiments. *(DOI not captured — see unverified list.)* |
| Strack van Schijndel, Sun & de Visser (2021), *Fast fault detection on a quadrotor using onboard sensors and a Kalman filter approach*, arXiv [2102.06439](https://arxiv.org/abs/2102.06439) | 3 / C | KF residual detector over **26 real propeller ejections**; reports detection delays **30–130 ms**, no missed detections or false alarms. |
| Yang et al. (2026), *Failure detection and recovery … multiple model L₁ adaptive controller*, IEEE RA-L 11(1) 346–353, [10.1109/LRA.2025.3630964](https://doi.org/10.1109/LRA.2025.3630964) | 3 / A | Experimentally "fast detection within **0.045 seconds**". |
| Zhou et al. (2025), *Rotor-failure-aware quadrotors flight in unknown environments*, arXiv [2510.11306](https://arxiv.org/abs/2510.11306) | 3 / C | Per-mode latencies: motor-speed FDD **28 ms**; takeoff acceleration threshold **20 ms**; thrust-loss propeller estimation **184 ms**; propeller-strike test **within 27 ms**. |
| Eschmann, Albani & Loianno (2024), *Data-driven system identification of quadrotors subject to motor delays*, IROS, arXiv [2404.07837](https://arxiv.org/abs/2404.07837) | 3 / B | **Crazyflie 2.1 (27 g, brushed): motor time constant ≈ 0.072 s** (data-driven), ≈0.073 s from the manufacturer step response. The closest published analogue to our ~50 g brushed V995. |

### Published detection-latency envelope, and what it means for our cells

Roughly **20–130 ms** for complete motor/propeller failure: the fast end
(≈20–45 ms) needs RPM feedback or an aggressive angular-acceleration threshold;
the ≈100–184 ms end is thrust-loss/partial-degradation estimation from IMU
residuals alone.

- Our `delay = 0.11 s` cell sits **inside** the published envelope, near the
  IMU-only end. Defensible.
- Our `delay = 0.30 s` cell is **beyond any published detection latency**. It
  should be described as a deliberate stress case, not a representative one.
- Detection delay (20–184 ms) and brushed motor lag (≈72 ms) are the **same
  order**. They are not separable in a recovery budget, and our model currently
  treats spool-up and detection as independent additive latencies. Worth stating
  as a limitation.
- No source reports detection latency as a **distribution** over failure
  conditions. Our treatment of delay as a swept state variable is ahead of what
  is published — that is a framing to claim, carefully, not a number to cite.

## Unverified — do not cite until confirmed

- Avram, Zhang & Muse (2017) DOI string (journal/volume/pages confirmed).
- JGCD *Attainable control set optimization for fault-tolerant multirotor design
  and control allocation*, [10.2514/1.G009745](https://arc.aiaa.org/doi/10.2514/1.G009745)
  — title/DOI/journal confirmed, **authors and year not**.
- CGI flown on the X-35B (secondary source only).
- The "[28, 132] ms, 95% confidence bounds, Bebop 2, 500 Hz" phrasing of the
  Strack van Schijndel result — the fetched abstract says "30 to 130 ms".
- Motor time constants "17/28/40/60/80 ms" for 3-inch quadrotors — could not be
  confirmed at source.
- "~0.1 s FDD observation delay" attributed to Chen et al., arXiv 2503.02649 —
  paper exists, figure not found in the abstract.
