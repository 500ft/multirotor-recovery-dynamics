#!/usr/bin/env python3
"""Motor-level control allocation under propulsion failures (Study A, DR-SS-01).

The mixer model in ``sim_release_recovery`` bounds roll/pitch torque by a scalar
capability formula that assumes all four motors are healthy. This module replaces
that scalar with the actual actuator map so *failure classes* become representable:
each motor's thrust is a decision variable in ``[0, cap]``, failed motors are forced
to zero, and the partial-authority class caps every motor below its healthy limit.

Geometry (X configuration, top view, body axes x forward / y left):

    m2 (-a, +a, CW)      m1 (+a, +a, CCW)
    m3 (-a, -a, CCW)     m4 (+a, -a, CW)

with ``a = arm / sqrt(2)``. The wrench map is ``w = B f`` with
``w = (T, tau_x, tau_y, tau_z)``:

    T     = f1 + f2 + f3 + f4
    tau_x = a (f1 + f2 - f3 - f4)
    tau_y = a (-f1 + f2 + f3 - f4)
    tau_z = kappa (f1 - f2 + f3 - f4)

``kappa`` (drag-torque per unit thrust) is derived from the same yaw-torque bound the
mixer model uses: full differential thrust on one spin pair produces the placeholder
yaw limit, so ``kappa = yaw_torque_n_m / (2 f_max)``.

Allocation is REDUCED-ATTITUDE by design: the commanded wrench is ``(T, tau_x,
tau_y)`` only. After the loss of a rotor the drag-torque budget cannot balance yaw
(the vehicle spins about body z — the established rotor-out flight regime), so
spending clipped motor authority on a hopeless yaw command would misallocate the
little control that remains. The achieved yaw torque (including the spin-direction
imbalance that drives the post-failure spin) is still computed and fed to the
dynamics, so the spin and its gyroscopic coupling are simulated, not ignored.

The least-squares solve + box clip is a single pass: clipping can degrade the
achieved collective below the command near saturation. This is a declared
conservative simplification (a real allocator could redistribute), recorded in
``docs/specs/survivable-set/design.md``.

Analytic anchors reproduced exactly by the map (tested in
``tests/test_failure_allocation.py``):

* one rotor out (m4): zero roll/pitch torque forces ``f2 = 0, f1 = f3`` — flight on
  the remaining diagonal pair, balanced collective ceiling ``2 f_max``, unbalanced
  yaw (spin).
* two opposite out (m2, m4): torque available only about the diagonal joining the
  survivors; spin, collective ceiling ``2 f_max``.
* two adjacent out (m3, m4): both survivors on one side — roll trim is impossible
  at any positive thrust. No hover exists; the class is expected to depend on the
  descent-device actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(frozen=True)
class FailureCase:
    """One propulsion-failure class: dead motors and a per-motor authority cap."""

    name: str
    failed: tuple[int, ...] = ()      # 0-based motor indices forced to zero thrust
    authority_frac: float = 1.0       # per-motor cap as a fraction of the healthy cap


FAILURE_CLASSES: dict[str, FailureCase] = {
    "one_out": FailureCase("one_out", failed=(3,)),
    "two_adjacent": FailureCase("two_adjacent", failed=(2, 3)),
    "two_opposite": FailureCase("two_opposite", failed=(1, 3)),
    "partial_authority": FailureCase("partial_authority", authority_frac=0.6),
}

# X-configuration geometry: unit-arm positions and spin directions (CCW = +1).
_MOTOR_XY = np.array([[+1.0, +1.0], [-1.0, +1.0], [-1.0, -1.0], [+1.0, -1.0]])
_SPIN = np.array([+1.0, -1.0, +1.0, -1.0])


class MotorAllocation:
    """Wrench allocation onto the healthy motors of one failure case.

    Build from mixer-mode parameters (``with_mixer`` — ``arm_m`` and
    ``yaw_torque_n_m`` set); ``apply`` replaces the scalar mixer clip inside
    ``simulate``.
    """

    def __init__(self, case: FailureCase, arm_m: float, max_thrust_n: float,
                 yaw_torque_n_m: float):
        a = arm_m / sqrt(2.0)
        f_max = max_thrust_n / 4.0
        kappa = yaw_torque_n_m / (2.0 * f_max)
        b_full = np.vstack([
            np.ones(4),
            a * _MOTOR_XY[:, 1],
            -a * _MOTOR_XY[:, 0],
            kappa * _SPIN,
        ])
        self.case = case
        self.healthy = tuple(i for i in range(4) if i not in case.failed)
        if not self.healthy:
            raise ValueError("all motors failed: no allocation exists")
        self._b = b_full[:, self.healthy]
        self._pinv3 = np.linalg.pinv(self._b[:3, :])

    def max_collective(self, max_thrust_avail_n: float) -> float:
        """Total thrust ceiling of the surviving, possibly derated motors."""
        return len(self.healthy) * self.case.authority_frac * max_thrust_avail_n / 4.0

    def apply(self, torque_cmd: np.ndarray, thrust_cmd: float,
              max_thrust_avail_n: float) -> tuple[np.ndarray, float]:
        """Allocate (T, tau_x, tau_y) onto the healthy motors; return achieved wrench.

        Yaw command is dropped (reduced-attitude allocation, see module docstring);
        the achieved yaw torque from the clipped thrust pattern is returned so the
        dynamics integrate the post-failure spin.
        """
        cap = self.case.authority_frac * max_thrust_avail_n / 4.0
        w3 = np.array([thrust_cmd, torque_cmd[0], torque_cmd[1]])
        f = np.clip(self._pinv3 @ w3, 0.0, cap)
        w = self._b @ f
        return np.array([w[1], w[2], w[3]]), float(w[0])
