# Component Specifications Under Load

Compiled 2026-07-03 during the availability audit. These are **vendor/manufacturer
figures** unless marked *derived*; none of them replace the pre-registered bench
gates (`Engineering Plan/stage1-verification-gates.md`). Every flying part must
still be weighed and bench-tested on receipt.

Components are grouped by procurement wave to match
[procurement-2026-07.md](https://github.com/500ft/multirotor-recovery-dynamics/blob/6b5f45e0bb39ffdeeef004dbebd51f8e4d1e7a1b/Engineering%20Plan/procurement-2026-07.md): **Wave 1**
is bench-decisive (order now), **Wave 2** is gated on the EST-REC-007 torque
measurement. Each part carries an **If not in the drone** line — its reuse value
if the drone path dies or the part is displaced from the build.

---

## Wave 1 — bench-decisive

### Propulsion: Happymodel EX1103 11000KV + Gemfan 2023R, 2S (7.4 V)

Vendor bench points (Happymodel Bassline data, reproduced by retailers; not
independent, and 0.4 V above the 7.0 V acceptance condition):

| Current (A) | Thrust (gf) | Power (W) | Efficiency (gf/W) |
|---:|---:|---:|---:|
| 1.07 | 23.0 | 7.92 | 2.90 |
| 2.12 | 40.9 | 15.69 | 2.61 |
| 3.17 | 56.6 | 23.46 | 2.41 |
| 4.05 | 68.6 | 29.97 | 2.29 |
| ~9.20 (max) | 121.9 | 68.08 | 1.79 |

Motor: 3.8 g, 1.5 mm shaft, 9N12P, Φ13.5 × 15.5 mm.

*Derived planning points at the 135.7 g nominal mass (mark: DERIVED, verify on
the thrust stand):*

- Hover thrust: 33.9 gf/motor → interpolated ~1.7 A/motor → ~6.8 A pack draw.
- Estimated hover endurance: 0.8 × 550 mAh / 6.8 A ≈ **3.9 min** (planning only).
- T/W gate floor at 135.7 g: 67.9 gf/motor needed; vendor max claims 121.9 gf.
- Full-throttle pack demand: 4 × 9.2 A = **36.8 A** (sets battery and connector load).

**If not in the drone:** any 2-inch micro build; BLDC characterization
specimens for the thrust-stand rig (order 6, fly 4 — two are spares/specimens).

### Propellers: Gemfan Hurricane 2023-3

- 2.0 in diameter (52.17 mm disk), 2.3 in pitch, 3-blade, 1.5 mm 3-hole
  T-mount, 0.88 g each (official; some retailers list 0.8 g — weigh the set).
- This is the exact prop behind the EX1103 vendor thrust point; any prop change
  reopens the propulsion gate.

**If not in the drone:** consumable — spares feed the thrust-stand sweeps and
any 1103-class build.

### ESC: Flywoo GOKU G45M 45A 2-6S AM32 4-in-1

- 45 A continuous / 50 A burst (10 s) **per channel** — peak motor demand of
  9.2 A uses ~20% of the rating, so the ESC is thermally unconstrained here.
- Input 2-6S per Flywoo (some retailers list 3-6S) — **2S at 7.0 V under load is
  bench-verify, OQ-009**.
- AM32 firmware (GOKU_F4A32_PRO target), bidirectional DShot, telemetry,
  24-128 kHz PWM, DShot300/600/1200.
- Onboard current sensor → ArduPilot battery monitor; calibrate
  `BATT_AMP_PERVLT` on the bench.
- 6.4 g, 33 × 30 × 6.1 mm, 20×20 M3 mount; ships with capacitor + softmounts.

**If not in the drone:** general micro-BLDC driver with current telemetry —
pairs with the EX1103s on the thrust stand or drives any 2-6S motor rig.

### Flight controller: Holybro Kakute H7 Mini v1.5

- STM32H743 @ 480 MHz, ICM-42688-P IMU (v1.5), BMP280 baro, microSD blackbox,
  6 UARTs, 2-6S direct battery input.
- 5 V BEC rated 2 A; the design budgets a conservative **1.5 A**, with 620 mA
  worst-case peripheral load planned (58.7% margin).
- 5.5 g; 20×20 mount (3.6 mm holes, M2 grommets).

**If not in the drone:** generic ArduPilot/PX4 dev board and logging IMU node
for any vehicle (rover, boat, RoboRacer-style data capture) — estimator access
and blackbox make it a portable sensor-fusion testbed.

### Battery: GNB GNB5502S100AHV (2S 550 mAh 100C LiHV, XT30)

- 7.6 V nominal / 8.7 V full (LiHV 4.35 V/cell); acceptance testing at 7.0 V
  under load (3.5 V/cell).
- Claimed 100C → 55 A continuous; full-throttle demand 36.8 A is 67% of the
  claim. **C-rating is not accepted as proof** — sag and temperature are
  bench-gated.
- Charge rate 1C standard (up to 5C claimed); 29 g ±1 g; 12 × 18 × 69 mm.
- XT30 connector: ~30 A continuous class; the 36.8 A point is a transient
  full-throttle peak, not a continuous condition — confirm connector temperature
  during the bench sweep.

**If not in the drone:** bench/portable 2S power for the thrust stand and small
electronics. Batteries age — buy the minimum now (2 packs), 3rd pack in Wave 2.

### Wave 1 support gear (non-flying)

| Item | Role | If not in the drone |
|---|---|---|
| ToolkitRC M6AC charger | LiHV-capable 1-6S balance charger | Lifetime bench charger; also charges future RoboRacer packs |
| 1-2 kg load cell + HX711 + cal masses | Thrust and EST-REC-007 torque measurement | Highest cross-project reuse: guard push test, RoboRacer mast deflection, any force measurement |
| Torque-arm jig (printed) | Per-motor thrust at a known arm → τ_rp | Part of a permanent propulsion-characterization rig |
| Smoke stopper XT30 + LiPo bag | Bench insurance | Permanent shop safety stock |
| Wiring lot + M2 hardware | Harness build | Universal shop stock |

---

## Wave 2 — gated on EST-REC-007 PASS

### Vision: Arduino Nicla Vision (ABX00051)

- STM32H747 dual core (M7 480 MHz + M4 240 MHz), GC2145 2 MP rolling-shutter
  camera, VL53L1X ToF, LSM6DSOX IMU, on-board Wi-Fi/BLE (disable in flight).
- VIN 3.5-5.5 V; **105 mA average at image capture** (datasheet); inference
  peak current and p95 event latency are BENCH_REQUIRED (gates: ≤50 ms
  recovery / ≤100 ms log-only).
- ~19.8 g with headers.

**If not in the drone:** standalone cam + IMU + ToF platform — the
release-detection classifier is a publishable standalone deliverable (TinyML /
Edge Impulse), and the board works for any embedded-vision coursework or demo.

### Positioning: MicoAir MTF-01 (flow + lidar)

- PMW3901 optical flow + ToF rangefinder, one UART, 100 Hz output.
- Range **8 m** @ 90% reflectance/600 Lux, derating to **5 m** @ 60 kLux;
  accuracy 4 cm below 2 m, 2% above.
- Flow FOV 42°; max measurable speed 7 m/s at 1 m height (scales with height).
- 4.0-5.5 V, 500 mW at 5 V (~100 mA); 4.5 g, 29.3 × 17 × 14.5 mm.
- ArduPilot: `SERIAL4_PROTOCOL=1`, `SERIAL4_OPTIONS=1024`, `FLOW_TYPE=5`,
  `RNGFND1_TYPE=10`, sensor `mav_id=200` via MicoAssistant.

**If not in the drone:** velocity/height sensing for any indoor robot —
ArduPilot/PX4/INAV compatible, so it drops onto a rover or a future UAV
unchanged.

### Control link: BetaFPV ELRS Lite RX (Flat Antenna V1.2)

- 2.4 GHz ExpressLRS (CRSF), full-duplex telemetry; vendor range claim
  ~1000 m at 50 mW TX / 500 Hz.
- 5 V supply (no official current figure — budgeted 50/100 mA nominal/worst,
  measure with telemetry active); 0.46 g.

**If not in the drone:** any ELRS-based RC vehicle (needs an ELRS TX — see
support gear below).

### Status: VIFLY Finder Mini + WS2812 LED

- 100 dB self-powered buzzer, internal 40 mAh cell, up to ~7 h alarm after
  battery ejection; 2.7 g.
- WS2812 LED on the dedicated NeoPixel output; charging + LED worst case
  budgeted at 150 mA.

**If not in the drone:** transfers to any future UAV or RC plane — lost-model
alarm value is vehicle-agnostic.

### Wave 2 support gear (non-flying)

| Item | Role | If not in the drone |
|---|---|---|
| RadioMaster Pocket ELRS TX | Manual cage-hover control | Any RC/UAV project; skip if a TX is already owned |
| GNB 550 (3rd pack) | Flight rotation | As Wave 1 packs |
| Frame + guard print + fasteners | Airframe | Filament/hardware stock |
| PVC + net cage | Hover test enclosure | Generic UAV test enclosure |
| Tethered release fixture | Release testing | Generic rigging |
