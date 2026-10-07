"""Reproduce the G1 source probe and exposed-excerpt adapter check, without fitting.

Reads pinned source metadata/code and one IDSIA training CSV header. It never
imports upstream code, executes notebooks, or reads held-out flight outcomes.
The scientific qualification remains a source review in docs/nanobench-g1.md.
"""
import argparse
import ast
import contextlib
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import zipfile

import yaml

from Analysis.audit_nanobench_excerpt import audit
from Analysis.nanobench_data import ROOT, sha256

RECORD = ROOT / 'Data/nanobench-g1'


def qualify(cache, output, fetch=False):
    started = time.perf_counter()
    registration = json.loads((RECORD / 'registration.json').read_text())
    for name, expected in registration['hashes'].items():
        if sha256(ROOT / name) != expected:
            raise ValueError(f'registered input changed: {name}')

    sources = json.loads((RECORD / 'sources.json').read_text())['files']
    checked = []
    for source in sources:
        if not source['reproduce']:
            continue  # Dated moving-endpoint observations have a separate record.
        path = cache / source['path']
        if not path.exists() and fetch:
            path.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['curl', '--fail', '--silent', '--show-error',
                            '--location', source['url'], '--output', str(path)], check=True)
            if source['json_compact']:
                path.write_text(json.dumps(json.loads(path.read_text()),
                                           separators=(',', ':'), ensure_ascii=False))
        if sha256(path) != source['sha256']:
            raise ValueError(f'source hash mismatch: {source["path"]}')
        checked.append(source['path'])

    trees = {}
    for name in ['nanobench', 'idsia-main', 'idsia-dev']:
        tree = json.loads((cache / f'{name}-tree.json').read_text())
        if tree['truncated']:
            raise ValueError(f'incomplete source tree: {name}')
        paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob']
        trees[name] = dict(revision=tree['sha'], blob_count=len(paths),
            license_paths=[p for p in paths if Path(p).name.lower().startswith(
                ('license', 'licence', 'copying'))],
            # Return paths for human review. A name search cannot prove absence.
            acquisition_candidate_paths=[p for p in paths if any(
                token in p.lower() for token in ['collect', 'raw/', 'align', 'config',
                                                 'timestamp', 'processing/', 'loader', 'build_dataset'])])

    metadata = yaml.safe_load((cache / 'nanobench/datasets/dataset/A1b_multisine_sysid_rep1_metadata.yaml').read_text())
    def timestamp(key):
        return datetime.strptime(metadata[key], '%Y%m%dT%H%M%SZ')
    duration = (timestamp('recording_end_utc') - timestamp('recording_start_utc')).total_seconds()
    # Counts / recording duration describe average delivery only. They do not
    # locate samples, identify a delay, or measure a channel's bandwidth.
    blocks = {k: dict(raw_rows=v, mean_rows_per_recording_second=v/duration)
              for k, v in metadata['row_counts'].items()}

    with tempfile.TemporaryDirectory() as temp:
        audit_path = Path(temp) / 'excerpt.json'
        with contextlib.redirect_stdout(io.StringIO()):
            audit(audit_path)
        replayed = json.loads(audit_path.read_text())
    original = json.loads((ROOT / 'Data/nanobench-baseline/excerpt-audit.json').read_text())
    replayed.pop('runtime_s')
    original.pop('runtime_s')
    differing_keys = sorted(k for k in original.keys() | replayed.keys()
                            if original.get(k) != replayed.get(k))
    if differing_keys:
        raise ValueError(f'excerpt reproduction changed: {differing_keys}')

    # Inspect only the header of this named training flight. Do not extract
    # the archive or open test members. Its hash is compared to the main LFS
    # pointer using archive bytes, without parsing any numerical observations.
    with zipfile.ZipFile(cache / 'idsia-data-v1.0.zip') as archive:
        members = archive.namelist()
        member = 'train/chirp_20251017_run1.csv'
        with archive.open(member) as stream:
            header = next(csv.reader([stream.readline().decode().strip()]))
        with archive.open(member) as stream:
            member_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
    pointer = (cache / 'idsia-main/data/train/chirp_20251017_run1.csv').read_text()
    pointer_hash = next(line.split('sha256:')[1] for line in pointer.splitlines()
                        if line.startswith('oid sha256:'))
    if pointer_hash != member_hash:
        raise ValueError('release training member differs from pinned main LFS object')

    topic_text = (cache / 'idsia-dev/utils/topic_utils.py').read_text()
    topic_ast = ast.parse(topic_text)
    extracts = [node for node in topic_ast.body if isinstance(node, ast.FunctionDef)
                and node.name == 'extract_motors']
    # Python uses the last definition. Record the timestamp omission there,
    # rather than trusting the earlier function with the same name.
    effective = extracts[-1]
    notebook = json.loads((cache / 'idsia-dev/processing/csv_to_processed.ipynb').read_text())
    code_cells = [(i, ''.join(c['source'])) for i, c in enumerate(notebook['cells'])
                  if c['cell_type'] == 'code']
    notebook_locators = {}
    for symbol in ['convert_erpm_to_rads', 'align_motor_signals', 'filter_dataframe',
                   '_filter_series', 'remove_motor_spikes']:
        notebook_locators[symbol] = [i for i, code in code_cells if f'def {symbol}(' in code]

    result = dict(
        registration='Data/nanobench-g1/registration.json',
        code_sha256=sha256(Path(__file__)),
        sources_sha256=sha256(RECORD / 'sources.json'),
        checked_sources=checked, trees=trees,
        nanobench_development_metadata=dict(flight=registration['domain']['flight'],
            fields=sorted(metadata), firmware_version=metadata['firmware_version'],
            crazyflie_id=metadata['crazyflie_id'], recording_duration_s=duration,
            blocks=blocks,
            interpretation='Average deliveries over coarse UTC recording duration, not independent samples or effective bandwidth. No per-sample timestamps or alignment offsets in this metadata.'),
        adapter_reproduction=dict(deterministic_fields_equal=True,
            original_result='Data/nanobench-baseline/excerpt-audit.json',
            ignored_field='runtime_s',
            interpretation='Reproduces the previous arithmetic and mismatch, not physical agreement.'),
        idsia_schema=dict(archive_member=member, header=header,
            member_sha256=member_hash, matches_main_lfs_object=True,
            archive_license_paths=[p for p in members if Path(p).name.lower().startswith(
                ('license', 'licence', 'copying'))],
            numerical_rows_parsed=0, notebook_outputs_read=False,
            motor_extractor_definition_lines=[n.lineno for n in extracts],
            effective_motor_extractor_line=effective.lineno,
            effective_motor_extractor_mentions_stm32_timestamp=(
                'stm32_timestamp' in ast.get_source_segment(topic_text, effective)),
            notebook_code_cell_locators_zero_based=notebook_locators),
        gate='G1 incomplete: source review finds collection timing and deployed configuration unresolved. See docs/nanobench-g1.md.',
        fits_executed=0, final_test_predictions_executed=0,
        iteration='Source probe and unchanged excerpt replay only. No processing or model change; mismatch retained.',
        runtime_s=time.perf_counter()-started)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ['gate', 'adapter_reproduction', 'runtime_s']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fetch', action='store_true', help='Acquire missing pinned files with curl; keep downloads outside git.')
    args = parser.parse_args()
    qualify(args.cache, args.output, args.fetch)
