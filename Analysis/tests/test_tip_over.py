"""Tip-over geometry bound, per literature/claim-ledger.md B1."""

import unittest
from math import atan

from Analysis.tip_over import (BARE_FOOTPRINT_RADIUS_M,
                               GUARD_FOOTPRINT_RADIUS_M, bracket_deg,
                               tip_over_angle_rad)


class TestTipOverAngle(unittest.TestCase):
    def test_matches_hand_derived_atan(self):
        # 60 mm footprint, 30 mm CG height -> atan(2)
        got = tip_over_angle_rad(0.060, 0.030)
        self.assertAlmostEqual(got, atan(2.0), places=9)

    def test_rejects_nonpositive_cg_height(self):
        with self.assertRaises(ValueError):
            tip_over_angle_rad(0.060, 0.0)

    def test_bracket_widens_with_footprint(self):
        bare_lo, bare_hi = bracket_deg(BARE_FOOTPRINT_RADIUS_M)
        guard_lo, guard_hi = bracket_deg(max(GUARD_FOOTPRINT_RADIUS_M))
        # a wider footprint tips over later at every CG height in the bracket
        self.assertGreater(guard_lo, bare_lo)
        self.assertGreater(guard_hi, bare_hi)

    def test_asserted_criteria_sit_inside_geometric_bound(self):
        # BARE_CRITERION / GUARDED_CRITERION tilt limits in Analysis/survivable_set.py
        bare_lo, _ = bracket_deg(BARE_FOOTPRINT_RADIUS_M)
        guard_lo = min(bracket_deg(r)[0] for r in GUARD_FOOTPRINT_RADIUS_M)
        self.assertGreater(bare_lo, 30.0)
        self.assertGreater(guard_lo, 60.0)


if __name__ == "__main__":
    unittest.main()
