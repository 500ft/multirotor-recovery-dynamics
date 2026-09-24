# Study A2 — Spin-Aware Variant + Machinery Revision (DR-SS-02)

Status: PREREGISTRATION addendum to [design.md](design.md), frozen 2026-09-16
before the first committed two-variant sweep. Changing any number after results
exist requires a new study ID, not an edit.

## 1. Why an A2 exists

The first committed Study A sweep killed the mechanism with `both_actions_fail`
in every primary cell. Per design.md §7's interpretation clause that is a
*controller* finding: the fixed-frame PD cannot handle rotor-out flight. A2 is
the controls follow-on — not a mechanism redesign.

## 2. Machinery revision (applies to BOTH variants; Study A regenerated)

Single-trial verification against the design.md §7b anchors exposed two machinery
defects in the first committed sweep, fixed here and applied to both variants —
the superseded Study A data is regenerated in the same commit so no conclusion
rests on the defective machinery:

1. **Allocation.** The single-pass pseudo-inverse + clip distorted both the
   torque axis and the collective whenever a motor saturated (for one-out, half
   of every slow spin revolution). Replaced by cascaded allocation: exact joint
   solve first (identical where feasible), then saturated motors pinned and the
   free ones re-solved with torque-priority weighting (`TORQUE_PRIORITY = 10`).
   The collective ceiling is now the *balanced* (zero roll/pitch trim) ceiling —
   one-out hovers on 2 f_max, not 3 f_max — with a 0.9 airmode reserve in
   allocation mode (0.75 of the balanced ceiling would starve the vertical axis
   below hover thrust).
2. **Descent policy.** Arrest-first: the touchdown descent rate is tracked only
   below 25 deg tilt; above it the vertical loop brakes. Descending while
   righting spends the height the arrest needs and arrives hot.

Also revised, with provenance: the mechanism mass credit is now tied to the BOM
(EST-MASS-012 carries frame+guard+mounts; removable-guard share EST 16 g against
the live rollup — computed, not typed, so a budget change cannot stale it).
Inertia share stays EST 0.30 pending the CAD mass model (OQ-010).

## 3. The A2 controller delta (the only difference between variants)

* **Gyroscopic feedforward**: the commanded roll/pitch torque adds the tilt-plane
  component of `w x Iw` computed from the MEASURED rate and modeled inertia (the
  same idealization the gravity compensation already makes). The PD alone ignores
  this precession torque, which grows with the rotor-out drag spin.
* **Bounded terminal spin**: yaw rotational drag `tau_z = -c w_z |w_z|` with
  `c = 6e-6 N·m·s²` (EST, owner input OQ-010) — a *plant* term absent from the
  first model, in which the drag spin grew without limit. Coherence requirement:
  the implied terminal spin (~26 rad/s) must sit inside the gyro range
  (35 rad/s); an unmeasurable spin cannot be claimed controlled. Tested.

Seeds include the variant index; the parachute action uses no controller and is
computed once and shared.

## 4. Preregistered hypothesis (falsifiable, before the sweep)

Single-trial evidence during freezing showed the allocator, not the feedforward,
is the dominant lever at h ≤ 3 m (crashes happen in < 1 s at ~7 rad/s spin,
before precession matters). Therefore:

* **H-A2.1**: A2 raises P_safe over variant A primarily in tall cells (h = 6 m)
  for `one_out` and `two_opposite`, where the spin has time to build.
* **H-A2.2**: at h ≤ 3 m, A2 and A are within Monte Carlo uncertainty of each
  other everywhere.
* The **kill criterion** of design.md §7 is re-evaluated on the A2 primary
  results under the identical rule.

If A2 fails to separate from A everywhere, the honest conclusion is that
feedforward alone is insufficient and a genuinely spin-locked rotor-out
controller (primary-axis / reduced-attitude in the spun frame) becomes the next
work item.

**Outcome, amended 2026-09-23 after the paired re-analysis** (`design.md` §7a).
The original unpaired comparison reported H-A2.1 as "not supported". With
identical draws in both arms the result is sharper and worse for A2: across 192
paired comparisons the spin-aware variant won **zero** discordant pairs while the
baseline won all 15 that exist (exact 95 % CI on π = [0.782, 1.000]). So
feedforward is not neutral here — it is mildly harmful in the cells where the two
differ at all. The registered conclusion stands and strengthens: a genuinely
spin-locked rotor-out controller is the next work item, and per
`literature/notes/01` §2 that is **adoption of a known controller**
(Mueller & D'Andrea's primary-axis relaxed hover, which is also patented), not an
invention.

## 5. Integrator defense

`python -m Analysis.run_survivable_set --convergence` repeats primary-cell
trials at dt = 5e-4 (production) and 2.5e-4: max impact-speed delta 0.0044 m/s,
landed/not-landed agreement 12/12 (`Data/survivable_set_convergence.json`) —
two orders of magnitude below the 0.5 m/s spacing of the criterion variants.

## 6. Boundary finding carried forward

With this control family, a 6 rad/s tumble at failure remains outside the
arrest envelope for `one_out` and `two_opposite` at any tested height — tilt
passes 78 deg before the reduced torque authority can arrest, independent of the
descent that follows. Any claim of rotor-out recovery from fast tumbles must
come from a different controller class, not from tuning this one.
