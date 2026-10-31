"""Fail-closed research input contracts. No dataset labels or measurements are inferred.

CSV paths are relative to the repository by default; OLID_DATA_ROOT can explicitly
select a separate OLID image directory. Manifest entries remain relative to that root; annotation/matching evidence must be supplied
by the investigator. A declaration is auditable metadata, not independent verification.
"""
import csv
import hashlib
import math
import os
from datetime import date
from pathlib import Path, PureWindowsPath

DEFICIENCIES = {'Tomato___N_Deficiency', 'Tomato___NK_Deficiency'}
OLID_CONDITIONS = DEFICIENCIES | {'Tomato___healthy'}
FEATURES = ['temperature', 'rainfall', 'humidity', 'soil_moisture']

def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def local_file(root, relative):
    root = Path(root).resolve()
    p = (root / relative).resolve()
    if not relative or Path(relative).is_absolute() or not p.is_relative_to(root):
        raise ValueError('image/mask path must remain inside the repository')
    if not p.is_file():
        raise ValueError(f'missing input file: {relative}')
    return p

def olid_data_root(repository_root):
    """Explicit, process-local opt-in for OLID only; never infer an external directory.

    Read at call time so importing this module does not access the external dataset.
    A configured value must be an existing absolute directory, not a drive/share root.
    Unset preserves repository-relative manifest behavior; blank is a configuration error.
    """
    value = os.environ.get('OLID_DATA_ROOT')
    if value is None:
        return Path(repository_root).resolve(strict=True)
    if not value or not value.strip():
        raise ValueError('OLID_DATA_ROOT must not be empty')
    selected = Path(value)
    if not selected.is_absolute():
        raise ValueError('OLID_DATA_ROOT must be an absolute dataset directory')
    if value.startswith(('\\\\?\\', '\\\\.\\')):
        raise ValueError('OLID_DATA_ROOT must not use Windows device paths')
    try:
        selected = selected.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError('OLID_DATA_ROOT directory does not exist or cannot be resolved') from exc
    if not selected.is_dir() or selected.parent == selected:
        raise ValueError('OLID_DATA_ROOT must be a dataset directory, not a file or filesystem root')
    return selected


def olid_image_file(repository_root, relative):
    """Resolve a manifest-relative file only inside the explicitly selected OLID root.

    Check lexical paths before filesystem access and resolved paths before opening files.
    Symlinks/junctions escaping the selected root remain forbidden. Keep manifest paths
    relative even when the dataset root is absolute. Do not expand user/env placeholders.
    """
    selected = olid_data_root(repository_root)
    return _olid_file(selected, relative)


def _olid_file(selected, relative):
    if not isinstance(relative, str):
        raise ValueError('OLID image path must be a relative string')
    win = PureWindowsPath(relative)
    if (not relative or not relative.strip() or Path(relative).is_absolute()
            or win.drive or win.root or '..' in win.parts or '..' in Path(relative).parts
            or ':' in relative or '\x00' in relative):
        raise ValueError('OLID image path must be relative and stay inside its configured dataset root')
    # local_file resolves symlinks/junctions before checking containment and existence.
    return local_file(selected, relative)


def index_image_path(path, source, repository_root):
    """Keep legacy relative indices; permit an OLID absolute path only under its opted-in root.

    Existing ROOT / path consumers support native absolute paths. No dataset is copied.
    Generated indices are local artifacts; recreate them when moving the external dataset.
    """
    p = Path(path).resolve(strict=True)
    root = Path(repository_root).resolve(strict=True)
    if p.is_relative_to(root):
        return p.relative_to(root).as_posix()
    if source != 'OLID_I' or 'OLID_DATA_ROOT' not in os.environ:
        raise ValueError('external image requires explicit OLID_DATA_ROOT and OLID_I source')
    selected = olid_data_root(root)
    if not p.is_relative_to(selected):
        raise ValueError('external OLID image is outside OLID_DATA_ROOT')
    checked = _olid_file(selected, p.relative_to(selected).as_posix())
    return str(checked)


