"""Checks for paired aggregation in the requested scenario study."""

import unittest
from unittest.mock import patch

from Analysis.run_scenario_reselection import compare, run_pair


def record(pair, safe, status="contact", speed=3.0):
    r = {"case_index": 0, "pair": pair, "safe": safe, "status": status}
    if status == "contact":
        r.update(impact_speed_m_s=speed, impact_tilt_rad=0.1, t_contact_s=1.0)
    return r


class TestScenarioReselection(unittest.TestCase):
    def test_seed_pairs_all_arms_and_packages(self):
        case = {"class": "one_out", "h_m": 6.0, "vz0_m_s": 0.0,
                "omega0_rad_s": 2.0, "delay_s": 0.11}
        with patch("Analysis.run_scenario_reselection._one",
                   return_value={"safe": False, "status": "no_contact_timeout"}) as one:
            rows = run_pair((2, case, 9, 123))
        self.assertEqual(len(rows), 6)
        self.assertEqual({call.args[0] for call in one.call_args_list}, {(123, 2, 9)})
        self.assertEqual(len({(r["package"], r["arm"]) for r in rows}), 6)

    def test_no_disagreement_is_not_superiority(self):
        rows = [record(i, False) for i in range(20)]
        r = compare(rows, rows, 0.00625)
        self.assertEqual(r["discordant"], 0)
        self.assertEqual(r["delta"], 0)
        self.assertEqual(r["verdict"], "no_discordant_pairs")

    def test_binary_and_continuous_denominators_are_separate(self):
        a = [record(0, True, speed=1), record(1, False, "no_contact_timeout"),
             record(2, None, "trim_infeasible")]
        b = [record(0, False, speed=3), record(1, True, speed=1),
             record(2, None, "trim_infeasible")]
        r = compare(a, b, 0.05)
        self.assertEqual((r["n"], r["only_a"], r["only_b"], r["neither"]), (3, 1, 1, 1))
        self.assertEqual(r["feasible_trim"]["n"], 2)
        self.assertEqual(r["continuous"]["n_both_contact"], 1)
        self.assertEqual(r["continuous"]["impact_speed_m_s"]["mean_delta"], -2)

    def test_mismatched_pairs_fail(self):
        with self.assertRaises(ValueError):
            compare([record(0, True)], [record(1, True)], 0.05)


if __name__ == "__main__":
    unittest.main()
