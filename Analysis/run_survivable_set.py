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
* ``--figures-only``: redraw the four committed figures from the committed
                     results JSON. Runs no simulation and writes only Figures/.
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

from Analysis import figure_style as fs
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
    # PAIRED DESIGN (literature/claim-ledger.md E1): the seed deliberately
    # excludes the action index and the variant index, so every action and every
    # controller variant draws the SAME dispersed vehicle, the same imperfections
    # and the same initial tilt for a given trial. Trials therefore pair
    # one-to-one across actions and variants, which is what makes McNemar/exact
    # conditional analysis valid. Do not add ai or vi back into this prefix.
    for variant in variants:
        for ci, class_name in enumerate(sorted(FAILURE_CLASSES)):
            for ki, cell in enumerate(ss.EXPLORATORY_CELLS):
                if class_name in ss.PRIMARY_CLASSES and cell in ss.PRIMARY_CELLS:
                    continue  # covered by the higher-N primary tasks below
                for action in REALLOC_ACTIONS:
                    tasks += _chunked_tasks(class_name, cell, action, n_exp,
                                            (ss.BASE_SEED, 0, ci, ki), variant)
        for ci, class_name in enumerate(sorted(ss.PRIMARY_CLASSES)):
            for ki, cell in enumerate(ss.PRIMARY_CELLS):
                for action in REALLOC_ACTIONS:
                    tasks += _chunked_tasks(class_name, cell, action, n_pri,
                                            (ss.BASE_SEED, 1, ci, ki), variant)
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


VARIANT_NAME = {"a": "Baseline PD controller (variant a)",
                "a2": "Spin-aware controller (variant a2)"}
SIM_NOTE = ("Simulation-only prediction. Action inputs are estimates pending owner input "
            "(OQ-010).")


def _trial_note(rows):
    """State the trial counts actually present in the plotted rows."""
    counts = {}
    for r in rows:
        counts.setdefault("parachute" if r["action"] == "parachute" else "other", set()).add(r["n"])
    other = sorted(counts.get("other", ()))
    note = f"{other[0]} trials per cell"
    if len(other) > 1:
        note += f" ({', '.join(f'{n:,}' for n in other[1:])} in outlined primary cells)"
    if "parachute" in counts:
        note += f"; parachute-like device {', '.join(f'{n:,}' for n in sorted(counts['parachute']))}"
    return note + "."


