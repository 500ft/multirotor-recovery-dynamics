"""Study A/B machinery: exact bounds, action models, kill criterion, policy map."""

import unittest
from dataclasses import replace
from math import radians, sqrt

import numpy as np

from Analysis.monte_carlo_recovery import clopper_pearson_lower
from Analysis.sim_release_recovery import G, nominal_params, simulate, with_mixer
from Analysis.failure_allocation import FAILURE_CLASSES, MotorAllocation
from Analysis import survivable_set as ss


class TestClopperPearsonUpper(unittest.TestCase):
    def test_symmetry_with_lower(self):
        for s, n in ((0, 20), (5, 20), (19, 20), (20, 20)):
            self.assertAlmostEqual(ss.clopper_pearson_upper(s, n),
                                   1.0 - clopper_pearson_lower(n - s, n), places=12)

    def test_zero_and_full(self):
        self.assertAlmostEqual(ss.clopper_pearson_upper(20, 20), 1.0)
        # rule-of-three regime: upper(0, n) = 1 - alpha**(1/n) ~ 3/n
        self.assertAlmostEqual(ss.clopper_pearson_upper(0, 100),
                               1.0 - 0.05 ** (1.0 / 100), places=6)

    def test_brackets_point_estimate(self):
        lo = clopper_pearson_lower(160, 200)
        hi = ss.clopper_pearson_upper(160, 200)
        self.assertLess(lo, 0.8)
        self.assertGreater(hi, 0.8)