def olid_rows(manifest, root):
    selected = olid_data_root(root)
    rows, seen = [], set()
    for r in read_csv(manifest):
        p = _olid_file(selected, r.get('path', ''))
        key = str(p).casefold()
        if key in seen:
            raise ValueError('duplicate manifest image')
        seen.add(key)
        cond = r.get('condition')
        if cond not in OLID_CONDITIONS:
            raise ValueError(f'unverified OLID condition: {cond}')
        if r.get('source') != 'OLID_I' or r.get('acquisition') != 'field':
            raise ValueError('OLID source/acquisition must be explicit')
        if r.get('label_verified') != 'true' or not r.get('label_evidence', '').strip():
            raise ValueError('manual label review and evidence required')
        # Physical identity must come from capture records, never filename guesses.
        gid = r.get('group_id', '').strip()
        if not gid or r.get('group_evidence', '').strip() == '':
            raise ValueError('capture group and group evidence required; otherwise BLOCKED')
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if r.get('sha256') != digest:
            raise ValueError('image SHA256 does not match manifest')
        rows.append(dict(path=p, crop='Tomato', condition=cond,
                         source='OLID_I', acquisition='field', group_id='OLID_I:' + gid,
                         label_evidence=r['label_evidence'], group_evidence=r['group_evidence'],
                         sha256=digest, _note='manual_manifest', _key=p.name, _folder='OLID_I'))
    if not rows:
        raise ValueError('empty OLID manifest; no data loaded')
    return rows

def condition_cause(condition, known_biotic):
    if condition in DEFICIENCIES:
        return 'Abiotic'
    if condition in known_biotic:
        return 'None' if condition.endswith('___healthy') else 'Biotic'
    if condition == 'Tomato___healthy':
        return 'None'
    raise ValueError(f'unmapped condition: {condition}')

def paired_environment(samples, measurements):
    """Exact path/location/date matching, finite measurements, explicit provenance.

    Units: C, mm/day, relative humidity %, volumetric soil moisture %.
    No imputation or nearest-date/location matching is performed.
    """
    by_path = {}
    for r in measurements:
        if r.get('path') in by_path:
            raise ValueError('duplicate environmental measurement')
        by_path[r.get('path')] = r
    result = []
    for s in samples:
        r = by_path.get(s['path'])
        if not r or r.get('measurement_origin') != 'real' or not r.get('measurement_evidence', '').strip():
            raise ValueError('BLOCKED: missing real paired environmental evidence')
        for k in ('capture_location', 'capture_date'):
            if not s.get(k) or s[k] != r.get(k):
                raise ValueError(f'BLOCKED: unmatched {k}')
        date.fromisoformat(s['capture_date'])
        vals = [float(r[k]) for k in FEATURES]
        if not all(math.isfinite(v) for v in vals):
            raise ValueError('nonfinite measurement')
        if not (-50 <= vals[0] <= 70 and 0 <= vals[1] <= 2000 and
                all(0 <= v <= 100 for v in vals[2:])):
            raise ValueError('environment measurement outside supported units/ranges')
        if r.get('units') != 'C;mm/day;RH%;VWC%':
            raise ValueError('explicit environmental units required')
        result.append(dict(r))
    return result

def split_audit(rows):
    """Metadata checks supplement, not replace, split_data's MD5/pHash grouping."""
    paths, groups, counts = {}, {}, {}
    for r in rows:
        from class_meta import CONDITION_META
        known = set(CONDITION_META)
        expected = condition_cause(r['condition'], known)
        expected_health = 'Healthy' if expected == 'None' else 'Unhealthy'
        expected_crop = 'Tomato' if r['condition'] in DEFICIENCIES else CONDITION_META[r['condition']][0]
        if r['cause'] != expected or r['health'] != expected_health or r['crop'] != expected_crop:
            raise ValueError('inconsistent crop/health/cause/condition metadata')
        sp, p, g = r['split'], r['path'], r.get('group_id', '')
        if sp not in ('train', 'val', 'test') or not g:
            raise ValueError('invalid split or missing group')
        if p in paths:
            raise ValueError('duplicate path')
        paths[p] = sp
        if g in groups and groups[g] != sp:
            raise ValueError('group leaks between splits')
        groups[g] = sp
        k = (sp, r['source'], r['acquisition'], r['condition'], r['cause'])
        counts[k] = counts.get(k, 0) + 1
    missing = [(sp, cause) for sp in ('train', 'val', 'test') for cause in ('Biotic', 'Abiotic')
               if not any(r['split'] == sp and r['crop'] == 'Tomato' and
                          r['acquisition'] == 'field' and r['cause'] == cause for r in rows)]
    return counts, missing