def psafe_figure(rows, path: Path, variant: str):
    """Exact-lower-bound heatmaps over (h, omega) at the vz=0, delay=0.11 slice."""
    classes = sorted(FAILURE_CLASSES)
    hs, ws = (1.5, 3.0, 6.0), (2.0, 6.0)
    by_key = {(r["class"], r["cell"], r["action"]): r for r in rows}
    shown = [r for r in rows if r["cell"] in
             {ss.Cell(h, 0.0, w, 0.11).label() for h in hs for w in ws}]
    peak = max(shown, key=lambda r: r["p_safe_95_lower"])
    zero_actions = [a for a in ss.ACTIONS
                    if all(r["p_safe_95_lower"] == 0 for r in shown if r["action"] == a)]
    short = fs.FAILURE_NAME[peak["class"]].split(" (")[0]
    title = f"{short} peaks at {peak['p_safe_95_lower']:.2f}"
    if zero_actions:
        title += "; the " + " and ".join(fs.ACTION_NAME[a].lower() for a in zero_actions)
        title += " is 0 in every cell"
    with fs.style():
        fig, axes = plt.subplots(len(classes), len(ss.ACTIONS), figsize=(7.0, 8.6),
                                 sharex=True, sharey=True,
                                 gridspec_kw={"left": .1, "right": .83, "top": .775,
                                              "bottom": .07, "hspace": .55, "wspace": .08})
        for i, cls in enumerate(classes):
            for j, action in enumerate(ss.ACTIONS):
                grid = np.full((len(ws), len(hs)), np.nan)
                ns = {}
                for (a, h), (b, w) in product(enumerate(hs), enumerate(ws)):
                    cell = ss.Cell(h, 0.0, w, 0.11)
                    r = by_key.get((cls, cell.label(), action))
                    if r:
                        grid[b, a] = r["p_safe_95_lower"]
                        ns[(a, b)] = r["n"]
                ax = axes[i, j]
                im = ax.imshow(grid, vmin=0.0, vmax=1.0, cmap="viridis",
                               origin="lower", aspect="auto")
                base_n = min(ns.values()) if ns else None
                for (a, b), n in ns.items():
                    v = grid[b, a]
                    ax.text(a, b, "<0.01" if 0 < v < .005 else f"{v:.2f}", ha="center", va="center",
                            fontsize=fs.SMALL,
                            color="white" if v < 0.6 else "black")
                    if action != "parachute" and n != base_n:
                        ax.add_patch(plt.Rectangle((a - .45, b - .45), .9, .9, fill=False,
                                                   ec="white", lw=1.4))
                ax.set_xticks(range(len(hs)), [f"{h:g}" for h in hs])
                ax.set_yticks(range(len(ws)), [f"{w:g}" for w in ws])
                ax.tick_params(length=2)
                for spine in ax.spines.values():
                    spine.set_visible(False)
                if i == 0:
                    ax.text(.5, 1.36, fs.ACTION_NAME[action].replace(" only", "\nonly")
                            .replace("-like ", "-like\n").replace("Guard ", "Guard\n"),
                            transform=ax.transAxes, ha="center", va="bottom")
            axes[i, 0].text(0, 1.07, fs.FAILURE_NAME[cls], transform=axes[i, 0].transAxes,
                            ha="left", va="bottom")
        fig.supxlabel("Release height (m)", y=.015)
        fig.supylabel("Tumble rate at failure (rad/s)", x=.015)
        cax = fig.add_axes([.855, .3, .022, .4])
        cb = fig.colorbar(im, cax=cax)
        cb.set_label("Survival probability,\nexact 95% lower bound")
        cb.outline.set_visible(False)
        fig.text(.02, .985, title, va="top")
        cap = ""
        if peak["successes"] == peak["n"]:
            cap = (f"\n{peak['p_safe_95_lower']:.2f} is the bound that {peak['n']} survivals "
                   f"in {peak['n']} trials give.")
        fig.text(.02, .955, f"{SIM_NOTE}\n{VARIANT_NAME[variant]}. Slice: "
                 "no initial vertical speed, 0.11 s detection delay.\n" + _trial_note(shown)
                 + cap, va="top", fontsize=fs.SMALL, color=fs.GRAY)
        fs.save(fig, path)
    plt.close(fig)


def _cell_factors(label):
    """('h1.5', 'vz-1.5', 'w2', 'd0.11') -> (1.5, -1.5, 2.0, 0.11)."""
    h, vz, w, d = label.split("_")
    return float(h[1:]), float(vz[2:]), float(w[1:]), float(d[1:])


