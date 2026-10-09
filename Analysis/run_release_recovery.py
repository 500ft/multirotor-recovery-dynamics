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

from Analysis import figure_style as fs
from Analysis.sim_release_recovery import (best_params, max_recoverable_rate,
                                           nominal_params, simulate, worst_params)

REPO = Path(__file__).resolve().parents[1]
FIGS = REPO / "Figures"
DATA = REPO / "Data"
TIERS = [("best", best_params()), ("nominal", nominal_params()), ("worst", worst_params())]
INIT_TILT = np.radians(60.0)


def timeseries_figure(plt, p, rate, name):
    r = simulate(p, rate, INIT_TILT)
    log = r["log"]
    passive = p.detection_latency_s + p.motor_start_latency_s
    color = fs.TIER[name]
    with fs.style():
        fig, ax = plt.subplots(4, 1, figsize=(7.0, 7.4), sharex=True,
                               gridspec_kw={"left": .12, "right": .97, "top": .835,
                                            "bottom": .075, "hspace": .55})
        on = log["t"] >= passive
        tracks = [(np.degrees(log["tilt"]), "Tilt (deg)", "Tilt falls below the 5° upright threshold"),
                  (log["omega_mag"], "Body rate (rad/s)",
                   f"Body rate peaks at {log['omega_mag'][on].max():.1f} rad/s while righting, then settles"),
                  (log["z"], "Height\nchange (m)", "The descent stops well above the ground"),
                  (log["thrust"], "Thrust (N)", "Collective thrust saturates, then settles at hover")]
        for a, (y, label, title) in zip(ax, tracks):
            a.axvspan(0, passive, color=fs.LIGHT, lw=0)
            a.plot(log["t"], y, color=color, lw=1.6)
            a.set_ylabel(label)
            a.set_title(title)
            a.margins(x=.01, y=.08)
        ref = dict(color=fs.GRAY, ls=":", lw=1)
        ax[0].axhline(5, **ref)
        ax[0].text(.99, 5, "5° upright", transform=ax[0].get_yaxis_transform(),
                   ha="right", va="bottom", fontsize=fs.SMALL, color=fs.GRAY)
        ax[2].axhline(-p.available_height_m, **ref)
        ax[2].text(.99, -p.available_height_m, f"ground, {p.available_height_m:g} m below release",
                   transform=ax[2].get_yaxis_transform(), ha="right", va="bottom",
                   fontsize=fs.SMALL, color=fs.GRAY)
        ax[3].axhline(p.max_thrust_n, **ref)
        ax[3].text(.99, p.max_thrust_n, f"maximum {p.max_thrust_n:g} N",
                   transform=ax[3].get_yaxis_transform(), ha="right", va="bottom",
                   fontsize=fs.SMALL, color=fs.GRAY)
        ax[2].text(passive + .05, -1.5, "motors off\n(detect + spool)",
                   va="center", fontsize=fs.SMALL, color=fs.GRAY)
        if r["recovery_time_s"]:
            for a in ax:
                a.axvline(r["recovery_time_s"], color=color, ls="--", lw=.9)
            ax[1].text(r["recovery_time_s"] + .05, .9,
                       f"stabilized at {r['recovery_time_s']:.2f} s",
                       transform=ax[1].get_xaxis_transform(), va="top",
                       fontsize=fs.SMALL, color=color)
        ax[-1].set_xlabel("Time after release (s)")
        for a, letter in zip(ax, "abcd"):
            fs.panel_letter(fig, a, letter, dx=-.11, dy=.012)
        rt = (f"stabilizes in {r['recovery_time_s']:.2f} s" if r["recovery_time_s"]
              else "does not stabilize")
        fig.text(.02, .975, f"The {name} tier {rt} after a {np.degrees(INIT_TILT):.0f}° tilt and "
                 f"{rate:g} rad/s tumble, losing {r['max_descent_m']:.2f} m of "
                 f"{p.available_height_m:g} m", va="top")
        fig.text(.02, .94, "Deterministic 6-DoF simulation of the historical designed aircraft "
                 "with estimated\nparameters, not measured hardware. Shaded: all motors off for "
                 "detection and spool latency.", va="top", fontsize=fs.SMALL, color=fs.GRAY)
        fs.save(fig, FIGS / "release_recovery_timeseries.png", ("png", "pdf"))
    plt.close(fig)
    return r


def envelope_figure(plt):
    rates = np.arange(0.0, 12.01, 0.5)
    summary, scans = {}, {}
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
        scans[name] = (np.array(descent), np.array(ok_rate))
    _draw_envelope(plt, rates, scans, summary)
    return summary


