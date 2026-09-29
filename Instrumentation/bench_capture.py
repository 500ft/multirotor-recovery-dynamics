"""Host-side capture for the bench-acquisition firmware (`firmware/code.py`).

Reads newline-delimited JSON records from the QT Py's USB serial stream and
demuxes them into one CSV per sensor plus a run manifest, per the raw-data
layout in `docs/data-and-figures.md` (`evidence/week-<date>/runs/<run_id>/`).

Fail-closed, per docs/bench-acquisition.md #4 step 6: a device reset mid-run
(a new epoch) or a record whose fields don't match that sensor's established
schema stops the run being reported as complete -- it is never silently
spliced or coerced. Malformed lines are counted and skipped, not raised on,
since a bench serial link drops partial lines under load.

    python -m Instrumentation.bench_capture --port /dev/ttyACM0 --out evidence/week-2026-10-01/runs/001
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _git_commit(repo: Path) -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                               capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def demux(lines, out_dir: Path) -> dict:
    """Consume an iterable of raw serial lines, write per-sensor CSVs + manifest.

    `lines` is any iterable of str (a live serial connection or, in tests, a
    list). Returns the manifest dict that was also written to disk.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    writers: dict[str, dict] = {}   # sensor -> {"file", "writer", "columns", "rows", "first_seq", "last_seq", "gaps"}
    epochs_seen: list[int] = []
    malformed = 0
    incomplete_reason = None
    started_at = None
    ended_at = None

    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            malformed += 1
            continue

        host_recv = datetime.now(timezone.utc).isoformat()
        started_at = started_at or host_recv
        ended_at = host_recv

        sensor = record.get("sensor")
        epoch = record.get("epoch")
        if sensor is None or epoch is None:
            malformed += 1
            continue
        if epoch not in epochs_seen:
            if epochs_seen:
                incomplete_reason = (
                    f"device reset mid-run: epoch changed {epochs_seen[-1]} -> {epoch} "
                    f"after {sum(w['rows'] for w in writers.values())} rows; run not spliced")
            epochs_seen.append(epoch)

        if sensor == "_meta":
            continue  # boot/init/stop bookkeeping; not a data row

        record["t_host_recv_iso"] = host_recv
        columns = sorted(record.keys())

        state = writers.get(sensor)
        if state is None:
            path = out_dir / f"{sensor}.csv"
            handle = path.open("w", newline="")
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            state = writers[sensor] = {
                "handle": handle, "writer": writer, "columns": columns,
                "rows": 0, "first_seq": record.get("seq"), "last_seq": record.get("seq"),
                "gaps": [],
            }
        elif columns != state["columns"]:
            incomplete_reason = (incomplete_reason or
                f"{sensor}: record schema changed mid-run "
                f"({state['columns']} -> {columns}); run not coerced")
            continue

        seq = record.get("seq")
        if seq is not None and state["last_seq"] is not None and seq != state["last_seq"] + 1 \
                and state["rows"] > 0:
            state["gaps"].append([state["last_seq"], seq])
        state["last_seq"] = seq

        state["writer"].writerow(record)
        state["rows"] += 1

    for state in writers.values():
        state["handle"].close()

    manifest = {
        "started_at": started_at,
        "ended_at": ended_at,
        "epochs_seen": epochs_seen,
        "malformed_lines": malformed,
        "complete": incomplete_reason is None,
        "incomplete_reason": incomplete_reason,
        "sensors": {
            name: {"rows": s["rows"], "first_seq": s["first_seq"], "last_seq": s["last_seq"],
                   "gaps": s["gaps"], "columns": s["columns"]}
            for name, s in writers.items()
        },
    }
    with (out_dir / "manifest.json").open("w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def _serial_lines(port: str, baudrate: int):
    import serial  # deferred: only needed for a live capture, not for tests
    with serial.Serial(port, baudrate=baudrate, timeout=1) as ser:
        while True:
            line = ser.readline()
            if line:
                yield line.decode("utf-8", errors="replace")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", required=True, help="serial device, e.g. /dev/ttyACM0 or COM5")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", required=True, type=Path, help="run directory to create")
    args = ap.parse_args(argv)

    repo = Path(__file__).resolve().parents[1]
    manifest = demux(_serial_lines(args.port, args.baud), args.out)
    manifest["git_commit"] = _git_commit(repo)
    with (args.out / "manifest.json").open("w") as fh:
        json.dump(manifest, fh, indent=2)
    print(json.dumps(manifest, indent=2))
    if not manifest["complete"]:
        raise SystemExit(f"run incomplete: {manifest['incomplete_reason']}")


if __name__ == "__main__":
    main()
