"""DR-SS-SCENARIO-01 analytic anchors, per the closeout handoff section 4C.

These run BEFORE any scenario sweep. Each checks the plant against a hand-derived
result, not against another simulation. Failure here stops the rerun.
"""

import unittest
from dataclasses import replace
from math import radians

import numpy as np

from Analysis.failure_allocation import (FAILURE_CLASSES, FailureCase,
                                         MotorAllocation, healthy_wrench_map,
                                         solve_healthy_trim)
from Analysis.sim_release_recovery import (G, SCENARIOS, nominal_params,
                                           simulate, with_mixer)

ARM, TMAX, YAW = 0.060, 4.2, 0.004


def _clean(mass=0.13):
    """Ideal vehicle: no CG offset, no bias, no drag — so anchors are exact."""
    p = with_mixer(nominal_params(), arm_m=ARM)
    return replace(p, mass_kg=mass, max_thrust_n=TMAX, drag_coefficient=0.0,
                   projected_area_m2=0.0)


def _alloc(p, case):
    return MotorAllocation(case, arm_m=p.arm_m, max_thrust_n=p.max_thrust_n,
                           yaw_torque_n_m=p.yaw_torque_n_m)


class TestTrimAnchors(unittest.TestCase):
    def test_symmetric_trim_is_mg_over_four(self):
        p = _clean()
        f, ok = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                   p.mass_kg, G)
        self.assertTrue(ok)
        np.testing.assert_allclose(f, p.mass_kg * G / 4.0, rtol=1e-6)

    def test_trim_cancels_a_cg_offset_moment(self):
        p = _clean()
        cg = (0.002, -0.001)
        f, ok = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                   p.mass_kg, G, cg_offset_m=cg)
        self.assertTrue(ok)
        w = healthy_wrench_map(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m) @ f
        self.assertAlmostEqual(w[0], p.mass_kg * G, places=6)
        # allocator moment plus the CG moment it must cancel
        self.assertAlmostEqual(w[1] + cg[1] * w[0], 0.0, places=7)
        self.assertAlmostEqual(w[2] - cg[0] * w[0], 0.0, places=7)

    def test_infeasible_trim_is_reported_not_silently_replaced(self):
        p = _clean(mass=5.0)      # far beyond the rotor caps
        f, ok = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                   p.mass_kg, G)
        self.assertFalse(ok)


class TestHeldWrenchAnchors(unittest.TestCase):
    """Anchors 1-5: what the plant must do in the instant after the fault."""

    def _initial_az(self, case, tilt=0.0, w0=0.0):
        p = _clean()
        f, ok = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                   p.mass_kg, G)
        self.assertTrue(ok)
        r = simulate(p, w0, tilt, motor_alloc=_alloc(p, case),
                     trim_thrusts=f, scenario="in_flight_hold_matched",
                     t_max=0.02, dt=5e-4)
        vz = r["log"]["vz"]
        return float(vz[2] - vz[1]) / 5e-4      # az over one early step

    def test_no_fault_holds_hover(self):
        """Anchor 1: all four held at trim -> no net vertical acceleration."""
        self.assertAlmostEqual(self._initial_az(FailureCase("nominal")), 0.0,
                               delta=0.05)

    def test_one_out_gives_minus_g_over_four(self):
        """Anchor 2: losing one of four rotors leaves 3mg/4 -> az = -g/4."""
        self.assertAlmostEqual(self._initial_az(FAILURE_CLASSES["one_out"]),
                               -G / 4.0, delta=0.05)

    def test_two_out_gives_minus_g_over_two(self):
        """Anchor 3: losing two leaves mg/2 -> az = -g/2, both topologies."""
        for name in ("two_adjacent", "two_opposite"):
            self.assertAlmostEqual(self._initial_az(FAILURE_CLASSES[name]),
                                   -G / 2.0, delta=0.05, msg=name)

    def test_adjacent_and_opposite_have_distinct_moment_signatures(self):
        """Anchor 3b: same collective loss, different moments."""
        p = _clean()
        f, _ = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                  p.mass_kg, G)
        b = healthy_wrench_map(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m)
        sig = {}
        for name in ("two_adjacent", "two_opposite"):
            fh = f.copy()
            fh[list(FAILURE_CLASSES[name].failed)] = 0.0
            sig[name] = b @ fh
        self.assertAlmostEqual(sig["two_adjacent"][0], sig["two_opposite"][0],
                               places=9)                     # same collective
        self.assertFalse(np.allclose(sig["two_adjacent"][1:3],
                                     sig["two_opposite"][1:3]))
        # Spin directions decide which topology cancels yaw drag. Losing the
        # ADJACENT pair (2,3) leaves rotors 0,1 with opposite spins, so their
        # drag torques cancel. Losing the OPPOSITE pair (1,3) leaves 0,2 — both
        # the same spin — so yaw drag adds. (An earlier version of this test
        # asserted the reverse; the anchor caught it.)
        self.assertAlmostEqual(sig["two_adjacent"][3], 0.0, places=9)
        self.assertNotAlmostEqual(sig["two_opposite"][3], 0.0, places=9)

    def test_partial_authority_is_a_cap_not_an_effectiveness_multiplier(self):
        """Anchor 5 / R02: a 60% CAP leaves a hover command untouched, because
        hover thrust per rotor is below the cap. An effectiveness multiplier
        would not. These must not be conflated."""
        p = _clean()
        f, _ = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                  p.mass_kg, G)
        cap = FAILURE_CLASSES["partial_authority"].authority_frac * p.max_thrust_n / 4.0
        self.assertLess(max(f), cap, "hover trim should sit under the reduced cap")
        az = self._initial_az(FAILURE_CLASSES["partial_authority"])
        self.assertAlmostEqual(az, 0.0, delta=0.05)