class TestParachuteModel(unittest.TestCase):
    def test_long_fall_reaches_terminal(self):
        v = ss.parachute_impact_speed(200.0, 0.0, deploy_s=0.5, terminal_m_s=2.5)
        self.assertAlmostEqual(v, 2.5, delta=1e-6)

    def test_ground_before_deployment_is_ballistic(self):
        h = 1.0     # ballistic delay drop at 0.8 s is ~3.1 m > h
        v = ss.parachute_impact_speed(h, 0.0, deploy_s=0.8, terminal_m_s=2.5)
        self.assertAlmostEqual(v, sqrt(2.0 * G * h), delta=1e-9)

    def test_fast_initial_descent_decays_toward_terminal(self):
        v = ss.parachute_impact_speed(3.0, -8.0, deploy_s=0.1, terminal_m_s=2.5)
        self.assertLess(v, 8.0)
        self.assertGreater(v, 2.5)

    def test_calibration_against_published_model_outputs(self):
        """CALIBRATION check against Siotia et al. (2026), doi:10.1038/s41598-026-47045-0.

        Renamed 2026-09-24 (critique C03): this is NOT validation. Their 10 m and
        25 m landing outcomes are simulation/HIL results, not physical drop
        measurements, so agreeing with them is model-to-model calibration. The
        test pins our fitted inflation interval so it cannot drift silently; it
        cannot establish that either model matches reality, and it says nothing
        about the V995.

        Their 2 kg vehicle: 0.8 s deployment, 9.1 m/s from 10 m and 3.2 m/s from
        25 m. The pre-2026-09-22 model (no inflation phase) predicted 3.2 m/s at
        10 m — 2.8x optimistic — which is literature/claim-ledger.md C1.
        """
        published = {10.0: 9.1, 25.0: 3.2}
        for h, measured in published.items():
            v = ss.parachute_impact_speed(h, 0.0, deploy_s=0.8, terminal_m_s=3.2,
                                          inflate_s=ss.PARACHUTE_INFLATE_S)
            self.assertAlmostEqual(v, measured, delta=1.0,
                                   msg=f"{h} m: modelled {v:.2f}, measured {measured}")

    def test_low_altitude_case_is_sensitive_to_the_inflation_estimate(self):
        """The 10 m case sits where ballistic distance ~ available height, so the
        answer is steeply sensitive to an EST parameter. That is a property of the
        physics, not a modelling artifact, and it is why the parachute action's
        low-altitude cells carry more uncertainty than their bounds suggest."""
        a = ss.parachute_impact_speed(10.0, 0.0, 0.8, 3.2, inflate_s=0.594)
        b = ss.parachute_impact_speed(10.0, 0.0, 0.8, 3.2, inflate_s=0.600)
        self.assertGreater(abs(b - a), 0.5)   # 6 ms of inflation -> >0.5 m/s

    def test_terminal_speed_interpretation_mismatch_is_recorded(self):
        """C03: we take terminal from their 25 m landing outcome (3.2 m/s), but
        their stated m/Cd/A/rho give ~4.22 m/s. Unresolved; asserted so the
        discrepancy cannot be quietly tuned away."""
        from math import sqrt
        m, g, rho, cd, area = 2.0, 9.81, 1.225, 1.2, 1.5
        from_stated_params = sqrt(2 * m * g / (rho * cd * area))
        self.assertAlmostEqual(from_stated_params, 4.22, delta=0.02)
        self.assertGreater(abs(from_stated_params - 3.2), 0.9)

    def test_inflation_phase_is_what_fixes_the_low_altitude_case(self):
        # without the inflation phase the model is optimistic by ~2.8x at 10 m
        without = ss.parachute_impact_speed(10.0, 0.0, 0.8, 3.2, inflate_s=0.0)
        with_inflation = ss.parachute_impact_speed(10.0, 0.0, 0.8, 3.2,
                                                   inflate_s=ss.PARACHUTE_INFLATE_S)
        self.assertLess(without, 4.0)            # the old, unsupported answer
        self.assertGreater(with_inflation, 8.0)  # the measured regime
        self.assertGreater(with_inflation, without)

    def test_inflation_never_helps(self):
        # a longer inflation can only raise impact speed, never lower it
        prev = 0.0
        for inflate in (0.0, 0.3, 0.6, 1.0, 2.0):
            v = ss.parachute_impact_speed(20.0, 0.0, 0.8, 1.8, inflate_s=inflate)
            self.assertGreaterEqual(v, prev - 1e-9)
            prev = v

    def test_terminal_speed_coherent_with_bare_criterion(self):
        # a descent device whose terminal speed exceeds the impact limit is
        # impossible by construction (the spec's coherence requirement)
        self.assertLess(ss.PARACHUTE_TERMINAL_M_S, ss.BARE_CRITERION[0])

    def test_dispersed_terminal_speed_can_exceed_the_limit(self):
        """Known, documented property: the NOMINAL terminal speed clears the bare
        limit but the top of the dispersion does not, so a minority of draws are
        impossible at any height. Asserted so the property cannot change silently;
        narrowing the dispersion would mean inventing data (OQ-010)."""
        dispersed_max = ss.PARACHUTE_TERMINAL_M_S * 1.15
        self.assertGreater(dispersed_max, ss.BARE_CRITERION[0])
        impossible_fraction = ((dispersed_max - ss.BARE_CRITERION[0])
                               / (dispersed_max - ss.PARACHUTE_TERMINAL_M_S * 0.85))
        self.assertLess(impossible_fraction, 0.20)   # ~13% at present values

    def test_monotonic_in_height_after_deployment(self):
        vs = [ss.parachute_impact_speed(h, 0.0, deploy_s=0.4, terminal_m_s=2.5)
              for h in (2.0, 4.0, 8.0, 16.0)]
        # above the deployment-loss height, more height means closer to terminal
        self.assertGreater(vs[1], vs[3])


class TestLandingCriterion(unittest.TestCase):
    def test_bounds_enforced(self):
        crit = (2.0, radians(30.0))
        self.assertTrue(ss.landing_ok(1.9, radians(29.0), crit))
        self.assertFalse(ss.landing_ok(2.1, radians(10.0), crit))
        self.assertFalse(ss.landing_ok(1.0, radians(31.0), crit))

    def test_never_landed_is_unsafe_under_every_criterion(self):
        for crit in (ss.BARE_CRITERION, ss.GUARDED_CRITERION,
                     *ss.SENSITIVITY.values()):
            self.assertFalse(ss.landing_ok(float("inf"), float("inf"), crit))


def _row(cls, cell, action, s, n):
    return {"class": cls, "cell": cell, "action": action, "n": n, "successes": s,
            "p_safe": s / n, "p_safe_95_lower": clopper_pearson_lower(s, n),
            "p_safe_95_upper": ss.clopper_pearson_upper(s, n),
            "sensitivity_successes": {"strict": s, "lenient": s}}


