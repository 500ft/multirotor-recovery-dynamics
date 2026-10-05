"""Plot the executed development CSV; no data acquisition or scoring."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(results, output):
    with results.open() as f:
        rows = list(csv.DictReader(f))
    names = ['cf21plus_firmware', 'thrust_upgrade_firmware', 'legacy_propellers_firmware', 'persistence']
    labels = ['2.1+ curve', 'Thrust-upgrade curve', 'Legacy-propeller curve', 'Persistence']
    colors = ['#0072B2', '#D55E00', '#009E73', '#333333']
    horizons = sorted({float(r['horizon_s']) for r in rows if float(r['horizon_s']) > 0})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), layout='constrained')
    for ax, metric, unit in zip(axes, ['velocity', 'body_rate'], ['m/s', 'rad/s']):
        for name, label, color in zip(names, labels, colors):
            values = []
            for horizon in horizons:
                selected = [r for r in rows if r['model'] == name and r['metric'] == metric
                            and float(r['horizon_s']) == horizon]
                flights = sorted({r['flight'] for r in selected})
                # Within-flight vector RMSE, then unweighted mean over flights.
                per_flight = [np.sqrt(sum(float(r['rmse'])**2 for r in selected
                                         if r['flight'] == flight)) for flight in flights]
                values.append(np.mean(per_flight))
            ax.plot(horizons, values, 'o-', color=color, label=label, linewidth=1.8)
        ax.set_xlabel('Nominal open-loop horizon (s)')
        ax.set_ylabel(f'Mean flight vector RMSE ({unit})')
        ax.set_title('World velocity' if metric == 'velocity' else 'Body angular rate')
        ax.set_xticks(horizons); ax.grid(alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle('Documented models accumulate error on development flights', fontsize=13)
    fig.supxlabel('NanoBench observations collected by Ullah and Baca. Same starts for all models.\n'
                  'Equal flight weighting; no uncertainty interval. Per-axis and per-flight values remain in the CSV.', fontsize=9)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args(); plot(a.results, a.output)
