# 01 — Fault-tolerant control after rotor loss

Repo artifacts this cluster governs: `docs/specs/survivable-set/design.md` §1
(novelty claim) and §3 (failure classes); `design-a2.md` §4, §6; the whole
premise that a *policy over actions* is the open contribution.

## Headline findings for this repo

1. **More is established than `design.md` §1 admits.** It currently concedes
   "controlled flight after one- and two-rotor loss via thrust reallocation".
   The literature has gone further: **all four of our failure classes** —
   one, two adjacent, two opposite, three — are solved by a *single
   non-switching passive controller* with **outdoor flight validation**
   (Ke, Cai & Quan, T-RO 2023). Our `two_adjacent` class is not an open
   problem in the controls sense; it is a hard case with a thin evidence base.
2. **Recovery from arbitrary tumbling attitude/rate after rotor loss is solved
   and flight-demonstrated** — Sun et al. (ICRA 2020), validated by Monte Carlo
   over randomised initial conditions *plus* real flight ("casually tossed into
   the air"). This is the closest substantive precedent to our study and must be
   the related-work anchor, not a footnote.
3. **The primary-axis spinning failsafe is patented** (US 9,856,016 B2, Mueller,
   granted 2018, with a continuation family). The repo must not present "spin
   about a body-fixed primary axis and tilt it" as its own idea.
4. **Someone else is already staking a claim adjacent to ours.** Siotia et al.
   (Sci. Rep. 2026) assert in print that the field lacks "an integrated framework
   that explicitly detects unrecoverable loss-of-control states and dynamically
   transitions between active stabilization and passive descent using
   altitude-aware decision logic." We must cite them and state how we differ.
5. **Sub-250 g: partial degradation is NOT open** — Çintaş & Özyer (2026)
   demonstrate it in real flight on a 30.6 g Crazyflie. Complete rotor loss below
   250 g remains a *search-bounded* absence, not a confirmed gap (§6).
6. **A two-action switching threshold already exists** for propeller damage
   (Mao et al., RA-L 2024) — cite before claiming the policy idea is unprecedented.

## 1. Canonical results

| Ref | A/E | Key finding |
| --- | --- | --- |
| Mueller & D'Andrea (2014), *Stability and control of a quadrocopter despite the complete loss of one, two, or three propellers*, ICRA, [10.1109/ICRA.2014.6906588](https://doi.org/10.1109/ICRA.2014.6906588) | 3 / A | Periodic solutions maintaining height after losing one, **two opposing**, or three propellers; vehicle spins about a body-fixed **primary axis**, tilt gives translational control; LTI reduced-attitude linearisation enables cascaded design. One- and two-opposing validated **in experiment**; three-propeller **in nonlinear simulation only**. **Does not treat two adjacent.** |
| Mueller & D'Andrea (2016), *Relaxed hover solutions for multicopters*, IJRR 35(8), [10.1177/0278364915596233](https://doi.org/10.1177/0278364915596233) | 3 / A–B | Defines "relaxed hover"; post-failure angular velocity is zero or parallel to gravity. Experiment validates single and two-opposing; **simulation** validates two-adjacent and three. This is the paper that closes our `two_adjacent` case — in sim. |
| **US 9,856,016 B2**, *Controlled flight of a multicopter experiencing a failure affecting an effector*, Mueller, granted 2018-01-02 (family: 10,308,349; 10,562,611; 10,946,950; 11,591,071) | 3 / — | **Prior art / IP.** The primary-axis failsafe is patented. Relevant to any claim of mechanism or method novelty. |
| Lanzon, Freddi & Longhi (2014), *Flight control of a quadrotor vehicle subsequent to a rotor failure*, JGCD, [10.2514/1.59869](https://doi.org/10.2514/1.59869) | 3 / C | Robust feedback linearisation that **sacrifices yaw**; roll/pitch held at zero with constant vertical angular rate. Simulation. *(Note author order — often miscited Freddi-first.)* |
| Freddi, Lanzon & Longhi (2011), *A feedback linearization approach to fault tolerance in quadrotor vehicles*, IFAC WC, [10.3182/20110828-6-IT-1002.02016](https://doi.org/10.3182/20110828-6-IT-1002.02016) | 3 / C | Earlier one-rotor-out feedback linearisation. Simulation. |
| Lippiello, Ruggiero & Serra (2014), *Emergency landing for a quadrotor in case of a propeller failure: a backstepping approach*, IROS, [10.1109/IROS.2014.6943242](https://doi.org/10.1109/IROS.2014.6943242); PID companion, SSRR, [10.1109/SSRR.2014.7017647](https://doi.org/10.1109/SSRR.2014.7017647) | 3 / C | **A distinct action from ours**: deliberately shut down the rotor *opposite* the failed one → bi-rotor → track a planned emergency-landing trajectory. Simulation. A candidate 4th action for our policy. |
| **Sun, Wang, Chu & de Visser (2021)**, *Incremental nonlinear FTC of a quadrotor with complete loss of two opposing rotors*, T-RO 37(1), [10.1109/TRO.2020.3010626](https://doi.org/10.1109/TRO.2020.3010626), arXiv [2002.07837](https://arxiv.org/abs/2002.07837) | 3 / A–B | INDI FTC for **two opposing rotors**, flight-validated **>8 m/s** in a wind tunnel under wind disturbance; generalises to single-failure and nominal. Strongest existing two-opposite result. |
| Sun, Sijbers, Wang & de Visser (2018), *High-speed flight of quadrotor despite loss of single rotor*, RA-L 3(4), [10.1109/LRA.2018.2851028](https://doi.org/10.1109/LRA.2018.2851028) | 3 / A–B | One rotor **physically removed**, free flight >9 m/s in the Open Jet Facility; spin-induced aerodynamic effects analysed. |
| **Sun, Baert, Strack van Schijndel & de Visser (2020)**, *Upset recovery control for quadrotors subjected to a complete rotor failure from large initial disturbances*, ICRA, [10.1109/ICRA40945.2020.9197239](https://doi.org/10.1109/ICRA40945.2020.9197239), arXiv [2002.09425](https://arxiv.org/abs/2002.09425) | 3 / A–B | **The single most relevant paper to this repo.** Cascaded position/altitude + almost-globally convergent attitude control + **QP allocation with a derived undesirable-angular-velocity constraint**. Monte Carlo over arbitrary initial attitude/rate **plus real flight**. |
| **Ke, Cai & Quan (2023)**, *Uniform passive fault-tolerant control of a quadcopter with one, two, or three rotor failure*, T-RO, [10.1109/TRO.2023.3297048](https://doi.org/10.1109/TRO.2023.3297048), arXiv [2211.12972](https://arxiv.org/abs/2211.12972) | 3 / A | **One controller, one parameter set, no fault information, no switching**, covering fault-free → one → two adjacent → two opposite → three. **Outdoor flight, GPS + onboard sensors only.** Current high-water mark for breadth. ⚠️ arXiv v2 comment flags "important errors… need to be corrected" — cite the T-RO version and note it. |
| Sun, Cioffi, de Visser & Scaramuzza (2021), *Autonomous quadrotor flight despite rotor failure with onboard vision sensors: frames vs. events*, RA-L, [10.1109/LRA.2020.3048875](https://doi.org/10.1109/LRA.2020.3048875) | 3 / A–B | Onboard vision through the post-failure spin. **Yaw rate exceeds 20 rad/s** and blurs frame cameras — a hard sensing constraint, and ours is a *measurement-limited* envelope too (`gyro_limit_rad_s`). |
| Nan, Sun, Foehn & Scaramuzza (2022), *Nonlinear MPC for quadrotor FTC*, RA-L 7(2), [10.1109/LRA.2022.3154033](https://doi.org/10.1109/LRA.2022.3154033) | 3 / A–B | NMPC over full nonlinear damaged dynamics with per-rotor thrust constraints; real flight. |
| Narasimhan, de Visser, de Wagter & Rischmueller (2020), *Fault tolerant control of multirotor UAV for piloted outdoor flights*, arXiv [2011.00481](https://arxiv.org/abs/2011.00481) | 3 / D | Frames recoverability as an **Attainable Virtual Control Set** property rather than controller tuning — conceptually close to our allocation-limited framing. |
| Yeom, Balu T M, Li & Loianno (2024), *Experimental system design of an active fault-tolerant quadrotor*, ICUAS, arXiv [2404.06340](https://arxiv.org/abs/2404.06340) | 3 / B | Transitions to FTC **by surrendering yaw**, and modifies **rotational drag mechanically** so the post-failure spin stays inside sensing limits. Directly relevant to our EST `A2_YAW_DRAG_N_M_S2` and the gyro-range coherence test. |
| Yeom, Li & Loianno (2023), *Geometric FTC of quadrotors in case of rotor failures: an attitude based comparative study*, IROS, arXiv [2306.13522](https://arxiv.org/abs/2306.13522) | 3 / C | Compares attitude-error metrics for FTC on SO(3)×R³. |
| Beyer, Steen & Hecker (2023), *Incremental passive FTC for quadrotors subjected to complete rotor failures*, JGCD, [10.2514/1.G007475](https://doi.org/10.2514/1.G007475) | 3 / ? | Exists; **validation modality unverified**. |
| Lu & van Kampen (2015), *Active FTC for quadrotors subjected to a complete rotor failure*, IROS, [10.1109/IROS.2015.7354046](https://doi.org/10.1109/IROS.2015.7354046) | 3 / ? | Canonical active FTC; **modality unverified — do not grade until read.** |

## 2. Reduced attitude / primary axis / yaw sacrifice — closed topic

Established with no open theoretical gap: Mueller & D'Andrea (2014, 2016) + the
patent family; explicit yaw sacrifice in Lanzon et al. (2014) and Yeom et al.
(2024); control-authority-set framing in Narasimhan et al. (2020); attitude-metric
choice in Yeom et al. (2023).

**Consequence for `design-a2.md` §4.** Our registered next step — "a genuinely
spin-locked rotor-out controller (primary-axis / reduced-attitude in the spun
frame)" — is *implementing a known controller*, not inventing one. That is a
perfectly good work item; it must be described as adoption, with these citations.

Adjacent curiosity: Parkala & Kandath (2026), *Spinning quadrotor: hover thrust
augmentation with passive lifting surfaces*, ICUAS, [10.1109/ICUAS69441.2026.11598692](https://doi.org/10.1109/ICUAS69441.2026.11598692),
arXiv [2608.23163](https://arxiv.org/abs/2608.23163) (1/C–D) — deliberate sustained
yaw as a *design* choice, preliminary hardware showing **22% reduction in thrust
required**. Useful if we ever argue spinning is not purely a penalty.

## 3. Partial loss of effectiveness vs complete failure

| Ref | A/E | Key finding |
| --- | --- | --- |
| Du, Quan, Yang & Cai (2015), *Controllability analysis for multirotor helicopter rotor degradation and failure*, JGCD, [10.2514/1.G000731](https://doi.org/10.2514/1.G000731) | 2 / C | **The theoretical anchor for our `partial_authority` class.** Classical LTI controllability is *insufficient* under positive/bounded inputs; introduces an available-control-authority index and a necessary-and-sufficient condition. |
| Du, Quan & Cai (2015), *Controllability analysis and degraded control for a class of hexacopters subject to rotor failures*, JIRS, [10.1007/s10846-014-0103-0](https://doi.org/10.1007/s10846-014-0103-0) | 2 / C | Companion, hexacopter. |
| **Mao, Yeom, Nair & Loianno (2024)**, *From propeller damage estimation and adaptation to fault tolerant control*, RA-L, [10.1109/LRA.2024.3380923](https://doi.org/10.1109/LRA.2024.3380923), arXiv [2310.13091](https://arxiv.org/abs/2310.13091) | 3 / B | **Closest published work to an action-selection policy.** L1 adaptive compensation for single/dual propeller damage with a **seamless transition to FTC once damage is severe**, and the authors *experimentally identify the conditions under which adaptive remains preferable over FTC*. A two-action switching threshold, derived from experiment. |
| Ahmadi, Asadi, Nabavi-Chashmi & Tutsoy (2023), *Modified adaptive discrete-time INDI for quad-rotors in the presence of motor faults*, MSSP, [10.1016/j.ymssp.2022.109989](https://doi.org/10.1016/j.ymssp.2022.109989) | 2 / C | Motor-fault INDI. |
| Wang, Sun, van Kampen & Chu (2019), *Quadrotor FTC incremental sliding mode control…*, AST, [10.1016/j.ast.2019.03.001](https://doi.org/10.1016/j.ast.2019.03.001) | 2–3 / ? | Modality unverified. |

## 4. Upset recovery, detection delay, height loss

- **Sun et al. ICRA 2020** (above) — the reference for "arbitrary initial
  orientation and angular velocity + one rotor gone".
- Tzoumanikas, Yan & Leutenegger (2020), *Nonlinear MPC with motor failure
  identification and recovery*, ICRA, [10.1109/ICRA40945.2020.9196690](https://doi.org/10.1109/ICRA40945.2020.9196690),
  arXiv [2002.06598](https://arxiv.org/abs/2002.06598) — aboutness 2 (**hexacopter**,
  which keeps full controllability after one loss). Verified numbers: EKF
  identification at 400 Hz, **failure identified and failsafe triggered within
  0.18 s**, **maximum height loss 0.60 m**. Best-verified delay/height pair found —
  but a *floor*, not a quad number.
- Zhao et al. (2026), *Agile fall recovery for quadrotors with bidirectional
  thrust via RL*, arXiv [2606.16513](https://arxiv.org/abs/2606.16513) — 2/D,
  recovery from arbitrary *ground* attitude, zero-shot sim-to-real claimed.
- **Siotia, Shankar, Nair & Nair (2026)**, *Enhancing UAV survivability through
  real-time stall detection and parachute assisted recovery*, Scientific Reports,
  [10.1038/s41598-026-47045-0](https://doi.org/10.1038/s41598-026-47045-0) — 2/B–C,
  HIL only. See cluster 03 for its altitude numbers. ⚠️ **Contested gap** — see
  `../novelty-and-gaps.md`.

## 5. Learning-based

- Sharma, Poddar & Sujit (2021), arXiv [2109.10488](https://arxiv.org/abs/2109.10488)
  — 3/C–D, SAC for hover/landing/path-following after single-rotor loss, custom
  simulator only.
- Chen, Zhao, Liu, Li & Lou (2025), *Learning-based passive FTC of a quadrotor
  with rotor failure*, IROS, [10.1109/IROS60139.2025.11245951](https://doi.org/10.1109/IROS60139.2025.11245951)
  — 3/?, a **Selector-Controller** network folding detection and control into one
  policy across fault-free → partial → complete. **The learned analogue of a
  recovery-action selector — check carefully before claiming novelty.**

## 6. Sub-250 g: a counterexample exists, for a *different* failure mode

**Amended 2026-09-24 (critique C02), and the amendment matters.**

**Çintaş & Özyer (2026)**, *A robust fault-tolerant control algorithm for
GPS-denied mini quadrotors using PID-TinyMPC and visual-inertial odometry*,
Control Engineering Practice 169:106779,
[10.1016/j.conengprac.2026.106779](https://doi.org/10.1016/j.conengprac.2026.106779)
— aboutness 3 for `partial_authority`, 1 for complete loss; evidence **B**
(real indoor flight). **Crazyflie 2.1, 30.6 g** including a 3.6 g FPV camera;
onboard IMU/barometer at 100 Hz, monocular VIO at 30 Hz.

**It handles partial rotor-speed degradation, not complete rotor loss**, and says
so: it cites Mueller & D'Andrea and Sun et al. for complete loss and frames its
own gap as *"performance degradation (rotor speed reduction) situations"*.
Contribution (1) reads *"even under partial rotor speed reduction or failure"*.
The degradation magnitude is in the paywalled body and was not read; the abstract
was not retrievable, so quotes come from the publisher-served Introduction,
Contributions, Experiment setup and Conclusion.

**Two consequences for us:**

1. **Our `partial_authority` class now has a sub-35 g real-flight precedent.**
   That class is no longer an empty lane — it is the one failure class where
   small-scale FTC has been demonstrated in flight. Cite this before describing
   any partial-degradation result as unprecedented at this scale.
2. **The complete-loss statement survives, narrowed and search-bounded:** *we
   found no published demonstration of recovery from complete rotor loss on a
   sub-250 g multirotor.* A dedicated verified pass was not completed, so treat
   this as an open question, **not** a confirmed gap. Canonical complete-loss
   demonstrations remain ~0.4–1.5 kg platforms.

**Corrected 2026-09-24 (critique C07).** This note previously argued that
post-failure spin rate rises as inertia falls. That is wrong for the *terminal*
spin. For a single-axis model `Izz ṙ = τ_res − c₁r − c₂|r|r`, the equilibrium
satisfies `τ_res = c₁r + c₂|r|r` — **`Izz` cancels**. Inertia sets how fast the
spin builds (the transient), not where it settles. A smaller aircraft therefore
does *not* necessarily spin faster at equilibrium; residual reaction torque,
rotational drag, geometry and thrust all scale together and must be scaled
together before any such claim is made.

What survives, and is citable: high post-failure spin is a demonstrated *sensing*
problem at full scale (>20 rad/s blurring frame cameras, Sun et al. 2021; Yeom
et al. 2024 deliberately modify rotational drag to hold the spin inside sensing
constraints). Whether it is worse at sub-250 g is **an open question requiring the
scaling to be worked through or measured**, not something this note establishes.
Our own gyro-limited envelope (`max_recoverable_rate`, `gyro_limit_rad_s`) is a
modelled sensing limit, not evidence about scale.

State it as *"no published flight demonstration at sub-250 g that we could find"*,
never as "no one has considered it".

## 7. What is established — do not claim as novel

1. Quadrotor hovers and is position-controlled after one rotor loss by giving up
   yaw. Settled 2011–2014, flight-validated, **patented**.
2. The relaxed-hover / primary-axis mechanism is Mueller & D'Andrea's.
3. Two-opposite loss is flight-validated at >8 m/s under wind (T-RO 2021).
4. Two-adjacent and three-rotor loss are solved — analytically/in sim by Mueller &
   D'Andrea, and **in outdoor flight** by Ke et al. (T-RO 2023).
5. Recovery from arbitrary tumbling attitude/rate after rotor loss is solved and
   flight-demonstrated (ICRA 2020), including the allocator trick that makes it work.
6. Onboard-only operation is solved (vision through the spin; NMPC with per-rotor
   constraints).
7. Fast detection exists: 0.18 s with 0.60 m height loss (hexacopter, verified).
8. Controllability under partial degradation is solved theory (Du et al. 2015).
9. A two-action switching threshold has been derived experimentally (Mao et al. 2024).
10. Learned passive FTC spanning partial → complete without switching is published
    (Chen et al. 2025).

## 8. What is genuinely open — the policy question

The literature is overwhelmingly about **one action**: here is a controller, it
stabilises the damaged vehicle. Recovery as a **choice among qualitatively
different actions, indexed by post-failure state**, is close to unoccupied:

1. **Action selection over (h, v_z, tumble rate, detection delay).** Mao et al.
   (2024) do two actions on one axis (damage severity). Nothing maps the
   height/vertical-speed/tumble/delay space to a choice.
2. **Height and vertical speed are outcomes in the literature, never decision
   variables.** Height loss is reported (0.60 m), never used as an input that
   changes which action is correct.
3. **Detection delay is a performance metric, not a policy input.** Nobody
   publishes the recoverable set *as a function of detection delay*. That function
   is the natural core of our contribution.
4. **The abort boundary is unquantified for quadrotors** — Sun et al. (2020)
   recover from arbitrary attitude at generous altitude; nobody characterises where
   the vertical budget runs out first.
5. **Sub-250 g**: partial degradation has a real-flight precedent at 30.6 g;
   complete loss is a search-bounded absence (§6).
6. **Two-adjacent evidence is thin** — a policy result saying "no thrust action
   survives two-adjacent at low height" is defensible and cite-supported, but it is
   a claim about a thin base and must say so.

## Unverified — do not cite until confirmed

- Validation modality (sim/bench/flight) for Lu & van Kampen (2015), Beyer et al.
  (2023), Wang et al. (2019), Chen et al. (2025).
- "30–130 ms detection delays" attributed here — traced instead in cluster 02.
- "Maximum allowable partial fault for hovering is 50% motor effectiveness";
  "70% motor failure → 0.13 m altitude loss"; "height dropped only 0.9 m during a
  2-second recovery"; "motor faults detected in ~250 ms on an F550 hexarotor" —
  all surfaced without traceable sources.
- Page/volume numbers were not verified for most entries — DOIs and titles were.
