# Measurement and Instrumentation Plan

Current prerequisites and completion evidence are in [roadmap A](../ROADMAP.md#a-qualify-component-instrumentation-and-propulsion).
This directory retains useful acquisition, calibration and safety assets. The
historical register and wiring proposal do not establish installed performance
or approval to energize. A thrust cell and INA260 provide no reaction-torque
measurement without a separately qualified method. RPM and component-temperature
channels, stand capacity/resolution, tare, synchronization and containment remain
to be qualified for the selected propulsion configuration.

Analysis is only accepted when the measurement system can resolve the predicted difference. The authoritative register is [instrumentation.csv](../Engineering%20Data/instrumentation.csv).

## Dynamic-Test Synchronization

```mermaid
flowchart LR
    TC[Test controller] -->|GPIO release event| R[Release fixture]
    TC -->|same GPIO event| LED[Visible sync LED]
    TC -->|timestamp| EL[External logger]
    LED --> CAM[High-speed camera]
    EL --> PWR[Current / voltage / RPM]
    FC[Flight controller] -->|IMU + state logs| ALIGN[Post-test alignment]
    CAM --> ALIGN
    EL --> ALIGN
    ALIGN --> DATA[Aligned test dataset]
```

Synchronization requirements:

- one hardware event triggers release and the visible LED
- external logger records the same event
- vehicle logs record the event where hardware permits
- video aligns to the first illuminated frame
- sensor and synchronization uncertainty are reported separately

## Truth Sources

- High-speed calibrated video is the baseline trajectory and deflection truth source.
- Motion capture should be pursued through NYU for final recovery-envelope validation.
- Barometric altitude and integrated IMU position are not sole truth sources for sub-meter tests.
- CAD inertia must be checked using a bifilar or trifilar pendulum.
- Motor-start latency must use actual RPM or current onset, not command time.

## Calibration Records

Store calibration outputs under `Data/Calibration/` using:

```text
YYYY-MM-DD_instrument_calibration-name/
```

Each calibration record must state:

- instrument identifier
- reference standard
- procedure
- raw data
- fitted calibration
- residual/error estimate
- operator and date

## Measurement Readiness Gate

Before a test:

- instrument resolution is smaller than the expected design difference
- uncertainty is estimated
- synchronization path is verified
- cameras and scale/fiducials are fixed before arming
- file naming and test ID are assigned

If measurement uncertainty exceeds the expected design difference, improve the measurement system before drawing a conclusion.