def policy_figure(policy, path: Path, variant: str):
    """Study B decision map: best action per (class, cell), shaded where ambiguous."""
    classes = sorted(FAILURE_CLASSES)
    cells = [c.label() for c in ss.EXPLORATORY_CELLS]
    rows = {(r["class"], r["cell"]): r for r in policy if r["cell"] in cells}
    total = len(rows)
    clear = [r for r in rows.values() if not r["ambiguous_with"]]

    def kind(r):
        if r["best_p_safe_95_lower"] == 0:
            return "none"
        return "clear" if not r["ambiguous_with"] else "overlap"

    if not clear:
        title = f"No design package is clearly best in any of the {total} failure-state cells"
    else:
        title = (f"A design package is clearly best in {len(clear)} of {total} "
                 "failure-state cells")
    primary = {c.label() for c in ss.PRIMARY_CELLS}
    seen = set()
    with fs.style():
        fig = plt.figure(figsize=(7.0, 8.0))
        grid = fig.add_gridspec(1, 2, width_ratios=[1.45, 2.2], left=.02, right=.98,
                                top=.77, bottom=.13, wspace=.02)
        table = fig.add_subplot(grid[0, 0])
        heat = fig.add_subplot(grid[0, 1], sharey=table)
        for j, cls in enumerate(classes):
            for i, cell in enumerate(cells):
                r = rows.get((cls, cell))
                if r is None:
                    continue
                k = kind(r)
                base = fs.ACTION[r["best_action"]]
                face = {"none": "#eeeeee", "overlap": fs.tint(base, .35), "clear": base}[k]
                seen.add((k, r["best_action"] if k != "none" else None))
                heat.add_patch(plt.Rectangle((j, i), 1, 1, fc=face, ec="white", lw=1))
                if cls in ss.PRIMARY_CLASSES and cell in primary:
                    heat.add_patch(plt.Rectangle((j + .06, i + .1), .88, .8, fill=False,
                                                 ec=fs.INK, lw=1.1))
                v = r["best_p_safe_95_lower"]
                # Two decimals, except a positive bound that would print as 0.00.
                heat.text(j + .5, i + .5, "<0.01" if 0 < v < .005 else f"{v:.2f}", ha="center",
                          va="center", fontsize=fs.SMALL,
                          color="white" if k == "clear" else fs.INK)
        heat.set_xlim(0, len(classes))
        heat.set_ylim(len(cells), 0)
        heat.set_xticks([j + .5 for j in range(len(classes))],
                        [fs.FAILURE_NAME[c].replace(" rotors out", "\nrotors out")
                         .replace(" authority ", " authority\n").replace(" rotor out", "\nrotor out")
                         for c in classes])
        heat.xaxis.tick_top()
        heat.tick_params(length=0, labelleft=False, labelsize=fs.SMALL)
        heat.spines[:].set_visible(False)
        heat.set_xlabel("Best package's survival lower bound, by failure class")
        heat.xaxis.set_label_position("top")
        # Left: the four state factors of each row, read as a small table.
        heads = ["Height\n(m)", "Vertical\nspeed (m/s)", "Tumble\nrate (rad/s)", "Delay\n(s)"]
        xs = [.11, .37, .66, .91]
        for x, h in zip(xs, heads):
            table.text(x, -.4, h, ha="center", va="bottom", fontsize=fs.SMALL)
        previous = None
        for i, cell in enumerate(cells):
            f = _cell_factors(cell)
            for k, (x, v) in enumerate(zip(xs, f)):
                if k == 0 and v == previous:
                    continue
                table.text(x, i + .5, f"{v:g}", ha="center", va="center", fontsize=fs.TICK)
            if previous is not None and f[0] != previous:
                for ax in (table, heat):
                    ax.axhline(i, color=fs.GRAY, lw=.8)
            previous = f[0]
        table.set_xlim(0, 1)
        table.axis("off")
        names = {"realloc_only": "reallocation", "mechanism": "mechanism",
                 "parachute": "parachute-like device"}
        handles, labels = [], []
        order = [("clear", a) for a in ss.ACTIONS] + [("overlap", a) for a in ss.ACTIONS]
        for k, a in order + [("none", None)]:
            if (k, a) not in seen:
                continue
            face = ("#eeeeee" if k == "none" else
                    fs.ACTION[a] if k == "clear" else fs.tint(fs.ACTION[a], .35))
            handles.append(plt.Rectangle((0, 0), 1, 1, fc=face, ec="none"))
            labels.append({"clear": f"Best: {names.get(a)}, interval clear of the others",
                           "overlap": f"Best: {names.get(a)}, within Monte Carlo uncertainty",
                           "none": "No package above 0 (all lower bounds 0)"}[k])
        fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(.03, .005),
                   ncol=1, handlelength=1.2, borderaxespad=0)
        fig.text(.02, .985, title, va="top")
        fig.text(.02, .955, "Ranks aircraft design packages by exact 95% lower bound; "
                 "it is not a runtime policy (design.md 6b).\n"
                 f"{SIM_NOTE}\n{VARIANT_NAME[variant]}.\n"
                 f"{ss.EXPLORATORY_TRIALS} trials per cell ({ss.PRIMARY_TRIALS} in outlined "
                 f"primary cells); parachute-like device {ss.PARACHUTE_TRIALS:,}.",
                 va="top", fontsize=fs.SMALL, color=fs.GRAY)
        fs.save(fig, path)
    plt.close(fig)