class TestKillCriterion(unittest.TestCase):
    def test_clear_dominance_justifies(self):
        rows = [_row("one_out", "c", "mechanism", 295, 300),
                _row("one_out", "c", "realloc_only", 150, 300)]
        verdict = ss.kill_criterion(rows, expected_pairs=1)
        self.assertTrue(verdict["mechanism_justified"])
        self.assertTrue(verdict["comparisons"][0]["mechanism_dominates"])

    def test_tie_within_uncertainty_kills(self):
        rows = [_row("one_out", "c", "mechanism", 290, 300),
                _row("one_out", "c", "realloc_only", 285, 300)]
        verdict = ss.kill_criterion(rows, expected_pairs=1)
        self.assertFalse(verdict["mechanism_justified"])
        self.assertIn("KILL", verdict["verdict"])
        self.assertFalse(verdict["comparisons"][0]["both_actions_fail"])

    def test_empty_or_truncated_comparison_set_is_incomplete_not_kill(self):
        # F09 (review-2026-09-19): any([]) is False, so an empty set used to
        # read as a completed negative verdict
        for rows in ([], [_row("one_out", "c", "mechanism", 0, 300),
                           _row("one_out", "c", "realloc_only", 0, 300)]):
            verdict = ss.kill_criterion(rows)
            self.assertIsNone(verdict["mechanism_justified"])
            self.assertIn("INCOMPLETE", verdict["verdict"])
            self.assertNotIn("KILL", verdict["verdict"])

    def test_explicit_expected_pairs_completes_a_small_set(self):
        rows = [_row("one_out", "c", "mechanism", 0, 300),
                _row("one_out", "c", "realloc_only", 0, 300)]
        verdict = ss.kill_criterion(rows, expected_pairs=1)
        self.assertIn("KILL", verdict["verdict"])

    def test_mutual_failure_is_flagged_as_controller_finding(self):
        rows = [_row("one_out", "c", "mechanism", 0, 300),
                _row("one_out", "c", "realloc_only", 0, 300)]
        verdict = ss.kill_criterion(rows, expected_pairs=1)
        self.assertFalse(verdict["mechanism_justified"])
        self.assertTrue(verdict["comparisons"][0]["both_actions_fail"])

    def test_reverse_dominance_reported(self):
        rows = [_row("one_out", "c", "mechanism", 150, 300),
                _row("one_out", "c", "realloc_only", 295, 300)]
        verdict = ss.kill_criterion(rows, expected_pairs=1)
        self.assertFalse(verdict["mechanism_justified"])
        self.assertTrue(verdict["comparisons"][0]["realloc_dominates"])


