# Scenario comparison with new test cases

Study ID: `DR-SS-SCENARIO-02`. The [registration](scenario-02.json) fixes the
test cases, sample count, seed and error rate. Commit this file and the runner
before drawing any new results. OQ-016 is resolved under the owner's request
to choose and test a solution.

## Decision

Use the proposed cases and retain the existing landing pass/fail rule. The
primary comparison is the corrected in-flight scenario I against release/startup
L, separately for each test case and each aircraft package. This measures how
the scenario assumption changes the result.

The selected cases came from the existing exploratory results. This is a new
simulation study using fresh random draws. It does not provide independent
validation of the model. The historical registrations and results stay frozen.

The proposal ranked cases by how close the average pass rate was to one half.
That identifies cases with mixed outcomes, but paired precision also depends on
how often the outcomes disagree. If b trials pass only in I and c pass only in L,
then the estimated change is (b-c)/N. With D = Y_I - Y_L, the variance of its
sample mean is [q - delta^2]/N, where q = P(D differs from zero). Marginal pass
rates alone do not supply q. We retain the cases for coverage of failure type,
height, initial descent and detection delay, without promising a difference.
The descending case changes both descent and delay, so it cannot isolate delay.

`two_adjacent` stays outside the primary binary comparison. Its existing grid
has no passing trial. Keep its continuous impact-speed and contact-time results
in the [original diagnostic](../../../Data/scenario-diagnostic/scenario_diagnostic.json).
A separate continuous-outcome study is deferred while the V995 bench work is
waiting on measurements.

## Run and analysis

- Reuse the A2 plant, controller and package definitions through
  `Analysis.run_scenario_diagnostic._one`. The [scenario contract](scenario-contract.md)
  defines L, H and I. No gains, force limits, impact thresholds or dynamics change.
- Pair the arms and packages using seed `(base_seed, case_index, pair_index)`.
  Package mass and inertia changes still apply. Sensor-noise streams share their
  seed; their values follow the existing controller update order.
- Each registered case runs both packages in all three arms. The count in the
  JSON is a fixed computation budget. It is not a claim of a particular power.
  Report the observed discordant count and uncertainty for every comparison.
- Primary inference covers I-L across all case-package combinations. Apply a
  Bonferroni correction using the registered family error rate divided by the
  number of those combinations. Use the existing exact conditional paired
  interval. It estimates which arm wins among discordant pairs. Report the
  overall pass-rate change alongside it. Do not interpret that interval as an
  interval on the pass-rate change.
- H-L and I-H explain the retained-thrust and timing contributions. Comparisons
  between the two packages are secondary. Their unadjusted results describe
  this run and do not decide the primary question.
- Count all attempted draws. A timeout or infeasible trim supplies no passing
  landing. Report their counts separately and also report results conditional
  on feasible trim. Continuous differences use pairs where both arms contact
  the ground; report the number of such pairs.
- If a case still has no discordant outcomes, report it and stop. Do not select
  another case after seeing this run.

## Reproduce

```sh
python -m unittest Analysis.tests.test_scenario_arms Analysis.tests.test_scenario_reselection
python -m Analysis.run_scenario_reselection --workers 8
```

The runner writes trial records and a summary under `Data/scenario-02/`. The
summary records the source commit and registration hash. The results depend on
the historical estimated aircraft, assumed landing limits, and ideal actuator
response. Measurements of the stock V995 are still required by the roadmap.
