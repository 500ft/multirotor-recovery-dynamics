# Roadmap

## Finish line

The owner selected the Crazyflie family and a public-data-first investigation,
with simulation before physical validation. No hardware or paid compute is
purchased before G5. The project produces:

1. A dynamics model checked on reserved whole NanoBench flights, with errors
   reported by flight, axis and prediction horizon.
2. A recovery-controller comparison using compiled Crazyflie firmware in
   CrazySim, with the intended onboard sensing and the same plant in both arms.
3. A feasible design comparison with coupled mass, inertia, propulsion and
   battery assumptions, followed by a purchase decision.

NanoBench contains ordinary flight, not tumbling. Its instrumented vehicle is
one configuration; a stock 2.1+ is another. Recovery and variant performance
remain predictions until independent flights test them. Passing a landing
criterion does not establish absence of physical damage.

## Current step

Phase 1 has an executed [NanoBench baseline replay](docs/nanobench-baseline.md),
frozen whole-flight assignments, documented source checks and development
errors. The documented models accumulate substantial angular-motion error
relative to persistence. Final-test predictions remain unexamined.

The [selected-excerpt audit](docs/nanobench-baseline.md#audit-of-the-exposed-development-excerpt)
reproduces the short-rate mismatch and finds no implementation defect in the
force/moment arithmetic. It verifies an explicit data-license grant and exposes
Euler-unit and voltage-processing description issues. The original development
result and blind split remain unchanged.

The [executed timing qualification](docs/nanobench-g1.md) could not recover raw
motor/gyro block times, applied offsets or deployed build settings from the
checked public sources. It reproduces the exposed excerpt's audit and stops
before fitting. G1 remains incomplete; G2 has no final-test evaluation.
The IDSIA alternative has processed motor-speed fields, but its reuse terms and
causal timing need clarification. Owner action: review the
[unsent license/data request](docs/idsia-data-request.txt) for possible outreach.

The proposed replacement finish line for recovery-failure warnings remains
undecided; [M1–M4](OPEN_QUESTIONS.md#pending-owner-decisions) have no recorded
owner answers. The current finish line and G5 purchase restriction stay in force.
No capability calculation or physical warning study is authorized by this
documentation reconciliation.

[Open questions](OPEN_QUESTIONS.md) track unresolved inputs. Historical aircraft
results remain in [current-results](Analysis/current-results.md#historical-designed-aircraft).

## Phases

The owner's ten-week outline is a planning estimate. Advance on the evidence
below; record runtime after the first replay and SITL smoke run before
estimating the larger campaigns. Agent work uses separate result PRs.

| Phase | Work | Owner | Completion evidence |
| --- | --- | --- | --- |
| 0 | Adopt the Crazyflie platform; retain historical work; source parameters | Owner decision, agent implementation | Complete; inputs distinguish configurations and evidence types |
| 1 | Pin NanoBench and replay documented motor models | Agent | Replay and [public-source timing qualification](docs/nanobench-g1.md) executed; frozen splits and original development results preserved. Collection timing/configuration remains unresolved, so G1 is incomplete |
| 2 | Identify only parameters the data can distinguish | Agent | Training-only fits; development checks; untouched final-test metrics; identifiability and residual analysis; comparison on the same protocol |
| 3 | Transfer the checked model to recovery simulation | Agent | Motor and sensor limits, estimator and release-state assumptions, timestep check, and continuous contact/recovery metrics |
| 4 | Run stock firmware in CrazySim | Agent | Pinned firmware/backend/configuration; boot, hover and release logs; motor outputs and supervisor transitions; intended sensing verified |
| 5 | Implement a recovery controller and compare it with stock | Owner and agent | Reproducible paired scenarios; final scenarios held out from tuning; stock, supervisor-only and controller-change arms |
| 6 | Build a component mass and geometry model | Owner with agent support | Configuration-specific mass, CG and inertia; component sources and uncertainty; comparison to flight-identified quantities |
| 7 | Compare feasible design variants | Agent | Coupled configuration table, screening and stable rankings; any further sensitivity analysis justified by the question |
| 8 | Write up results and decide whether to buy | Agent, then owner | Reproduction instructions, failed cases and limitations, report and accurate portfolio/resume; G5 decision |
| 9 | Characterize the purchased configuration and test predictions | Owner | Installed thrust calibration, independent inertia estimate, sensing/logging qualification, approved staged tests, predicted-versus-measured outcomes |

Run a small phase-4 installation/boot smoke test during phase 1 or 2 to expose
integration problems early. Complete its scientific stock comparison after
phase 3. Phase 6 may run alongside identification once the configurations are
specified. The remaining phases stay sequential.

## Replay and identification

- Pin the dataset revision, license, file hashes, firmware constants and
  metadata. Document every excluded recording. The previously inspected
  excitation flight belongs to development; identify it before freezing the
  split. If its identity cannot be recovered, reserve a different flight family
  and disclose the exposure. Final-test errors are evaluated once the model and
  processing choices are frozen; inspecting them earlier makes them development.
- Verify motor order, rotation signs, quaternion order, body/world axes,
  units, timing and whether the logged command is PWM after battery
  compensation. Do not compensate a signal twice. Apply a motor-voltage curve
  only after establishing that input meaning and its applicable range.
- Compare body specific force with body specific force. For body-to-world R,
  `a_world = R @ f_body + g_world`; do not compare accelerometer g units directly
  with world vertical acceleration or use a mean ratio near zero as the score.
- Report force residuals and roll/pitch/yaw rate predictions. Angular
  acceleration is a filtered derivative diagnostic with its processing stated.
  Short open-loop rollouts start from measured state, then propagate without
  feeding truth back. State how drag models obtain velocity; never feed future
  truth into a scored prediction.
- Choose numeric horizons, metrics, filters, fit bounds and practical error
  tolerances on training/development data before final evaluation. Compare the
  unmodified documented model, the fitted model and a simple persistence
  baseline. Compare NanoBench results only when inputs, targets, horizons,
  splits and normalization match; otherwise label the comparison descriptive.
- Fix dataset mass to the published measurement. Check excitation and parameter
  correlations before fitting inertia, thrust gain, torque gain, drag or lag.
  Angular data can constrain torque/inertia ratios without separating the two.
  Fit a reduced model or retain external priors when parameters are inseparable.
  Interpolated telemetry does not provide its nominal grid's full bandwidth;
  do not infer motor lag below the effective sampling/timing resolution.
- Fit alignment, scaling and other learned processing on training data. Use
  whole-flight resampling for intervals and distinguish parameter uncertainty
  from model error. A bootstrap cannot repair weak excitation or extrapolation.
  A residual reduction does not prove battery sag, deck airflow or drag caused
  the discrepancy.

## Recovery and design comparison

Phase 3 specifies the release envelope and a recoverability bound from gravity,
actuator authority, delay and available height before controller tuning. Track
height loss, time to controlled flight, horizontal/vertical contact velocity,
attitude, spin and translational/rotational impact energy. Define any binary
thresholds and their basis before the final campaign; physical damage limits
remain unmeasured. Include initial translation, rotation, attitude, motor state,
battery state and estimator initialization. Ground contact must stop the
free-flight model or enter a separately justified contact model.

Phase 4 logs the firmware supervisor, arming, estimator and motor path. The
[CrazySim source](https://github.com/gtfactslab/CrazySim/tree/3ec8b55da4bff887da542a9f314da825460e65be)
includes external pose and optional sensor models. Confirm the active inputs;
keep external-pose diagnostic runs separate from onboard-only recovery.
Account for gyro range, accelerometer limits and optical-flow/range validity
when tilted. A Python port can support algorithm experiments, but it cannot
complete the compiled-firmware milestone. Prefer another existing machine or
supported backend before narrowing that milestone.

Phase 5 preserves an independent disarm path and crash handling. A supervisor
change must not silently disable all tumble protection. Test uncommanded motion,
ordinary landing, invalid sensors and link loss as well as intended releases.
An out-of-tree app is preferred where supported; record any necessary firmware
patch explicitly. Compare firmware arms under identical sensing and plant
parameters so safety-policy changes cannot masquerade as controller gains.

Phase 6 keeps the dataset vehicle, stock purchase candidate and proposed
variants separate. Matching total mass alone cannot validate inertia. CAD and
identification are independent checks only to the extent their inputs are
independent. Propeller/motor options are discrete hardware combinations; frame
size, arm, mass, inertia, clearance and drag must change together.

Phase 7 starts with feasible configurations and paired scenario screening.
Separate design choices, controller tuning and uncertain physical parameters.
Use Sobol indices only for justified input distributions and dependencies;
report convergence and computational cost. The dataset's listed battery
telemetry is voltage, with no current channel. It cannot by itself identify an
electrical-energy model or endurance for new batteries. Battery-drain analysis
may describe the recorded configuration; variant endurance needs additional
power/capacity evidence and otherwise remains an explicit estimate or is omitted.

## Decision gates

| Gate | When | Evidence needed | If missing |
| --- | --- | --- | --- |
| G1 | After replay | Frames, timing, command semantics and usable excitation established; development metrics defined | Repair ingestion; narrow to observable quantities before fitting |
| G2 | After identification | Final-test errors meet predeclared use tolerances; baseline comparison and identifiable parameter subset reported | Report the miss; revise using development data and obtain a new holdout before another final claim |
| G3 | Before recovery-controller claims | Compiled firmware runs repeatably with known plant and sensor inputs | Use another available backend/host, or report algorithm-only simulation with the firmware milestone incomplete |
| G4 | After controller comparison | Held-out paired scenarios show a useful improvement within the stated model and sensing limits | Diagnose the limiting physics/policy and report unsuccessful cases without inventing a hardware verdict |
| G5 | After write-up | Owner approves an exact configuration, full test budget, a worthwhile registered prediction and a staged safety/measurement plan | Finish this stage as a model study; later hardware work remains an option |

## Cost, safety and publication

Phases 0-8 use public data, open-source tools and existing machines. No hardware,
subscriptions or paid runners are authorized. Public-repository standard
[GitHub-hosted runners](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
have free compute usage; larger runners and excess storage can incur charges.
Keep jobs bounded, use standard runners, and retain only necessary artifacts.

Design the emergency-stop and sensing requirements during simulation. Before
phase 9, revise the [safety plan](Safety/README.md) for the actual aircraft and
facility. A net alone does not qualify the setup. Flow and logging decks are
options to evaluate for mass, sensor validity and bandwidth, not a committed
shopping list. Bench calibration and installed instrumentation precede releases.

Every PR updates this roadmap only when the current step or finish line changes.
The [register guide](Engineering%20Data/README.md) defines input provenance;
identified values never erase their published sources. Result numbers live in
machine-readable outputs; README and resume can quote completed results with
scope. Historical plots stay labeled with their original aircraft. No recovery
validation or endurance claim is published before its supporting work exists.

Rotor-out, parachute development, the V995 fixture and fabrication of the old
designed aircraft are outside this version.