class TestPairedAnalysis(unittest.TestCase):
    """literature/claim-ledger.md E1: the action comparison is paired."""

    def test_table_counts(self):
        t = ss.paired_table([True, True, False, False], [True, False, True, False])
        self.assertEqual((t["both_safe"], t["only_a"], t["only_b"], t["neither"]),
                         (1, 1, 1, 1))
        self.assertEqual((t["n"], t["discordant"]), (4, 2))

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            ss.paired_table([True], [True, False])

    def test_identical_outcomes_are_not_a_tie_but_an_absence_of_evidence(self):
        v = ss.paired_verdict(ss.paired_table([True] * 50, [True] * 50))
        self.assertEqual(v["verdict"], "no_discordant_pairs")
        self.assertEqual(v["discordant"], 0)
        self.assertEqual(v["midp"], 1.0)
        self.assertIsNone(v["pi_lower"])

    def test_clean_dominance_detected(self):
        v = ss.paired_verdict(ss.paired_table([True] * 12, [False] * 12))
        self.assertEqual(v["verdict"], "a_superior")
        self.assertLess(v["midp"], 0.01)
        v2 = ss.paired_verdict(ss.paired_table([False] * 12, [True] * 12))
        self.assertEqual(v2["verdict"], "b_superior")

    def test_small_discordant_count_is_not_distinguished(self):
        v = ss.paired_verdict(ss.paired_table([True] * 5 + [False] * 5,
                                              [False] * 5 + [True] * 5))
        self.assertEqual(v["verdict"], "not_distinguished")
        self.assertEqual(v["midp"], 1.0)

    def test_reports_marginal_delta_not_only_conditional_pi(self):
        """C09: pi is the conditional win-rate among discordant pairs; delta is
        the unconditional improvement in landing success. They are different
        numbers and both must be reported."""
        # 10 of 100 favour A, 2 favour B -> delta = 0.08, pi = 10/12 = 0.833
        a = [True] * 10 + [False] * 2 + [True] * 44 + [False] * 44
        b = [False] * 10 + [True] * 2 + [True] * 44 + [False] * 44
        v = ss.paired_verdict(ss.paired_table(a, b))
        self.assertAlmostEqual(v["delta"], 0.08, places=9)
        self.assertNotAlmostEqual(v["delta"], v["only_a"] / v["discordant"])
        self.assertAlmostEqual(v["only_a"] / v["discordant"], 10 / 12, places=9)

    def test_delta_is_zero_and_defined_when_no_discordant_pairs(self):
        v = ss.paired_verdict(ss.paired_table([True] * 20, [True] * 20))
        self.assertEqual(v["delta"], 0.0)
        self.assertEqual(v["verdict"], "no_discordant_pairs")

    def test_midp_matches_exact_binomial_construction(self):
        # b of m successes under Binomial(m, 1/2); all-one-sided case is 0.5**m
        for m in (1, 5, 10):
            self.assertAlmostEqual(ss.mcnemar_midp(m, 0), 0.5 ** m, places=12)
        self.assertEqual(ss.mcnemar_midp(0, 0), 1.0)
        # symmetry
        self.assertAlmostEqual(ss.mcnemar_midp(7, 2), ss.mcnemar_midp(2, 7))

    def test_pairing_requires_identical_draws(self):
        """The seed must not depend on the action, or the pairing is fictional."""
        from Analysis.run_survivable_set import build_tasks
        seeds = {}
        for class_name, cell, action, n, seed, variant in build_tasks(scale=10):
            if action in ("mechanism", "realloc_only"):
                seeds.setdefault((class_name, cell, variant, seed), set()).add(action)
        paired = [k for k, v in seeds.items() if len(v) == 2]
        self.assertTrue(paired, "no (class, cell, variant, seed) shared by both actions")


class TestPolicyMap(unittest.TestCase):
    def test_best_action_by_lower_bound_with_ambiguity(self):
        rows = [_row("one_out", "c", "mechanism", 295, 300),
                _row("one_out", "c", "realloc_only", 200, 300),
                _row("one_out", "c", "parachute", 290, 300)]
        (row,) = ss.policy_map(rows)
        self.assertEqual(row["best_action"], "mechanism")
        self.assertEqual(row["ambiguous_with"], ["parachute"])

    def test_clear_winner_has_no_ambiguity(self):
        rows = [_row("one_out", "c", "mechanism", 299, 300),
                _row("one_out", "c", "realloc_only", 100, 300),
                _row("one_out", "c", "parachute", 120, 300)]
        (row,) = ss.policy_map(rows)
        self.assertEqual(row["best_action"], "mechanism")
        self.assertEqual(row["ambiguous_with"], [])


class TestMergeRows(unittest.TestCase):
    def test_chunks_merge_to_totals(self):
        a, b = _row("x", "c", "mechanism", 20, 25), _row("x", "c", "mechanism", 22, 25)
        m = ss.merge_rows([a, b])
        self.assertEqual((m["successes"], m["n"]), (42, 50))
        self.assertAlmostEqual(m["p_safe_95_lower"], clopper_pearson_lower(42, 50))
        self.assertEqual(m["sensitivity_successes"]["strict"], 42)


