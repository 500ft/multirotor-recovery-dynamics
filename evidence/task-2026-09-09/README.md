# DR-CAD-10 verification — 2026-09-09

**Review amendment:** this is the original day-2 evidence snapshot, not the final
acceptance verdict. [Adversarial review](../review-2026-09-09/README.md) reproduced
admission/version/round-trip gaps and corrects the premature completion claim.
The CAD workflow is now installed; hosted verification is pending. The historical
exports below are preserved rather than silently regenerated under revised code.

Base: `7a2e907f435896e63c8595d98b91e270526bb163` (head of the day-1 branch `task/priority-one-20260908`, PR #10). Candidate
identity is the containing PR head. No physical specimen, fabrication or measurement is
claimed; this task delivers tooling that regenerates and tests **model** geometry from the
registered parameters, carrying their evidence states through unchanged.

Deliverables: [`cad/generate.py`](../../cad/generate.py), [`cad/contract.json`](../../cad/contract.json),
[`cad/tests/test_geometry.py`](../../cad/tests/test_geometry.py), [`cad/requirements.lock`](../../cad/requirements.lock),
and the geometry CI as [`ci-proposed/cad-geometry-workflow.patch`](https://github.com/500ft/multirotor-recovery-dynamics/blob/935a38b5f4d187669ce2f6d0ceb88ef0a8d79c6c/ci-proposed/cad-geometry-workflow.patch).
Authoritative status: [CAD_TASKS.csv](../../docs/CAD_TASKS.csv). The earlier sprint ledger is byte-preserved.

## Environment lock

Pinned after a clean isolated conda-forge install and a STEP export/reimport smoke test
(20 × 10 × 5 mm box: volume 1000.000000 → 1000.000000 mm³, relative difference 0):
Python 3.11.16, CadQuery 2.8.0, OCP 7.9.3.1, numpy 2.4.6.
`test_installed_versions_match_lock` fails if the running environment departs from the lock.

## Reproduction and observed evidence

Commands run from the repository root in the locked environment.

| Command | Observed result |
| --- | --- |
| `python cad/generate.py --parameters cad/bench/parameters.csv --output evidence/task-2026-09-09/cad-out` | exit 0, 1.1 s — `motor_envelope: volume 2218.652 mm^3  bbox [13.5, 13.5, 15.5]  -> evidence/task-2026-09-09/cad-out` |
| `python -m pytest cad/tests -q` | exit 0, 2.9 s — **12 passed** |
| `git apply --check ci-proposed/cad-geometry-workflow.patch` | exit 0 |
| embedded CAD ledger validator (docs/CAD_PLAN_CHECKS.md) | see below, run after this ledger edit |

## Geometry family: `motor_envelope`

| metric | analytic (from register) | CadQuery solid | after STEP re-import |
| --- | ---: | ---: | ---: |
| volume, mm³ | 2218.651637 | 2218.651637 | 2218.651637 |
| bbox, mm | [13.5, 13.5, 15.5] | [13.5, 13.5, 15.5] | [13.5, 13.5, 15.5] |
| mass, g | not claimed — no density registered | — | — |

Retained: [`cad-out/geometry.json`](cad-out/geometry.json) (all metrics, input evidence states,
file hashes, versions) and [`cad-out/motor_envelope.step`](cad-out/motor_envelope.step).

## Fail-closed behaviour proven by test

Altered parameter → contract assertion fails · invalid dimensions → `GeometryInputError` ·
missing register row → `GeometryInputError` · empty (pending) value → `GeometryInputError` ·
unit mismatch → `GeometryInputError` · truncated STEP → import/metric check raises ·
CLI on bad input → exit 2 with `REFUSED`.

## Not modelled, and why
- **prop_swept_envelope** — prop_diameter is registered (52.17 mm vendor_nominal) but no blade height / swept thickness is; a disc needs both
- **motor_mount_pattern** — motor_mount_pitch_circle, motor_mount_hole_diameter and thread engagement are pending owner inputs (DR-CAD-02)
- **motor_shaft** — motor_shaft_diameter is registered but shaft length is not


Pending parameters in the register (11) are listed in `geometry.json`
and remain owner inputs. Passing this contract means the code regenerates the intended model;
it says nothing about an as-built part.