class TestSwitchTiming(unittest.TestCase):
    """Anchors 6-7: the event clock."""

    def _run(self, scenario, delay=None, tmax=1.0):
        p = _clean()
        if delay is not None:
            p = replace(p, detection_latency_s=delay)
        f, _ = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                  p.mass_kg, G)
        return p, simulate(p, 0.0, 0.0, motor_alloc=_alloc(p, FAILURE_CLASSES["one_out"]),
                           trim_thrusts=f, scenario=scenario, t_max=tmax)

    def test_immediate_arm_switches_earlier_than_matched(self):
        p, ri = self._run("in_flight_hold_immediate")
        _, rm = self._run("in_flight_hold_matched")
        self.assertAlmostEqual(ri["t_switch_requested_s"], p.detection_latency_s,
                               places=9)
        self.assertAlmostEqual(rm["t_switch_requested_s"],
                               p.detection_latency_s + p.motor_start_latency_s,
                               places=9)
        self.assertLess(ri["t_switch_requested_s"], rm["t_switch_requested_s"])

    def test_realized_switch_is_recorded_for_a_delay_off_the_dt_grid(self):
        """R06: a delay not divisible by dt must still be logged honestly."""
        odd = 0.10007                      # not a multiple of dt = 5e-4
        p, r = self._run("in_flight_hold_matched", delay=odd)
        self.assertAlmostEqual(r["t_switch_requested_s"],
                               odd + p.motor_start_latency_s, places=9)
        self.assertIsNotNone(r["t_switch_realized_s"])
        self.assertGreaterEqual(r["t_switch_realized_s"], r["t_switch_requested_s"])
        self.assertLess(r["t_switch_realized_s"] - r["t_switch_requested_s"], 5e-4)

    def test_zero_detection_delay_switches_immediately(self):
        _, r = self._run("in_flight_hold_immediate", delay=0.0)
        self.assertAlmostEqual(r["t_switch_requested_s"], 0.0, places=9)


class TestScenarioContract(unittest.TestCase):
    def test_legacy_is_the_default_and_unchanged(self):
        p = _clean()
        a = simulate(p, 1.0, radians(10.0), t_max=0.5)
        b = simulate(p, 1.0, radians(10.0), t_max=0.5, scenario="release_startup")
        self.assertEqual(a["scenario"], "release_startup")
        np.testing.assert_allclose(a["log"]["vz"], b["log"]["vz"])

    def test_legacy_has_no_thrust_before_the_switch(self):
        p = _clean()
        r = simulate(p, 0.0, 0.0, t_max=0.5)
        pre = [th for t, th in zip(r["log"]["t"], r["log"]["thrust"])
               if t < r["t_switch_requested_s"]]
        self.assertEqual(max(pre), 0.0)

    def test_in_flight_arms_hold_thrust_before_the_switch(self):
        """The whole point of the correction: healthy rotors keep producing."""
        p = _clean()
        f, _ = solve_healthy_trim(p.arm_m, p.max_thrust_n, p.yaw_torque_n_m,
                                  p.mass_kg, G)
        for scenario in ("in_flight_hold_matched", "in_flight_hold_immediate"):
            r = simulate(p, 0.0, 0.0, motor_alloc=_alloc(p, FAILURE_CLASSES["one_out"]),
                         trim_thrusts=f, scenario=scenario, t_max=0.5)
            pre = [th for t, th in zip(r["log"]["t"], r["log"]["thrust"])
                   if t < r["t_switch_requested_s"]]
            self.assertGreater(min(pre), 0.0, scenario)
            self.assertAlmostEqual(max(pre), 0.75 * p.mass_kg * G, delta=1e-6)

    def test_in_flight_arms_require_their_inputs(self):
        p = _clean()
        with self.assertRaises(ValueError):
            simulate(p, 0.0, 0.0, scenario="in_flight_hold_matched")

    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError):
            simulate(_clean(), 0.0, 0.0, scenario="wishful")

    def test_scenarios_tuple_is_the_registered_set(self):
        self.assertEqual(SCENARIOS, ("release_startup", "in_flight_hold_matched",
                                     "in_flight_hold_immediate"))


if __name__ == "__main__":
    unittest.main()
