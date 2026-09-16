#!/usr/bin/env python3
"""Run the Study A/B survivable-set sweep and write data + figures.

Entry point:  python -m Analysis.run_survivable_set  [--quick] [--workers N]

Writes ``Data/survivable_set_results.json`` (full preregistration echo, per-cell
exact bounds, kill-criterion verdict, policy map) and two figures. ``--quick``
divides every trial count by 10 for a smoke run and labels the output QUICK — a
quick run must never be quoted as a result.

The sweep is embarrassingly parallel; work is chunked so the pool stays busy and
every chunk carries its own deterministic seed, making the totals independent of
scheduling and worker count.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from Analysis.failure_allocation import FAILURE_CLASSES
from Analysis import survivable_set as ss

CHUNK = 25          # trials per parallel task
REALLOC_ACTIONS = ("realloc_only", "mechanism")


def _run_task(task):
    class_name, cell, action, n, seed = task
    return ss.evaluate_cell(class_name, cell, action, n, seed)


def _chunked_tasks(class_name, cell, action, n, seed_prefix):
    chunks = [CHUNK] * (n // CHUNK)
    if n % CHUNK:
        chunks.append(n % CHUNK)
    return [(class_name, cell, action, c, (*seed_prefix, j))
            for j, c in enumerate(chunks)]


def build_tasks(scale: int = 1):
    """(exploratory + primary) task list; ``scale`` divides trial counts (--quick)."""
    tasks = []
    n_exp = max(2, ss.EXPLORATORY_TRIALS // scale)
    n_pri = max(4, ss.PRIMARY_TRIALS // scale)
    n_par = max(20, ss.PARACHUTE_TRIALS // scale)
    for ci, class_name in enumerate(sorted(FAILURE_CLASSES)):
        for ki, cell in enumerate(ss.EXPLORATORY_CELLS):
            if class_name in ss.PRIMARY_CLASSES and cell in ss.PRIMARY_CELLS:
                continue  # covered by the higher-N primary tasks below
            for ai, action in enumerate(REALLOC_ACTIONS):
                tasks += _chunked_tasks(class_name, cell, action, n_exp,
                                        (ss.BASE_SEED, 0, ci, ki, ai))
    # parachute is failure-class independent: evaluate once per cell
    for ki, cell in enumerate(ss.EXPLORATORY_CELLS):
        tasks += _chunked_tasks("any", cell, "parachute", n_par,
                                (ss.BASE_SEED, 0, 99, ki, 2))
    for ci, class_name in enumerate(sorted(ss.PRIMARY_CLASSES)):
        for ki, cell in enumerate(ss.PRIMARY_CELLS):
            for ai, action in enumerate(REALLOC_ACTIONS):
                tasks += _chunked_tasks(class_name, cell, action, n_pri,
                                        (ss.BASE_SEED, 1, ci, ki, ai))
    return tasks


def merge_results(rows):
    by_key = {}
    for r in rows:
        by_key.setdefault((r["class"], r["cell"], r["action"]), []).append(r)
    return [ss.merge_rows(chunks) for chunks in by_key.values()]


def broadcast_parachute(rows):
    """Give every failure class its (shared) parachute row for the policy map."""
    out = [r for r in rows if r["action"] != "parachute"]
    for r in rows:
        if r["action"] == "parachute":
            for class_name in sorted(FAILURE_CLASSES):
                out.append({**r, "class": class_name})
    return out


def psafe_figure(rows, path: Path):
    """Exact-lower-bound heatmaps over (h, omega) at the vz=0, delay=0.11 slice."""
    classes = sorted(FAILURE_CLASSES)
    hs, ws = (1.5, 3.0, 6.0), (2.0, 6.0)
    by_key = {(r["class"], r["cell"], r["action"]): r for r in rows}
    fig, axes = plt.subplots(len(classes), len(ss.ACTIONS),
                             figsize=(10.5, 11.5), constrained_layout=True)
    for i, cls in enumerate(classes):
        for j, action in enumerate(ss.ACTIONS):
            grid = np.full((len(ws), len(hs)), np.nan)
            for (a, h), (b, w) in product(enumerate(hs), enumerate(ws)):
                cell = ss.Cell(h, 0.0, w, 0.11)
                r = by_key.get((cls, cell.label(), action))
                if r:
                    grid[b, a] = r["p_safe_95_lower"]
            ax = axes[i, j]
            im = ax.imshow(grid, vmin=0.0, vmax=1.0, cmap="viridis",
                           origin="lower", aspect="auto")
            for (a, _), (b, _) in product(enumerate(hs), enumerate(ws)):
                if not np.isnan(grid[b, a]):
                    ax.text(a, b, f"{grid[b, a]:.2f}", ha="center", va="center",
                            color="white" if grid[b, a] < 0.6 else "black",
                            fontsize=9)
            ax.set_xticks(range(len(hs)), [f"{h:g}" for h in hs])
            ax.set_yticks(range(len(ws)), [f"{w:g}" for w in ws])
            if i == 0:
                ax.set_title(action)
            if i == len(classes) - 1:
                ax.set_xlabel("release height h [m]")
            if j == 0:
                ax.set_ylabel(f"{cls}\ntumble rate [rad/s]")
    fig.colorbar(im, ax=axes, shrink=0.5, label="P_safe exact 95% lower bound")
    fig.suptitle("Survivable set (slice: vz0 = 0, delay = 0.11 s) — "
                 "SIMULATION-ONLY PREDICTION, EST inputs pending (OQ-010)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def policy_figure(policy, path: Path):
    """Study B decision map: best action per (class, cell); '?' where ambiguous."""
    classes = sorted(FAILURE_CLASSES)
    cells = [c.label() for c in ss.EXPLORATORY_CELLS]
    idx = {a: k for k, a in enumerate(ss.ACTIONS)}
    grid = np.full((len(classes), len(cells)), np.nan)
    marks = {}
    for row in policy:
        if row["cell"] not in cells:
            continue
        i, j = classes.index(row["class"]), cells.index(row["cell"])
        grid[i, j] = idx[row["best_action"]]
        marks[(i, j)] = "?" if row["ambiguous_with"] else ""
    fig, ax = plt.subplots(figsize=(13, 3.6), constrained_layout=True)
    cmap = matplotlib.colors.ListedColormap(["#c44e52", "#4c72b0", "#55a868"])
    ax.imshow(grid, cmap=cmap, vmin=-0.5, vmax=2.5, aspect="auto")
    for (i, j), m in marks.items():
        letter = ss.ACTIONS[int(grid[i, j])][0].upper()
        ax.text(j, i, letter + m, ha="center", va="center", fontsize=7)
    ax.set_yticks(range(len(classes)), classes)
    ax.set_xticks(range(len(cells)), cells, rotation=90, fontsize=6)
    ax.set_title("Recovery policy map: best action by exact lower bound "
                 "(R=realloc_only, M=mechanism, P=parachute; '?' = within "
                 "Monte Carlo uncertainty of an alternative)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="1/10 trial counts; smoke run only, never a result")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args(argv)
    scale = 10 if args.quick else 1

    tasks = build_tasks(scale)
    t0 = time.time()
    print(f"survivable-set sweep: {len(tasks)} tasks, {args.workers} workers"
          + (" [QUICK]" if args.quick else ""))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        raw = list(pool.map(_run_task, tasks, chunksize=1))
    rows = merge_results(raw)
    print(f"sweep done in {time.time() - t0:.0f} s")

    exploratory = broadcast_parachute(
        [r for r in rows if r["cell"] in {c.label() for c in ss.EXPLORATORY_CELLS}])
    primary_cells = {c.label() for c in ss.PRIMARY_CELLS}
    primary = [r for r in rows
               if r["cell"] in primary_cells and r["n"] >= ss.PRIMARY_TRIALS // scale
               and r["action"] in REALLOC_ACTIONS]
    kill = ss.kill_criterion(primary)
    policy = ss.policy_map(exploratory)

    repo = Path(__file__).resolve().parents[1]
    out = {
        "note": (("QUICK SMOKE RUN — not a result. " if args.quick else "")
                 + "SIMULATION-ONLY PREDICTION (Study A/B). Mechanism and "
                 "parachute action parameters are EST owner inputs (OQ-010); "
                 "the bench/drop gates (Study C) must run before any survivable-"
                 "set claim leaves this file. Preregistration: "
                 "docs/specs/survivable-set/design.md"),
        "preregistration": {
            "landing_criterion_bare": [ss.BARE_CRITERION[0],
                                       float(np.degrees(ss.BARE_CRITERION[1]))],
            "landing_criterion_guarded_EST": [ss.GUARDED_CRITERION[0],
                                              float(np.degrees(ss.GUARDED_CRITERION[1]))],
            "sensitivity": {k: [v[0], float(np.degrees(v[1]))]
                            for k, v in ss.SENSITIVITY.items()},
            "mech_mass_frac_EST": ss.MECH_MASS_FRAC,
            "mech_inertia_frac_EST": ss.MECH_INERTIA_FRAC,
            "parachute_EST": {"terminal_m_s": ss.PARACHUTE_TERMINAL_M_S,
                              "deploy_s": ss.PARACHUTE_DEPLOY_S},
            "descent_rate_m_s": ss.DESCENT_RATE_M_S,
            "init_tilt_max_deg": float(np.degrees(ss.INIT_TILT_MAX_RAD)),
            "primary_cells": [c.label() for c in ss.PRIMARY_CELLS],
            "primary_classes": list(ss.PRIMARY_CLASSES),
            "trials": {"exploratory": ss.EXPLORATORY_TRIALS // scale,
                       "primary": ss.PRIMARY_TRIALS // scale,
                       "parachute": ss.PARACHUTE_TRIALS // scale},
            "base_seed": ss.BASE_SEED,
        },
        "kill_criterion": kill,
        "policy": policy,
        "exploratory": sorted(exploratory,
                              key=lambda r: (r["class"], r["cell"], r["action"])),
        "primary": sorted(primary,
                          key=lambda r: (r["class"], r["cell"], r["action"])),
    }
    data_path = repo / "Data" / "survivable_set_results.json"
    with data_path.open("w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[written] {data_path.relative_to(repo)}")
    print(f"kill criterion: {kill['verdict']}")

    if not args.quick:
        psafe_figure(exploratory, repo / "Figures" / "survivable_set_psafe.png")
        policy_figure(policy, repo / "Figures" / "survivable_set_policy.png")
        print("[written] Figures/survivable_set_psafe.png, "
              "Figures/survivable_set_policy.png")


if __name__ == "__main__":
    main()
