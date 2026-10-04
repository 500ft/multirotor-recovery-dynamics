# Engineering data

The active Crazyflie inputs are in [platform_crazyflie.csv](platform_crazyflie.csv).
Other tables in this directory describe the historical designed aircraft unless
explicitly labeled otherwise. They remain available for reproducing that work.
The [roadmap](../ROADMAP.md) defines current work.

## Parameter evidence

Each row identifies its configuration, unit, source and locator. A manufacturer's
specification, a published measurement, a literature model and a firmware default
are distinct evidence types. None means this project measured a delivered part.

Add identified parameters as separate rows with the training configuration,
result-file location, fit bounds and uncertainty. Keep the published rows so a
reader can compare the initial model with the fit. A later physical measurement
also gets its own configuration and evidence reference. Mass, inertia and
propulsion from different airframes must not be combined silently.

## Firmware thrust curves

The pinned Bitcraze defaults define a per-motor cubic:

`v_motor = v_battery * PWM / 65535`

`T = c0 + c1*v_motor + c2*v_motor**2 + c3*v_motor**3`

The coefficient rows and their source revision are in the CSV. These curves
are candidates for replay after checking the dataset's motor-command semantics,
propellers and voltage range. A better residual alone cannot identify which
propeller was installed. Negative intercepts and nonzero zero-voltage values
also show why a cubic must not be extrapolated to a stopped motor. Document the
valid operating range and the zero-command/dead-zone treatment.

`THRUST_MIN` bounds the firmware's inversion and `THRUST_MAX` scales commands.
The source explicitly describes the maximum as a trade-off for consistency over
battery levels. It is not an experimentally demonstrated physical maximum.
Use the selected firmware/configuration's command path when modeling saturation.
The torque ratio is another firmware default; its applicability needs checking.

In the pinned [motor driver](https://github.com/bitcraze/crazyflie-firmware/blob/f6e0f0a3b526861328caf3296a7ecf00bb915d39/src/drivers/src/motors.c),
`motorsCompensateBatteryVoltage` maps thrust requests to PWM, and
`motorsSetRatio` stores the resulting motor ratio. Trace the collection firmware
before deciding whether NanoBench logs the corresponding signal. Replaying
post-compensation PWM must not apply compensation a second time.

## Source baseline

- [NanoBench dataset and documentation](https://github.com/syediu/nanobench-iros2026/tree/934a1ab92c458cad99c9278a5cb63bf68af6e56c):
  instrumented vehicle, signal units, alignment and per-block sample counts.
  The replay task pins downloaded files and their license at acquisition.
- [Bitcraze platform constants](https://github.com/bitcraze/crazyflie-firmware/blob/f6e0f0a3b526861328caf3296a7ecf00bb915d39/src/platform/interface/platform_defaults_cf2.h):
  firmware model inputs, conditional on build options.
- [CrazySim source](https://github.com/gtfactslab/CrazySim/tree/3ec8b55da4bff887da542a9f314da825460e65be):
  candidate SITL integration; pin its submodules and build options when used.

The upstream firmware and dataset preserve their own licenses. A source link
here does not relicense their code or data under this repository's MIT license.