def _draw_envelope(plt, rates, scans, summary):
    """Plot the scan already computed above; no simulation happens here."""
    names = [n for n, _ in TIERS]
    budget = TIERS[1][1].available_height_m
    gyro = TIERS[0][1].gyro_limit_rad_s
    first_fail = {n: rates[~scans[n][1]].min() if (~scans[n][1]).any() else None for n in names}
    with fs.style():
        fig = plt.figure(figsize=(7.0, 4.9))
        grid = fig.add_gridspec(2, 2, width_ratios=[1.75, 1], height_ratios=[.42, 1],
                                left=.13, right=.97, top=.76, bottom=.14,
                                hspace=.3, wspace=.38)
        strip = fig.add_subplot(grid[0, 0])
        lost = fig.add_subplot(grid[1, 0], sharex=strip)
        edge_ax = fig.add_subplot(grid[:, 1])
        for i, name in enumerate(names):
            descent, ok = scans[name]
            c = fs.TIER[name]
            lost.plot(rates, descent, "o-", ms=3.5, lw=1.5, color=c)
            strip.plot(rates[~ok], np.full((~ok).sum(), i), "x", ms=4.5, mew=1.3, color=c)
            # Direct label at the last recovered rate before the first failure,
            # or mid-scan for a tier that never fails.
            fails = (~ok).any()
            j = np.flatnonzero(~ok)[0] - 1 if fails else len(rates) * 2 // 3
            lost.annotate(name, (rates[j], descent[j]), xytext=(4, 2) if fails else (-6, 6),
                          textcoords="offset points", ha="left" if fails else "right",
                          va="bottom", fontsize=fs.SMALL, color=c)
        strip.set_yticks(range(len(names)), names)
        strip.set_ylim(len(names) - .4, -.6)
        strip.tick_params(labelbottom=False, length=0)
        strip.spines[["left", "bottom"]].set_visible(False)
        strip.set_title("Tumble rates with no recovery (x)")
        strip.grid(axis="x")
        lost.axhline(budget, color=fs.GRAY, ls=":", lw=1)
        lost.text(4.25, budget, f"{budget:g} m height budget", ha="left", va="bottom",
                  fontsize=fs.SMALL, color=fs.GRAY)
        lost.set_ylim(0, budget * 1.12)
        lost.set_xlim(rates[0] - .4, rates[-1] + .4)
        lost.set_xlabel("Initial tumble rate (rad/s)")
        lost.set_ylabel("Altitude lost when\nrecovered (m)")
        within = all(np.nanmax(scans[n][0]) < budget for n in names)
        lost.set_title(f"Every recovery stays within the {budget:g} m budget" if within
                       else "Altitude lost on recovered releases")
        for i, name in enumerate(names):
            s = summary[name]
            c = fs.TIER[name]
            gyro_edge = s["envelope_edge"] == "gyro_limit"
            rate = s["max_recoverable_rate_rad_s"]
            edge_ax.plot(rate, i, "o", ms=7, mew=1.5, color=c, mfc="white" if gyro_edge else c)
            note = ("no failure up to\nthe gyro range" if gyro_edge
                    else f"fails at {rate + rates[1] - rates[0]:g} rad/s")
            edge_ax.annotate(f"{rate:g} rad/s\n{note}", (rate, i),
                             xytext=(-8, 0) if gyro_edge else (0, -8), textcoords="offset points",
                             ha="right" if gyro_edge else "center",
                             va="center" if gyro_edge else "top", fontsize=fs.SMALL, color=c)
        edge_ax.axvline(gyro, color=fs.GRAY, ls=":", lw=1)
        edge_ax.text(gyro / 1.18, len(names) - .2, f"gyro range\n{np.degrees(gyro):.0f}°/s",
                     ha="right", va="center", fontsize=fs.SMALL, color=fs.GRAY)
        edge_ax.set_xscale("log")
        edge_ax.set_xlim(.3, 70)
        edge_ax.set_xticks([1, 3, 10, 30], ["1", "3", "10", "30"])
        edge_ax.minorticks_off()
        edge_ax.set_yticks(range(len(names)), names)
        edge_ax.set_ylim(len(names) + .1, -.6)
        edge_ax.tick_params(axis="y", length=0)
        edge_ax.spines["left"].set_visible(False)
        edge_ax.grid(axis="y")
        edge_ax.set_xlabel("Highest rate recovered\nbefore first failure (rad/s)")
        only = [n for n in names if summary[n]["envelope_edge"] == "gyro_limit"]
        edge_ax.set_title(f"Only the {only[0]} tier reaches\nthe gyro range" if len(only) == 1
                          else "Envelope edge per tier")
        fs.panel_letter(fig, strip, "a", dx=-.08)
        fs.panel_letter(fig, edge_ax, "b", dx=-.07)
        failing = sorted((first_fail[n], n) for n in names if first_fail[n] is not None)
        never = [n for n in names if first_fail[n] is None]
        headline = "; ".join(f"{n.capitalize() if k == 0 else n} tier first fails at {r:g} rad/s"
                             if k == 0 else f"{n} at {r:g}" for k, (r, n) in enumerate(failing))
        if never:
            headline += f"; {' and '.join(never)} never fails in the scan"
        fig.text(.02, .975, headline, va="top")
        fig.text(.02, .925, f"Deterministic 6-DoF simulation with estimated parameter tiers; "
                 f"{np.degrees(INIT_TILT):.0f}° initial tilt,\n{budget:g} m height budget, "
                 f"{rates[1] - rates[0]:g} rad/s scan steps.", va="top",
                 fontsize=fs.SMALL, color=fs.GRAY)
        fs.save(fig, FIGS / "release_recovery_envelope.png", ("png", "pdf"))
    plt.close(fig)


def main():
    FIGS.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)
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
