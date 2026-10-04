"""Physics and no-feedback tests for the executed NanoBench replay."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from numpy.testing import assert_allclose

from Analysis.nanobench_data import ACC, GYRO, MOTORS, QUAT, RECORD, columns, load, sha256
from Analysis.nanobench_replay import (
    angular_acceleration, body_torque, derivative, documented_models, motor_forces,
    persistence, propagate, rotate, rollout, select_models, trailing_mean,
)

FIXTURE = Path(__file__).parent/'fixtures/nanobench'
PROTOCOL = json.loads((RECORD/'protocol.json').read_text())


class ReplayPhysicsTests(unittest.TestCase):
    def setUp(self):
        self.models = documented_models(PROTOCOL)
        self.model = self.models['cf21plus_firmware']
        self.state = np.zeros((1, 13)); self.state[:, 9] = 1
        self.g = PROTOCOL['gravity_m_s2']

    def test_measured_mass_and_si_units(self):
        self.assertAlmostEqual(self.model['mass_kg'], .04085)
        # A kilogram/gram error would make the hover cancellation test fail too.
        assert_allclose(self.model['inertia_kg_m2'], [1.4e-5, 1.4e-5, 2.17e-5])
        force = np.full((1, 4), self.model['mass_kg']*self.g/4)
        assert_allclose(derivative(self.state, force, self.model, self.g), 0, atol=1e-14)
        freefall = derivative(self.state, force*0, self.model, self.g)
        assert_allclose(freefall[0, 3:6], [0, 0, -self.g])

    def test_scalar_last_body_to_world_gravity(self):
        # +90 degrees about body y: body thrust points along world +x.
        q = np.array([0, np.sqrt(.5), 0, np.sqrt(.5)])
        assert_allclose(rotate(q, np.array([0., 0., 1.])), [1, 0, 0], atol=1e-14)
        self.state[:, 6:10] = q
        f = np.full((1, 4), self.model['mass_kg']*self.g/4)
        assert_allclose(derivative(self.state, f, self.model, self.g)[0, 3:6],
                        [self.g, 0, -self.g], atol=1e-14)

    def test_motor_mapping_independent_cross_product(self):
        d = self.model['arm_m']/np.sqrt(2)
        positions = np.array([[d, -d, 0], [-d, -d, 0], [-d, d, 0], [d, d, 0]])
        # Unit upward force on each rotor: roll/pitch must equal r cross F.
        expected = np.cross(positions, [0, 0, 1])
        expected[:, 2] = np.array([-1, 1, -1, 1])*self.model['torque_per_thrust_m']
        assert_allclose(body_torque(np.eye(4), self.model), expected)
        assert_allclose(body_torque(np.ones(4), self.model), 0, atol=1e-15)

    def test_si_mixer_round_trip(self):
        # Independent forward mixer equations from collection firmware lines 98-107.
        desired = np.array([1e-4, -2e-4, 3e-5])
        d = self.model['arm_m']/np.sqrt(2)
        r, p, y = desired / [4*d, 4*d, 4*self.model['torque_per_thrust_m']]
        force = np.array([.1-r-p-y, .1-r+p+y, .1+r+p-y, .1+r-p+y])
        assert_allclose(body_torque(force, self.model), desired, atol=1e-17)

    def test_zero_command_all_curves_and_no_physical_cap(self):
        for model in self.models.values():
            assert_allclose(motor_forces(np.zeros((2, 4)), [3., 4.2], model), 0)
        f = motor_forces(np.full(4, 65535), 4.2, self.model)
        self.assertTrue(np.all(f > self.model['command_max_n']))
        self.assertGreater(self.models['thrust_upgrade_firmware']['thrust_coefficients'][0], 0)

    def test_pwm_voltage_forward_mapping_once(self):
        model = dict(self.model, thrust_coefficients=[0., 1., 0., 0.])
        assert_allclose(motor_forces(np.full(4, 32767.5), 4., model), 2.)
        for pwm, voltage in [(np.full(4, -1), 4), (np.full(4, 65536), 4), (np.ones(4), 0)]:
            with self.assertRaises(ValueError):
                motor_forces(pwm, voltage, model)

    def test_euler_free_rotation_cross_term(self):
        omega = np.array([1., 2., 3.]); j = np.array(self.model['inertia_kg_m2'])
        expected = np.array([(j[1]-j[2])*6/j[0], (j[2]-j[0])*3/j[1], (j[0]-j[1])*2/j[2]])
        assert_allclose(angular_acceleration(omega, np.zeros(4), self.model), expected)

    def test_long_rollout_has_no_state_resets(self):
        self.state[0, :6] = [1., 2., 3., .2, -.3, .4]
        dt = np.full((1, 50), .01)
        outputs = rollout(self.state, np.zeros((1, 50, 4)), dt, self.model, PROTOCOL, [10, 25, 50])
        for k, state in outputs.items():
            t = .01*k
            assert_allclose(state[0, :3], self.state[0, :3]+t*self.state[0, 3:6]+[0, 0, -.5*self.g*t*t], atol=1e-13)
            assert_allclose(state[0, 3:6], self.state[0, 3:6]+[0, 0, -self.g*t], atol=1e-13)
        assert_allclose(self.state[0, :6], [1, 2, 3, .2, -.3, .4])

    def test_recorded_commands_change_next_intervals_only(self):
        inputs = np.full((1, 50, 4), self.model['mass_kg']*self.g/4)
        first = rollout(self.state, inputs, np.full((1, 50), .01), self.model, PROTOCOL, [10, 50])
        inputs[:, 10:] = 0
        second = rollout(self.state, inputs, np.full((1, 50), .01), self.model, PROTOCOL, [10, 50])
        assert_allclose(first[10], second[10])
        self.assertLess(second[50][0, 2], first[50][0, 2]-.5)

    def test_constant_spin_attitude_and_persistence(self):
        self.state[0, 12] = 2.
        end = propagate(self.state, np.zeros((1, 4)), .5, self.model, self.g, .005)
        expected = [0, 0, np.sin(.5), np.cos(.5)]
        assert_allclose(end[0, 6:10], expected, atol=1e-10)
        assert_allclose(persistence(self.state, np.array([.5]))[0, 6:10], expected)
        # Constant-rate persistence leaves world velocity unchanged.
        assert_allclose(persistence(self.state, np.array([.5]))[0, 3:6], 0)

    def test_trailing_filter_has_no_future_or_global_nan_contamination(self):
        x = np.arange(20.)[:, None]
        y = trailing_mean(x, 3)
        changed = x.copy(); changed[10:] = 1000
        assert_allclose(trailing_mean(changed, 3)[:10], y[:10])
        x[5] = np.nan
        self.assertTrue(np.isnan(trailing_mean(x, 3)[5:8]).all())
        self.assertTrue(np.isfinite(trailing_mean(x, 3)[8:]).all())

    def test_final_split_requires_frozen_model_and_protocol(self):
        with self.assertRaisesRegex(ValueError, 'final_test requires'):
            select_models(PROTOCOL, 'final_test', None, None)
        frozen = dict(protocol_sha256=sha256(RECORD/'protocol.json'), model=self.model,
                      training_result='test-only-synthetic', frozen_commit='test-only')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'frozen.json'; p.write_text(json.dumps(frozen))
            selected = select_models(PROTOCOL, 'final_test', p, frozen['protocol_sha256'])
            self.assertEqual(selected['frozen_fitted'], self.model)

    def test_real_development_excerpt_uses_documented_units(self):
        source = json.loads((FIXTURE/'source.json').read_text())
        self.assertEqual(sha256(FIXTURE/'excitation.csv'), source['excerpt_sha256'])
        data = load(FIXTURE/'excitation.csv')
        # Authors' upright flight has approximately one g body specific force.
        self.assertTrue(.5 < np.median(data['imu_acc_z']) < 1.5)
        self.assertTrue(3 < np.median(data['pwr_pm_vbat']) < 4.3)
        self.assertTrue(np.allclose(np.linalg.norm(columns(data, QUAT), axis=1), 1., atol=.002))
        f = motor_forces(columns(data, MOTORS), data['pwr_pm_vbat'], self.model)
        self.assertEqual(f.shape, (70, 4))
        self.assertTrue(np.isfinite(f).all())
        # Body rates already arrive in rad/s; no degrees conversion in ingestion.
        self.assertEqual(columns(data, GYRO)[0, 0], data['imu_gyro_x'][0])


if __name__ == '__main__':
    unittest.main()
