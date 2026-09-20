#!/usr/bin/env python3
"""Study A/B: survivable set and recovery policy after partial propulsion loss.

Research question (preregistered in ``docs/specs/survivable-set/design.md``): after a
propulsion failure at post-failure state ``(h, vz, omega, delay)``, which recovery
action maximises the probability of a survivable landing — and does the dedicated
recovery mechanism enlarge the survivable set beyond thrust reallocation alone?

Actions compared (definitions frozen before any sweep is run):

* ``realloc_only`` — the mechanism-less vehicle: per-motor thrust reallocation
  (``failure_allocation``) under the same PD controller, WITHOUT the guard-enabled
  quarter-collective inverted-authority floor, judged against the bare landing
  criterion, with the mechanism's mass and rim inertia removed (EST credit).
* ``mechanism`` — the guarded vehicle: same reallocation plus the control floor
  (the behavior the guard physically enables — motors keep spinning inverted), judged
  against the guard-relaxed impact criterion (EST until drop-test data exists).
* ``parachute`` — a parachute-like drag device: motors cut, ballistic fall during the
  deployment delay, then quadratic-drag approach to terminal speed (closed form; no
  6-DoF run needed). Independent of the failure class since propulsion is unused.

Statistics: exact one-sided Clopper-Pearson bounds (reusing the gated implementation
in ``monte_carlo_recovery``); a cell "supports" an action only through its bound,
never its point estimate. KILL CRITERION (preregistered): the mechanism is justified
only if, in at least one primary (failure class x cell), its 95% lower bound exceeds
the reallocation action's 95% upper bound — dominance beyond Monte Carlo
uncertainty. Otherwise the mechanism has not earned its mass and the study reports
that and redirects to the policy alone.

All mechanism/parachute parameters marked EST are owner inputs (OQ-010); the sweep
is a SIMULATION-ONLY PREDICTION until the bench/drop gates (Study C) run.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from math import exp, radians, sqrt

import numpy as np

from Analysis.budget import load_mass_budget, rollup
from Analysis.failure_allocation import FAILURE_CLASSES, MotorAllocation
from Analysis.monte_carlo_recovery import clopper_pearson_lower, draw_case
from Analysis.sim_release_recovery import G, nominal_params, simulate, with_mixer

# ---------------------------------------------------------------- preregistration
# Landing criterion: touchdown is survivable if the impact vertical speed and tilt
# are both within bounds. Numbers are PREREGISTERED-ASSUMED for the sub-250 g
# guarded class (impact KE at 165 g / 2.0 m/s is 0.33 J); sensitivity variants are
# reported alongside so the conclusion's dependence on the choice is visible.
BARE_CRITERION = (2.0, radians(30.0))        # (max |vz| m/s, max tilt) — no guard
GUARDED_CRITERION = (2.5, radians(60.0))     # EST: guard absorbs energy, tolerates tilt
SENSITIVITY = {"strict": (1.5, radians(20.0)), "lenient": (3.0, radians(45.0))}

# Mechanism-less vehicle credit (owner input OQ-010): removing the guard saves mass
# and, because the guard is rim material, proportionally more lateral inertia. The
# mass share is tied to the BOM: EST-MASS-012 carries frame+guard+mounts at 42.5 g
# nominal, of which the removable guard portion is EST 16 g until the CAD mass
# model splits the line; the fraction is computed against the live rollup so a
# budget change cannot silently stale it. Inertia share stays EST pending CAD.
MECH_MASS_G_EST = 16.0
MECH_MASS_FRAC = MECH_MASS_G_EST / float(rollup(load_mass_budget())["nominal_g"])
MECH_INERTIA_FRAC = 0.30

# Parachute-like device (EST, owner input OQ-010): small canopy sized for ~1.8 m/s
# at the frozen-max 165 g (~0.47 m^2 at Cd 1.4), sprung deployment. COHERENCE
# REQUIREMENT: the terminal speed must sit below the bare impact-speed limit or the
# action is impossible by construction (the first drafted value, 2.5 m/s, violated
# this and was corrected before any committed run — see the spec's audit note).
PARACHUTE_TERMINAL_M_S = 1.8
PARACHUTE_DEPLOY_S = 0.8
PARACHUTE_TILT_MAX_RAD = radians(45.0)       # pendulum under canopy, drawn U(0, max)

DESCENT_RATE_M_S = 1.0                       # commanded touchdown descent rate
INIT_TILT_MAX_RAD = radians(30.0)            # tilt at failure, drawn U(0, max)
ARM_M = 0.060                                # ASSUMED build arm (matches run_sweep)
T_MAX_S = 12.0

# Study A2 (docs/specs/survivable-set/design-a2.md): spin-aware variant. The yaw
# rotational-drag coefficient is EST (owner input, OQ-010): sized so the rotor-out
# drag-torque spin reaches a terminal rate ~ sqrt(kappa*T_bal / c) ~ 26 rad/s,
# safely inside the gyro range (35 rad/s) — a spin the sensor cannot measure could
# not be claimed as controlled.
A2_YAW_DRAG_N_M_S2 = 6e-6
VARIANTS = ("a", "a2")

ACTIONS = ("realloc_only", "mechanism", "parachute")


@dataclass(frozen=True)
class Cell:
    """One post-failure state: height, vertical speed, tumble rate, detection delay."""

    h_m: float
    vz0_m_s: float
    omega0_rad_s: float
    delay_s: float

    def label(self) -> str:
        return (f"h{self.h_m:g}_vz{self.vz0_m_s:g}"
                f"_w{self.omega0_rad_s:g}_d{self.delay_s:g}")


EXPLORATORY_CELLS = tuple(
    Cell(h, vz, w, d)
    for h, vz, w, d in product((1.5, 3.0, 6.0), (0.0, -1.5), (2.0, 6.0), (0.11, 0.30))
)
# Primary cells for the kill criterion: the cage-testable Study-C drop condition
# (3 m, tumbling, BOM-latency detection) and a low/late worst case.
PRIMARY_CELLS = (Cell(3.0, 0.0, 6.0, 0.11), Cell(1.5, -1.5, 2.0, 0.30))
PRIMARY_CLASSES = ("one_out", "two_adjacent")   # bracket easiest / hardest classes
EXPLORATORY_TRIALS = 30
PRIMARY_TRIALS = 300
PARACHUTE_TRIALS = 2000
BASE_SEED = 20260916


def clopper_pearson_upper(successes: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided upper bound, by symmetry with the gated lower bound."""
    return 1.0 - clopper_pearson_lower(n - successes, n, alpha)


