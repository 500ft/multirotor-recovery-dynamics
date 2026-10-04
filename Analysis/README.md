# Executable Analysis

Historical work for the earlier aircraft. The Crazyflie study follows the
[roadmap](../ROADMAP.md); these old tasks and thresholds do not transfer to it.

These tools provide reproducible preliminary calculations. They do not replace CAD, bench testing, 3-D simulation, or physical validation.

Run all checks:

```bash
python3 -m unittest discover -s Analysis/tests -v
```

Generate current reports:

```bash
python3 Analysis/budget.py
python3 Analysis/recovery.py
python3 Analysis/guard.py
python3 Analysis/classifier_stats.py
python3 Analysis/render_state_machine.py
```

## Model Status

| Tool | Purpose | Status |
|---|---|---|
| `budget.py` | mass rollup and freeze-rule check | executable; inputs are estimates |
| `recovery.py` | conservative first-order recovery envelope | executable; not a full 3-D controller simulation |
| `rigid_body.py` | dependency-free 3-D attitude integration kernel | executable; controller coupling still pending |
| `guard.py` | low-energy linear-elastic guard functional check | executable; not a fracture model |
| `classifier_stats.py` | confidence upper-bound calculations | executable |
| `render_state_machine.py` | render Mermaid from the authoritative JSON source | executable |
| `gates.py` | pre-registered propulsion/current/vision decision thresholds | executable; awaiting measurements |
| `hardware_resources.py` | validate UART/pad/timer allocation | executable; catalog map verified |

Replace every placeholder input with CAD, datasheet, or measured values before using results for design freeze.
