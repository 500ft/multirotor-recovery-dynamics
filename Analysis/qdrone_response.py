"""Descriptive response summary of the registered QDrone2 development recording."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'Data/qdrone-response'
HEADERS = ['Time (s)', 'zd (m)', 'zw (m)', 'Battery Voltage (V)',
           'm1 (V)', 'm2 (V)', 'm3 (V)', 'm4 (V)', 'xw (m)', 'yw (m)',
           'roll (rad)', 'pitch (rad)', 'yaw (rad)']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_recording(path):
    book = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        if book.sheetnames != ['Sheet1']:
            raise ValueError('unexpected source sheets')
        rows = book['Sheet1'].iter_rows(values_only=True)
        if list(next(rows)) != HEADERS:
            raise ValueError('source columns or units differ from inspected header')
        # Read literal source values, never evaluate spreadsheet formulas or
        # silently substitute their potentially stale cached results.
        data = np.asarray(list(rows), dtype=float)
    finally:
        book.close()
    if data.ndim != 2 or data.shape[1] != len(HEADERS):
        raise ValueError('unexpected recording shape')
    return data


def summarize(data, protocol):
    t, reference, altitude, voltage = data[:, :4].T
    if len(t) < 2 or not np.isfinite(t).all() or not (np.diff(t) > 0).all():
        raise ValueError('finite strictly increasing timestamps required')
    if not np.isfinite(reference).all():
        raise ValueError('cannot identify reference changes with missing command')
    starts = np.flatnonzero(abs(np.diff(reference)) > protocol['step_threshold_m']) + 1
    events = []
    for ordinal, start in enumerate(starts):
        end = t[start] + protocol['horizon_s']
        next_start = int(starts[ordinal + 1]) if ordinal + 1 < len(starts) else None
        event = dict(step=ordinal + 1, source_row_zero_based=int(start), time_s=float(t[start]),
            target_m=float(reference[start]), change_m=float(reference[start]-reference[start-1]),
            direction='up' if reference[start] > reference[start-1] else 'down',
            precommand_voltage_v=float(voltage[start-1]) if np.isfinite(voltage[start-1]) else None,
            precommand_voltage_time_s=float(t[start-1]), horizon_s=protocol['horizon_s'])
        events.append(event)
        if end > t[-1] + 1e-12:
            event.update(status='incomplete', reason='recording_ended'); continue
        if next_start is not None and t[next_start] < end - 1e-12:
            event.update(status='incomplete', reason='next_command_inside_horizon'); continue
        # Use observed timestamps, adding just the prescribed endpoint. This
        # interpolation scores an observed response, not a causal predictor.
        stop = int(np.searchsorted(t, end, side='left'))
        stop = min(stop, len(t)-1)
        if not np.isfinite(data[start:stop+1, 2:4]).all():
            event.update(status='incomplete', reason='nonfinite_response'); continue
        ts = np.r_[t[start:stop], end]
        z = np.r_[altitude[start:stop], np.interp(end, t, altitude)]
        v = np.r_[voltage[start:stop], np.interp(end, t, voltage)]
        error = z - reference[start]
        duration = ts[-1]-ts[0]
        mean = lambda x: float(np.trapezoid(x, ts)/duration)
        event.update(status='complete', bias_m=mean(error), mae_m=mean(abs(error)),
            rmse_m=float(np.sqrt(mean(error**2))), mean_voltage_v=mean(v),
            samples_used=int(stop-start+1), maximum_interval_s=float(np.diff(ts).max()))
    dt = np.diff(t)
    return dict(rows=len(t), time_start_s=float(t[0]), time_end_s=float(t[-1]),
        dt_min_s=float(dt.min()), dt_median_s=float(np.median(dt)), dt_max_s=float(dt.max()),
        columns=HEADERS, detected_steps=len(events), complete_steps=sum(e['status']=='complete' for e in events),
        initial_steady_fragment='Not scored as a commanded response.',
        final_recorded_voltage_v=float(voltage[-1]), events=events)


def plot(data, result, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), layout='constrained')
    t = data[:, 0]
    axes[0].step(t, data[:, 1], where='post', color='#777777', label='Recorded reference')
    axes[0].plot(t, data[:, 2], color='#0072B2', label='Observed altitude', linewidth=.8)
    axes[0].set(ylabel='Altitude (m)', xlabel='Recorded time (s)')
    axes[0].legend(loc='lower left', bbox_to_anchor=(0, 1.01), ncol=2)
    axes[1].plot(t, data[:, 3], color='#009E73', linewidth=.8)
    axes[1].set(ylabel='Battery voltage (V)', xlabel='Recorded time (s)')
    for direction, marker in [('up', '^'), ('down', 'v')]:
        events = [e for e in result['events'] if e['status']=='complete' and e['direction']==direction
                  and e['precommand_voltage_v'] is not None]
        artist = axes[2].scatter([e['precommand_voltage_v'] for e in events], [e['rmse_m'] for e in events],
            c=[e['time_s'] for e in events], vmin=t[0], vmax=t[-1], cmap='viridis',
            marker=marker, s=65, edgecolors='black', linewidths=.4, label=direction.capitalize())
    axes[2].set(xlabel='Last recorded battery voltage before command (V)',
                ylabel=f"Altitude RMSE over {result['protocol_horizon_s']:g} s (m)")
    axes[2].legend(title='Reference change', loc='lower left', bbox_to_anchor=(0, 1.01), ncol=2)
    fig.colorbar(artist, ax=axes[2], label='Command time (s)')
    for ax in axes:
        ax.grid(alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('QDrone2: continuous tracking response during one recorded discharge')
    fig.supxlabel('Development description, original MPC. Repeated steps share one recording; voltage and time co-vary.\n'
                  'Observations: Borbolla-Burillo et al., Zenodo 19464105, CC BY 4.0. No recovery-failure labels.', fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(cache, output, figure, fetch=False):
    started = time.perf_counter()
    sources = json.loads((RECORD/'sources.json').read_text())
    protocol = json.loads((RECORD/'protocol.json').read_text())
    for item in sources['files']:
        path = cache/item['name']
        if fetch and not path.exists():
            cache.mkdir(parents=True, exist_ok=True)
            subprocess.run(['curl', '-fsSL', item['url'], '-o', str(path)], check=True)
        if digest(path) != item['sha256']:
            raise ValueError(f'input hash mismatch: {item["name"]}')
    data = read_recording(cache/protocol['selected_file'])
    result = summarize(data, protocol)
    result.update(dataset='QDrone2', role=protocol['role'], source_sha256=protocol['selected_sha256'],
        protocol_sha256=digest(RECORD/'protocol.json'), code_sha256=digest(Path(__file__)),
        source_record='Data/qdrone-response/sources.json', protocol_horizon_s=protocol['horizon_s'],
        selected_recordings=1, independently_identified_packs=None, archive_independent_run_count=None,
        independence='Repeated commands share one discharge. Archive figure panels do not establish independent runs or pack identities.',
        endpoint='Continuous altitude tracking under original MPC. Source describes a voltage-based stop rule; recording end alone is not a labeled recovery failure.',
        warning_performance='Not evaluated; no independent recovery outcomes or fitted predictor.',
        runtime_s=time.perf_counter()-started)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    if figure:
        plot(data, result, figure)
    print(json.dumps({k:result[k] for k in ['rows', 'detected_steps', 'complete_steps', 'runtime_s']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--figure', type=Path)
    parser.add_argument('--fetch', action='store_true')
    args = parser.parse_args()
    run(args.cache, args.output, args.figure, args.fetch)