class TestDropTestPrediction(unittest.TestCase):
    """The registered Study C prediction must match the committed sweep data.

    Same rationale as test_results_numbers: a document that quotes generated
    numbers drifts silently unless a test pins it to the generator's output.
    """

    CELL = "h3_vz0_w6_d0.11"

    @classmethod
    def setUpClass(cls):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        cls.doc = (root / "docs" / "specs" / "survivable-set"
                   / "drop-test-prediction.md").read_text(encoding="utf-8")
        cls.data = {
            "a": json.loads((root / "Data" / "survivable_set_results.json")
                            .read_text()),
            "a2": json.loads((root / "Data" / "survivable_set_results_a2.json")
                             .read_text()),
        }

    def _rows(self):
        import re
        pat = re.compile(
            r"^\| (a2?) \| (\w+) \| (\w+) \| (\d+)/(\d+) \| ([\d.]+) \| ([\d.]+) \|",
            re.M)
        rows = pat.findall(self.doc)
        self.assertGreaterEqual(len(rows), 10, "prediction table not found")
        return rows

    def test_every_table_row_matches_the_committed_sweep(self):
        for variant, cls_name, action, s, n, lo, hi in self._rows():
            match = [r for r in self.data[variant]["exploratory"]
                     if (r["class"], r["cell"], r["action"])
                     == (cls_name, self.CELL, action)]
            self.assertTrue(match, f"no sweep row for {variant}/{cls_name}/{action}")
            r = match[0]
            self.assertEqual((int(s), int(n)), (r["successes"], r["n"]),
                             f"stale s/n in prediction row {variant}/{cls_name}/{action}")
            self.assertAlmostEqual(float(lo), r["p_safe_95_lower"], places=4)
            self.assertAlmostEqual(float(hi), r["p_safe_95_upper"], places=4)

    def test_registered_cell_is_a_primary_cell(self):
        self.assertIn(self.CELL, [c.label() for c in ss.PRIMARY_CELLS])


