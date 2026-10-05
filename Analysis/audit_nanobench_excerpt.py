"""Audit the already published development excerpt; no fitting or split changes."""
import argparse
import json
from pathlib import Path
import time

import numpy as np

from Analysis.nanobench_data import ROOT, RECORD, MOTORS, GYRO, QUAT, POSITION, VELOCITY, columns, load, sha256
from Analysis.nanobench_replay import documented_models, motor_forces, body_torque, angular_acceleration, rollout

FIXTURE = ROOT / 'Analysis/tests/fixtures/nanobench/excitation.csv'


def audit(output):
    started = time.perf_counter()
    source = json.loads(FIXTURE.with_name('source.json').read_text())
    if sha256(FIXTURE) != source['excerpt_sha256']:
        raise ValueError('development excerpt hash mismatch')
    data = load(FIXTURE)
    protocol = json.loads((RECORD/'protocol.json').read_text())
    model = documented_models(protocol)['cf21plus_firmware']
    pwm = columns(data, MOTORS)
    voltage = data['pwr_pm_vbat']
    omega = columns(data, GYRO)
    dt = np.diff(data['t'])

    # Independent arithmetic: explicit polynomial and r cross F, avoiding the
    # replay's polynomial helper and signed torque matrix.
    v_motor = voltage[:, None] * pwm / 65535
    c0, c1, c2, c3 = model['thrust_coefficients']
    forces = c0 + c1*v_motor + c2*v_motor**2 + c3*v_motor**3
    forces = np.where(pwm == 0, 0., np.maximum(forces, 0.))
    d = model['arm_m']/np.sqrt(2)
    r = np.array([[d, -d, 0], [-d, -d, 0], [-d, d, 0], [d, d, 0]])
    vectors = np.zeros((len(data), 4, 3)); vectors[:, :, 2] = forces
    torque_each = np.cross(r, vectors)
    torque_each[:, :, 2] = forces * model['torque_per_thrust_m'] * [-1, 1, -1, 1]
    torque = torque_each.sum(axis=1)
    jx, jy, jz = model['inertia_kg_m2']
    p, q, w = omega.T
    alpha = np.column_stack(((torque[:, 0]+(jy-jz)*q*w)/jx,
                             (torque[:, 1]+(jz-jx)*w*p)/jy,
                             (torque[:, 2]+(jx-jy)*p*q)/jz))
    implementation_differences = dict(
        max_force_abs_difference_n=float(abs(forces-motor_forces(pwm, voltage, model)).max()),
        max_torque_abs_difference_n_m=float(abs(torque-body_torque(forces, model)).max()),
        max_alpha_abs_difference_rad_s2=float(abs(alpha-angular_acceleration(omega, forces, model)).max()))
    # Exact selection fixed by the existing excerpt: first row and its next
    # interval, plus its first registered (shortest) rollout horizon.
    endpoint = round(min(protocol['horizons_s'])/float(np.median(dt)))
    initial = np.column_stack((columns(data, POSITION), columns(data, VELOCITY),
                              columns(data, QUAT), omega))[:1]
    initial[:, 6:10] /= np.linalg.norm(initial[:, 6:10], axis=1, keepdims=True)
    predictions = rollout(initial, forces[None, :endpoint], dt[None, :endpoint], model, protocol, [1, endpoint])
    intervals = []
    for end in [1, endpoint]:
        predicted_delta = predictions[end][0, 10:13]-omega[0]
        observed_delta = omega[end]-omega[0]
        intervals.append(dict(end_excerpt_row=end, elapsed_s=float(data['t'][end]-data['t'][0]),
            predicted_body_rate_increment_rad_s=predicted_delta.tolist(),
            observed_body_rate_increment_rad_s=observed_delta.tolist(),
            residual_rad_s=(predicted_delta-observed_delta).tolist()))
    # Quaternion-derived body rotation increment, an independent convention
    # check at the first pair; no shift or axis selection is optimized.
    a, b = columns(data, QUAT)[:2]
    a = a/np.linalg.norm(a); b = b/np.linalg.norm(b)
    if np.dot(a, b) < 0: b = -b
    vector = a[3]*b[:3]-b[3]*a[:3]-np.cross(a[:3], b[:3])
    scalar = np.dot(a, b)
    angle = 2*np.arctan2(np.linalg.norm(vector), scalar)
    q_rate = vector * angle/np.linalg.norm(vector)/dt[0] if np.linalg.norm(vector) else vector
    # Audit the declared Euler units against the scalar-last quaternion.
    # Neither the replay nor this diagnostic uses these Euler fields as state.
    quat = columns(data, QUAT)
    quat /= np.linalg.norm(quat, axis=1, keepdims=True)
    x, y, z, scalar_q = quat.T
    euler = np.column_stack((np.arctan2(2*(scalar_q*x+y*z), 1-2*(x*x+y*y)),
                             np.arcsin(np.clip(2*(scalar_q*y-z*x), -1, 1)),
                             np.arctan2(2*(scalar_q*z+x*y), 1-2*(y*y+z*z))))
    published_euler = columns(data, ['roll', 'pitch', 'yaw'])
    def wrapped_rmse(error):
        wrapped = np.arctan2(np.sin(error), np.cos(error))
        return np.sqrt(np.mean(wrapped**2, axis=0)).tolist()
    result = dict(candidate='cf21plus_firmware',
        source_record='Analysis/tests/fixtures/nanobench/source.json',
        source_sha256=source['source_sha256'], excerpt_sha256=source['excerpt_sha256'],
        selection='Existing development excerpt, all rows for arithmetic check, first row for hand calculation, first interval and shortest frozen horizon for increments. No outcome-based selection.',
        scope='Conditional arithmetic/convention diagnostic; no performance threshold or physical validation.',
        protocol_sha256=sha256(RECORD/'protocol.json'), register_sha256=sha256(ROOT/'Engineering Data/platform_crazyflie.csv'),
        replay_sha256=sha256(ROOT/'Analysis/nanobench_replay.py'), audit_sha256=sha256(Path(__file__)),
        implementation_differences=implementation_differences,
        first_row=dict(original_zero_based_row=source['zero_based_data_rows'][0],
            pwm_m1_m4=pwm[0].tolist(), battery_voltage_v=float(voltage[0]),
            motor_voltage_v=v_motor[0].tolist(), per_motor_thrust_n=forces[0].tolist(),
            torque_per_motor_n_m=torque_each[0].tolist(), net_torque_n_m=torque[0].tolist(),
            measured_body_rate_rad_s=omega[0].tolist(),
            predicted_alpha_rad_s2=alpha[0].tolist(),
            euler_first_interval_increment_rad_s=(alpha[0]*dt[0]).tolist(),
            quaternion_pair_average_body_rate_rad_s=q_rate.tolist(),
            gyro_pair_average_body_rate_rad_s=omega[:2].mean(axis=0).tolist()),
        intervals=intervals,
        source_consistency=dict(
            euler_as_radians_quaternion_rmse_rad=wrapped_rmse(published_euler-euler),
            euler_as_declared_degrees_quaternion_rmse_rad=wrapped_rmse(np.deg2rad(published_euler)-euler),
            finding='Excerpt Euler values agree with quaternion-derived radians despite README degree labels. Replay does not use the Euler columns.',
            adjacent_voltage_changes=int(np.count_nonzero(np.diff(voltage))),
            voltage_note='The released voltage changes between adjacent grid rows. The README forward-fill description cannot by itself establish the processing of this CSV; no resampling correction is inferred.'),
        excerpt_grid=dict(rows=len(data), dt_min_s=float(dt.min()), dt_max_s=float(dt.max()),
            fractional_pwm_values=int((pwm!=np.round(pwm)).sum()),
            interpretation='Fractional PWM in an aligned product is not the original uint16 logging stream. Raw block times and interpolation weights are unavailable; grid spacing does not establish independent bandwidth.'),
        result='Independent arithmetic agrees with replay to floating-point rounding; the short recorded rate increment differs substantially. No implementation correction established by this diagnostic.',
        runtime_s=time.perf_counter()-started)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    audit(parser.parse_args().output)