def render_committed_figures(repo: Path):
    """Redraw the four figures from the committed results; runs no simulation."""
    for variant in ss.VARIANTS:
        suffix = "" if variant == "a" else f"_{variant}"
        data = json.loads((repo / "Data" / f"survivable_set_results{suffix}.json").read_text())
        psafe_figure(data["exploratory"], repo / "Figures" / f"survivable_set_psafe{suffix}.png",
                     variant)
        policy_figure(data["policy"], repo / "Figures" / f"survivable_set_policy{suffix}.png",
                      variant)
        print(f"[written] Figures/survivable_set_{{psafe,policy}}{suffix}.png")


def paired_action_comparisons(rows, variant):
    """Mechanism vs reallocation on identical trials, per (class, cell).

    The unpaired marginal intervals stay in the output; this is the comparison
    that is actually valid (literature/claim-ledger.md E1). Action A is
    ``mechanism``, action B is ``realloc_only``.
    """
    by_key = {}
    for r in rows:
        if r.get("variant") == variant and r["action"] in REALLOC_ACTIONS:
            by_key.setdefault((r["class"], r["cell"]), {})[r["action"]] = r
    out = []
    for (cls, cell), acts in sorted(by_key.items()):
        if set(acts) != set(REALLOC_ACTIONS):
            continue
        a, b = acts["mechanism"], acts["realloc_only"]
        if not a.get("outcomes") or len(a["outcomes"]) != len(b["outcomes"]):
            continue
        table = ss.paired_table(a["outcomes"], b["outcomes"])
        out.append({"class": cls, "cell": cell, "a": "mechanism",
                    "b": "realloc_only", **ss.paired_verdict(table)})
    return out


def paired_variant_comparisons(rows, va, vb):
    """Controller variant A vs A2 on identical trials, per (class, cell, action)."""
    by_key = {}
    for r in rows:
        if r["action"] in REALLOC_ACTIONS:
            by_key.setdefault((r["class"], r["cell"], r["action"]),
                              {})[r.get("variant")] = r
    out = []
    for (cls, cell, action), vs in sorted(by_key.items()):
        if va not in vs or vb not in vs:
            continue
        a, b = vs[va], vs[vb]
        if not a.get("outcomes") or len(a["outcomes"]) != len(b["outcomes"]):
            continue
        table = ss.paired_table(a["outcomes"], b["outcomes"])
        out.append({"class": cls, "cell": cell, "action": action,
                    "a": va, "b": vb, **ss.paired_verdict(table)})
    return out


def _strip_outcomes(rows):
    """Per-trial vectors are needed for pairing, not for the committed record."""
    return [{k: v for k, v in r.items() if k != "outcomes"} for r in rows]


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
        "paired_mechanism_vs_realloc": paired_action_comparisons(rows, variant),
        "policy": ss.policy_map(_strip_outcomes(exploratory)),
        "exploratory": _strip_outcomes(
            sorted(exploratory, key=lambda r: (r["class"], r["cell"], r["action"]))),
        "primary": _strip_outcomes(
            sorted(primary, key=lambda r: (r["class"], r["cell"], r["action"]))),
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
        "scenario": ss.SCENARIO,
        "scenario_note": ("All motors are off for detection+spool latency, then "
                          "the controller engages: a RELEASE/STARTUP transient, "
                          "NOT an in-flight failure in which healthy motors keep "
                          "running until detection. Every rotor-out result here "
                          "is conditional on that reading (critique C04)."),
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
    ap.add_argument("--figures-only", action="store_true",
                    help="redraw Figures/ from the committed results JSON; no simulation")
    ap.add_argument("--output-dir", default=None,
                    help="write results here (required-safe for --quick: "
                         "defaults to a scratch dir, never the repo)")
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]

    if args.smoke:
        run_smoke(args.workers)
        return
    if args.figures_only:
        render_committed_figures(repo)
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
        if variant == ss.VARIANTS[0] and len(ss.VARIANTS) > 1:
            out["paired_variant_comparison"] = paired_variant_comparisons(
                rows, ss.VARIANTS[0], ss.VARIANTS[1])
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
