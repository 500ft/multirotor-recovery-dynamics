# 07: Loss-of-control prediction from onboard data

Repo artifacts this cluster governs: the research question in `ROADMAP.md`;
the F.1 baselines and preregistration; `novelty-and-gaps.md` §6;
`claim-ledger.md` H1.

Added 2026-10-09. Search scope: abstract-level, web search only, forward
citations not searched.

## Headline findings for this repo

1. **The nearest prior work predicts loss of control 2 s ahead on real flight
   data, from onboard sensors only.** Altena, van Beers & de Visser (2023)
   report 172 real-world loss-of-control events on three quadcopters (53 g
   Tiny Whoop, 73 g URUAV UZ85, 265 g GEPRC CineGO). All four recurrent
   architectures they trained predicted the event 2 s before it occurred, and
   the predictors transferred across changes in mass, blade diameter and
   blade count.
2. **The clearest early signal was rotor-command saturation.** That is
   effectively the thrust-margin signal, so it is the physics comparator the
   maneuver-specific warning must beat.
3. **The event differs from ours.** Their loss of control was forced by
   commanding an excessive yaw rate (2000 deg/s), an unrecoverable upset by
   design. This repository asks about a battery- or thrust-limited loss of
   recovery capability.
4. **A null result is likely.** If the physics quantity does most of the
   predicting in their data, the maneuver-specific warning here may not beat
   the thrust-margin baseline. This is a risk to milestone F, which depends on
   the flight outcomes from E. Milestone status is unchanged; that is an owner
   decision not yet made.

## 1. Loss-of-control prediction

| Ref | A/E | Key finding |
| --- | --- | --- |
| **Altena, van Beers & de Visser (2023)**, *Loss-of-Control Prediction of a Quadcopter Using Recurrent Neural Networks*, Journal of Aerospace Information Systems 20(10) 648–659, [10.2514/1.I011231](https://doi.org/10.2514/1.I011231) | 3 / B | 172 real-world loss-of-control events on three quadcopters (53 g, 73 g, 265 g). Loss of control forced by a 2000 deg/s yaw-rate command. Four recurrent network architectures on onboard sensor measurements only; commanded rotor values saturate before loss of control and were the clearest early signal; all four predicted the event 2 s ahead; transfer across mass, blade diameter and blade count. Graded from the abstract; full text not read. |

## 2. Gaps (report as absences)

- A warning compared with a physics comparator at matched false-alarm rate
  was not found in the 2026-10-09 review (abstract-level, web search only,
  forward citations not searched).
- A warning tested on held-out battery packs was not found in the 2026-10-09
  review (abstract-level, web search only, forward citations not searched).

## 3. Consequence for the roadmap

Cite Altena et al. as the related-work anchor for F.1. Keep the physics
feasibility baseline as the preregistered primary comparator so a null result
is reportable rather than a failure of the study.

## Unverified (do not cite until confirmed)

- Whether Altena et al. report a threshold or physics baseline, false-alarm
  rates or lead-time distributions in the full text. Only the abstract was
  read. Read the paper before asserting the gaps in §2 in any write-up.