def landing_ok(impact_speed_m_s: float, impact_tilt_rad: float,
               criterion: tuple[float, float]) -> bool:
    vz_max, tilt_max = criterion
    return impact_speed_m_s <= vz_max and impact_tilt_rad <= tilt_max


def parachute_impact_speed(h_m: float, vz0_m_s: float, deploy_s: float,
                           terminal_m_s: float) -> float:
    """Impact speed for the drag-device action (closed form, downward positive).

    Ballistic (drag-free, conservative) fall during deployment, then quadratic-drag
    approach to terminal speed over the remaining drop:
    ``s^2 = v_t^2 + (s1^2 - v_t^2) exp(-2 g d / v_t^2)``. If the ground arrives
    before deployment completes, the fall is ballistic the whole way.
    """
    s0 = max(0.0, -vz0_m_s)
    d1 = s0 * deploy_s + 0.5 * G * deploy_s ** 2
    if d1 >= h_m:
        return sqrt(s0 ** 2 + 2.0 * G * h_m)
    s1 = s0 + G * deploy_s
    d2 = h_m - d1
    return sqrt(terminal_m_s ** 2
                + (s1 ** 2 - terminal_m_s ** 2) * exp(-2.0 * G * d2 / terminal_m_s ** 2))


def _draw_vehicle(rng: np.random.Generator, cell: Cell, *, mechanism: bool):
    """One dispersed vehicle configured for a Study-A cell.

    Reuses the gated dispersion draw; the cell's delay is a state coordinate and
    overrides the dispersed detection latency exactly. The mechanism-less vehicle
    takes the EST mass/inertia credit.
    """
    p, imp = draw_case(rng)
    if not mechanism:
        p = replace(p, mass_kg=p.mass_kg * (1.0 - MECH_MASS_FRAC),
                    inertia_lateral_kg_m2=p.inertia_lateral_kg_m2
                    * (1.0 - MECH_INERTIA_FRAC))
    arm_scale = p.max_torque_n_m / nominal_params().max_torque_n_m
    p = with_mixer(p, arm_m=ARM_M * arm_scale)
    p = replace(p, available_height_m=cell.h_m, detection_latency_s=cell.delay_s)
    return p, imp


