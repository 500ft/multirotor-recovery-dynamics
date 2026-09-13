# Bench-first fixture preparation — 2026-09-09

Status: design recommendations, not released fixture geometry, calibration or permission to run a motor. [Input requests](input-requests.csv) are generated from every pending row in [parameters.csv](parameters.csv); edit the register only when evidence is accepted, then regenerate with `python cad/input_requests.py`. CI tests detect drift.

## Decisions made now

| Decision | Reason, evidence and limit |
| --- | --- |
| Model the single-motor thrust stand before vehicle packaging | The gate needs six individual motor curves at 7.0 V, not a finished airframe or six-motor vehicle. Preserve the existing symmetric four-motor derivation and motor roster. |
| Shortlist Phidgets 3132_0, 780 g single-point cell with a bridge interface | Its manufacturer specifies 780 g capacity, M3x0.5 threads, and repeatability/nonlinearity/hysteresis each 390 mg. Nominal capacity is 7.65 N using the register's 9.81 convention. The motor manufacturer's largest listed point is 121.9 g at 7.4 V with a 2023R prop: about 1.20 N. This is useful sizing evidence, NOT our 7.0 V thrust result or permission to substitute a different prop. |
| Keep cell selection proposed until total installed load and uncertainty are checked | Capacity must cover motor/adapter dead weight, thrust, transient loads and load direction. The published 936 g overload is not an operating allowance. Consumer-grade specifications do not establish installed accuracy, vibration performance or calibration. |
| Use a metal load path and removable motor adapter | A replaceable adapter accommodates a verified motor interface without remodeling the sensor support. Avoid printed polymer as the primary metrology load path because creep and mount compliance add unmeasured drift. Material thickness and anchor coordinates await fixture calculation, not a guessed “stiff” label. |
| Prefer direct axial thrust sensing | It avoids adding pivot friction to the measured force. The register's stand-calibration lever describes a lever-based route; do not invent a length if that route is not used. A later explicit contract amendment must mark applicability before fixture release. Vehicle authority radius remains a separate measured quantity. |

Primary sources inspected 2026-09-09: [Happymodel EX1103 specification and bench table](https://www.happymodel.cn/index.php/2022/09/05/bassline-spare-part-ex1103-kv11000-brushless-motor/), [Phidgets 3132 specifications](https://www.phidgets.com/?prodid=223), [manufacturer mechanical drawing, dated 2025-06-10](https://www.phidgets.com/productfiles/3132/3132_0/Documentation/3132_0_Mechanical.pdf). The drawing exposes multiple interface dimensions and four M3x0.5 through holes; a single “mount spacing” number is insufficient to describe both end interfaces. Transcribe dimensioned coordinates only after inspecting the actual drawing and identifying the delivered revision. No drawing dimensions are inferred from a photograph.

The motor page confirms envelope/shaft values already in the register, but its accessible specification table does not establish the mounting hole coordinates, screw penetration or matching prop screw spacing. Those stay pending. Vendor nominal is not measured fit.

## Geometry contract before a model

Implemented as `cad/bench/fixture-contract.json` (DR-CAD-12): `python cad/fixture_contract.py --check` verifies it against the register, `--release` refuses while any clause is pending.

The next fixture model must consume an identified cell revision, a motor-hole coordinate register with thread/depth, adapter/fastener stack, force-axis datum and actual bench anchors. Export STEP and a machine-readable report covering number of separate solids, each interface coordinate, minimum screw penetration/clearance, force-axis offset, and sensor deflection clearance. Compare numeric metrics against a reviewed parameter contract, not screenshots alone. Tolerances must come from drawings and inspected mating parts; unknown limits block release. No fixture STEP is produced in this task.

Trace the load: prop/motor → adapter → cell loaded end → fixed end → anchored base. Cable forces, off-axis moment, motor torque reaction and containment attachments must not bypass or preload the measurement unintentionally. Record dead load and predicted peak load separately. A CAD collision check does not prove structural stability or prop containment.

## One bounded remaining physical sitting

1. Identify motor/prop/cell revisions and photograph labels with a scale. Verify motor-hole coordinates, hole/thread gauge and usable depth; measure installed adapter/fastener stack without bottoming screws into windings.
2. Measure actual bench anchors and vehicle center-to-motor radius. Record instrument ID, resolution, repeated readings, datum and units from the generated sheet. The 0.060 m planning radius cannot populate raw `arm_m`.
3. Characterize the installed load cell with traceable loads in the intended direction, including zero return, hysteresis, cable routing and ADC/bridge behavior. Retain uncertainties, not just a calibration line.
4. Complete the existing [safety checklist](../../Instrumentation/propulsion-bench-safety-checklist.md) before any powered work: containment, restrained assembly, props-off commissioning, electrical protection, reachable shutdown and battery handling remain prerequisites.

Follow the [authority evidence contract](../../docs/specs/measured-authority-gate/evidence-contract.md): raw `thrust_n` is measured force; `arm_m` is vehicle geometry. Neither nominal vendor thrust nor a stand lever may fill them. The authority calculation and uncertainty artifact must explain the mixer mapping; the admission checker alone does not prove it.

## Why the remaining inputs cannot be researched away

A website can specify a nominal cell or motor, but cannot identify delivered revisions, bench anchors, installed cable forces, screw clearance or calibrated geometry. This task resolves selection rationale and request routing; it deliberately does not close DR-CAD-02 or the measured-authority gate.
