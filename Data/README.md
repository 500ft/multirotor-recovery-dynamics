# Test Data

Historical work for the earlier aircraft. The Crazyflie study follows the
[roadmap](../ROADMAP.md); these old tasks and thresholds do not transfer to it.

Do not commit fabricated or manually edited measurement results.

Use this structure:

```text
Data/
  Calibration/YYYY-MM-DD_instrument_calibration-name/
  Bench/YYYY-MM-DD_test-id/
  Unpowered-Release/YYYY-MM-DD_test-id/
  Powered-Recovery/YYYY-MM-DD_test-id/
```

Each test directory should contain:

- `metadata.json`
- raw instrument exports
- raw flight logs
- video or a link to externally stored video
- processed outputs
- test notes and observed failures

Powered-recovery data is not permitted until the documented safety gate is approved.