def _realloc_trial(rng: np.random.Generator, class_name: str, cell: Cell,
                   *, mechanism: bool, variant: str = "a",
                   dt: float = 5e-4) -> tuple[float, float]:
    """One 6-DoF trial; returns (impact_speed_down_m_s, impact_tilt_rad).

    ``variant="a2"`` switches on the spin-aware controller (gyroscopic
    feedforward) and the EST yaw rotational drag; ``dt`` is exposed for the
    integrator-convergence diagnostic only. A run that never reaches the ground
    within ``T_MAX_S`` did not land; it is reported as an effectively infinite
    impact state (conservative: counted unsafe under every criterion).
    """
    p, imp = _draw_vehicle(rng, cell, mechanism=mechanism)
    if variant == "a2":
        p = replace(p, yaw_drag_n_m_s2=A2_YAW_DRAG_N_M_S2)
    alloc = MotorAllocation(FAILURE_CLASSES[class_name], arm_m=p.arm_m,
                            max_thrust_n=p.max_thrust_n,
                            yaw_torque_n_m=p.yaw_torque_n_m)
    tilt0 = rng.uniform(0.0, INIT_TILT_MAX_RAD)
    r = simulate(p, cell.omega0_rad_s, tilt0, imperfections=imp,
                 initial_vz_m_s=cell.vz0_m_s, descent_rate_m_s=DESCENT_RATE_M_S,
                 motor_alloc=alloc, control_floor=mechanism, t_max=T_MAX_S,
                 spin_aware=variant == "a2", dt=dt)
    if not r["crashed"]:
        return float("inf"), float("inf")
    return abs(float(r["log"]["vz"][-1])), float(r["log"]["tilt"][-1])


def evaluate_cell(class_name: str, cell: Cell, action: str, n: int,
                  seed: tuple[int, ...], variant: str = "a") -> dict:
    """Monte Carlo P_safe for one (failure class, cell, action) with exact bounds."""
    rng = np.random.default_rng(seed)
    counts = {"primary": 0, "strict": 0, "lenient": 0}
    for _ in range(n):
        if action == "parachute":
            speed = parachute_impact_speed(
                cell.h_m, cell.vz0_m_s,
                PARACHUTE_DEPLOY_S * rng.uniform(0.8, 1.5),
                PARACHUTE_TERMINAL_M_S * rng.uniform(0.85, 1.15))
            tilt = rng.uniform(0.0, PARACHUTE_TILT_MAX_RAD)
            criterion = BARE_CRITERION
        else:
            mechanism = action == "mechanism"
            speed, tilt = _realloc_trial(rng, class_name, cell,
                                         mechanism=mechanism, variant=variant)
            criterion = GUARDED_CRITERION if mechanism else BARE_CRITERION
        counts["primary"] += landing_ok(speed, tilt, criterion)
        counts["strict"] += landing_ok(speed, tilt, SENSITIVITY["strict"])
        counts["lenient"] += landing_ok(speed, tilt, SENSITIVITY["lenient"])
    s = counts["primary"]
    return {
        "class": class_name, "cell": cell.label(), "action": action,
        "variant": variant,
        "n": n, "successes": s, "p_safe": s / n,
        "p_safe_95_lower": clopper_pearson_lower(s, n),
        "p_safe_95_upper": clopper_pearson_upper(s, n),
        "sensitivity_successes": {k: counts[k] for k in ("strict", "lenient")},
    }


