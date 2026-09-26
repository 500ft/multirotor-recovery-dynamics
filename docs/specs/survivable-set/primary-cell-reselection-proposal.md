# Proposed primary-cell reselection — for owner registration

Status: **PROPOSAL, not registered.** Prepared 2026-09-26 in response to the
DR-SS-SCENARIO-01 diagnostic finding. **No study currently uses these cells and
no sweep has been run against them.** They must be registered by the owner before
any decisive run, exactly as `design.md` §9 requires.

## Why this exists

The scenario diagnostic (288 trajectories, PR #38) found that **all four current
primary cells are saturated**: every package fails in every arm, so every paired
contrast is 0/24 discordant. The binary proxy cannot move there, which means a
full registered rerun on those cells would measure nothing and return
`no_discordant_pairs` by saturation rather than by agreement.

## Evidence — how much of the grid can resolve anything

From the committed exploratory results (`Data/survivable_set_results.json`),
counting class × cell combinations where the two packages are not both pinned at
0.00 or both at 1.00:

| | count |
| --- | ---: |
| Saturated (all 0 or all 1) | **71 of 96** |
| Resolvable | **25 of 96** |
| Current primary cells that are resolvable | **0 of 4** |

Two structural findings fall out, and both matter more than the cell list:

1. **`two_adjacent` has no resolvable cell anywhere in the grid.** Every
   combination is pinned at zero. It therefore **cannot serve as a primary class
   for any binary-proxy comparison** — not because the class is uninteresting,
   but because the outcome measure has no resolving power on it. A study wanting
   to say something about two-adjacent loss needs a *continuous* outcome
   (impact speed, altitude consumed) or a different criterion.
2. **Resolvable cells are concentrated at ω = 2 rad/s.** At ω = 6 rad/s the
   rotor-out classes are almost entirely saturated at zero — consistent with the
   `design-a2.md` §6 boundary finding that a 6 rad/s tumble is outside this
   control family's arrest envelope at every tested height.

## Candidate cells, ranked by resolving power

Ranked by closeness of the two-package mean to 0.5, where a paired comparison has
the most power to detect a shift:

| Rank | Class | Cell | mechanism | realloc | mean |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | `one_out` | `h6_vz0_w2_d0.11` | 0.47 | 0.50 | **0.48** |
| 2 | `partial_authority` | `h1.5_vz0_w6_d0.11` | 0.50 | 0.57 | **0.53** |
| 3 | `one_out` | `h6_vz-1.5_w2_d0.3` | 0.37 | 0.53 | 0.45 |
| 4 | `one_out` | `h6_vz-1.5_w2_d0.11` | 0.37 | 0.50 | 0.43 |
| 5 | `two_opposite` | `h6_vz0_w2_d0.11` | 0.27 | 0.50 | 0.38 |
| 6 | `partial_authority` | `h3_vz-1.5_w2_d0.3` | 0.27 | 0.47 | 0.37 |

## Proposed set — two cells, three classes

| Class | Cell | Why |
| --- | --- | --- |
| `one_out` | `h6_vz0_w2_d0.11` | highest resolving power in the grid; the marginal rotor-out case |
| `one_out` | `h6_vz-1.5_w2_d0.3` | same class under a descending start **and** the stress-case detection delay, so delay stays a swept coordinate |
| `two_opposite` | `h6_vz0_w2_d0.11` | second rotor-out topology at a resolvable point |
| `partial_authority` | `h1.5_vz0_w6_d0.11` | the only class with a sub-35 g real-flight precedent (ledger G3), resolvable at low height and high tumble |

`two_adjacent` is **deliberately excluded from primary status** and retained as an
exploratory class reported on continuous outcomes only, per finding 1.

## What must be decided before this is registered

1. **Selection-on-outcome.** These cells were chosen by looking at results from
   the existing study. That is legitimate for *design of a new experiment* but it
   is **not** a fresh confirmatory test of the same hypothesis on the same model:
   the cells were picked because they are informative, which is a form of
   selection. Register the reselection explicitly and describe the resulting run
   as **a new study with its own ID**, not a continuation of the frozen one.
2. **Whether the primary outcome stays binary.** Given 71/96 saturation, a
   continuous primary outcome (impact speed, altitude consumed) would carry far
   more information per trajectory. That is a larger change and needs its own
   registration; the binary proxy is what is currently frozen.
3. **Trial count.** At N = 300 per (class, cell, package, arm) the three-arm
   design over four class-cells is 7200 trajectories. Benchmark first: the
   diagnostic ran 288 in ~35 s, so ~15 min is the order of magnitude — compute is
   not the constraint, registration is.
4. **Whether `two_adjacent` needs a continuous-outcome study** to say anything at
   all about the hardest failure class.

## What this proposal does not do

It does not change any registered cell, does not run anything, and does not claim
the new cells will show an effect. It identifies where the current outcome measure
can and cannot see, which the diagnostic revealed and the frozen grid hides.
