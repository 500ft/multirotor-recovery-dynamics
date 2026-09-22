#!/usr/bin/env python3
"""Run the Study A/A2/B survivable-set sweeps and write data + figures.

Entry point:  python -m Analysis.run_survivable_set  [options]

Default runs BOTH controller variants — ``a`` (baseline PD) and ``a2``
(spin-aware: gyroscopic feedforward + EST yaw rotational drag, see
``docs/specs/survivable-set/design-a2.md``) — and writes one results file and one
figure pair per variant: ``Data/survivable_set_results{,_a2}.json``,
``Figures/survivable_set_{psafe,policy}{,_a2}.png``. The parachute action does not
use the controller, so its rows are computed once and shared across variants.

Other modes:

* ``--quick``      : 1/10 trial counts, labelled QUICK — never a quotable result.
* ``--smoke``      : minimal pipeline exercise for CI (primary cells, two classes,
                     a handful of trials, variant a2, no files written; exit 0 on
                     structural success).
* ``--convergence``: integrator diagnostic — repeats a few primary-cell trials at
                     dt = 5e-4 (production) and 2.5e-4 (halved), reports impact-
                     state deviations, writes ``Data/survivable_set_convergence.json``.

The sweep is embarrassingly parallel; work is chunked so the pool stays busy and
every chunk carries its own deterministic seed (variant included), making the
totals independent of scheduling and worker count.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
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
    class_name, cell, action, n, seed, variant = task
    return ss.evaluate_cell(class_name, cell, action, n, seed, variant=variant)


def _chunked_tasks(class_name, cell, action, n, seed_prefix, variant):
    chunks = [CHUNK] * (n // CHUNK)
    if n % CHUNK:
        chunks.append(n % CHUNK)
    return [(class_name, cell, action, c, (*seed_prefix, j), variant)
            for j, c in enumerate(chunks)]


def build_tasks(scale: int = 1, variants=ss.VARIANTS):
    """(exploratory + primary) task list; ``scale`` divides trial counts."""
    tasks = []
    n_exp = max(2, ss.EXPLORATORY_TRIALS // scale)
    n_pri = max(4, ss.PRIMARY_TRIALS // scale)
    n_par = max(20, ss.PARACHUTE_TRIALS // scale)
    for vi, variant in enumerate(variants):
        for ci, class_name in enumerate(sorted(FAILURE_CLASSES)):
            for ki, cell in enumerate(ss.EXPLORATORY_CELLS):
                if class_name in ss.PRIMARY_CLASSES and cell in ss.PRIMARY_CELLS:
                    continue  # covered by the higher-N primary tasks below
                for ai, action in enumerate(REALLOC_ACTIONS):
                    tasks += _chunked_tasks(class_name, cell, action, n_exp,
                                            (ss.BASE_SEED, vi, 0, ci, ki, ai),
                                            variant)
        for ci, class_name in enumerate(sorted(ss.PRIMARY_CLASSES)):
            for ki, cell in enumerate(ss.PRIMARY_CELLS):
                for ai, action in enumerate(REALLOC_ACTIONS):
                    tasks += _chunked_tasks(class_name, cell, action, n_pri,
                                            (ss.BASE_SEED, vi, 1, ci, ki, ai),
                                            variant)
    # parachute is controller- and class-independent: once per cell, shared
    for ki, cell in enumerate(ss.EXPLORATORY_CELLS):
        tasks += _chunked_tasks("any", cell, "parachute", n_par,
                                (ss.BASE_SEED, 9, 0, 99, ki, 2), "a")
    return tasks


def merge_results(rows):
    by_key = {}
    for r in rows:
        by_key.setdefault((r.get("variant", "a"), r["class"], r["cell"],
                           r["action"]), []).append(r)
    return [ss.merge_rows(chunks) for chunks in by_key.values()]


def broadcast_parachute(rows, parachute_rows, variant):
    """Give every failure class its (shared) parachute row for the policy map."""
    out = [dict(r) for r in rows]
    for r in parachute_rows:
        for class_name in sorted(FAILURE_CLASSES):
            out.append({**r, "class": class_name, "variant": variant})
    return out


def psafe_figure(rows, path: Path, variant: str):
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
    fig.suptitle(f"Survivable set, variant {variant} (slice: vz0 = 0, delay = "
                 "0.11 s) — SIMULATION-ONLY PREDICTION, EST inputs pending (OQ-010)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def policy_figure(policy, path: Path, variant: str):
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
    ax.set_title(f"Recovery policy map, variant {variant}: best action by exact "
                 "lower bound (R=realloc_only, M=mechanism, P=parachute; "
                 "'?' = within Monte Carlo uncertainty of an alternative)")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def assemble_variant(rows, parachute_rows, variant, scale):
    """Kill criterion + policy + sorted row lists for one controller variant."""
    own = [r for r in rows if r.get("variant") == variant
           and r["action"] != "parachute"]
    exploratory = broadcast_parachute(
        [r for r in own
         if r["cell"] in {c.label() for c in ss.EXPLORATORY_CELLS}],
        parachute_rows, variant)
    primary_cells = {c.label() for c in ss.PRIMARY_CELLS}
    primary = [r for r in own
               if r["cell"] in primary_cells and r["n"] >= ss.PRIMARY_TRIALS // scale]
    return {
        "variant": variant,
        "kill_criterion": ss.kill_criterion(primary),
        "policy": ss.policy_map(exploratory),
        "exploratory": sorted(exploratory,
                              key=lambda r: (r["class"], r["cell"], r["action"])),
        "primary": sorted(primary,
                          key=lambda r: (r["class"], r["cell"], r["action"])),
    }


def preregistration_block(scale):
    return {
        "landing_criterion_bare": [ss.BARE_CRITERION[0],
                                   float(np.degrees(ss.BARE_CRITERION[1]))],
        "landing_criterion_guarded_EST": [ss.GUARDED_CRITERION[0],
                                          float(np.degrees(ss.GUARDED_CRITERION[1]))],
        "sensitivity": {k: [v[0], float(np.degrees(v[1]))]
                        for k, v in ss.SENSITIVITY.items()},
        "mech_mass_g_EST": ss.MECH_MASS_G_EST,
        "mech_mass_frac": ss.MECH_MASS_FRAC,
        "mech_inertia_frac_EST": ss.MECH_INERTIA_FRAC,
        "parachute_EST": {"terminal_m_s": ss.PARACHUTE_TERMINAL_M_S,
                          "deploy_s": ss.PARACHUTE_DEPLOY_S},
        "a2_yaw_drag_n_m_s2_EST": ss.A2_YAW_DRAG_N_M_S2,
        "descent_rate_m_s": ss.DESCENT_RATE_M_S,
        "init_tilt_max_deg": float(np.degrees(ss.INIT_TILT_MAX_RAD)),
        "primary_cells": [c.label() for c in ss.PRIMARY_CELLS],
        "primary_classes": list(ss.PRIMARY_CLASSES),
        "trials": {"exploratory": ss.EXPLORATORY_TRIALS // scale,
                   "primary": ss.PRIMARY_TRIALS // scale,
                   "parachute": ss.PARACHUTE_TRIALS // scale},
        "base_seed": ss.BASE_SEED,
        "machinery_rev": ("2026-09-16: cascaded torque-priority allocation, "
                          "balanced collective ceiling (0.9 airmode reserve in "
                          "allocation mode), arrest-first descent; supersedes the "
                          "single-pass pinv allocation of the first committed "
                          "sweep — see design-a2.md"),
    }


def resolve_output_dir(repo: Path, quick: bool, output_dir: str | None) -> Path:
    """Where a sweep writes. Full runs: the repo (tracked results). Quick runs:
    never the repo — a scratch directory by default, and an explicit
    ``--output-dir`` under Data/ or Figures/ is refused (F03, review-2026-09-19:
    a quick run silently replaced the committed 300-trial results)."""
    repo = repo.resolve()
    if not quick:
        return Path(output_dir).resolve() if output_dir else repo
    out = Path(output_dir or tempfile.mkdtemp(prefix="survivable-set-quick-")).resolve()
    for tracked in (repo / "Data", repo / "Figures"):
        if out == tracked or tracked in out.parents:
            raise SystemExit(f"refusing --quick output under tracked {tracked}")
    return out


def run_smoke(workers):
    """CI pipeline exercise: tiny counts, no files. Fails loudly on structure."""
    tasks = []
    for ci, class_name in enumerate(("one_out", "partial_authority")):
        for ki, cell in enumerate(ss.PRIMARY_CELLS):
            for ai, action in enumerate(REALLOC_ACTIONS):
                tasks += _chunked_tasks(class_name, cell, action, 3,
                                        (1, ci, ki, ai), "a2")
    for ki, cell in enumerate(ss.PRIMARY_CELLS):
        tasks += _chunked_tasks("any", cell, "parachute", 50, (2, ki), "a")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        raw = list(pool.map(_run_task, tasks, chunksize=1))
    rows = merge_results(raw)
    parachute = [r for r in rows if r["action"] == "parachute"]
    realloc = [r for r in rows if r["action"] != "parachute"]
    policy = ss.policy_map(broadcast_parachute(realloc, parachute, "a2"))
    kill = ss.kill_criterion(realloc)
    assert policy and "mechanism_justified" in kill
    print(f"smoke OK: {len(rows)} merged rows, {len(policy)} policy rows, "
          f"kill verdict computed")


def run_convergence(repo: Path):
    """Impact-state sensitivity to halving dt on primary-cell trials."""
    rows = []
    for class_name in ("one_out", "partial_authority"):
        for cell in ss.PRIMARY_CELLS:
            for k in range(3):
                out = {}
                for dt in (5e-4, 2.5e-4):
                    rng = np.random.default_rng((ss.BASE_SEED, 7, k))
                    speed, tilt = ss._realloc_trial(rng, class_name, cell,
                                                    mechanism=True, variant="a2",
                                                    dt=dt)
                    out[dt] = (speed, tilt)
                (s1, t1), (s2, t2) = out[5e-4], out[2.5e-4]
                rows.append({
                    "class": class_name, "cell": cell.label(), "trial": k,
                    "impact_speed_dt5e-4": float(s1),
                    "impact_speed_dt2.5e-4": float(s2),
                    "impact_tilt_rad_dt5e-4": float(t1),
                    "impact_tilt_rad_dt2.5e-4": float(t2),
                    "speed_delta": (float(abs(s1 - s2))
                                    if np.isfinite(s1) and np.isfinite(s2)
                                    else None),
                    "landed_agrees": bool(np.isfinite(s1) == np.isfinite(s2)),
                })
    finite = [r["speed_delta"] for r in rows if r["speed_delta"] is not None]
    summary = {
        "max_impact_speed_delta_m_s": max(finite) if finite else None,
        "landed_agreement": all(r["landed_agrees"] for r in rows),
        "note": ("Integrator diagnostic: production dt=5e-4 vs halved. Deltas "
                 "small against the 0.5 m/s spacing of the criterion variants "
                 "support the dt choice; a large delta would demand a smaller "
                 "production step."),
        "trials": rows,
    }
    path = repo / "Data" / "survivable_set_convergence.json"
    with path.open("w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[written] {path.relative_to(repo)}; "
          f"max impact-speed delta = {summary['max_impact_speed_delta_m_s']}, "
          f"landed agreement = {summary['landed_agreement']}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="1/10 trial counts; smoke run only, never a result")
    ap.add_argument("--smoke", action="store_true",
                    help="CI pipeline exercise: tiny counts, writes nothing")
    ap.add_argument("--convergence", action="store_true",
                    help="dt-halving diagnostic on primary-cell trials")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--output-dir", default=None,
                    help="write results here (required-safe for --quick: "
                         "defaults to a scratch dir, never the repo)")
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]

    if args.smoke:
        run_smoke(args.workers)
        return
    if args.convergence:
        run_convergence(repo)
        return

    scale = 10 if args.quick else 1
    out_dir = resolve_output_dir(repo, args.quick, args.output_dir)
    (out_dir / "Data").mkdir(parents=True, exist_ok=True)
    (out_dir / "Figures").mkdir(parents=True, exist_ok=True)
    tasks = build_tasks(scale)
    t0 = time.time()
    print(f"survivable-set sweep: {len(tasks)} tasks, {args.workers} workers"
          + (" [QUICK]" if args.quick else ""))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        raw = list(pool.map(_run_task, tasks, chunksize=1))
    rows = merge_results(raw)
    print(f"sweep done in {time.time() - t0:.0f} s")

    parachute_rows = [
        r for r in rows if r["action"] == "parachute"
        and r["cell"] in {c.label() for c in ss.EXPLORATORY_CELLS}]
    for variant in ss.VARIANTS:
        block = assemble_variant(rows, parachute_rows, variant, scale)
        suffix = "" if variant == "a" else f"_{variant}"
        out = {
            "note": (("QUICK SMOKE RUN — not a result. " if args.quick else "")
                     + f"SIMULATION-ONLY PREDICTION (Study {variant.upper()}/B). "
                     "Mechanism and parachute action parameters are EST owner "
                     "inputs (OQ-010); the bench/drop gates (Study C) must run "
                     "before any survivable-set claim leaves this file. "
                     "Preregistration: docs/specs/survivable-set/design.md + "
                     "design-a2.md"),
            "preregistration": preregistration_block(scale),
            **block,
        }
        data_path = out_dir / "Data" / f"survivable_set_results{suffix}.json"
        with data_path.open("w") as fh:
            json.dump(out, fh, indent=2)
        print(f"[written] {data_path}")
        print(f"[{variant}] kill criterion: {block['kill_criterion']['verdict']}")
        if not args.quick:
            psafe_figure(block["exploratory"],
                         out_dir / "Figures" / f"survivable_set_psafe{suffix}.png",
                         variant)
            policy_figure(block["policy"],
                          out_dir / "Figures" / f"survivable_set_policy{suffix}.png",
                          variant)
    if not args.quick:
        print("[written] Figures/survivable_set_{psafe,policy}{,_a2}.png")


if __name__ == "__main__":
    main()
