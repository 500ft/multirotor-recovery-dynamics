#!/usr/bin/env python3
"""Static tip-over geometry bound for the landing criterion.

`literature/claim-ledger.md` B1 flags the tilt limit in
`docs/specs/survivable-set/design.md` Sec.5 (30 deg bare / 60 deg guarded) as
having "no published basis at all" and calls for "a tip-over calculation on
our own guard geometry" instead. This module is that calculation.

It is a static wedge check, not a landing-impact simulation: at what tilt does
the CG's vertical projection cross the edge of the ground-contact footprint,
past which the vehicle rotates over rather than rocking back? No CAD mass
model exists yet (DR-CAD-05 is deferred), so CG height is a labelled ASSUMED
fraction of the stack height, not a measured value. This bounds the tilt
limit from geometry; it does not replace the drop test the design doc still
requires.
"""

from __future__ import annotations

from math import atan, degrees

# Bare-frame footprint radius: the motor-arm reach already assumed for the
# recovery sim (Analysis/survivable_set.py ARM_M, Analysis/sim_release_recovery.py).
BARE_FOOTPRINT_RADIUS_M = 0.060

# Guarded footprint radius: half of Design Report/README.md's "approximate
# outer footprint 125-140 mm square envelope" (EST, guard ring is the new
# ground-contact edge under tilt).
GUARD_FOOTPRINT_RADIUS_M = (0.125 / 2, 0.140 / 2)

# CG height as a fraction of the stack height (35-45 mm, README "Stack height
# target"). ASSUMED bracket, not measured: no CAD mass model exists (EST-MASS-012,
# DR-CAD-05 deferred). 0.35 skews low for a bottom-mounted battery; 0.65 skews
# high for top-heavy avionics; 0.50 is the symmetric default.
CG_HEIGHT_FRACTION = (0.35, 0.65)
STACK_HEIGHT_M = (0.035, 0.045)


def tip_over_angle_rad(footprint_radius_m: float, cg_height_m: float) -> float:
    """Tilt at which the CG's vertical projection leaves the footprint."""
    if cg_height_m <= 0:
        raise ValueError("cg_height_m must be positive")
    return atan(footprint_radius_m / cg_height_m)


def bracket_deg(footprint_radius_m: float) -> tuple[float, float]:
    """Min/max tip-over angle (deg) over the CG-height and stack-height brackets."""
    cg_heights = [f * h for f in CG_HEIGHT_FRACTION for h in STACK_HEIGHT_M]
    angles = [degrees(tip_over_angle_rad(footprint_radius_m, h)) for h in cg_heights]
    return min(angles), max(angles)


def _demo() -> None:
    bare_lo, bare_hi = bracket_deg(BARE_FOOTPRINT_RADIUS_M)
    guard_brackets = [bracket_deg(r) for r in GUARD_FOOTPRINT_RADIUS_M]
    guard_lo = min(lo for lo, _ in guard_brackets)
    guard_hi = max(hi for _, hi in guard_brackets)
    print(f"bare tip-over bracket:    {bare_lo:.1f}-{bare_hi:.1f} deg "
          f"(current BARE_CRITERION tilt limit: 30 deg)")
    print(f"guarded tip-over bracket: {guard_lo:.1f}-{guard_hi:.1f} deg "
          f"(current GUARDED_CRITERION tilt limit: 60 deg)")
    assert bare_lo > 30.0, "geometric tip-over bound no longer clears the asserted bare tilt limit"
    assert guard_lo > 60.0, "geometric tip-over bound no longer clears the asserted guarded tilt limit"
    print("both asserted tilt limits sit strictly inside the geometric tip-over bound.")


if __name__ == "__main__":
    _demo()
