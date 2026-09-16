# Open Questions

Track unresolved design decisions here. Close each item with evidence rather than removing it silently.

| ID | Question | Decision Needed From | Required Evidence | Status |
|---|---|---|---|---|
| OQ-001 | Does the locked propulsion set (EX1103 11000KV / Gemfan 2023-3 / GNB 2S 550 mAh) meet thrust reserve on the bench? | Propulsion bench testing | Thrust/current/RPM curves at 8.4/7.6/7.0 V; >=112.5 gf/motor at 7.0 V for full 225 g reserve | OPEN (catalog selection LOCKED 2026-06-20; performance bench-gated) |
| OQ-002 | What is the frozen maximum flying mass? | CAD and BOM rollup | `roundup_to_5g(Sigma worst + 5 g)` and result `<=225 g` | OPEN (primary response to a propulsion miss is mass freeze, not a prop change) |
| OQ-003 | Can batteries eventually be integrated into hollow frame members? | Later packaging study | Crash protection, thermal, serviceability, and abuse testing | DEFERRED |
| OQ-004 | Which NYU facility can provide motion-capture or high-speed video access? | Faculty/lab outreach | Confirmed equipment access and supervision | OPEN |
| OQ-005 | What gyro range and estimator envelope are reliable on the Holybro Kakute H7 Mini (ArduPilot)? | Bench + flight test on locked FC | Kakute IMU datasheet, ArduPilot EKF3 config, and external-truth comparison | OPEN (FC locked: Kakute H7 Mini) |
| OQ-006 | What release heights are testable in the available enclosure? | Test-facility design | Cage dimensions and recovery simulation | OPEN |
| OQ-007 | Is the locked flight controller (Holybro Kakute H7 Mini **v1.5**) still procurable in the exact revision? | Procurement before any order | Live first-party or authorized-reseller stock of v1.5; if unavailable, an H7 20x20 successor with a re-verified UART/DShot resource map | CLOSED 2026-07-03: v1.5 in stock at Holybro direct at $58.99 (v1.3 sold out). The 2026-06-22 "effectively unavailable" finding was stale. FC stays locked. |
| OQ-008 | Are the EOL/legacy parts in the locked BOM (Matek 3901-L0X, HGLRC XJB BS13A) actually orderable now? | Procurement before any order | Confirmed in-stock standalone units, or pre-selected current substitutes | CLOSED 2026-07-03: both unavailable as standalone new stock. Substituted per gate policy (unavailability = blocker): ESC -> Flywoo GOKU G45M 45A 2-6S AM32 (6.4 g, current sensor); flow/lidar -> MicoAir MTF-01 (4.5 g, MAVLink, native ArduPilot). Budgets and interface map updated. |
| OQ-009 | Does the Flywoo GOKU G45M actually run 2S LiHV (7.0-8.4 V) under load, and does its current sensor integrate with ArduPilot battery monitoring on the Kakute? | ESC bench test before the propulsion gate | Spin-up and full-throttle at 7.0 V bench supply; BATT_AMP_PERVLT calibrated against a bench meter | OPEN (Flywoo specifies 2-6S; some retailer listings say 3-6S — treat 2S support as unverified until benched.) |
| OQ-010 | Study A action parameters are EST placeholders: mechanism mass/inertia fractions (0.12 / 0.30), guarded impact tolerance (2.5 m/s / 60 deg), parachute terminal speed and deployment delay (1.8 m/s / 0.8 s) — or a decision that no parachute variant exists | Owner (mass rollup + guard drop data + parachute decision) | Measured guard mass share from the BOM rollup; drop-test impact tolerance; canopy datasheet or removal of the action | OPEN (preregistered defaults frozen in `docs/specs/survivable-set/design.md`; survivable-set claims blocked until replaced) |

## Milestone Schedule

Target dates are placeholders until the student fills them in against their actual semester schedule.

| Milestone | Target Date | Status |
|---|---|---|
| Mass freeze | TBD | Not started |
| Manual hover test | TBD | Not started |
| Classifier dataset collection | TBD | Not started |
| Release-rig test | TBD | Not started |
| Powered recovery test | TBD | Not started |
