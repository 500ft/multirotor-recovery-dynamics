# Historical control architecture and recovery state machine

Historical specification for the earlier aircraft. The current study follows the
[roadmap](../ROADMAP.md); these old tasks and thresholds do not transfer to it.

The machine-readable [state specification](state_machine.json) remains because
the frozen historical drop protocol references its failsafe path. No current
controller implementation or flight authorization follows from these states.
The unused Mermaid renderer has been removed; the specification and tests remain.

## Architecture

```mermaid
flowchart LR
    IMU[IMU / estimator] --> FC[Flight controller]
    RC[Manual control + emergency stop] --> FC
    CAM[Camera / marker detector] --> CP[Companion processor]
    CP -->|bounded high-level setpoints| FC
    SM[Recovery state machine] --> FC
    HEALTH[Battery / gyro / link / cage health] --> SM
    FC --> ESC[4-in-1 ESC]
    ESC --> MOT[Four motors]
    FC --> LOG[Flight and state logs]
    CP --> LOG
```

The companion processor never commands individual motors. Manual override and critical flight-controller failsafes take priority.

## Recovery State Machine

```mermaid
stateDiagram-v2
    [*] --> SAFE_IDLE
    SAFE_IDLE --> DETECTION_CANDIDATE: motion_candidate
    DETECTION_CANDIDATE --> AIRBORNE_CONFIRMED: classifier_passes
    AIRBORNE_CONFIRMED --> RECOVERY_ALLOWED: all_safety_checks_pass
    RECOVERY_ALLOWED --> RECOVERY_ACTIVE: recovery_command
    RECOVERY_ACTIVE --> STABLE_HOVER: stable_hover_confirmed
    STABLE_HOVER --> TARGET_TRACK: tracking_enabled
    TARGET_TRACK --> STABLE_HOVER: target_lost / hold_then_land
    RECOVERY_ACTIVE --> FAILSAFE: timeout / gyro_saturation / estimator_invalid / low_voltage / abort
    SAFE_IDLE --> FAILSAFE: critical_fault
    DETECTION_CANDIDATE --> FAILSAFE: critical_fault
    AIRBORNE_CONFIRMED --> FAILSAFE: critical_fault
    RECOVERY_ALLOWED --> FAILSAFE: critical_fault
    STABLE_HOVER --> FAILSAFE: critical_fault
    TARGET_TRACK --> FAILSAFE: critical_fault
```

Every transition must log its trigger, evaluated guards, timeout, command, and reason.

## Estimator Envelope

- Initial angular rate must remain below 80% of the verified gyro measurement limit.
- Configured firmware gyro range must be verified against the IMU datasheet.
- Recovery is rejected on gyro saturation or invalid estimator health.
- External video or motion capture must validate onboard attitude estimates during controlled tests.
- No recovery claim is valid outside the tested estimator envelope.