class TestSimExtensions(unittest.TestCase):
    """The new simulate() arguments, exercised on real dynamics (slow-ish)."""

    def test_descent_mode_lands_softly_on_nominal_vehicle(self):
        p = with_mixer(nominal_params())
        r = simulate(p, 0.5, radians(10.0), descent_rate_m_s=1.0, t_max=8.0)
        self.assertTrue(r["crashed"])          # touched down, by construction
        impact_vz = abs(float(r["log"]["vz"][-1]))
        self.assertLess(impact_vz, 2.0)
        self.assertLess(float(r["log"]["tilt"][-1]), radians(30.0))

    def test_initial_vz_shortens_time_to_ground(self):
        p = with_mixer(nominal_params())
        slow = simulate(p, 0.5, radians(10.0), descent_rate_m_s=2.5, t_max=8.0)
        fast = simulate(p, 0.5, radians(10.0), descent_rate_m_s=2.5, t_max=8.0,
                        initial_vz_m_s=-2.0)
        self.assertTrue(slow["crashed"] and fast["crashed"])
        self.assertLess(fast["log"]["t"][-1], slow["log"]["t"][-1])

    def test_one_out_allocation_still_rights_the_vehicle(self):
        p = with_mixer(nominal_params())
        alloc = MotorAllocation(FAILURE_CLASSES["one_out"], arm_m=p.arm_m,
                                max_thrust_n=p.max_thrust_n,
                                yaw_torque_n_m=p.yaw_torque_n_m)
        r = simulate(p, 2.0, radians(20.0), motor_alloc=alloc,
                     descent_rate_m_s=1.0, t_max=10.0)
        self.assertTrue(r["crashed"])
        self.assertLess(abs(float(r["log"]["vz"][-1])), 2.5)

    def test_partial_authority_verification_anchor(self):
        # spec 7b: the partial-authority class must land as softly as the
        # full-complement vehicle — verifies allocation + descent machinery
        p = with_mixer(nominal_params())
        alloc = MotorAllocation(FAILURE_CLASSES["partial_authority"], arm_m=p.arm_m,
                                max_thrust_n=p.max_thrust_n,
                                yaw_torque_n_m=p.yaw_torque_n_m)
        r = simulate(p, 2.0, radians(15.0), motor_alloc=alloc,
                     descent_rate_m_s=1.0, t_max=10.0)
        self.assertTrue(r["crashed"])
        self.assertLess(abs(float(r["log"]["vz"][-1])), 1.5)
        self.assertLess(float(r["log"]["tilt"][-1]), radians(10.0))

    def test_two_adjacent_allocation_cannot_land_softly(self):
        p = with_mixer(nominal_params())
        alloc = MotorAllocation(FAILURE_CLASSES["two_adjacent"], arm_m=p.arm_m,
                                max_thrust_n=p.max_thrust_n,
                                yaw_torque_n_m=p.yaw_torque_n_m)
        r = simulate(p, 2.0, radians(20.0), motor_alloc=alloc,
                     descent_rate_m_s=1.0, t_max=10.0)
        impact_vz = abs(float(r["log"]["vz"][-1])) if r["crashed"] else float("inf")
        self.assertGreater(impact_vz, 2.0)

    def test_evaluate_cell_smoke(self):
        cell = ss.Cell(1.5, 0.0, 2.0, 0.11)
        row = ss.evaluate_cell("one_out", cell, "mechanism", 3, (1, 2, 3))
        self.assertEqual(row["n"], 3)
        self.assertLessEqual(row["p_safe_95_lower"], row["p_safe"])
        self.assertLessEqual(row["p_safe"], row["p_safe_95_upper"])
        # deterministic under the same seed
        again = ss.evaluate_cell("one_out", cell, "mechanism", 3, (1, 2, 3))
        self.assertEqual(row["successes"], again["successes"])

    def test_evaluate_cell_a2_variant_recorded_and_deterministic(self):
        cell = ss.Cell(1.5, 0.0, 2.0, 0.11)
        row = ss.evaluate_cell("one_out", cell, "mechanism", 3, (1, 2, 3),
                               variant="a2")
        self.assertEqual(row["variant"], "a2")
        again = ss.evaluate_cell("one_out", cell, "mechanism", 3, (1, 2, 3),
                                 variant="a2")
        self.assertEqual(row["successes"], again["successes"])

    def test_yaw_drag_bounds_rotor_out_spin_inside_gyro_range(self):
        # A2 coherence: the EST drag coefficient must hold the drag-torque spin
        # below the gyro range — an unmeasurable spin cannot be claimed controlled
        p = replace(with_mixer(nominal_params()), available_height_m=50.0,
                    yaw_drag_n_m_s2=ss.A2_YAW_DRAG_N_M_S2)
        alloc = MotorAllocation(FAILURE_CLASSES["one_out"], arm_m=p.arm_m,
                                max_thrust_n=p.max_thrust_n,
                                yaw_torque_n_m=p.yaw_torque_n_m)
        r = simulate(p, 2.0, radians(15.0), motor_alloc=alloc,
                     descent_rate_m_s=1.0, t_max=6.0, spin_aware=True)
        self.assertLess(float(np.max(np.abs(r["log"]["omega_mag"]))),
                        p.gyro_limit_rad_s)

    def test_mech_mass_fraction_is_tied_to_the_live_rollup(self):
        from Analysis.budget import load_mass_budget, rollup
        nominal = float(rollup(load_mass_budget())["nominal_g"])
        self.assertAlmostEqual(ss.MECH_MASS_FRAC, ss.MECH_MASS_G_EST / nominal,
                               places=12)
        self.assertLess(ss.MECH_MASS_FRAC, 0.5)


if __name__ == "__main__":
    unittest.main()


class TestRunnerOutputIsolation(unittest.TestCase):
    """F03 (review-2026-09-19): --quick replaced the committed 300-trial JSONs."""

    def test_quick_never_resolves_into_tracked_dirs(self):
        import tempfile
        from pathlib import Path
        from Analysis.run_survivable_set import resolve_output_dir
        repo = Path(tempfile.mkdtemp()).resolve()
        out = resolve_output_dir(repo, quick=True, output_dir=None)
        self.assertNotIn(repo, out.parents)
        for bad in (repo / "Data", repo / "Data" / "sub", repo / "Figures"):
            with self.assertRaises(SystemExit):
                resolve_output_dir(repo, quick=True, output_dir=str(bad))
        self.assertEqual(resolve_output_dir(repo, quick=False, output_dir=None), repo)
        scratch = Path(tempfile.mkdtemp())
        self.assertEqual(resolve_output_dir(repo, quick=True, output_dir=str(scratch)),
                         scratch.resolve())
