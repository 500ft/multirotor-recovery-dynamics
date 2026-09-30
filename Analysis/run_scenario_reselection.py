"""Run DR-SS-SCENARIO-02 without changing the historical studies.

Usage: python -m Analysis.run_scenario_reselection --workers 8
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np

from Analysis import survivable_set as ss
from Analysis.run_scenario_diagnostic import ARMS, PACKAGES, _one

REPO = Path(__file__).resolve().parents[1]
REGISTRATION = Path("docs/specs/survivable-set/scenario-02.json")
CONTRASTS = (("I-L", ARMS[2], ARMS[0]),
             ("H-L", ARMS[1], ARMS[0]),
             ("I-H", ARMS[2], ARMS[1]))


def run_pair(task):
    case_index, case, pair, base_seed = task
    cell = ss.Cell(**{k: v for k, v in case.items() if k != "class"})
    seed = (base_seed, case_index, pair)
    records = []
    for package in PACKAGES:
        for arm in ARMS:
            result = _one(seed, case["class"], cell, package, arm)
            records.append({"case_index": case_index, "class": case["class"],
                            "cell": cell.label(), "package": package,
                            "arm": arm, "pair": pair, **result})
    return records


def compare(a, b, alpha):
    """Paired binary results and contact-only continuous differences."""
    if len(a) != len(b) or not a:
        raise ValueError("comparison requires nonempty paired records")
    for x, y in zip(a, b):
        if (x["case_index"], x["pair"]) != (y["case_index"], y["pair"]):
            raise ValueError("records do not share case and pair indices")
    table = ss.paired_table([x["safe"] is True for x in a],
                            [x["safe"] is True for x in b])
    result = ss.paired_verdict(table, alpha=alpha)
    result["interval_alpha"] = alpha
    feasible = [(x, y) for x, y in zip(a, b)
                if x["status"] != "trim_infeasible"
                and y["status"] != "trim_infeasible"]
    result["feasible_trim"] = ss.paired_table(
        [x["safe"] is True for x, _ in feasible],
        [y["safe"] is True for _, y in feasible])
    contact = [(x, y) for x, y in zip(a, b)
               if x["status"] == y["status"] == "contact"]
    continuous = {"n_both_contact": len(contact)}
    for field in ("impact_speed_m_s", "impact_tilt_rad", "t_contact_s"):
        deltas = [x[field] - y[field] for x, y in contact]
        continuous[field] = {
            "mean_delta": float(np.mean(deltas)) if deltas else None,
            "min_delta": float(min(deltas)) if deltas else None,
            "max_delta": float(max(deltas)) if deltas else None,
        }
    result["continuous"] = continuous
    return result


def summarize(trials, registration):
    groups = {}
    for record in trials:
        key = (record["case_index"], record["package"], record["arm"])
        groups.setdefault(key, []).append(record)
    for rows in groups.values():
        rows.sort(key=lambda r: r["pair"])
        if [r["pair"] for r in rows] != list(range(registration["pairs_per_case"])):
            raise ValueError("missing or duplicate trial indices")
    family_size = len(registration["cases"]) * len(PACKAGES)
    primary_alpha = registration["family_alpha"] / family_size
    marginals, contrasts, packages = [], [], []
    for case_index, case in enumerate(registration["cases"]):
        cell = ss.Cell(**{k: v for k, v in case.items() if k != "class"})
        identity = {"case_index": case_index, "class": case["class"],
                    "cell": cell.label()}
        for package in PACKAGES:
            for arm in ARMS:
                rows = groups[(case_index, package, arm)]
                successes = sum(r["safe"] is True for r in rows)
                marginals.append({**identity, "package": package, "arm": arm,
                                  "attempted": len(rows), "successes": successes,
                                  "p_pass": successes / len(rows),
                                  "status_counts": dict(Counter(r["status"] for r in rows))})
            for name, arm_a, arm_b in CONTRASTS:
                primary = name == registration["primary_contrast"]
                result = compare(groups[(case_index, package, arm_a)],
                                 groups[(case_index, package, arm_b)],
                                 primary_alpha if primary else registration["family_alpha"])
                contrasts.append({**identity, "package": package, "contrast": name,
                                  "primary": primary, "a": arm_a, "b": arm_b, **result})
        for arm in ARMS:
            result = compare(groups[(case_index, PACKAGES[0], arm)],
                             groups[(case_index, PACKAGES[1], arm)],
                             registration["family_alpha"])
            packages.append({**identity, "arm": arm, "primary": False,
                             "a": PACKAGES[0], "b": PACKAGES[1], **result})
    return {"trajectories": len(trials), "primary_family_size": family_size,
            "status_counts": dict(Counter(r["status"] for r in trials)),
            "marginals": marginals, "scenario_contrasts": contrasts,
            "secondary_package_contrasts": packages}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, default=REPO / "Data/scenario-02")
    args = parser.parse_args(argv)
    registration_bytes = (REPO / REGISTRATION).read_bytes()
    registration = json.loads(registration_bytes)
    tasks = [(i, case, pair, registration["base_seed"])
             for i, case in enumerate(registration["cases"])
             for pair in range(registration["pairs_per_case"])]
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    args.out.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    trials = []
    with (args.out / "trials.jsonl").open("w") as output:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for index, records in enumerate(pool.map(run_pair, tasks), start=1):
                trials.extend(records)
                for record in records:
                    output.write(json.dumps(record, allow_nan=False) + "\n")
                if index % 25 == 0:
                    output.flush()
                    print(f"{index}/{len(tasks)} draws, {len(trials)} trajectories, "
                          f"{time.monotonic()-start:.1f} s", flush=True)
    summary = {
        "study_id": registration["study_id"],
        "registration": str(REGISTRATION),
        "registration_sha256": hashlib.sha256(registration_bytes).hexdigest(),
        "source_commit": source_commit,
        "python": platform.python_version(), "numpy": np.__version__,
        "seconds": round(time.monotonic() - start, 1),
        "trials": "trials.jsonl",
        "trials_sha256": hashlib.sha256((args.out / "trials.jsonl").read_bytes()).hexdigest(),
        **summarize(trials, registration),
    }
    (args.out / "results.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    for row in summary["scenario_contrasts"]:
        if row["primary"]:
            print(f"{row['class']} {row['cell']} {row['package']}: "
                  f"I-L={row['delta']:+.3f}, discordant={row['discordant']}/{row['n']}, "
                  f"{row['verdict']}")


if __name__ == "__main__":
    main()
