"""Documented-parameter NanoBench replay. No parameter fitting or controller."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from Analysis.nanobench_data import (
    ROOT, RECORD, MOTORS, POSITION, VELOCITY, QUAT, GYRO, ACC, REQUIRED,
    columns, load, sha256,
)

REGISTER = ROOT / 'Engineering Data/platform_crazyflie.csv'


def documented_models(protocol):
    with REGISTER.open() as f:
        register = list(csv.DictReader(f))
    by_id = {r['id']: r for r in register}
    mass = by_id[protocol['mass_register_id']]
    assert mass['unit'] == 'g'
    inertia = [by_id[i] for i in protocol['inertia_register_ids']]
    assert all(r['unit'] == 'kg m^2' for r in inertia)
    arm = by_id[protocol['arm_register_id']]
    assert arm['unit'] == 'm'
    models = {}
    for name in protocol['curves']:
        values = {r['parameter']: float(r['value']) for r in register if r['platform'] == name}
        models[name] = dict(mass_kg=float(mass['value']) / 1000,
            inertia_kg_m2=[float(r['value']) for r in inertia], arm_m=float(arm['value']),
            thrust_coefficients=[values[f'VMOTOR2THRUST{i}'] for i in range(4)],
            torque_per_thrust_m=values['THRUST2TORQUE'],
            inversion_min_n=values['THRUST_MIN'], command_max_n=values['THRUST_MAX'])
    return models


def motor_forces(pwm, voltage, model):
    """Post-compensation PWM -> motor voltage -> per-motor newtons.

    THRUST_MAX is intentionally absent from the calculation. Stopped motors
    produce zero; negative polynomial values are clipped, without inventing a
    calibrated dead zone. Inputs can have leading batch dimensions.
    """
    pwm, voltage = np.asarray(pwm), np.asarray(voltage)
    if (not np.isfinite(pwm).all() or not np.isfinite(voltage).all()
            or np.any((pwm < 0) | (pwm > 65535)) or np.any(voltage <= 0)):
        raise ValueError('invalid PWM or battery voltage')
    v_motor = pwm / 65535.0 * voltage[..., None]
    force = np.polynomial.polynomial.polyval(v_motor, model['thrust_coefficients'])
    return np.where(pwm == 0, 0.0, np.maximum(force, 0.0))


def body_torque(forces, model):
    """M1..M4; FLU body axes, SI mixer at the collection firmware revision."""
    d = model['arm_m'] / np.sqrt(2)
    k = model['torque_per_thrust_m']
    matrix = np.array([[-d, -d, d, d], [-d, d, d, -d], [-k, k, -k, k]])
    return np.asarray(forces) @ matrix.T


def qmul(a, b):
    """Hamilton product, scalar-last body-to-world quaternions."""
    return np.concatenate((a[..., 3:] * b[..., :3] + b[..., 3:] * a[..., :3]
        + np.cross(a[..., :3], b[..., :3]),
        a[..., 3:] * b[..., 3:] - np.sum(a[..., :3] * b[..., :3], axis=-1, keepdims=True)), axis=-1)


def rotate(q, vector):
    q = q / np.linalg.norm(q, axis=-1, keepdims=True)
    xyz = q[..., :3]
    uv = 2 * np.cross(xyz, vector)
    return vector + q[..., 3:] * uv + np.cross(xyz, uv)


def angular_acceleration(omega, forces, model):
    inertia = np.asarray(model['inertia_kg_m2'])
    return (body_torque(forces, model) - np.cross(omega, inertia * omega)) / inertia


def derivative(state, forces, model, gravity):
    # State layout: world position, world velocity, body->world xyzw, body rate.
    omega = state[..., 10:13]
    specific = np.zeros_like(omega)
    specific[..., 2] = forces.sum(axis=-1) / model['mass_kg']
    acceleration = rotate(state[..., 6:10], specific) + np.array([0., 0., -gravity])
    omega_q = np.concatenate((omega, np.zeros_like(omega[..., :1])), axis=-1)
    return np.concatenate((state[..., 3:6], acceleration,
        0.5 * qmul(state[..., 6:10], omega_q),
        angular_acceleration(omega, forces, model)), axis=-1)


def propagate(initial, forces, interval_s, model, gravity, maximum_step):
    """One ZOH input interval, batched RK4. There is no measured-state argument."""
    state = np.array(initial, dtype=float, copy=True)
    intervals = np.broadcast_to(np.asarray(interval_s), state.shape[:-1])
    steps = max(1, int(np.ceil(np.max(intervals) / maximum_step)))
    h = intervals[..., None] / steps
    for _ in range(steps):
        k1 = derivative(state, forces, model, gravity)
        k2 = derivative(state + h*k1/2, forces, model, gravity)
        k3 = derivative(state + h*k2/2, forces, model, gravity)
        k4 = derivative(state + h*k3, forces, model, gravity)
        state += h * (k1 + 2*k2 + 2*k3 + k4) / 6
        state[..., 6:10] /= np.linalg.norm(state[..., 6:10], axis=-1, keepdims=True)
    return state


def rollout(initial, forces, intervals, model, protocol, endpoints):
    """Propagate all windows without resets; inputs [window, interval, motor]."""
    state = np.array(initial, copy=True)
    outputs = {}
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        for j in range(forces.shape[1]):
            state = propagate(state, forces[:, j], intervals[:, j], model,
                              protocol['gravity_m_s2'], protocol['integration_step_s'])
            if j + 1 in endpoints:
                outputs[j + 1] = state.copy()
    return outputs


def persistence(initial, elapsed):
    state = initial.copy()
    state[:, :3] += elapsed[:, None] * initial[:, 3:6]
    angle = np.linalg.norm(initial[:, 10:13], axis=1) * elapsed
    # sin(angle/2)/|omega| = (elapsed/2)*sinc(angle/(2*pi)), including zero.
    xyz = initial[:, 10:13] * (elapsed/2 * np.sinc(angle/(2*np.pi)))[:, None]
    increment = np.column_stack((xyz, np.cos(angle/2)))
    state[:, 6:10] = qmul(initial[:, 6:10], increment)
    return state


def trailing_mean(values, samples):
    out = np.full_like(values, np.nan, dtype=float)
    windows = np.lib.stride_tricks.sliding_window_view(values, samples, axis=0)
    out[samples-1:] = windows.mean(axis=-1)
    return out


def all_valid(valid, samples):
    out = np.zeros(len(valid), dtype=bool)
    out[samples-1:] = np.convolve(valid.astype(int), np.ones(samples, dtype=int), 'valid') == samples
    return out


def eligible_rows(data, protocol):
    t = data['t']; pwm = columns(data, MOTORS); q = columns(data, QUAT)
    v = data['pwr_pm_vbat']; low, high = protocol['battery_range_v']
    reasons = {
        'nonfinite_required': ~np.isfinite(columns(data, REQUIRED)).all(axis=1),
        'ground_height': data['pz'] < protocol['minimum_world_height_m'],
        'motor_inactive': (pwm <= protocol['minimum_pwm_active']).any(axis=1),
        'pwm_out_of_range': ((pwm < 0) | (pwm > 65535)).any(axis=1),
        'voltage_out_of_range': (v < low) | (v > high),
        'quaternion_norm': abs(np.linalg.norm(q, axis=1)-1) > protocol['quaternion_norm_tolerance'],
        'flight_edge': (t-t[0] < protocol['edge_trim_s']) | (t[-1]-t < protocol['edge_trim_s']),
        'time_gap': np.r_[False, (np.diff(t) <= 0) | (np.diff(t) > protocol['maximum_grid_gap_s'])],
    }
    valid = ~np.logical_or.reduce(list(reasons.values()))
    return valid, {k: int(v.sum()) for k, v in reasons.items()}


def append_metrics(rows, flight, model, metric, horizon, residual, axes, unit):
    for i, axis in enumerate(axes):
        error = residual[:, i]
        finite = np.isfinite(error)
        good = error[finite]
        rows.append(dict(flight=flight, model=model, metric=metric, horizon_s=horizon,
            axis=axis, unit=unit, count=len(good), failed_count=int((~finite).sum()),
            bias=float(np.mean(good)) if len(good) else '',
            rmse=float(np.sqrt(np.mean(good**2))) if len(good) else ''))


def append_state_metrics(rows, flight, name, horizon, predicted, observed):
    # If a window fails numerically, exclude it from every metric, report failure.
    prediction = predicted.copy()
    prediction[~np.isfinite(prediction).all(axis=1)] = np.nan
    for metric, slc, unit in [('position', slice(0, 3), 'm'),
            ('velocity', slice(3, 6), 'm/s'), ('body_rate', slice(10, 13), 'rad/s')]:
        append_metrics(rows, flight, name, metric, horizon,
                       prediction[:, slc] - observed[:, slc], 'xyz', unit)
    dot = np.abs(np.sum(prediction[:, 6:10] * observed[:, 6:10], axis=1))
    angle = 2 * np.arccos(np.clip(dot, 0., 1.))
    append_metrics(rows, flight, name, 'attitude_angle', horizon, angle[:, None], ['angle'], 'rad')


def evaluate_flight(data, flight, models, protocol):
    """Diagnostics may use measured instantaneous rate; rollouts use starts only."""
    t = data['t']; dt = np.diff(t); median_dt = float(np.median(dt))
    valid, exclusions = eligible_rows(data, protocol)
    q = columns(data, QUAT); q /= np.linalg.norm(q, axis=1, keepdims=True)
    truth = np.column_stack((columns(data, POSITION), columns(data, VELOCITY), q, columns(data, GYRO)))
    endpoints = {round(h/median_dt): h for h in protocol['horizons_s']}
    if len(endpoints) != len(protocol['horizons_s']) or min(endpoints) < 1:
        raise ValueError('grid cannot resolve requested horizons')
    longest = max(endpoints)
    stride = max(1, round(protocol['start_stride_s']/median_dt))
    candidates = np.arange(0, len(data)-longest, stride)
    starts = candidates[all_valid(valid, longest+1)[candidates+longest]]
    index = starts[:, None] + np.arange(longest)
    intervals = dt[index]
    pwm = columns(data, MOTORS); voltage = data['pwr_pm_vbat']
    n = protocol['diagnostic_trailing_mean_samples']
    diag_mask = all_valid(valid, n+1)
    measured_specific = columns(data, ACC) * protocol['gravity_m_s2']
    observed_force = trailing_mean(measured_specific, n)
    averaged_rate = trailing_mean(truth[:, 10:13], n)
    observed_alpha = np.vstack((np.full((1, 3), np.nan), np.diff(averaged_rate, axis=0)/dt[:, None]))
    rows, ranges = [], {}
    # Evaluate curves on eligible rows only; rejected corrupt inputs never enter physics.
    for name, model in models.items():
        force = np.zeros((len(data), 4))
        force[valid] = motor_forces(pwm[valid], voltage[valid], model)
        positive = pwm[valid] > 0
        ranges[name] = dict(below_inversion_min_motor_samples=int((positive & (force[valid] < model['inversion_min_n'])).sum()),
            above_command_max_motor_samples=int((force[valid] > model['command_max_n']).sum()),
            eligible_motor_voltage_min_v=float(np.min(pwm[valid]/65535 * voltage[valid, None])) if valid.any() else None,
            eligible_motor_voltage_max_v=float(np.max(pwm[valid]/65535 * voltage[valid, None])) if valid.any() else None)
        specific = np.zeros((len(data), 3)); specific[:, 2] = force.sum(axis=1)/model['mass_kg']
        alpha = angular_acceleration(truth[:, 10:13], force, model)
        append_metrics(rows, flight, name, 'body_specific_force', 0,
                       (trailing_mean(specific, n)-observed_force)[diag_mask], 'xyz', 'm/s^2')
        append_metrics(rows, flight, name, 'angular_acceleration_diagnostic', 0,
                       (trailing_mean(alpha, n)-observed_alpha)[diag_mask], 'xyz', 'rad/s^2')
        if len(starts):
            predictions = rollout(truth[starts], force[index], intervals, model, protocol, endpoints)
            for endpoint, horizon in endpoints.items():
                append_state_metrics(rows, flight, name, horizon,
                                     predictions[endpoint], truth[starts+endpoint])
    previous = np.vstack((measured_specific[:1], measured_specific[:-1]))
    append_metrics(rows, flight, 'persistence', 'body_specific_force', 0,
                   (trailing_mean(previous, n)-observed_force)[diag_mask], 'xyz', 'm/s^2')
    append_metrics(rows, flight, 'persistence', 'angular_acceleration_diagnostic', 0,
                   -observed_alpha[diag_mask], 'xyz', 'rad/s^2')
    spans = {}
    for endpoint, horizon in endpoints.items():
        elapsed = t[starts+endpoint]-t[starts]
        spans[str(horizon)] = dict(min_s=float(elapsed.min()), max_s=float(elapsed.max())) if len(starts) else None
        if len(starts):
            append_state_metrics(rows, flight, 'persistence', horizon,
                                 persistence(truth[starts], elapsed), truth[starts+endpoint])
    # Convention check on development data: published Vicon WORLD rate -> BODY rate.
    conjugate = q.copy(); conjugate[:, :3] *= -1
    vicon_body = rotate(conjugate, columns(data, ['wx_vicon', 'wy_vicon', 'wz_vicon']))
    append_metrics(rows, flight, 'frame_check', 'vicon_body_rate_minus_imu', 0,
                   (trailing_mean(vicon_body-truth[:, 10:13], n))[diag_mask], 'xyz', 'rad/s')
    detail = dict(flight=flight, eligible_rows=int(valid.sum()), excluded_rows=int((~valid).sum()),
        excluded_by_reason_overlapping=exclusions, diagnostic_rows=int(diag_mask.sum()),
        candidate_windows=len(candidates), eligible_windows=len(starts),
        excluded_windows=len(candidates)-len(starts), actual_horizon_spans=spans,
        candidate_ranges=ranges, status='evaluated' if len(starts) else 'excluded_no_eligible_windows')
    return rows, detail


def select_models(protocol, split, frozen_model, protocol_hash):
    models = documented_models(protocol)
    if split == 'final_test' and (frozen_model is None or protocol_hash != sha256(RECORD/'protocol.json')):
        raise ValueError('final_test requires a frozen fitted-model file and matching --protocol-sha256')
    if frozen_model:
        frozen = json.loads(frozen_model.read_text())
        if frozen['protocol_sha256'] != sha256(RECORD/'protocol.json'):
            raise ValueError('fitted model uses a different protocol')
        # A future identification result supplies this same physical model schema.
        # Its provenance must cite the training artifact and a pre-evaluation commit.
        if not frozen.get('training_result') or not frozen.get('frozen_commit'):
            raise ValueError('fitted model needs training_result and frozen_commit')
        fitted = frozen['model']
        if set(fitted) != set(next(iter(models.values()))):
            raise ValueError('fitted model must have the documented physical parameter keys')
        if (fitted['mass_kg'] != next(iter(models.values()))['mass_kg']
                or np.shape(fitted['inertia_kg_m2']) != (3,)
                or np.shape(fitted['thrust_coefficients']) != (4,)
                or not np.isfinite(np.concatenate([np.atleast_1d(v) for v in fitted.values()])).all()
                or min(fitted['inertia_kg_m2']) <= 0 or fitted['arm_m'] <= 0
                or fitted['torque_per_thrust_m'] <= 0):
            raise ValueError('invalid fitted physical parameters or changed measured mass')
        models['frozen_fitted'] = fitted
    return models


def run(cache, output, split, frozen_model=None, protocol_hash=None):
    started = time.perf_counter()
    protocol = json.loads((RECORD/'protocol.json').read_text())
    models = select_models(protocol, split, frozen_model, protocol_hash)
    assignments = json.loads((RECORD/'split.json').read_text())['flights']
    inventory = json.loads((RECORD/'inventory.json').read_text())['flights']
    metrics, details = [], []
    # Read only the requested split. Inventory contains no model errors.
    for record in inventory:
        flight = record['path']
        if assignments[flight] != split:
            continue
        if record['duplicate_of'] or record['missing_required']:
            details.append(dict(flight=flight, status='excluded_duplicate_or_missing_columns',
                                duplicate_of=record['duplicate_of']))
            continue
        path = cache/flight
        if sha256(path) != record['sha256']:
            raise ValueError(f'flight hash mismatch: {flight}')
        rows, detail = evaluate_flight(load(path), flight, models, protocol)
        metrics.extend(rows); details.append(detail)
        print(f"{Path(flight).stem}: {detail['eligible_windows']} rollout starts", flush=True)
    if not metrics:
        raise ValueError('no eligible recordings')
    output.mkdir(parents=True, exist_ok=True)
    with (output/f'{split}-errors.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics[0])); writer.writeheader(); writer.writerows(metrics)
    run_record = dict(split=split, runtime_s=time.perf_counter()-started,
        python=platform.python_version(), numpy=np.__version__, machine=platform.machine(),
        code_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        replay_code_sha256=sha256(Path(__file__)), data_code_sha256=sha256(ROOT/'Analysis/nanobench_data.py'),
        source_sha256=sha256(RECORD/'sources.json'), split_sha256=sha256(RECORD/'split.json'),
        protocol_sha256=sha256(RECORD/'protocol.json'), register_sha256=sha256(REGISTER),
        inventory_sha256=sha256(RECORD/'inventory.json'),
        frozen_model_sha256=sha256(frozen_model) if frozen_model else None, flights=details)
    (output/f'{split}-run.json').write_text(json.dumps(run_record, indent=2, allow_nan=False)+'\n')
    print(f'Wrote {len(metrics)} metric rows in {run_record["runtime_s"]:.2f} s')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--split', choices=['development', 'training', 'final_test'], default='development')
    p.add_argument('--frozen-model', type=Path)
    p.add_argument('--protocol-sha256')
    args = p.parse_args()
    run(args.cache, args.output, args.split, args.frozen_model, args.protocol_sha256)


if __name__ == '__main__':
    main()
