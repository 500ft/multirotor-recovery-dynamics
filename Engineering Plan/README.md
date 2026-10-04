# Executable Engineering Plan

Historical work for the earlier aircraft. The Crazyflie study follows the
[roadmap](../ROADMAP.md); these old tasks and thresholds do not transfer to it.

This document is the implementation gate structure for the protected micro-UAV project. It separates completed repository infrastructure from physical evidence that must still be produced.

## Core Rules

- Requirements remain fixed single values with relational operators.
- Estimates use best, nominal, and worst values with basis and source.
- Worst-case values verify compliance.
- Every validation gate identifies its truth source, uncertainty, and synchronization method.
- No powered release test occurs before the safety review is approved.
- No missing physical evidence may be replaced by an unsupported claim.

Authoritative registers:

- [Requirements](../Engineering%20Data/requirements.csv)
- [Estimates](../Engineering%20Data/estimates.csv)
- [Mass budget](../Engineering%20Data/mass_budget.csv)
- [Instrumentation](../Engineering%20Data/instrumentation.csv)
- [FMEA](../Engineering%20Data/fmea.csv)
- [CAD mass-properties template](../Engineering%20Data/cad_mass_properties_template.csv)

## Tier 1: Requirements and Mass Properties

Mass freeze rule:

```text
frozen maximum mass = roundup_to_5g(Sigma worst + 5 g)
nominal margin = frozen maximum mass - Sigma nominal
```

Precedence:

1. The freeze rule produces the proposed fixed requirement.
2. If the result exceeds `225 g`, stop and reduce scope.
3. `200 g` is only a provisional planning ceiling.
4. Once frozen, the maximum cannot increase to absorb growth.

Required CAD evidence:

- native complete assembly
- STEP export
- component-level basis tags
- best/nominal/worst mass
- CG coordinates
- complete inertia tensor
- mass-properties report

Status: **catalog component selection complete; blocked on receipt measurements
and CAD modeling**.

## Tier 2: Measurement and Instrumentation

The [instrumentation plan](../Instrumentation/README.md) defines a truth source for each validation gate. Dynamic tests use a common hardware event, a visible synchronization LED, and logged timestamps. Sensor uncertainty and synchronization uncertainty are reported separately.

Status: **register and architecture complete; equipment selection and calibration pending**.

## Tier 3: Recovery and Propulsion Analysis

The repository includes an executable first-order recovery model. It is deliberately conservative and cannot replace 3-D rigid-body simulation or physical validation.

Required model inputs:

- mass, CG, and inertia
- initial attitude and angular velocity
- detection and motor-start latency
- torque and thrust
- battery voltage
- drag coefficient and projected area
- gyro range and estimator margin
- available test height

Required outputs:

- minimum recovery height
- attitude-arrest time
- vertical-velocity-arrest time
- altitude loss
- testable/deferred cases
- sensitivity ranking

Status: **executable preliminary model complete; measured inputs and 3-D extension pending**.

## Tier 4: Guard Structural Analysis

The functional elastic model defines:

```text
k       = radial guard stiffness [N/m]
c_sigma = stress per unit force [Pa/N]
delta   = sqrt(2 E_impact / k)
F_eq    = sqrt(2 E_impact k)
sigma   = c_sigma F_eq
```

Acceptance:

```text
available clearance / delta >= 2
elastic allowable stress / sigma >= 3
```

These equations apply only to low-energy linear-elastic behavior. They do not establish fracture survival. Catastrophic behavior requires physical impact testing.

Status: **executable functional check complete; FEA and physical calibration pending**.

## Tier 5: Test Safety

The [safety plan](../Safety/README.md) and FMEA are hard gates. No powered release is allowed before all required controls are verified and the safety review is approved.

Status: **documentation baseline complete; physical containment, rig, approvals, and checks pending**.

## Tier 6: Controls and Classifier Statistics

The [control architecture](../Controls/README.md) is generated from one state source. The classifier requirements are confidence bounds, not claims of a true zero false-positive rate.

A negative trial is one supervised handling segment (pick up, carry, set down, or place in pocket/bag) of fixed duration, conducted while the vehicle is disarmed or in Stage 1 log-only mode, during which the launch/release classifier must not produce a positive detection. The 300- and 1000-negative-trial counts below are the number of such segments required, run across varied handling conditions, before the corresponding false-positive bound is considered verified.

Stage 1:

```text
95% upper false-positive bound <= 1%
at least 300 negative trials
at least 100 positive trials
sensitivity >= 90%
```

Live-recovery gate:

```text
95% upper false-positive bound <= 0.3%
at least 1000 negative trials
independent cage and manual interlocks
```

Status: **state specification and statistical tooling complete; datasets pending**.

## Verification Gates

| Gate | Required Evidence | Current Status |
|---|---|---|
| Modeling foundation | CAD mass properties, closed mass budget, calibrated instrument plan, verified simulator | INCOMPLETE |
| Bench validation | thrust/current/RPM curves, inertia check, guard calibration, gyro verification | INCOMPLETE |
| Unpowered release | release-rig FMEA controls, synchronized trajectory data, drag/tumble data | INCOMPLETE |
| Powered recovery | approved safety review, classifier gates, verified estimator/recovery envelope | BLOCKED |

## Immediate Execution Order

1. Verify exact purchase SKUs, hardware interfaces, accessories, and stock.
2. Order the locked Stage 1 stack and weigh each delivered component.
3. Build and calibrate the thrust stand; characterize propulsion at 8.4, 7.6,
   and 7.0 V.
4. Create the complete CAD assembly and export mass properties.
5. Freeze the maximum mass using the defined rule and measured thrust limit.
6. Replace simulator placeholders with CAD and bench data.
7. Build and validate the guard and release fixture.
8. Collect unpowered release data before considering powered recovery.
