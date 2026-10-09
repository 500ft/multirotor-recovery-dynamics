"""Plot the executed development CSV; no data acquisition or scoring."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from Analysis import figure_style as fs

NAMES = ['cf21plus_firmware', 'thrust_upgrade_firmware', 'legacy_propellers_firmware', 'persistence']
LABELS = {'cf21plus_firmware': '2.1+ curve', 'thrust_upgrade_firmware': 'Thrust-upgrade curve',
          'legacy_propellers_firmware': 'Legacy-propeller curve',
          'persistence': 'Persistence (hold state)'}
METRICS = [('velocity', 'World velocity error (m/s)'), ('body_rate', 'Body angular rate error (rad/s)')]


def summarize(rows):
    """Within-flight vector RMSE, then unweighted mean over flights."""
    horizons = sorted({float(r['horizon_s']) for r in rows if float(r['horizon_s']) > 0})
    values, flights = {}, set()
    for metric, _ in METRICS:
        for name in NAMES:
            series = []
            for horizon in horizons:
                selected = [r for r in rows if r['model'] == name and r['metric'] == metric
                            and float(r['horizon_s']) == horizon]
                per = sorted({r['flight'] for r in selected})
                flights.add(len(per))
                per_flight = [np.sqrt(sum(float(r['rmse'])**2 for r in selected
                                         if r['flight'] == flight)) for flight in per]
                series.append(np.mean(per_flight))
            values[metric, name] = np.array(series)
    return horizons, values, flights


def plot(results, output):
    with results.open() as f:
        rows = list(csv.DictReader(f))
    horizons, values, flights = summarize(rows)
    lowest = all(np.all(values[m, 'persistence'] < values[m, n])
                 for m, _ in METRICS for n in NAMES[:-1])
    title = 'Documented models accumulate error on development flights'
    if lowest:
        title += '; persistence stays lowest'
    n_note = (f'n = {flights.pop()} development flights per point'
              if len(flights) == 1 else 'flight count varies by point; see CSV')
    with fs.style():
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 4.0),
                                 gridspec_kw={'left': .09, 'right': .76, 'top': .66,
                                              'bottom': .13, 'wspace': .36})
        for ax, (metric, label), letter in zip(axes, METRICS, 'ab'):
            for name in NAMES:
                ax.plot(horizons, values[metric, name], 'o-', ms=4, lw=1.6,
                        color=fs.MODEL[name])
            ax.set_xticks(horizons, [f'{h:g}' for h in horizons])
            ax.set_xlabel('Open-loop horizon (s)')
            ax.set_ylabel(label)
            ax.set_ylim(bottom=0)
            ax.grid(axis='y')
            ax.set_axisbelow(True)
            ax.margins(x=.06)
            fs.panel_letter(fig, ax, letter, dx=-.075, dy=.065)
        ends = {n: values['velocity', n][-1] for n in NAMES}
        top3 = max(v for n, v in ends.items() if n != 'persistence')
        spread = top3 - min(v for n, v in ends.items() if n != 'persistence')
        axes[0].set_title('Velocity: the motor curves\nmeet by 0.5 s'
                          if spread < .05 * top3 else 'World velocity')
        worst = {m: max(NAMES[:-1], key=lambda n: values[m, n].max()) for m, _ in METRICS}
        always = all(np.all(values['body_rate', worst['body_rate']] >= values['body_rate', n])
                     for n in NAMES[:-1])
        axes[1].set_title(f"Body rate: the {LABELS[worst['body_rate']].lower()}\nis worst at every horizon"
                          if always else 'Body angular rate')
        # Direct labels at the right end of the body-rate lines, nudged apart.
        y = {n: values['body_rate', n][-1] for n in NAMES}
        lo, hi = axes[1].get_ylim()
        gap = .065 * (hi - lo)
        placed = []
        for name in sorted(NAMES, key=lambda n: y[n]):
            pos = y[name] if not placed else max(y[name], placed[-1] + gap)
            placed.append(pos)
            axes[1].annotate(LABELS[name], (horizons[-1], y[name]), xytext=(horizons[-1] + .03, pos),
                             textcoords='data', va='center', fontsize=fs.SMALL,
                             color=fs.MODEL[name], annotation_clip=False)
        fig.text(.02, .975, title, va='top')
        fig.text(.02, .92, 'NanoBench observations collected by Ullah and Baca. Same starts '
                 f'for all models;\n{n_note}. Mean of within-flight vector RMSE, equal flight '
                 'weighting,\nno uncertainty interval. Per-axis and per-flight values are '
                 'in the CSV.', va='top', fontsize=fs.SMALL, color=fs.GRAY)
        output.parent.mkdir(parents=True, exist_ok=True)
        fs.save(fig, output)
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args(); plot(a.results, a.output)
