#!/usr/bin/env python3
"""DR-SS-SCENARIO-01 diagnostic: legacy vs in-flight failure scenarios.

Registered in docs/specs/survivable-set/scenario-contract.md BEFORE execution.
Runs the three arms (L / H / I) on identical physical draws and reports the
paired arm differences. Exploratory, 288 trajectories, one frozen controller
bundle — plumbing validation and effect direction, NOT a full-grid verdict.

    python -m Analysis.run_scenario_diagnostic [--out DIR] [--pairs N]

Writes its own output directory; it never touches the historical study files.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from Analysis import survivable_set as ss
from Analysis.failure_allocation import FAILURE_CLASSES, MotorAllocation, solve_healthy_trim
from Analysis.sim_release_recovery import G, simulate

ARMS = ("release_startup", "in_flight_hold_matched", "in_flight_hold_immediate")
CLASSES = ("one_out", "two_adjacent")
PACKAGES = ("mechanism", "realloc_only")
PAIRS = 12
BASE_SEED = 20260925


def _one(rng_seed, class_name, cell, package, arm):
    """One trajectory. The physical draw depends only on the seed, so the same
    seed gives the same vehicle in every arm and package (paired design)."""
    rng = np.random.default_rng(rng_seed)
    mechanism = package == "mechanism"
    p, imp = ss._draw_vehicle(rng, cell, mechanism=mechanism)
    p = replace(p, yaw_drag_n_m_s2=ss.A2_YAW_DRAG_N_M_S2)      # frozen bundle
    tilt0 = rng.uniform(0.0, ss.INIT_TILT_MAX_RAD)             # drawn identically
    alloc = MotorAllocation(FAILURE_CLASSES[class_name], arm_m=p.arm_m,
                            max_thrust_n=p.max_thrust_n,
                            yaw_torque_n_m=p.yaw_torque_n_m)
    trim, feasible = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                        p.mass_kg, G, cg_offset_m=imp.cg_offset_m,
                                        torque_bias_n_m=imp.torque_bias_n_m)
    if not feasible:
        return {"status": "trim_infeasible", "safe": None}
    r = simulate(p, cell.omega0_rad_s, tilt0, imperfections=imp,
                 initial_vz_m_s=cell.vz0_m_s, descent_rate_m_s=ss.DESCENT_RATE_M_S,
                 motor_alloc=alloc, control_floor=mechanism, t_max=ss.T_MAX_S,
                 spin_aware=True, scenario=arm,
                 trim_thrusts=None if arm == "release_startup" else trim)
    if not r["crashed"]:
        return {"status": "no_contact_timeout", "safe": False,
                "t_switch_s": r["t_switch_realized_s"]}
    speed = abs(float(r["log"]["vz"][-1]))
    tilt = float(r["log"]["tilt"][-1])
    crit = ss.GUARDED_CRITERION if mechanism else ss.BARE_CRITERION
    return {"status": "contact", "safe": bool(ss.landing_ok(speed, tilt, crit)),
            "impact_speed_m_s": speed, "impact_tilt_rad": tilt,
            "t_contact_s": float(r["log"]["t"][-1]),
            "t_switch_s": r["t_switch_realized_s"],
            "max_descent_m": float(r["max_descent_m"])}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--pairs", type=int, default=PAIRS)
    args = ap.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out) if args.out else repo / "Data" / "scenario-diagnostic"
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    trials, counts = [], {}
    for class_name in CLASSES:
        for cell in ss.PRIMARY_CELLS:
            for package in PACKAGES:
                for k in range(args.pairs):
                    # one physical draw, shared across every arm
                    seed = (BASE_SEED, CLASSES.index(class_name),
                            ss.PRIMARY_CELLS.index(cell), PACKAGES.index(package), k)
                    for arm in ARMS:
                        rec = _one(seed, class_name, cell, package, arm)
                        rec.update({"class": class_name, "cell": cell.label(),
                                    "package": package, "arm": arm, "pair": k})
                        trials.append(rec)
                        counts[rec["status"]] = counts.get(rec["status"], 0) + 1

    # paired arm differences on the matched case index
    by_key = {}
    for t in trials:
        by_key.setdefault((t["class"], t["cell"], t["package"], t["pair"]),
                          {})[t["arm"]] = t
    contrasts, continuous = {}, {}
    for a, b, name in (("in_flight_hold_matched", "release_startup", "H-L"),
                       ("in_flight_hold_immediate", "in_flight_hold_matched", "I-H"),
                       ("in_flight_hold_immediate", "release_startup", "I-L")):
        rows = {}
        for (cls, cell, pkg, _), arms in by_key.items():
            if a not in arms or b not in arms:
                continue
            xa, xb = arms[a]["safe"], arms[b]["safe"]
            if xa is None or xb is None:
                continue
            g = rows.setdefault((cls, pkg), {"n": 0, "only_a": 0, "only_b": 0,
                                             "both": 0, "neither": 0})
            g["n"] += 1
            if xa and xb: g["both"] += 1
            elif xa: g["only_a"] += 1
            elif xb: g["only_b"] += 1
            else: g["neither"] += 1
        # Continuous paired deltas. The binary proxy saturates at the primary
        # cells (everything fails in every arm), so the scenario effect is only
        # visible here. Reported per (class, cell) -- pooling would hide that the
        # sign depends on the cell.
        cont = {}
        for (cls, cell, pkg, _), arms in by_key.items():
            if a not in arms or b not in arms:
                continue
            xa, xb = arms[a], arms[b]
            if xa.get("impact_speed_m_s") is None or xb.get("impact_speed_m_s") is None:
                continue
            gg = cont.setdefault((cls, cell), {"d_impact": [], "d_contact": []})
            gg["d_impact"].append(xa["impact_speed_m_s"] - xb["impact_speed_m_s"])
            gg["d_contact"].append(xa["t_contact_s"] - xb["t_contact_s"])
        continuous[name] = [
            {"class": c, "cell": cl, "n": len(v["d_impact"]),
             "mean_d_impact_speed_m_s": float(np.mean(v["d_impact"])),
             "min_d_impact_speed_m_s": float(np.min(v["d_impact"])),
             "max_d_impact_speed_m_s": float(np.max(v["d_impact"])),
             "mean_d_time_to_contact_s": float(np.mean(v["d_contact"]))}
            for (c, cl), v in sorted(cont.items())]
        contrasts[name] = [
            {"class": c, "package": p, **v,
             "delta": (v["only_a"] - v["only_b"]) / v["n"] if v["n"] else None,
             "midp": ss.mcnemar_midp(v["only_a"], v["only_b"])}
            for (c, p), v in sorted(rows.items())]

    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                             capture_output=True, text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    out = {
        "study": "DR-SS-SCENARIO-01",
        "status": "EXPLORATORY DIAGNOSTIC — not a full-grid verdict",
        "registration": "docs/specs/survivable-set/scenario-contract.md",
        "note": ("Simulation on the historical design profile under an idealized "
                 "complete rotor effectiveness loss (R01). Not measured V995 "
                 "performance. One frozen controller bundle across arms, so this "
                 "does NOT estimate feedforward or drag effects."),
        "commit": sha, "python": platform.python_version(),
        "numpy": np.__version__, "seconds": round(time.time() - t0, 1),
        "design": {"arms": list(ARMS), "classes": list(CLASSES),
                   "cells": [c.label() for c in ss.PRIMARY_CELLS],
                   "packages": list(PACKAGES), "pairs": args.pairs,
                   "trajectories": len(trials), "base_seed": BASE_SEED},
        "status_counts": counts,
        "contrasts": contrasts,
        "continuous_contrasts": continuous,
        "trials": trials,
    }
    path = out_dir / "scenario_diagnostic.json"
    with path.open("w") as fh:
        json.dump(out, fh, indent=2)
    print(f"{len(trials)} trajectories in {out['seconds']} s -> {path}")
    print("status:", counts)
    for name, rows in continuous.items():
        print(f"\n{name} (continuous, paired):")
        for r in rows:
            print(f"  {r['class']:13s} {r['cell']:20s} n={r['n']:2d} "
                  f"d_impact={r['mean_d_impact_speed_m_s']:+.3f} m/s "
                  f"[{r['min_d_impact_speed_m_s']:+.2f},{r['max_d_impact_speed_m_s']:+.2f}] "
                  f"d_t_contact={r['mean_d_time_to_contact_s']:+.3f} s")
    for name, rows in contrasts.items():
        print(f"\n{name} (binary proxy):")
        for r in rows:
            print(f"  {r['class']:13s} {r['package']:13s} n={r['n']:2d} "
                  f"only_{name[0]}={r['only_a']:2d} only_{name[-1]}={r['only_b']:2d} "
                  f"both={r['both']:2d} neither={r['neither']:2d} "
                  f"delta={r['delta']:+.3f} midp={r['midp']:.3f}")


if __name__ == "__main__":
    main()
