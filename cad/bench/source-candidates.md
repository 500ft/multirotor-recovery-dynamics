# Source-backed candidate packet — 2026-09-15 (T01)

Status: **candidate research only**. Nothing here is an accepted register value, a
delivered-part identity, or an Owner decision. Every value below is a manufacturer or
retailer claim pending D2/D4 acceptance and, where fit-critical, delivered-part
inspection. Sources fetched 2026-09-15; access noted per entry. Governed by
[DAY4_PLAN.md](../../docs/DAY4_PLAN.md) (T01) and the earlier
[fixture preparation](fixture-preparation.md).

## C1 — Load cell candidate: Phidgets 3132_0 (existing unselected proposal, extended)

Identity: "Single Point Load Cell - 780g", part 3132_0, mechanical drawing **Rev 1,
dated 2025-06-10** (sheet 1 of 2 body, sheet 2 of 2 cable).
Sources, both accessible 2026-09-15:
[product page](https://www.phidgets.com/?prodid=223),
[mechanical drawing PDF](https://www.phidgets.com/productfiles/3132/3132_0/Documentation/3132_0_Mechanical.pdf).

From the product page (units as published): capacity 780 g; maximum overload 936 g
(survival, not operating allowance); repeatability / non-linearity / hysteresis each
390 mg max; screw thread M3×0.5.

Transcribed from drawing Rev 1 (mm, no tolerance block printed on either sheet):

| Feature | Value | Printed or derived |
| --- | --- | --- |
| Body length × width × height | 45 × 9.25 × 5.95 | printed |
| Mounting holes | 4× M3×0.5 THRU, one face, along length | printed |
| Outer hole-pair span | 37 | printed |
| Inner hole-pair span | 22 | printed |
| Per-end hole pitch | 7.5 = (37 − 22)/2 | derived, needs drawing/inspection confirmation |
| Cable | 210 long, 30 AWG, SMM-003T-P0.5 crimp pins, full Wheatstone bridge (red/black excitation, white/green signal) | printed |

Explicit unknowns: which hole pair is the loaded vs fixed end; lateral hole position
across the 9.25 width (not dimensioned on sheet 1); thread engagement depth available
above the through hole; dimensional tolerances (none printed); delivered revision.
Not established by this entry: installed accuracy, off-axis behavior, calibration,
availability or price.

## C2 — Motor mount interface: Happymodel EX1103 11000KV (locked BOM motor)

Source, accessible 2026-09-15:
[manufacturer page](https://www.happymodel.cn/index.php/2022/09/05/bassline-spare-part-ex1103-kv11000-brushless-motor/).

Page-confirmed (as published): stator 11 mm × 3 mm; shaft Φ1.5 mm; body Φ13.5 mm ×
15.5 mm; 3.8 g; 9N12P; 1–2S; bench table at 7.4 V with 2023R prop up to 121.9 g at
9.20 A (sizing evidence only — not a 7.0 V result, and 2023R is not the locked prop).

**The accessible page does not state the mounting hole pattern, thread size, hole
count, or usable screw depth.** The register rows `motor_mount_hole_diameter`,
`motor_mount_pitch_circle`, `motor_mount_thread_engagement` therefore cannot be
served from this source. Route to close: manufacturer drawing request, or caliper
inspection of a delivered motor (D4 `await inspection`). No inference from photos.

## C3 — Prop hub interface: Gemfan 2023 3-blade (locked BOM prop)

Sources, accessible 2026-09-15:
[BetaFPV listing](https://betafpv.com/products/gemfan-2023-3-blade-propellers1-5mm-shaft-4pcs),
[Flywoo listing](https://flywoo.net/products/gf-2023-3-1.5mm-shaft-3-blade-propellers).

Retailer-stated (as published): center bore 1.5 mm; 3-hole T-mount hub; diameter
52.17 mm (2 in), pitch 2.3 in; hub/center thickness 5 mm; 0.88 g; polycarbonate.

Explicit unknowns: side-hole diameter and coordinates (not stated on accessible
pages); bore tolerance (needed for D3's signed fit — retailer nominal cannot supply
it); exact catalog variant (plain 2023 vs Hurricane 2023S listings exist — the
delivered part identity must be pinned under D4 before any value is accepted).

## C4 — Bench anchors and screw stacks

Not researchable: bench anchor pattern, available space, adapter/washer/screw stacks
and delivered-part fits require physical access. Retained as the physical block per
[fixture-preparation.md](fixture-preparation.md); D4 `await inspection` covers them.
