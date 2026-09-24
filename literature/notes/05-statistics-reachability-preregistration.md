# 05 — Statistics, reachable/survivable sets, preregistration

Repo artifacts this cluster governs: `clopper_pearson_lower/_upper`,
`kill_criterion`, `policy_map` in `Analysis/survivable_set.py`;
`docs/specs/survivable-set/design.md` §6–7; the A-vs-A2 comparison in
`design-a2.md` §4; `evidence/week-2026-09-19/` W06 backlog items.

## Headline findings for this repo

1. **Our comparison can be made much more precise (corrected 2026-09-24,
   critique C09).** Mechanism vs reallocation, and A vs A2, were compared through
   two independently computed Clopper–Pearson intervals. That design is **valid
   but low-powered**, not erroneous — an earlier version of this note said it
   "manufactures" the non-result, which overstated the case and is withdrawn.
   Common random numbers induce positive covariance and, via
   `Var(A−B) = Var(A)+Var(B)−2Cov(A,B)`, sharpen the contrast; they also make a
   paired analysis available. Correct objects: McNemar on discordant pairs
   (mid-p preferred), Tango's score interval, and **both** π (conditional
   discordant win-rate) and Δ (unconditional marginal difference).
2. **"No demonstrated advantage" needs a preregistered margin δ.** Without one,
   a null result is only "underpowered". With one, it becomes a testable
   non-inferiority claim. Absence of evidence ≠ evidence of absence
   (Altman & Bland 1995).
