# Literature review

Assembled 2026-09-22. Purpose: give every load-bearing claim in this repository a
checkable external reference, and find out where our claims are unsupported,
already-established, or contradicted by measured data.

**Everything here was verified online at assembly time.** Each entry carries
authors, year, venue and a DOI/arXiv/stable URL. References that could not be
resolved to a publisher record are quarantined in a per-note
"**Unverified — do not cite until confirmed**" section and must not be cited
until someone opens the source. Several numbers that circulate widely in
secondary summaries are listed there specifically because they could *not* be
traced. No reference in this folder was written from memory.

## How to read this

| File | Covers | Governs |
| --- | --- | --- |
| [`notes/01-rotor-loss-fault-tolerant-control.md`](notes/01-rotor-loss-fault-tolerant-control.md) | Control after one/two/three rotor loss; reduced attitude; partial degradation; upset recovery | `design.md` §1 novelty claim, §3 failure classes; `design-a2.md` §4, §6 |
| [`notes/02-control-allocation-and-fdi.md`](notes/02-control-allocation-and-fdi.md) | Allocation under saturation/failure; attitude priority; fault detection latency; motor lag | `Analysis/failure_allocation.py`; airmode logic; the `delay` state coordinate |
| [`notes/03-parachute-and-descent-recovery.md`](notes/03-parachute-and-descent-recovery.md) | ASTM F3322, EASA M2 MoC, deployment altitude/latency, Part 107 categories, alternatives | the `parachute` action; OQ-010 |
| [`notes/04-impact-severity-and-crashworthiness.md`](notes/04-impact-severity-and-crashworthiness.md) | ASSURE A4/A14, HIC, the 11/25 ft-lb criteria, vehicle crashworthiness, terminal velocity | `BARE_CRITERION`, `GUARDED_CRITERION`; `design.md` §5 |
| [`notes/05-statistics-reachability-preregistration.md`](notes/05-statistics-reachability-preregistration.md) | Clopper–Pearson, paired binary designs, rare-event MC, reachable sets, preregistration | `kill_criterion`, `policy_map`, the A-vs-A2 comparison, `design.md` §6–7 |
| [`notes/06-measurement-thrust-stand-uncertainty.md`](notes/06-measurement-thrust-stand-uncertainty.md) | GUM/VIM, OIML R 60, low-Re propellers, thrust-stand design, ground effect, ducts | `docs/bench-acquisition.md`, the R3 calibration plan, OQ-012, the authority gate |
| [`claim-ledger.md`](claim-ledger.md) | Every load-bearing repo claim → support, contradiction, required action | all of the above |
| [`novelty-and-gaps.md`](novelty-and-gaps.md) | What is established, what is genuinely open, who else is claiming our gap | `design.md` §1 |
| [`references.bib`](references.bib) | BibTeX for the verified entries | — |

## Grading

Two independent scales, never blended (a highly-cited paper that is tangential is
still tangential):

- **Aboutness 0–3** — is it about *our* question? 3 = directly; 2 = same problem
  family; 1 = background; 0 = excluded.
- **Evidence A–D** — how good is the support? **A** = flight/experimentally
  validated, replicated, or binding regulatory/standards text; **B** = single
  well-controlled experiment, validated simulation, or peer-reviewed conference;
  **C** = simulation/analysis only, or verified citation whose internals were not
  read; **D** = preprint, position paper, vendor or grey literature.

## The five findings that change the repo

1. **Our comparison design is unpaired and should not be.** Mechanism vs
   reallocation, and A vs A2, were analysed as two independent Clopper–Pearson
   intervals — a **valid but low-powered** design, not an erroneous one (wording
   corrected 2026-09-24, critique C09: the earlier claim that it "manufactures"
   the non-result overstated the case). Running both arms on common random
   numbers induces positive covariance and sharpens the contrast, and makes a
   paired analysis available. → note 05 §3.
2. **The landing criterion cannot rest on injury data, but 1.5–3 m/s has a real
   anchor.** At 165 g and 3 m/s we carry 0.74 J against a most-conservative
   published yardstick of 14.9 J — non-binding by ~27×. The defensible source for
   the band is rotorcraft/transport **landing-gear certification** (14 CFR
   27.725/27.727, 29.725, 25.473 → 1.83–3.12 m/s), by explicit analogy.
   → note 04 §7.
3. **The parachute action is optimistic by roughly an order of magnitude in
   altitude.** Measured floors are 10–15 m for 0.9–2 kg airframes; we model
   usefulness at 6 m. And for a sub-250 g vehicle the real argument is **mass**
   (lightest COTS ≈185 g = 74 % of the budget), not altitude. → note 03 §1.
4. **Our allocator is a named 30-year-old method the literature calls
   suboptimal** — the redistributed pseudo-inverse. Name it, cite it, justify it
   on compute cost, and stop implying novelty. → note 02.
5. **More of the control problem is solved than `design.md` §1 concedes** —
   including two-adjacent loss, in outdoor flight, with a single non-switching
   controller. Our open lane is narrower and sharper than claimed, and **someone
   else is already publishing an adjacent gap claim**. → `novelty-and-gaps.md`.

**Corrections applied 2026-09-24** after an external critique, listed here because
several were errors in this review itself: the comparison in the study is a
**design** comparison, not a runtime policy (`design.md` §6b); the claim that no
detection-latency **distribution** exists was **false** (note 02 §4); the
spin-scaling rationale for sub-250 g difficulty was **wrong physics** — terminal
spin is independent of `Izz` (note 01 §6); a **30.6 g real-flight FTC result**
exists for partial degradation (ledger G3); Siotia et al.'s landing numbers are
**simulation/HIL, not measurements**, so our parachute fit is calibration rather
than validation (ledger C1); and two one-sided bounds on **different** proportions
do not form a central interval for their difference (ledger E1).

## Standing rules

- A reference in the "Unverified" list is **not** a citation. Move it up only by
  opening the source.
- Paywalled standards (ASTM E74, ISO 376, ASME PTC 19.1, F3322 §6, F3389) are
  cited by **designation and scope only** — no clause numbers, no thresholds.
- Where a number is our own arithmetic on a published input, it is labelled as
  such. Do not let derived numbers migrate into the text as quoted results.
- NYU library access will resolve several paywalled items (Magister 2010, Koh
  2018, la Cour-Harbo 2017/2018, Campolettano 2017). That is the cheapest next
  step for anyone extending this.
