"""Acquire the pinned NanoBench files and inventory published recordings. No scoring."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'Data/nanobench-baseline'
REVISION = '934a1ab92c458cad99c9278a5cb63bf68af6e56c'
MOTORS = [f'motor_motor_m{i}' for i in range(1, 5)]
POSITION = ['px', 'py', 'pz']
VELOCITY = ['vx', 'vy', 'vz']
QUAT = ['qx', 'qy', 'qz', 'qw']
GYRO = [f'imu_gyro_{a}' for a in 'xyz']
ACC = [f'imu_acc_{a}' for a in 'xyz']
REQUIRED = ['t'] + POSITION + VELOCITY + QUAT + GYRO + ACC + MOTORS + ['pwr_pm_vbat']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def acquire(cache):
    """Only download the exact allowlisted files, verifying their committed hashes."""
    entries = json.loads((RECORD / 'sources.json').read_text())['files']
    def fetch(e):
        dest = cache / e['path']
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            temporary = dest.with_suffix(dest.suffix + '.part')
            subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                            '--retry', '2', e['url'], '-o', str(temporary)], check=True)
            if sha256(temporary) != e['sha256']:
                raise ValueError(f"download hash mismatch: {e['path']}")
            temporary.rename(dest)
        if sha256(dest) != e['sha256']:
            raise ValueError(f"cache hash mismatch: {e['path']}")
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, entries))
    print(f'Verified {len(entries)} pinned files in {cache}')


def metadata(path):
    """Keep the authors' metadata, including nested experiment parameters."""
    return yaml.safe_load(path.read_text())


def load(path):
    return np.genfromtxt(path, delimiter=',', names=True, dtype=float, encoding='utf-8')


def columns(data, names):
    return np.column_stack([data[n] for n in names])


def inventory(cache):
    entries = json.loads((RECORD / 'sources.json').read_text())['files']
    assignments = json.loads((RECORD / 'split.json').read_text())['flights']
    seen, rows = {}, []
    for entry in entries:
        rel = entry['path']
        if not rel.endswith('.csv'):
            continue
        path = cache / rel
        if sha256(path) != entry['sha256']:
            raise ValueError(f'hash mismatch: {rel}')
        d = load(path); names = list(d.dtype.names)
        meta_path = path.with_name(path.stem + '_metadata.yaml')
        m = metadata(meta_path) if meta_path.exists() else {}
        t = d['t']; duration = float(t[-1] - t[0]); dt = np.diff(t)
        missing = sorted(set(REQUIRED) - set(names))
        duplicate = seen.get(entry['sha256'])
        seen.setdefault(entry['sha256'], rel)
        row = dict(path=rel, split=assignments[rel], sha256=entry['sha256'],
                   duplicate_of=duplicate, metadata=m, columns=names,
                   missing_required=missing, rows=len(d), duration_s=duration,
                   dt_min_s=float(dt.min()), dt_median_s=float(np.median(dt)),
                   dt_max_s=float(dt.max()), nonfinite_by_column={n:int((~np.isfinite(d[n])).sum()) for n in names if not np.isfinite(d[n]).all()},
                   nonmonotonic_time_count=int((dt<=0).sum()))
        blocks = {}
        for block, count in m.get('row_counts', {}).items():
            # Raw counts may cover a wider interval; these are upper bounds on
            # distinct original samples in the aligned interval, not statistical ESS.
            blocks[block] = dict(raw_count=count,
                effective_count_upper_bound=min(count, len(d)),
                interpolated_fraction_lower_bound=max(0., 1-count/len(d)),
                raw_count_per_aligned_second=count/duration if duration else None)
        row['blocks'] = blocks
        if not missing:
            q = columns(d, QUAT); pwm = columns(d, MOTORS); v = d['pwr_pm_vbat']
            row.update(pwm_min=float(np.nanmin(pwm)), pwm_max=float(np.nanmax(pwm)),
                voltage_min_v=float(np.nanmin(v)), voltage_max_v=float(np.nanmax(v)),
                quaternion_norm_max_error=float(np.nanmax(abs(np.linalg.norm(q, axis=1)-1))),
                invalid_pwm_rows=int(((pwm<0)|(pwm>65535)).any(axis=1).sum()),
                stopped_rows=int((pwm==0).all(axis=1).sum()))
        rows.append(row)
    result = {'dataset_revision':REVISION,
        'counts_meaning':'raw per-block counts are upper bounds on distinct samples in aligned rows; statistical independence and exact interpolation fraction cannot be recovered without raw timestamps',
        'flights':rows}
    (RECORD / 'inventory.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print('Inventoried',len(rows),'CSV recordings; duplicates',sum(r['duplicate_of'] is not None for r in rows))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['acquire','inventory']);p.add_argument('--cache',required=True,type=Path)
    a=p.parse_args(); {'acquire':acquire,'inventory':inventory}[a.action](a.cache)

if __name__=='__main__':
    main()
