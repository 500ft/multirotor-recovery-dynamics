"""Allocation-map checks against the hand-derived rotor-out anchors."""

import unittest
from math import sqrt

import numpy as np

from Analysis.failure_allocation import FAILURE_CLASSES, FailureCase, MotorAllocation

ARM = 0.060
T_MAX = 4.2
YAW = 0.004


def make(name):
    return MotorAllocation(FAILURE_CLASSES[name], arm_m=ARM, max_thrust_n=T_MAX,
                           yaw_torque_n_m=YAW)


class TestGeometry(unittest.TestCase):
    def test_nominal_pure_collective_splits_evenly(self):
        alloc = MotorAllocation(FailureCase("nominal"), ARM, T_MAX, YAW)
        torque, thrust = alloc.apply(np.zeros(3), 1.2, T_MAX)
        self.assertAlmostEqual(thrust, 1.2, places=12)
        np.testing.assert_allclose(torque, 0.0, atol=1e-12)

    def test_nominal_roll_torque_matches_mixer_formula(self):
        # at mid-collective the full-complement map must reproduce the scalar
        # mixer capability the gated model uses: tau = 2*sqrt(2)*arm*d
        alloc = MotorAllocation(FailureCase("nominal"), ARM, T_MAX, YAW)
        thrust_cmd = T_MAX / 2.0
        d_max = T_MAX / 4.0 - thrust_cmd / 4.0
        tau_capability = 2.0 * sqrt(2.0) * ARM * d_max
        torque, thrust = alloc.apply(np.array([tau_capability, 0.0, 0.0]),
                                     thrust_cmd, T_MAX)
        self.assertAlmostEqual(torque[0], tau_capability, delta=1e-9)
        self.assertAlmostEqual(thrust, thrust_cmd, delta=1e-9)

    def test_one_out_balanced_flight_is_the_diagonal_pair(self):
        # zero roll/pitch torque with m4 dead forces f2 = 0, f1 = f3: the
        # remaining diagonal pair, collective ceiling 2*f_max.
        alloc = make("one_out")
        torque, thrust = alloc.apply(np.zeros(3), 2.0 * T_MAX / 4.0, T_MAX)
        self.assertAlmostEqual(thrust, 2.0 * T_MAX / 4.0, delta=1e-9)
        np.testing.assert_allclose(torque[:2], 0.0, atol=1e-9)
        # the co-rotating pair leaves an unbalanced drag torque: the spin
        self.assertGreater(abs(torque[2]), 0.9 * YAW)

    def test_one_out_collective_ceiling(self):
        alloc = make("one_out")
        _, thrust = alloc.apply(np.zeros(3), T_MAX, T_MAX)
        self.assertLessEqual(thrust, 3.0 * T_MAX / 4.0 + 1e-9)
        # max_collective is the BALANCED ceiling: the odd survivor's thrust
        # cannot be used without unbalancing, so one-out hovers on 2 f_max
        self.assertAlmostEqual(alloc.max_collective(T_MAX), 2.0 * T_MAX / 4.0)

    def test_one_out_dead_halfplane_torque_not_zeroed(self):
        # torque directions whose exact solution needs negative thrust on the
        # dead motor's balancer must still yield a moment aligned with the
        # command (the cascaded re-solve), not collapse to zero — one-out spins
        # slowly, so the command sweeps through this half-plane every revolution
        # (directions along the (1,-1) survivor-pair axis keep a feasible
        # component; a command exactly on (1,1) is genuinely unreachable with
        # the balancer pinned at zero and correctly yields no torque)
        alloc = make("one_out")
        for cmd in (np.array([-0.02, 0.0, 0.0]), np.array([0.0, -0.02, 0.0]),
                    np.array([-0.02, 0.01, 0.0])):
            torque, _ = alloc.apply(cmd, 2.0 * T_MAX / 4.0 * 0.6, T_MAX)
            self.assertGreater(float(np.dot(torque[:2], cmd[:2])), 0.0)

    def test_two_opposite_torque_only_about_one_diagonal(self):
        # survivors m1 (+a,+a) and m3 (-a,-a) lie on one diagonal: the achievable
        # torque axis is fixed along (1,-1), so tau_x = -tau_y always.
        alloc = make("two_opposite")
        for cmd in (np.array([0.02, 0.0, 0.0]), np.array([0.0, 0.02, 0.0]),
                    np.array([0.01, -0.02, 0.0])):
            torque, _ = alloc.apply(cmd, T_MAX / 4.0, T_MAX)
            self.assertAlmostEqual(torque[0], -torque[1], delta=1e-9)

    def test_two_adjacent_cannot_trim_roll_at_positive_thrust(self):
        # both survivors sit at +y: any positive collective produces positive
        # roll torque — hover trim does not exist for this class.
        alloc = make("two_adjacent")
        torque, thrust = alloc.apply(np.zeros(3), T_MAX / 4.0, T_MAX)
        if thrust > 1e-6:
            self.assertGreater(torque[0], 0.0)

    def test_partial_authority_caps_every_motor(self):
        alloc = make("partial_authority")
        self.assertAlmostEqual(alloc.max_collective(T_MAX), 0.6 * T_MAX)
        _, thrust = alloc.apply(np.zeros(3), T_MAX, T_MAX)
        self.assertLessEqual(thrust, 0.6 * T_MAX + 1e-9)

    def test_all_motors_failed_rejected(self):
        with self.assertRaises(ValueError):
            MotorAllocation(FailureCase("dead", failed=(0, 1, 2, 3)), ARM, T_MAX, YAW)

    def test_battery_sag_shrinks_caps(self):
        alloc = make("one_out")
        _, full = alloc.apply(np.zeros(3), T_MAX, T_MAX)
        _, sagged = alloc.apply(np.zeros(3), T_MAX, 0.9 * T_MAX)
        self.assertAlmostEqual(sagged, 0.9 * full, delta=1e-9)


if __name__ == "__main__":
    unittest.main()
