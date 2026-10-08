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

ROOT = Path(__file__).resolve().parents[1]
BLUE, GREEN, PURPLE, GRAY = '#2980b9', '#27ae60', '#7d3c98', '#62676d'
DIRECTIONS = [('up', '^', BLUE), ('down', 'v', PURPLE)]


def make_figure(data, result):
    """All traces use source samples; scatter values come from stored events."""
    with plt.rc_context({'font.size': 11, 'axes.titlesize': 12,
                         'axes.labelsize': 11, 'legend.fontsize': 10,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white',
                         'pdf.fonttype': 42, 'path.simplify': False}):
        fig = plt.figure(figsize=(10, 9.4))
        grid = fig.add_gridspec(3, 2, height_ratios=[1.15, 1, 1.05],
                               left=.085, right=.975, bottom=.12, top=.855,
                               hspace=.52, wspace=.23)
        altitude = fig.add_subplot(grid[0, :])
        voltage = fig.add_subplot(grid[1, :], sharex=altitude)
        by_time = fig.add_subplot(grid[2, 0])
        by_voltage = fig.add_subplot(grid[2, 1], sharey=by_time)
        t = data[:, 0]
        altitude.plot(t, data[:, 2], color=BLUE, lw=1.15, label='Observed altitude')
        altitude.step(t, data[:, 1], where='post', color=GRAY, lw=1.1,
                      ls='--', label='Recorded reference')
        altitude.set(title='A  Altitude tracking', ylabel='Altitude [m]')
        altitude.legend(loc='lower right', bbox_to_anchor=(1, 1.015),
                        ncol=2, frameon=False)
        altitude.tick_params(labelbottom=False)
        voltage.plot(t, data[:, 3], color=GREEN, lw=.65)
        voltage.set(title='B  Recorded battery voltage', ylabel='Voltage [V]',
                    xlabel='Recorded time [s]', xlim=(t[0], t[-1]))
        # A vertical reference shows the censored window without inventing an RMSE.
        incomplete = [e for e in result['events'] if e['status'] != 'complete']
        for e in incomplete:
            for ax in (altitude, voltage):
                ax.axvline(e['time_s'], color=GRAY, ls=':', lw=1)
        for direction, marker, color in DIRECTIONS:
            events = [e for e in result['events'] if e['status'] == 'complete'
                      and e['direction'] == direction]
            for ax, key in ((by_time, 'time_s'), (by_voltage, 'precommand_voltage_v')):
                selected = [e for e in events if e[key] is not None]
                ax.scatter([e[key] for e in selected], [e['rmse_m'] for e in selected],
                           marker=marker, color=color, s=42, edgecolor='white',
                           linewidth=.35, label=direction.capitalize(), zorder=3)
        by_time.set(title='C  Response error over time', xlabel='Command time [s]',
                    ylabel=f"{result['protocol_horizon_s']:g} s altitude RMSE [m]",
                    xlim=(t[0], t[-1]))
        by_voltage.set(title='D  The same errors vs voltage',
                       xlabel='Precommand battery voltage [V]')
        upper = np.ceil(max(e['rmse_m'] for e in result['events']
                            if e['status'] == 'complete') * 1.1 * 10) / 10
        by_time.set_ylim(0, upper)
        by_time.legend(loc='center left', frameon=False, title='Reference change')
        by_voltage.tick_params(labelleft=False)
        for ax in (by_time, by_voltage):
            ax.axhline(0, color=GRAY, lw=.8)
            ax.yaxis.set_major_locator(MaxNLocator(3))
        for ax in (altitude, voltage, by_time, by_voltage):
            ax.set_title(ax.get_title(), loc='left', pad=10)
            ax.set_title('', loc='center')
            ax.grid(axis='y', color='#d6d9dc', lw=.6, alpha=.65)
            ax.set_axisbelow(True)
            ax.spines[['top', 'right']].set_visible(False)
            ax.spines[['left', 'bottom']].set_color('#80858a')
            ax.xaxis.set_major_locator(MaxNLocator(6))
        fig.suptitle('QDrone2 | tracking during one recorded discharge',
                     x=.085, y=.978, ha='left', fontsize=15)
        fig.text(.085, .935, 'DEVELOPMENT OBSERVATIONS · original MPC · no recovery-failure labels',
                 fontsize=11, color=GRAY)
        fig.text(.085, .903,
                 f"{result['complete_steps']} complete response windows; {len(incomplete)} incomplete. "
                 'Dotted line: incomplete command.', fontsize=10)
        fig.text(.085, .051, 'Repeated commands share one recording. Demand, voltage and elapsed time co-vary.', fontsize=10)
        fig.text(.085, .023, 'Observations: Borbolla-Burillo et al. · Zenodo 19464105 · CC BY 4.0', fontsize=9, color=GRAY)
    return fig


def plot(data, result, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = make_figure(data, result)
    fig.savefig(path, dpi=180, facecolor='white')
    fig.savefig(path.with_suffix('.pdf'), facecolor='white',
                metadata={'CreationDate': None, 'ModDate': None})
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