3. **The closest prior work exists and we must cite it**: Sun & de Visser (2019)
   compute a Monte-Carlo safe flight envelope for a quadrotor by exactly our
   reasoning (HJ reachability doesn't scale past ~4–5D → sample instead), and
   Sun et al. (2020) do Monte-Carlo recovery from large post-rotor-failure
   disturbances. Our novelty claim must be narrowed accordingly (see §7).
4. **Our 95%-lower + 95%-upper pair is a 90% central interval**, not 95% — as
   suspected in the Day-1 audit, now with a citable basis.

## 1. Binomial confidence intervals

| Ref | A/E | Key finding |
| --- | --- | --- |
| Clopper & Pearson (1934), *The use of confidence or fiducial limits illustrated in the case of the binomial*, Biometrika 26(4) 404–413, [10.1093/biomet/26.4.404](https://doi.org/10.1093/biomet/26.4.404) | 3 / A | The exact interval by inverting the equal-tailed binomial test. Coverage **≥ 1−α for every p** — the property we are buying. |
| Brown, Cai & DasGupta (2001), *Interval estimation for a binomial proportion*, Statistical Science 16(2) 101–133, [10.1214/ss/1009213286](https://doi.org/10.1214/ss/1009213286) | 3 / A | The canonical critique: CP is "wastefully conservative"; recommends Wilson/Agresti–Coull/Jeffreys as defaults. **Cite as the acknowledged criticism of our choice.** |
| Agresti & Coull (1998), *Approximate is better than "exact"…*, The American Statistician 52(2) 119–126, [10.1080/00031305.1998.10480550](https://doi.org/10.1080/00031305.1998.10480550) | 3 / A | The anti-exact position in one title; adjusted-Wald interval. |
| Thulin (2014), *The cost of using exact confidence intervals for a binomial proportion*, EJS 8(1) 817–840, [10.1214/14-EJS909](https://doi.org/10.1214/14-EJS909) | 3 / A | **Quantifies** the conservatism and gives a closed-form CP sample-size formula — directly usable for sizing trials per cell. |
| Hanley & Lippman-Hand (1983), *If nothing goes wrong, is everything all right?*, JAMA 249(13) 1743–1745, [10.1001/jama.1983.03330370053031](https://doi.org/10.1001/jama.1983.03330370053031) | 3 / A | Rule of three: 0 events in n ⟹ 95% upper ≈ 3/n — which **is** our one-sided CP bound at x=0. Cite for every zero-count cell (we have many). |

**Why CP stays, stated honestly.** The criticism is conservatism only. CP is
still right when coverage must never fall below nominal for any true p, when n is
small or p near 0/1 (our grid lands there constantly), and when the claim is a
*bound* rather than an estimate. Crucially the direction is favourable: a
conservative **lower** bound on P(survivable landing) errs toward understating
survivability. We should say this explicitly rather than ignoring the critique.

**Multiplicity gap (no citation needed, but a real hole).** Per-cell 95%
intervals over K cells are not 95% simultaneous. Any claim about the *set* needs
either an explicit "per-cell, no simultaneity claimed" or a Bonferroni-style
adjustment. Our specs currently say neither. Preregister one.

## 2. One-sided vs two-sided — the error we made

A 100(1−α)% two-sided central interval is the intersection of two
100(1−α/2)% one-sided bounds. **A 95% lower bound combined with a 95% upper bound
is a 90% central interval**, not 95%; for joint 95% you need 97.5% one-sided
bounds. In CP terms: the two-sided 95% interval solves the tail equations at
0.025 per side; the one-sided 95% lower bound solves at 0.05.

| Ref | A/E | Use |
| --- | --- | --- |
| Brown, Cai & DasGupta (2001) as above | 3 / A | States CP as the equal-tailed inversion — the in-print form of the fact. |
| Meeker, Hahn & Escobar (2017), *Statistical Intervals*, 2nd ed., Wiley, [10.1002/9781118594841](https://doi.org/10.1002/9781118594841) | 3 / B | The engineering/reliability reference treating one-sided **bounds** as first-class objects. |
| ICH E9 (1998) *Statistical principles for clinical trials*; intro note: Lewis (1999), Statistics in Medicine 18(15) 1903–1942 | 2 / B | The regulatory convention (one-sided 2.5% ↔ two-sided 95%); cleanest authority for "don't silently swap sidedness". |

**Action.** `kill_criterion` compares a 95% lower against a 95% upper. Keep the
rule (it is preregistered) but **label it correctly**: it is a comparison of
one-sided 95% bounds, equivalent to a 90% central construction, not a 95%
interval comparison.

## 3. Paired binary outcomes — the fix for our comparison

| Ref | A/E | Key finding |
| --- | --- | --- |
| McNemar (1947), *Note on the sampling error of the difference between correlated proportions*, Psychometrika 12(2) 153–157, [10.1007/BF02295996](https://doi.org/10.1007/BF02295996) | 3 / A | The matched-pair test; conditions on discordant pairs only. |
| Fagerland, Lydersen & Laake (2013), *The McNemar test for binary matched-pairs data: mid-p and asymptotic are better than exact conditional*, BMC Med Res Methodol 13:91, [10.1186/1471-2288-13-91](https://doi.org/10.1186/1471-2288-13-91) | 3 / A | Exact conditional McNemar is needlessly conservative; **mid-p recommended as default**, exact only when a strict level guarantee is required. |
| Tango (1998), *Equivalence test and confidence interval for the difference in proportions for the paired-sample design*, Statistics in Medicine 17(8) 891–908, [10.1002/(SICI)1097-0258(19980430)17:8<891::AID-SIM780>3.0.CO;2-B](https://doi.org/10.1002/(SICI)1097-0258(19980430)17:8%3C891::AID-SIM780%3E3.0.CO;2-B) | 3 / A | **The key paper for our controller comparison**: score-based equivalence test *and* CI for the paired risk difference. |

**Concrete repo change.** Seeds currently include the action index
(`_chunked_tasks(..., (BASE_SEED, vi, tier, ci, ki, ai), variant)`), so
`mechanism` and `realloc_only` draw *different* vehicles — the comparison is
unpaired by construction. The W05 diagnostic already plans "draw the vehicle once
and feed the same realization to both"; this literature says that is not an
optimisation but a **correctness requirement**, and that the analysis must then be
McNemar/Tango on discordant pairs, not two CP intervals.

## 4. Rare-event Monte Carlo and how many trials

| Ref | A/E | Key finding |
| --- | --- | --- |
| Kalra & Paddock (2016), *Driving to safety…*, RAND RR-1478-RC, [10.7249/RR1478](https://doi.org/10.7249/RR1478) | 3 / B | The canonical "you cannot test your way to a rare-failure guarantee"; simulation/accelerated/scenario testing are *required*. **Cite for why per-cell resolvable bounds beat a global "we ran N trials".** |
| Corso, Moss, Koren, Lee & Kochenderfer (2021), *A survey of algorithms for black-box safety validation of cyber-physical systems*, JAIR 72 377–428, [10.1613/jair.1.12716](https://doi.org/10.1613/jair.1.12716) | 3 / A | Separates falsification, most-likely-failure, and **failure-probability estimation** as distinct goals. We are doing the third — useful for method framing. |
| Lee, Kochenderfer, Mengshoel, Brat & Owen (2015), *Adaptive stress testing of airborne collision avoidance systems*, DASC, [10.1109/DASC.2015.7311613](https://doi.org/10.1109/DASC.2015.7311613) | 3 / B | Originating AST: MDP + MCTS search for the most likely failure trajectory, simulator-only. |
| Zhao et al. (2017), *Accelerated evaluation of automated vehicles… importance sampling*, IEEE T-ITS 18(3) 595–607, [10.1109/TITS.2016.2582208](https://doi.org/10.1109/TITS.2016.2582208) | 2 / A | Importance sampling with unbiased reweighting; orders-of-magnitude fewer trials. The template if our per-cell failure rates get too small for crude MC. |
| Riedmaier, Ponn, Ludwig, Schick & Diermeyer (2020), *Survey on scenario-based safety assessment of automated vehicles*, IEEE Access 8 87456–87477, [10.1109/ACCESS.2020.2993730](https://doi.org/10.1109/ACCESS.2020.2993730) | 2 / A | Justifies "cell-wise over a gridded state space" as a recognised validation architecture. |

## 5. Reachability / viability / safe-set computation

| Ref | A/E | Key finding |
| --- | --- | --- |
| Mitchell, Bayen & Tomlin (2005), *A time-dependent Hamilton–Jacobi formulation of reachable sets for continuous dynamic games*, IEEE T-AC 50(7) 947–957, [10.1109/TAC.2005.851439](https://doi.org/10.1109/TAC.2005.851439) | 3 / A | The formal object our Monte-Carlo grid approximates: backward reachable set as the zero sublevel set of an HJI viscosity solution. |
| Bansal, Chen, Herbert & Tomlin (2017), *Hamilton-Jacobi reachability: a brief overview and recent advances*, CDC 2242–2253, [10.1109/CDC.2017.8263977](https://doi.org/10.1109/CDC.2017.8263977) | 3 / B | The curse of dimensionality caps exact HJ at ~4–5D. **This is the citation that justifies sampling instead of solving.** |
| Saint-Pierre (1994), *Approximation of the viability kernel*, Applied Math & Optimization 29(2) 187–209, [10.1007/BF01204182](https://doi.org/10.1007/BF01204182) | 2 / A | Viability-kernel counterpart: largest set from which constraints can be maintained. |
| Nabi, Lombaerts, Zhang, van Kampen, Chu & de Visser (2018), *Effects of structural failure on the safe flight envelope of aircraft*, JGCD 41(6), [10.2514/1.G003184](https://doi.org/10.2514/1.G003184) | 3 / A | **Post-failure safe set via reachability** — same framing as ours, fixed-wing, deterministic. |
| **Sun & de Visser (2019), *Quadrotor safe flight envelope prediction in the high-speed regime: a Monte-Carlo approach*, AIAA SciTech 2019-0948, [10.2514/6.2019-0948](https://doi.org/10.2514/6.2019-0948)** | **3 / B** | **Closest methodological precedent.** Explicitly rejects level-set HJ above ~4 states and substitutes Monte-Carlo estimation of a quadrotor safe flight envelope. Binary safe/unsafe labels per sampled state; **no per-cell confidence bounds**. Nominal, not post-failure. |
| Yin, Chu, Zhang, Niestroy & de Visser (2019), *Probabilistic flight envelope estimation with application to unstable overactuated aircraft*, JGCD 42(12) 2650–2663, [10.2514/1.G004193](https://doi.org/10.2514/1.G004193) | 3 / A | Nearest published "probability attached to each envelope point" — but fixed-wing, overactuated, not failure-conditioned. |
| **Sun, Baert, Strack van Schijndel & de Visser (2020), *Upset recovery control for quadrotors subjected to a complete rotor failure from large initial disturbances*, ICRA, [10.1109/ICRA40945.2020.9197239](https://doi.org/10.1109/ICRA40945.2020.9197239), arXiv [2002.09425](https://arxiv.org/abs/2002.09425)** | **3 / B** | **Closest substantive precedent.** Post-rotor-failure recovery from large initial attitude/rate disturbances, validated by Monte Carlo over randomised initial conditions, with an angular-velocity constraint derived from the shrunken attainable moment set. Framed as controller capability, not an estimated set with boundary uncertainty. |
| Mueller & D'Andrea (2014), *Stability and control of a quadrocopter despite the complete loss of one, two, or three propellers*, ICRA 45–52, [10.1109/ICRA.2014.6906588](https://doi.org/10.1109/ICRA.2014.6906588) | 2 / B | The existence result underpinning the area; defines what "recovered" can mean after propulsion loss. |

## 6. Preregistration, reproducibility, V&V

| Ref | A/E | Key finding |
| --- | --- | --- |
| Nosek, Ebersole, DeHaven & Mellor (2018), *The preregistration revolution*, PNAS 115(11) 2600–2606, [10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114) | 3 / A | Prediction vs postdiction; preregistration restores the diagnosticity of a confirmatory test. **The citation for our `design.md` preregistration practice.** |
| Chambers & Tzavella (2022), *The past, present and future of Registered Reports*, Nature Human Behaviour 6(1) 29–42, [10.1038/s41562-021-01193-7](https://doi.org/10.1038/s41562-021-01193-7) | 2 / A | The stronger form: protocol peer-reviewed before results exist. |
| Sandve, Nekrutenko, Taylor & Hovig (2013), *Ten simple rules for reproducible computational research*, PLoS Comp Biol 9(10) e1003285, [10.1371/journal.pcbi.1003285](https://doi.org/10.1371/journal.pcbi.1003285) | 2 / A | **Record all random seeds** — load-bearing for our paired design and our `trial_id` backlog item. |
| ASME V&V 10-2019, *Verification and Validation in Computational Solid Mechanics* | 2 / A | Framework vocabulary (code vs solution verification vs validation vs UQ). |
| ASME V&V 20-2009 (R2021), *Verification and Validation in CFD and Heat Transfer* | 2 / A | Quantifies accuracy at a stated validation point. |

**Scoping honesty.** Neither ASME standard covers flight-dynamics/GNC simulation
(one is solid mechanics, the other CFD/heat transfer). Borrow the **framework**;
never claim compliance with a standard whose scope excludes our application.

## 7. Novelty claim, narrowed to what survives

`design.md` §1 currently says the open contribution is "a *policy* over the
post-failure state … with a quantified survivable set". The literature above
requires narrowing that. Defensible wording:

> We are not aware of published work that estimates, **per post-failure state
> cell**, P(survivable landing) with **exact binomial bounds** against a
> **preregistered** survivability criterion, and uses it to select among distinct
> recovery *actions*. The closest prior work is Sun & de Visser (2019)
> (Monte-Carlo quadrotor safe envelope; binary labels, nominal conditions),
> Yin et al. (2019) (probabilistic envelope, fixed-wing), and Sun et al. (2020)
> (post-rotor-failure recovery validated by Monte Carlo, no set estimate with
> boundary uncertainty).

That is checkable and survives a reviewer finding one more paper.

## 8. How to report "the mechanism did not beat the baseline"

Never infer equivalence from overlapping intervals — Altman & Bland (1995),
*Absence of evidence is not evidence of absence*, BMJ 311(7003) 485,
[10.1136/bmj.311.7003.485](https://doi.org/10.1136/bmj.311.7003.485) (3/A).

1. **Exploit the pairing** (§3) — discordant counts, not two proportions.
2. **Pre-specify a margin δ** before running. Piaggio et al. (2012), *Reporting
   of noninferiority and equivalence randomized trials (CONSORT extension)*,
   JAMA 308(24) 2594–2604, [10.1001/jama.2012.87802](https://doi.org/10.1001/jama.2012.87802) (3/A).
3. **Test with TOST** — Schuirmann (1987), J. Pharmacokin. Biopharm. 15(6)
   657–680, [10.1007/BF01068419](https://doi.org/10.1007/BF01068419) (3/A);
   Lakens (2017), SPPS 8(4) 355–362, [10.1177/1948550617697177](https://doi.org/10.1177/1948550617697177) (3/A);
   Tango (1998) for the paired-binary case.
4. **Get sidedness right** — TOST reads off a 90% two-sided interval at α=0.05
   per side (§2).

Report exactly one of: **superiority** (CI above 0), **non-inferiority**
(lower bound above −δ, δ named), or **inconclusive** (CI spans −δ and 0; state
achieved n and the detectable effect size). Our current A-vs-A2 and
mechanism-vs-baseline statements are category 3 and should say so.

## Unverified — do not cite until confirmed

- Meeker, Hahn & Escobar (2017) — exact page/section for the 1−2α statement.
- ICH E9 (1998) — clause number for the one-sided 2.5% convention.
- Lombaerts, Schuet, Wheeler, Acosta & Kaneshige, *Robust maneuvering envelope
  estimation based on reachability analysis…* — real, venue/year/DOI unresolved.
- *Efficient methods for flight envelope estimation through reachability
  analysis*, AIAA, DOI reported as 10.2514/6.2016-0083 — authors unconfirmed.
- ASME V&V 10.1 and the wider VVUQ family (e.g. VVUQ 40) — siblings not verified.
- Whether Sun & de Visser (2019) or Sun et al. (2020) report per-cell confidence
  intervals in their full text — **abstracts only were read. Read both in full
  before asserting the novelty gap in §7 in any paper.**
