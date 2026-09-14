#!/usr/bin/env python3
"""Lane A deliverable runner: produce the release-to-stabilization demonstration.

Generates (1) a time-series figure of a successful recovery (release -> passive tumble/fall ->
controller engages -> arrests tumble -> rights -> hovers) and (2) the recovery envelope across
the three locked-BOM tiers, plus a results JSON. This is the demonstrable result that converts
the project from "plan" to "characterized control result".

Run from the repo root:  python -m Analysis.run_release_recovery
Outputs: Figures/release_recovery_timeseries.{png,pdf}, Figures/release_recovery_envelope.{png,pdf},
         Data/release_recovery_results.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from Analysis.sim_release_recovery import (best_params, max_recoverable_rate,
                                           nominal_params, simulate, worst_params)

REPO = Path(__file__).resolve().parents[1]
FIGS = REPO / "Figures"
DATA = REPO / "Data"
TIERS = [("best", best_params()), ("nominal", nominal_params()), ("worst", worst_params())]
INIT_TILT = np.radians(60.0)


def _style():
    import matplotlib as mpl
    mpl.rcParams.update({"figure.dpi": 120, "savefig.dpi": 300, "savefig.bbox": "tight",
                         "font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "lines.linewidth": 1.8, "legend.frameon": False})


def timeseries_figure(plt, p, rate, name):
    r = simulate(p, rate, INIT_TILT)
    log = r["log"]
    passive = p.detection_latency_s + p.motor_start_latency_s
    fig, ax = plt.subplots(2, 2, figsize=(9, 5.6))
    ax = ax.ravel()
    ax[0].plot(log["t"], np.degrees(log["tilt"]), color="#0072B2"); ax[0].set_ylabel("tilt [deg]")
    ax[0].axhline(5, ls=":", color="grey", lw=1)
    ax[1].plot(log["t"], log["omega_mag"], color="#D55E00"); ax[1].set_ylabel("body rate |ω| [rad/s]")
    ax[2].plot(log["t"], log["z"], color="#009E73"); ax[2].set_ylabel("altitude z [m]")
    ax[2].axhline(-p.available_height_m, ls=":", color="red", lw=1, label="ground (−budget)")
    ax[2].legend(loc="lower right", fontsize=8)
    ax[3].plot(log["t"], log["thrust"], color="#CC79A7"); ax[3].set_ylabel("collective thrust [N]")
    ax[3].axhline(p.max_thrust_n, ls=":", color="grey", lw=1)
    for a in ax:
        a.set_xlabel("time [s]")
        a.axvspan(0, passive, color="0.85", label="motors off (detect+spool)")
    ax[0].legend(loc="upper right", fontsize=8)
    rt = f"{r['recovery_time_s']:.2f} s" if r["recovery_time_s"] else "no recovery"
    fig.suptitle(f"Release-to-stabilization — {name} BOM, {np.degrees(rate):.0f}°/s tumble + 60° tilt"
                 f"  →  recovery {rt}, altitude lost {r['max_descent_m']:.2f}/{p.available_height_m} m",
                 fontsize=11)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"release_recovery_timeseries.{ext}")
    plt.close(fig)
    return r


def envelope_figure(plt):
    rates = np.arange(0.0, 12.01, 0.5)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    colors = {"best": "#0072B2", "nominal": "#009E73", "worst": "#D55E00"}
    summary = {}
    for name, p in TIERS:
        descent, ok_rate = [], []
        for rt in rates:
            r = simulate(p, rt, INIT_TILT)
            descent.append(r["max_descent_m"] if r["success"] else np.nan)
            ok_rate.append(r["success"])
        mr, edge = max_recoverable_rate(p, INIT_TILT, with_edge=True)
        summary[name] = {"max_recoverable_rate_rad_s": mr,
                         "max_recoverable_rate_deg_s": float(np.degrees(mr)),
                         "envelope_edge": edge,   # "failure" = real dynamic boundary;
                         # "gyro_limit" = never failed up to the sensor range — the
                         # envelope is measurement-limited, not authority-limited
                         "max_torque_n_m": p.max_torque_n_m, "max_thrust_n": p.max_thrust_n,
                         "available_height_m": p.available_height_m}
        edge_tag = "" if edge == "failure" else " (gyro-limited)"
        ax[0].plot(rates, descent, "o-", ms=4, color=colors[name],
                   label=f"{name} (max {mr:.1f} rad/s{edge_tag})")
        ax[1].bar(name, np.degrees(mr), color=colors[name])
    ax[0].axhline(TIERS[1][1].available_height_m, ls=":", color="red", lw=1, label="height budget")
    ax[0].set_xlabel("initial tumble rate [rad/s]"); ax[0].set_ylabel("altitude lost [m]")
    ax[0].set_title("Altitude lost vs tumble rate"); ax[0].legend(fontsize=8)
    ax[1].set_ylabel("max recoverable rate [deg/s]")
    ax[1].set_title("Recovery envelope by BOM tier")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"release_recovery_envelope.{ext}")
    plt.close(fig)
    return summary


def main():
    FIGS.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
    _style()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    demo = timeseries_figure(plt, nominal_params(), rate=2.0, name="nominal")
    envelope = envelope_figure(plt)

    results = {
        "scenario": {"initial_tilt_deg": 60.0, "available_height_m": 3.0,
                     "note": "released from rest with tumble + tilt; motors off during "
                             "detection+spool latency, then closed-loop recovery"},
        "demo_case": {"tier": "nominal", "initial_rate_rad_s": 2.0,
                      "success": demo["success"], "recovery_time_s": demo["recovery_time_s"],
                      "altitude_lost_m": demo["max_descent_m"], "peak_thrust_n": demo["peak_thrust_n"]},
        "envelope_by_tier": envelope,
    }
    with (DATA / "release_recovery_results.json").open("w") as fh:
        json.dump(results, fh, indent=2)

    print("=== Release-to-stabilization (Lane A) ===")
    print(f"demo: nominal BOM, 2.0 rad/s tumble + 60° tilt -> "
          f"recover {demo['recovery_time_s']:.2f}s, altitude lost {demo['max_descent_m']:.2f} m")
    for name, s in envelope.items():
        print(f"  {name:8s} max recoverable tumble: {s['max_recoverable_rate_rad_s']:.1f} rad/s "
              f"({s['max_recoverable_rate_deg_s']:.0f} deg/s)")
    print(f"figures -> {FIGS}/  results -> {DATA}/release_recovery_results.json")


if __name__ == "__main__":
    main()
