import unittest
import numpy as np

from Analysis.qdrone_response import summarize


class QDroneResponseTests(unittest.TestCase):
    def sample(self):
        # Nonuniform grid, change at t=1. The last pre-command voltage differs
        # deliberately from voltage at/after the command.
        return np.array([[0, 0, 0, 16], [1, 1, 0, 14],
                         [1.5, 1, 0, 13], [3, 1, 0, 12], [4, 1, 0, 11]], float)

    def evaluate(self, data):
        return summarize(data, {'horizon_s': 2., 'step_threshold_m': .5})

    def test_nonuniform_time_weighted_voltage_and_signed_error(self):
        event = self.evaluate(self.sample())['events'][0]
        self.assertEqual(event['precommand_voltage_v'], 16)
        self.assertAlmostEqual(event['mean_voltage_v'], (.5*13.5+1.5*12.5)/2)
        self.assertEqual(event['bias_m'], -1)
        self.assertEqual(event['mae_m'], 1)
        self.assertEqual(event['rmse_m'], 1)

    def test_endpoint_between_samples(self):
        data = self.sample(); data[3, 0] = 3.5
        data[:, 2] = 1  # Zero tracking error throughout the selected window.
        event = self.evaluate(data)['events'][0]
        self.assertEqual(event['rmse_m'], 0)
        # At t=3 voltage is 12.25, linearly interpolated from actual times.
        self.assertAlmostEqual(event['mean_voltage_v'], (.5*13.5+1.5*12.625)/2)

    def test_end_censoring_is_retained(self):
        result = self.evaluate(self.sample()[:3])
        self.assertEqual(result['detected_steps'], 1)
        self.assertEqual(result['complete_steps'], 0)
        self.assertEqual(result['events'][0]['reason'], 'recording_ended')
        self.assertNotIn('rmse_m', result['events'][0])

    def test_next_command_and_nonfinite_response_are_retained(self):
        data = self.sample(); data[2:, 1] = 0
        result = self.evaluate(data)
        self.assertEqual(result['detected_steps'], 2)
        self.assertEqual(result['events'][0]['reason'], 'next_command_inside_horizon')
        self.assertEqual(result['events'][1]['direction'], 'down')
        data = self.sample(); data[2, 2] = np.nan
        self.assertEqual(self.evaluate(data)['events'][0]['reason'], 'nonfinite_response')

    def test_repeated_time_and_missing_command_reject_recording(self):
        data = self.sample(); data[2, 0] = data[1, 0]
        with self.assertRaises(ValueError): self.evaluate(data)
        data = self.sample(); data[2, 1] = np.nan
        with self.assertRaises(ValueError): self.evaluate(data)
