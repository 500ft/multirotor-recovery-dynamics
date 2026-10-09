"""Render the stored QDrone2 development result without recalculating metrics."""
import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

from Analysis import figure_style as fs

ROOT = Path(__file__).resolve().parents[1]
GRAY = fs.GRAY
DIRECTIONS = [('up', '^', fs.QDRONE['up']), ('down', 'v', fs.QDRONE['down'])]


def make_figure(data, result):
    """All traces use source samples; scatter values come from stored events."""
    complete = [e for e in result['events'] if e['status'] == 'complete']
    incomplete = [e for e in result['events'] if e['status'] != 'complete']
    rmse = {d: [e['rmse_m'] for e in complete if e['direction'] == d] for d, _, _ in DIRECTIONS}
    split = bool(rmse['up'] and rmse['down']) and min(rmse['down']) > max(rmse['up'])
    with fs.style():
        fig = plt.figure(figsize=(7.2, 8.0))
        outer = fig.add_gridspec(2, 1, height_ratios=[2.15, 1.05], left=.105, right=.88,
                                 bottom=.125, top=.845, hspace=.42)
        traces = outer[0].subgridspec(2, 1, height_ratios=[1.15, 1], hspace=.32)
        errors = outer[1].subgridspec(1, 2, wspace=.12)
        altitude = fig.add_subplot(traces[0])
        voltage = fig.add_subplot(traces[1], sharex=altitude)
        by_time = fig.add_subplot(errors[0])
        by_voltage = fig.add_subplot(errors[1], sharey=by_time)
        t = data[:, 0]
        altitude.plot(t, data[:, 2], color=fs.QDRONE['altitude'], lw=1.0, label='Observed')
        altitude.step(t, data[:, 1], where='post', color=fs.QDRONE['reference'], lw=1.0,
                      ls='--', label='Reference')
        altitude.set(title='Altitude follows the recorded reference steps', ylabel='Altitude (m)')
        altitude.legend(loc='lower right', bbox_to_anchor=(1, 1.0), ncol=2, handlelength=2.2)
        altitude.tick_params(labelbottom=False)
        voltage.plot(t, data[:, 3], color=fs.QDRONE['voltage'], lw=.6)
        voltage.set(title='Voltage declines across the recording and swings at each command',
                    ylabel='Voltage (V)', xlabel='Recorded time (s)', xlim=(t[0], t[-1]))
        # A vertical reference shows the censored window without inventing an RMSE.
        for e in incomplete:
            for ax in (altitude, voltage):
                ax.axvline(e['time_s'], color=GRAY, ls=':', lw=1)
        for direction, marker, color in DIRECTIONS:
            events = [e for e in complete if e['direction'] == direction]
            for ax, key in ((by_time, 'time_s'), (by_voltage, 'precommand_voltage_v')):
                selected = [e for e in events if e[key] is not None]
                ax.scatter([e[key] for e in selected], [e['rmse_m'] for e in selected],
                           marker=marker, color=color, s=30, edgecolor='white',
                           linewidth=.35, zorder=3)
        by_time.set(title='Every down step has a higher\nRMSE than every up step' if split
                    else 'Response error over time',
                    xlabel='Command time (s)',
                    ylabel=f"{result['protocol_horizon_s']:g} s altitude RMSE (m)",
                    xlim=(t[0], t[-1]))
        by_voltage.set(title='The gap holds across the\nprecommand voltage range' if split
                       else 'The same errors against voltage',
                       xlabel='Precommand voltage (V)')
        # The RMSE values span a narrow band, so the axis starts at the data floor
        # with labelled non-zero ticks rather than at zero.
        values = rmse['up'] + rmse['down']
        lo = np.floor((min(values) - .004) * 100) / 100
        hi = np.ceil((max(values) + .004) * 100) / 100
        by_time.set_ylim(lo, hi)
        by_time.set_yticks(np.round(np.linspace(lo, hi, 3), 3))
        by_voltage.tick_params(labelleft=False)
        right = max(e['precommand_voltage_v'] for e in complete)
        for direction, marker, color in DIRECTIONS:
            name = {'up': 'Up', 'down': 'Down'}[direction]
            glyph = {'up': '\u25b2', 'down': '\u25bc'}[direction]
            by_voltage.annotate(f'{glyph} {name}', (1.02, np.mean(rmse[direction])),
                                xycoords=('axes fraction', 'data'), va='center',
                                fontsize=fs.SMALL, color=color, annotation_clip=False)
        for ax in (altitude, voltage, by_time, by_voltage):
            ax.grid(axis='y')
            ax.set_axisbelow(True)
            ax.xaxis.set_major_locator(MaxNLocator(6))
        by_time.xaxis.set_major_locator(MaxNLocator(5))
        by_voltage.xaxis.set_major_locator(MaxNLocator(4))
        for ax, letter, dx, dy in ((altitude, 'a', -.085, .012), (voltage, 'b', -.085, .012),
                                   (by_time, 'c', -.085, .045), (by_voltage, 'd', -.03, .045)):
            fs.panel_letter(fig, ax, letter, dx=dx, dy=dy)
        fig.text(.02, .985, f"QDrone2 tracked {result['complete_steps']} complete altitude steps "
                 'during one recorded discharge', va='top')
        fig.text(.02, .952, 'DEVELOPMENT OBSERVATIONS \u00b7 original MPC \u00b7 no recovery-failure labels',
                 va='top', fontsize=fs.SMALL, color=GRAY)
        fig.text(.02, .925, f"{result['complete_steps']} complete response windows; "
                 f"{len(incomplete)} incomplete (dotted line).", va='top', fontsize=fs.SMALL)
        fig.text(.02, .045, 'Repeated commands share one recording. Demand, voltage and '
                 'elapsed time co-vary.', fontsize=fs.SMALL)
        fig.text(.02, .018, 'Observations: Borbolla-Burillo et al. \u00b7 Zenodo 19464105 \u00b7 CC BY 4.0',
                 fontsize=fs.SMALL, color=GRAY)
    return fig