def merge_rows(rows: list[dict]) -> dict:
    """Merge chunked ``evaluate_cell`` results for one (class, cell, action).

    Chunks exist so the parallel sweep stays load-balanced; each chunk has its own
    deterministic seed. Counts add; the exact bounds are recomputed on the totals.
    """
    first = rows[0]
    assert all((r["class"], r["cell"], r["action"])
               == (first["class"], first["cell"], first["action"]) for r in rows)
    n = sum(r["n"] for r in rows)
    s = sum(r["successes"] for r in rows)
    sens = {k: sum(r["sensitivity_successes"][k] for r in rows)
            for k in ("strict", "lenient")}
    return {
        "class": first["class"], "cell": first["cell"], "action": first["action"],
        "variant": first.get("variant", "a"),
        "n": n, "successes": s, "p_safe": s / n,
        "p_safe_95_lower": clopper_pearson_lower(s, n),
        "p_safe_95_upper": clopper_pearson_upper(s, n),
        "sensitivity_successes": sens,
    }


def kill_criterion(primary_results: list[dict],
                   expected_pairs: int | None = None) -> dict:
    """Preregistered mechanism-justification test on the primary (class, cell) set.

    Justified only if the mechanism's exact lower bound beats reallocation's exact
    upper bound somewhere; ties inside Monte Carlo uncertainty do NOT justify it.
    A truncated or empty comparison set is INCOMPLETE, never a verdict (F09,
    review-2026-09-19): ``expected_pairs`` defaults to the preregistered
    primary grid.
    """
    if expected_pairs is None:
        expected_pairs = len(PRIMARY_CLASSES) * len(PRIMARY_CELLS)
    by_key: dict[tuple[str, str], dict[str, dict]] = {}
    for r in primary_results:
        by_key.setdefault((r["class"], r["cell"]), {})[r["action"]] = r
    comparisons = []
    for (cls, cell), acts in sorted(by_key.items()):
        if "mechanism" not in acts or "realloc_only" not in acts:
            continue
        m, a = acts["mechanism"], acts["realloc_only"]
        comparisons.append({
            "class": cls, "cell": cell,
            "mechanism_lower": m["p_safe_95_lower"],
            "realloc_upper": a["p_safe_95_upper"],
            "mechanism_dominates": m["p_safe_95_lower"] > a["p_safe_95_upper"],
            "realloc_dominates": a["p_safe_95_lower"] > m["p_safe_95_upper"],
            # parity between two failing actions is a controller finding, not
            # evidence the actions are interchangeable — flag it for the report
            "both_actions_fail": (m["p_safe_95_upper"] < 0.5
                                  and a["p_safe_95_upper"] < 0.5),
        })
    if len(comparisons) < expected_pairs:
        return {
            "mechanism_justified": None,
            "verdict": (f"INCOMPLETE: {len(comparisons)}/{expected_pairs} primary "
                        "comparisons present — no verdict"),
            "comparisons": comparisons,
        }
    justified = any(c["mechanism_dominates"] for c in comparisons)
    return {
        "mechanism_justified": justified,
        "verdict": ("mechanism enlarges the survivable set beyond Monte Carlo "
                    "uncertainty" if justified else
                    "KILL: mechanism does not enlarge the survivable set beyond "
                    "Monte Carlo uncertainty — redirect to the policy alone"),
        "comparisons": comparisons,
    }


def policy_map(results: list[dict]) -> list[dict]:
    """Study B: best action per (class, cell) by exact lower bound, with ambiguity.

    An alternative action is 'ambiguous with' the best one when its interval
    overlaps the best action's lower bound — the map must say where it cannot
    distinguish, not silently pick a winner.
    """
    by_key: dict[tuple[str, str], dict[str, dict]] = {}
    for r in results:
        by_key.setdefault((r["class"], r["cell"]), {})[r["action"]] = r
    rows = []
    for (cls, cell), acts in sorted(by_key.items()):
        best = max(acts.values(), key=lambda r: (r["p_safe_95_lower"], r["p_safe"]))
        ambiguous = sorted(a for a, r in acts.items()
                           if a != best["action"]
                           and r["p_safe_95_upper"] >= best["p_safe_95_lower"])
        rows.append({"class": cls, "cell": cell, "best_action": best["action"],
                     "best_p_safe_95_lower": best["p_safe_95_lower"],
                     "ambiguous_with": ambiguous})
    return rows
