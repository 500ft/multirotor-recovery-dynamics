# Day 4 — decide the measurement route, then earn fixture readiness

Status: **proposed; Owner decisions pending**. Revised 2026-09-15.
Supersedes [PR #19](https://github.com/500ft/multirotor-recovery-dynamics/pull/19),
reviewed at `4a6b0b760751cbff3d72d644a214f3c9f882af0f`.
Implementation baseline: `358872c` on `main`.

The outcome is an evidence-backed route from decisions to a modelable thrust stand.
This replacement initially changes this plan only. It supplies no component values,
Owner approval, measured evidence, fixture model, or task completion.
The proposed implementation below is not already present in the repository.

## Review of the original plan

The six editable decisions and bench-first scope are useful. The execution path
needs these corrections before a filled decision can safely become a code/data change.

| Issue | Why it matters | Severity | How to fix it | Strong approach |
| --- | --- | --- | --- | --- |
| Track B edits `input-requests.csv` and the contract directly | Both are generated; `--check` detects drift but does not implement a route change | Major | Update canonical inputs and their consumers, then regenerate | One numeric register, reproducible derived files |
| D1 assumes not-applicable support exists | `fixture_contract.load_register()` requires a positive numeric lever or a pending row; no route/applicability model exists | Major | Implement and test explicit route applicability before excluding a lever | A direct-force choice removes only the stand lever requirement; vehicle `arm_m` and force calibration remain required |
| Physical inputs wait until the bench exists | Bench anchors and mating interfaces are needed to design that bench | Major | Obtain existing-part/bench observations before modeling; installed calibration follows assembly | Separate geometry prerequisites from later measurement acceptance |
| D5 is a bare `approved` switch | [DR-CAD-02](CAD_TASKS.csv) requires identified interfaces, geometry, metrology and access evidence | Major | Bind approval to an itemized packet and revision | A partial decision unlocks its stated scope, not all of DR-CAD-06 |
| D2 changes the shortlist and omits the installed load budget | The [existing proposal](../cad/bench/fixture-preparation.md) is Phidgets 3132_0 with direct axial sensing; capacity alone does not establish suitability | Major | Retain that proposal as unselected, or document an explicit alternative | Assess operating load, off-axis loads, calibration and uncertainty separately from overload rating |
| Four scalar dimensions are treated as a complete interface | Pitch circle/spacing do not encode hole count, clocking, thread/depth, both cell ends or a screw stack | Major | Require dimensioned coordinates, datums and tolerance sources | Extend the input representation only after the actual interfaces are identified |
| Existing CAD CI is treated as stand acceptance | `cad/generate.py` currently makes one motor-envelope cylinder; its green tests say nothing about a stand | Major | Add fixture-specific source, metrics and STEP round-trip verification under DR-CAD-06 | Compare numeric geometry to a reviewed fixture contract |
| Filling the register is treated as the end of refusal | `verdict()` also rejects weak evidence; `REQUIREMENTS_EVALUATED` can still list unresolved requirements | Major | Name the exact scope of each verdict and require every applicable fixture criterion to resolve | Input review, geometry acceptance, fabrication review and physical validation remain distinct |
| Reported test totals are carried forward without commands/environment | Historical totals cannot establish the new branch's checks | Minor | Capture actual collected tests, interpreter, exits and hosted status | Verify the candidate revision rather than repeat “68/34” |

Code references: [input requests](../cad/input_requests.py),
[fixture contract](../cad/fixture_contract.py), [nominal generator](../cad/generate.py),
[bench-input tests](../Analysis/tests/test_bench_inputs.py),
[fixture tests](../cad/tests/test_fixture_contract.py).

## How review → update → build works

1. Edit any D1–D6 block below. Identify the decision maker, date, source records
   and exact approved scope. Empty, conflicting or incomplete entries remain pending.
2. The Agent checks the evidence against that scope and implements only the ready
   slice. Other decisions do not have to arrive together. A decision authorizes its
   named software/design work; it does not certify a measurement or purchase a part.
3. When implementation starts, copy accepted decisions verbatim into the existing
   planned deliverable `cad/bench/owner-inputs.md` (new), citing this PR's decision
   commit. Replace each consumed block here with its record link; do not maintain
   two independently editable decision registers. A later change is a dated amendment
   that identifies affected outputs and requires their recheck.
4. Keep this replacement PR open during the agreed build slice. Before merge, rewrite
   its title/body around the work actually delivered and list remaining blockers.
   A plan-only merge needs an explicit change to that agreed delivery scope.
   Do not merge #19 as a second, competing instruction set.

Routine read-only source gathering and preparation of a candidate comparison do not
need a new approval. The Agent can do that while decisions are pending. Unverified
dimensions belong in a clearly labeled candidate packet, not accepted parameter rows.
Actual part identity, fit observations and attributed engineering approvals must come
from their real sources. This plan does not infer them from silence.

## Proposed implementation rules

### R1 — preserve the source of every input

`cad/bench/parameters.csv` remains the canonical numeric register. Regenerate
`cad/bench/input-requests.csv` with `python cad/input_requests.py` and
`cad/bench/fixture-contract.json` with `python cad/fixture_contract.py --refresh`.
Run both `--check` commands afterward. Do not hand-edit the generated files.

A design choice stays a design choice; a vendor drawing is not an inspection of a
delivered part. Every accepted entry must match its parameter-specific requirement,
with units, component revision, source location/datum, tolerance or uncertainty,
reviewer and date. An `owner_decision` evidence label must never make thrust, arm
length or installed calibration count as measured. Preserve all frozen protocol rows.

The current analysis test allows only the initial four evidence states and pins
some rows to pending; fixture tests also pin the current pending-clause count.
Update these tests alongside a legitimate schema/input transition. Replace stale
snapshots with semantic invariants and explicit baseline fixtures; retain rejection
of unsupported states, missing sources, guessed values and altered protocol constants.

### R2 — make the route explicit before changing applicability

Proposed minimal addition: `cad/bench/measurement-route.json` (new) records `route`
(`pending`, `direct-force`, or `lever-based`), `decision_source` and `decided_on`.
Add `cad/measurement_route.py` (new) with `load_route(path: Path) -> dict` and
`parameter_applicability(name: str, route: str) -> str`; share it between request and
contract generation. A selected route requires a valid, accessible decision record.
Unknown routes, malformed records or unsupported exemptions fail closed.

Applicability is separate from evidence state. For direct-force, only
`stand_calibration_lever` is `not_applicable`: its numeric cell stays blank, its
existing pending evidence state is not upgraded, and the contract records the
decision supporting the exclusion. A pending route cannot omit the request. For
lever-based, the lever remains required, with its own measurement record and datum.
Switching routes invalidates derived outputs and restores applicable requirements;
stale or populated non-applicable lever data cannot silently survive the transition.

`authority_arm_measured`, `arm_expanded_uncertainty`, force calibration and thrust
uncertainty remain required for authority admission in both routes. A direct-force
stand measures force, not vehicle torque. The separate vehicle radius and the
reviewed four-motor derivation are still needed. Equal lever/radius numbers are
allowed when the underlying records and datums are independent.

### R3 — separate readiness stages without waiving evidence

| Stage | What must exist | What may remain pending | Result it permits |
| --- | --- | --- | --- |
| Preparation | Source inventory, explicit unknowns, D1–D6 packet | Any undecided input | Candidate research and contract design |
| Geometry definition | D1 route; D2 identified sensor and load basis; D3/D4 fit/interface evidence; measured bench anchors; numerical tolerances; accepted D5 geometry scope | Installed calibration; actual vehicle arm if no vehicle exists; acquired propulsion data | DR-CAD-06 modeling only after the ledger's prerequisite wording is explicitly reconciled |
| Geometry acceptance | Native/source model, STEP, numerical comparison for every applicable interface/clearance/load-path criterion, reviewed structural calculations | Assembly inspection and installed calibration | Review of the DR-CAD-08 fabrication/calibration pack |
| Measurement readiness | Built/inspected fixture, installed calibration/uncertainty, actual vehicle geometry or a separately recorded plan to obtain it before authority admission, operator/facility and safety prerequisites | Propulsion observations not yet acquired | A separately authorized physical campaign |
| Authority admission | Six-motor raw/derived bundle, real vehicle arm and uncertainty, calibration and derivation artifacts, actual review | End-to-end dynamic recovery result | Static-authority verdict only |

This is a **proposed clarification of dependencies**, not a declaration that
DR-CAD-02 is done. D5 must accept the exact revised prerequisite wording before it
changes in `docs/CAD_PLAN.md`, `docs/CAD_TASKS.csv` or `docs/CAD_DEPENDENCIES.json`.
Retain the removed-from-geometry items as explicit later-stage requirements.
Do not bypass the current ledger with an informal “approved” label.

The current `--release` command is an input-review interface. `--check` means
“generated contract is current.” Neither command accepts a stand. In particular,
exit 0 with `REQUIREMENTS_EVALUATED` is insufficient when any applicable geometry
requirement is unresolved. Add fixture-specific acceptance only after its numeric
schema and criteria are reviewed; keep the nominal motor-envelope contract separate.

### R4 — close the mechanical and measurement budgets

Trace the load: motor/prop → adapter → cell loaded end → cell fixed end → anchored
base. Account for cable forces, torque reaction, off-axis loading and containment
attachments; none may unintentionally bypass or preload the force measurement.

For each credible signed load case, calculate the force and moment at the sensor:
`F_sensor = F_thrust + F_dead,projected + F_cable + F_transient` and
`M_sensor = sum(r × F) + M_motor`. Specify mounting orientation, load direction and
which terms act simultaneously. Compare these demands to the manufacturer's
operating limits using a documented design margin. Safe overload is a separate
survival limit, not usable measurement range. Check base reactions, sliding/tipping,
fastener engagement and deflection clearances with stated assumptions.

The register's `total_thrust_model = 4.2 N` is a four-motor simulation input, not a
measured single-motor peak. Dividing by four gives an assumption, not a bench design
limit. The current capacity floor uses the total; do not quietly weaken or reinterpret
it. A proposed single-motor design load must have its own source and review, including
dead load and transients, before the contract calculation changes.

Before selection, allocate a target force/geometry uncertainty and identify the
bridge/ADC, excitation, sampling/filtering, calibration reference and procedure.
Record the basis; no numerical budget or safety margin is chosen by this plan.
Installed calibration later establishes actual uncertainty, including zero return,
hysteresis, drift, alignment and cable effects. Datasheet resolution alone is not an
uncertainty budget. The existing authority derivation must propagate force, radius,
motor variation and relevant covariance; do not subtract uncertainty twice.

## Track A — six independently fillable decisions

### D1 — measurement route and applicability

The existing proposal favors direct axial sensing. Choosing it authorizes the R2
software amendment, not deletion of vehicle-arm or calibration requirements.
A lever route additionally needs pivot/force-line geometry and its calibration plan.

```text
DECISION: pending (direct-force | lever-based)
BASIS AND INTENDED LOAD DIRECTION:
R2 ROUTE/APPLICABILITY AMENDMENT: pending (accepted | changes required)
DECIDED BY / DATE / SOURCE RECORD:
```

### D2 — load cell and acquisition chain

Start with the existing, unselected Phidgets 3132_0 proposal; identify any alternative
explicitly rather than silently replacing the shortlist. Provide the exact part and
revision, both end-interface drawings, operating force/moment limits, overload limits,
load budget and acquisition/calibration route. Current availability/pricing must be
checked separately if procurement is later requested.

```text
DECISION: pending (select for design | request candidate comparison | defer)
CELL MODEL / REVISION / OWNED OR PROPOSED:
MANUFACTURER DRAWING URL / REVISION / PAGE:
RATED OPERATING CAPACITY (N) / LOAD DIRECTION / OFF-AXIS LIMITS:
OVERLOAD LIMIT AND SOURCE (separate from operating capacity):
SINGLE-MOTOR DESIGN LOAD / DEAD LOAD / TRANSIENT BASIS / MARGIN RECORD:
BRIDGE-ADC / CALIBRATION REFERENCE / TARGET UNCERTAINTY AND BASIS:
DECIDED BY / DATE / EXACT APPROVED DESIGN SCOPE:
```

### D3 — hub fit and retention

Define whether the selected requirement is clearance or interference, the acceptable
bore/shaft limits and the retention mechanism. The current `abs(bore - shaft) <= fit`
check is only a nominal screen; it does not prove either a signed fit or secure
retention. If that representation cannot express the chosen fit, propose the revised
inequality and regression cases before entering values. Never default to 0.05 mm.

```text
DECISION: pending (accept supplied fit specification | request fit proposal | defer)
PROP / MOTOR REVISIONS AND RETENTION METHOD:
FIT LIMITS (mm) / DATUM / DRAWING OR DESIGN BASIS:
DELIVERED-PART INSPECTION STILL REQUIRED:
DECIDED BY / DATE / SOURCE RECORD:
```

### D4 — complete mounting interfaces

Cover the four original motor/prop rows, both cell ends and the actual bench anchors.
For each interface supply hole count and coordinates/clocking, thread specification,
usable depth, screw/washer/adapter stack and tolerances. A motor-body length is not
safe screw penetration. Record which items are actual drawings, observations, design
choices, unresolved conflicts or unavailable sources; inferred dimensions cannot be
accepted as fit-critical geometry.

```text
DECISION: pending (sources supplied | review candidate sheet | await inspection)
MOTOR / PROP / CELL IDENTITIES AND DRAWING REVISIONS:
INTERFACE RECORDS (parameter or feature, value, unit, datum, tolerance, source/page):
BENCH ANCHOR RECORD / AVAILABLE SPACE / MOUNTING CONSTRAINTS:
MISSING OR CONFLICTING INPUTS AND HOW THEY WILL BE OBTAINED:
DECIDED BY / DATE / ROWS OR FEATURES ACCEPTED:
```

Drawings can be gathered now; existing anchors and delivered components can be
inspected before a stand exists by the person with access. If parts or the intended
bench are unavailable, retain that specific block. Source research cannot replace it.

### D5 — DR-CAD-02 packet review and modeling scope

First review the proposed R3 stage split. Then review the packet for D1–D4, source
revisions, tolerances, force-axis datum, load/stability basis, CAD source/access,
containment interface, calibration plan and operator/facility availability.
Record each outstanding item at its required stage. The [safety checklist](../Instrumentation/propulsion-bench-safety-checklist.md)
continues to govern physical work.

```text
DECISION: pending (approve specified geometry scope | changes required | pending)
R3 DEPENDENCY AMENDMENT / EXACT LEDGER WORDING ACCEPTED:
PACKET PATH / REVISION / ACCEPTED INTERFACE AND LOAD RECORDS:
CAD SOURCE ROUTE / ACCESS (existing plan: Onshape for hand-modeled fixture):
OPERATOR / FACILITY / CONTAINMENT INTERFACE EVIDENCE:
REMAINING ITEMS, REQUIRED STAGE AND RESPONSIBLE PERSON:
REVIEWED BY / DATE / SCOPE AUTHORIZED:
```

An approval without the packet or unresolved fit-critical inputs does not close
DR-CAD-02. A partial approval permits only its named preparation work. If another CAD
route is selected, record that change before implementation; account access is not assumed.

### D6 — DR-S09 evidence-contract review

Read [REVIEW_READY.md](REVIEW_READY.md), the
[authority evidence contract](specs/measured-authority-gate/evidence-contract.md),
and the [completion reconciliation](COMPLETION_RECONCILIATION.md). State whether the
six-motor roster, review responsibilities and acquisition/derivation are feasible.
Review acceptance closes only its stated review task; DR-S02 data/readiness stays open
until its own evidence exists. D6 can proceed independently of D1–D5.

```text
DECISION: pending (review accepted | changes required | pending)
REVIEWED REVISION AND DOCUMENTS:
FEEDBACK / REQUESTED CORRECTIONS:
DATA / MOTOR ROSTER / CALIBRATION-UNCERTAINTY REVIEWER AVAILABILITY:
REVIEWED BY / DATE / ACCEPTED SCOPE:
```

## Track B — ordered implementation slices

The table is a proposed work order, not a completion ledger. Each numbered action is
one bounded edit/review step (about 2–5 minutes of active Agent work after inputs are
available); source searches, full test runtime and external review take additional
time. Repeat a per-input action as needed. Do not compress physical work into this
estimate. Read-only preparation may overlap Owner review; shared-file edits are sequential.

| ID | Depends on | Action and exact files | Done when |
| --- | --- | --- | --- |
| T00 | None | Record base/head, working tree and interpreters in `evidence/task-day4-2026-09-15/README.md` (new during implementation) | Exact commands and observed exits establish the baseline |
| T01 | T00 | Prepare `cad/bench/source-candidates.md` (new): one source-backed interface or cell candidate per pass | Each entry has identity, source/page, units and explicit unknowns; no register change |
| T02 | Any completed D block | Create/update `cad/bench/owner-inputs.md` (new); transfer that decision with its originating commit | No invented acceptance; this plan links the consumed record |
| T03 | T02 + D1/R2 accepted | Add `cad/tests/test_measurement_route.py` (new) for pending/invalid/direct/lever choices and decision-source validation | Unsupported or unapproved route exclusions fail in the baseline implementation |
| T04 | T03 | Add the R2 loader/applicability functions in `cad/measurement_route.py` and accepted `cad/bench/measurement-route.json` (new) | Focused route tests pass; numeric evidence states are unchanged |
| T05 | T04 | Add route-request cases in `cad/tests/test_input_requests.py`; consume applicability in `cad/input_requests.py` | Only an approved direct-force lever is omitted; other pending/new rows remain visible |
| T06 | T05 | Add route cases in `cad/tests/test_fixture_contract.py`; update `load_register()`, `build()` and `evaluate_requirements()` in `cad/fixture_contract.py` | Direct route records its exclusion; lever route requires provenance; arm/calibration requirements survive |
| T07 | T06 | Update `Analysis/tests/test_bench_inputs.py` and baseline-specific CAD assertions | Accepted evidence transitions have semantic tests; unknown states, fabricated measurements and changed frozen values remain rejected |
| T08 | T07 | Regenerate `cad/bench/input-requests.csv` and `cad/bench/fixture-contract.json` using their generators | Both `--check` commands pass; current unresolved physical requirements are still reported |
| T09 | T01/T02 + relevant D2–D4 answer | In `cad/bench/owner-inputs.md`, validate one proposed input against its requirement and original source | Missing datum, revision, tolerance or conflicting source blocks only that input |
| T10 | T09 | Enter one representable accepted row in `cad/bench/parameters.csv`; update relevant tests and regenerate outputs | Value/state/source match the decision; focused tests and both generated-file checks pass |
| T11 | T09 | Document the missing interface/load fields and numerical comparisons in `cad/bench/fixture-definition.md` (new) | Both cell ends, hole coordinates, screw stack, signed fit, design loads, axis/clearance tolerances and inspection methods are specified or explicitly pending |
| T12 | T11 + relevant D2–D5 review | Freeze the proposed field/unit/source-to-criterion mapping in `cad/bench/fixture-definition.md` | Every required feature has an identified source or reviewed design choice; schema design is no longer implicit |
| T13 | T12 | Write fixture acceptance/negative cases in `cad/tests/test_fixture_geometry.py` (new) before extending contract consumers | Cases fail on missing/incorrect feature metrics; nominal cylinder tests cannot satisfy fixture acceptance |
| T14 | T13 | Implement one reviewed field/criterion per pass in `cad/fixture_contract.py` and `cad/bench/parameters.csv`; regenerate derived files | The matching case passes without weakening existing rejection/provenance rules |
| T15 | T11 + D5/R3 accepted | Reconcile stage prerequisites in `docs/CAD_PLAN.md`, `docs/CAD_TASKS.csv`, and `docs/CAD_DEPENDENCIES.json` only where applicable | `cad/ledger_validator.py live` passes; deferred calibration/arm evidence still has an explicit later gate |
| T16 | T12/T14/T15 + complete D5 packet | Inspect the proposed DR-CAD-06 start against every prerequisite; record disposition in `cad/bench/owner-inputs.md` | Each requirement has evidence or a correctly assigned later stage; no bare approval bypass |
| T17 | D6 + T02 | Record actual DR-S09 disposition in `docs/specs/measured-authority-gate/evidence-intake.md` and update its `docs/SPRINT_TASKS.csv` row only if satisfied | Feedback is attributed and reviewable; DR-S02 and physical gates are unaffected |
| T18 | Each completed slice | Run the relevant verification matrix below; record logs and update only completed task status | All applicable checks pass or expected refusals are captured; rejected inputs remain pending |
| T19 | T18 | Inspect final diff, refresh PR title/body with delivered behavior, checks and remaining decisions | Reviewer can reproduce the built slice; no stale claim that the plan itself completed a bench |

T03–T08 can run after D1 alone; T09–T10 can process independent representable D2–D4
inputs without waiting for D6. T11 can begin with a gap inventory while answers are
pending; T12 cannot freeze unknown dimensions or unchosen tolerances. T17 is independent
of fixture construction. Do not implement an unreviewed schema to make T12 look complete.

## DR-CAD-06 and beyond — conditional milestones

At T16, write the fixture's part-by-part modeling work order inside
`cad/bench/fixture-definition.md`, using the now-known geometry and selected CAD route.
The existing five-hour DR-CAD-06 allocation is a historical estimate, not a promise
for this decision session. Unknown interfaces prevent a truthful detailed modeling
schedule today. The eventual deliverable under `cad/bench/propulsion/` must include:

- Native/editable source with revision, STEP export and drawing/parameter provenance.
- `geometry.json` identifying each solid and reporting interface coordinates, screw
  penetration/clearance, force-axis offset, sensor deflection clearance and exclusion
  envelopes against numerical limits fixed before accepting the model.
- A fixture-specific verifier exercised by `cad/tests/test_fixture_geometry.py`;
  direct-versus-STEP-reimport comparison and negative controls for shifted holes,
  wrong units, missing solids and altered clearances. Extend the existing CAD CI
  workflow if needed; preserve its motor-envelope regression and version checks.
- Load/stability calculations, inspection plan and unresolved physical-review items.
  A collision-free STEP cannot establish containment strength or installed calibration.

Only then assemble the DR-CAD-08 pack under `cad/bench/release/` for its actual
fabrication/calibration review. Acquisition follows the separately authorized
physical setup; it is not an automatic successor of a green geometry test.

Keep the [frozen measured-authority protocol](specs/measured-authority-gate/design.md):
7.0 V under load; six sampled motors characterizing a four-motor craft; collective
grid 0.25, 0.375, 0.50, 0.625, 0.75; uncertainty-adjusted empirical fifth-percentile
authority at least 0.020 N·m at every point. A later fixed-controller evaluation uses
1,000 primary trials, at least 962 recoveries, exact one-sided 95% lower bound ≥0.95
and maximum descent ≤3.0 m. Static authority does not establish dynamic recovery.
Vehicle packaging and recovery testing remain dependent on their existing gates.

## Verification and acceptance

Use separate environments: Python 3.11 with `requirements.txt` for analysis, and the
versions in `cad/requirements.lock` for CAD. Their NumPy pins differ. Do not call a
CAD suite complete when a different environment skipped its geometry/version tests.

| Check | Command from repository root | Expected interpretation |
| --- | --- | --- |
| Pending request consistency | `python cad/input_requests.py --check` | Exit 0; no input accepted by generation |
| Contract consistency | `python cad/fixture_contract.py --check` | Exit 0; current baseline has 2 evaluable/10 pending clauses |
| Current refusal | `python cad/fixture_contract.py --release` | Baseline exit 2, `REFUSED INPUTS_INCOMPLETE`; capture this expected exit rather than hide it with `|| true` |
| Task dependencies | `python cad/ledger_validator.py live` | Exit 0; no false done status or dependency cycle |
| Analysis suite | `python -m unittest discover -s Analysis/tests -v` | Exit 0; record actual total, interpreter and elapsed time |
| CAD suite, in pinned CAD environment | `python -m pytest cad/tests -q` | Exit 0, including real STEP generation/reimport and version checks |
| Presentation audit | `python tools/check_presentation.py . "Multirotor Recovery Dynamics" multirotor-recovery-dynamics` | Exit 0, zero reported issues |
| Presentation negative controls | `python tools/test_presentation.py` | Exit 0; record actual output |
| Patch hygiene | `git diff --check` | Exit 0 |

Future route/input changes must additionally reject: missing route approval, an
arbitrary not-applicable row, populated non-applicable lever data, removal of the
vehicle-arm requirement, unsupported evidence state, source-less accepted values,
unjustified tolerance and incomplete mounting coordinates. Test route reversal and
equal lengths with distinct provenance as positive controls. Nominal/vendor evidence
must remain visibly distinct from installed measurement.

Readiness consumers must never interpret `REQUIREMENTS_EVALUATED` with unresolved
applicable criteria as geometry acceptance. Preserve synthetic `DEVELOPMENT_ONLY`
behavior and the current raw/derived authority evidence contract.

Before each implementation slice, compare current branch contents to this recorded
baseline; integrate any newly supplied decisions without overwriting them. After
push, record the hosted CI result for the actual PR head. A docs-only diff does not
trigger the path-filtered CAD workflow, so report local CAD verification separately.
No hosted result is claimed in advance.

### Validation of this planning revision — 2026-09-15

The commands above were exercised locally against code at `358872c`: **91 analysis
tests passed** in 153.267 s with Python 3.11.8 / NumPy 2.1.1 / Matplotlib 3.10.1;
**53 CAD tests passed** with the pinned Python 3.11.16 / CadQuery 2.8.0 / OCP 7.9.3.1 /
NumPy 2.4.6 / pytest 9.1.1 environment; **4 presentation negative-control tests passed**.
The presentation audit reported zero issues. Request/contract checks and the live
ledger passed; `--release` returned the expected exit 2 with `INPUTS_INCOMPLETE`.
The plan's local links, six decision blocks and T00–T19 sequence were also checked.
These are software/document checks; no decision or physical gate was closed.
Hosted CI for this replacement is reported in its PR, separately from these results.

| Requirement | Implementation coverage |
| --- | --- |
| Traceable, independently actionable decisions | T01–T02, T09–T10, T17 |
| Canonical register and reproducible derived files (R1) | T05–T10, T14, T18 |
| Explicit route applicability without lost measurements (R2) | T03–T08, T18 |
| Acyclic, scoped readiness gates (R3) | T11–T16, T18 |
| Defensible loads, fit, uncertainty and fixture verification (R4) | T09, T11–T14, conditional DR-CAD-06 |
| Preserved scientific thresholds and honest delivery state | T07, T17–T19 |

The smallest useful next return is **D1 with its R2 amendment decision**, plus any
available D2/D4 part identities or source records. Other blocks may remain pending.
The first implementation can therefore close route handling while geometry and
physical evidence are still incomplete; it cannot close those later gates by itself.