def plot(data, result, path):
    fig = make_figure(data, result)
    with fs.style():
        fs.save(fig, path, ('png', 'pdf'))
    plt.close(fig)


def write_tables(result, output):
    """Display precision only; CSV keeps the stored floats and every event."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    fields = ['step', 'direction', 'time_s', 'precommand_voltage_v',
              'bias_m', 'mae_m', 'rmse_m', 'status', 'reason']
    with (output/'qdrone-response.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: e.get(key, '') for key in fields} for e in result['events'])
    lines = ['# QDrone2 response table', '',
             'Generated from [results.json](../Data/qdrone-response/results.json).',
             '[Download CSV](qdrone-response.csv) for stored precision; display rounding is not measurement uncertainty.',
             'Rows follow command time. Missing metrics mean an incomplete window, never zero.', '',
             '| Step | Direction | Time [s] | Precommand [V] | Bias [m] | MAE [m] | RMSE [m] | Window |',
             '| ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- |']
    for e in result['events']:
        value = lambda key, digits: f"{e[key]:.{digits}f}" if e.get(key) is not None else 'N/A'
        status = 'Complete' if e['status'] == 'complete' else 'Incomplete: ' + e['reason'].replace('_', ' ')
        lines.append(f"| {e['step']} | {e['direction'].capitalize()} | {value('time_s', 3)} | "
                     f"{value('precommand_voltage_v', 3)} | {value('bias_m', 4)} | {value('mae_m', 4)} | "
                     f"{value('rmse_m', 4)} | {status} |")
    lines += ['', 'Original MPC; one development discharge. Repeated steps do not identify independent packs.',
              'Observations: Borbolla-Burillo et al., [Zenodo 19464105](https://doi.org/10.5281/zenodo.19464105), CC BY 4.0.',
              'Table derived here. [Method and limits](qdrone-response.md).', '']
    (output/'qdrone-response-table.md').write_text('\n'.join(lines))


def main():
    from Analysis.qdrone_response import digest, read_recording
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--figure', type=Path, required=True)
    parser.add_argument('--tables', type=Path, help='Output directory for Markdown and CSV views')
    args = parser.parse_args()
    record = ROOT/'Data/qdrone-response'
    result = json.loads((record/'results.json').read_text())
    sources = json.loads((record/'sources.json').read_text())
    protocol = json.loads((record/'protocol.json').read_text())
    for item in sources['files']:
        if digest(args.cache/item['name']) != item['sha256']:
            raise ValueError(f"input hash mismatch: {item['name']}")
    plot(read_recording(args.cache/protocol['selected_file']), result, args.figure)
    if args.tables:
        write_tables(result, args.tables)


if __name__ == '__main__':
    main()
