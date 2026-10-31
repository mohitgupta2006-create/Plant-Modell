"""Read source-labelled OLID files for inspection, NOT leakage-safe training/splitting.

Unknown capture groups are allowed in this inventory only. research_inputs.olid_rows
continues to require reviewed label evidence and real capture groups for model data.
"""
import hashlib
from research_inputs import read_csv, olid_data_root, _olid_file, OLID_CONDITIONS

STATUSES = {'active', 'quarantined', 'source_only', 'excluded_duplicate'}

def validate_inventory(manifest, repository_root):
    selected=olid_data_root(repository_root)
    rows=read_csv(manifest)
    if not rows: raise ValueError('empty OLID inventory')
    seen=set(); hashes={}
    for r in rows:
        p=_olid_file(selected,r.get('path',''))
        key=str(p).casefold()
        if key in seen: raise ValueError('duplicate inventory path')
        seen.add(key)
        if r.get('status') not in STATUSES: raise ValueError('invalid inventory status')
        if r.get('source')!='OLID_I' or not r.get('source_class') or not r.get('source_label'):
            raise ValueError('source provenance required')
        if r.get('source_label_checked')!='true' or not r.get('label_evidence'):
            raise ValueError('source label mapping evidence required')
        if r.get('diagnosis_verification') not in {'not_independently_verified','independently_verified'}:
            raise ValueError('explicit diagnosis verification status required')
        if r['diagnosis_verification']=='independently_verified' and not r.get('diagnosis_evidence'):
            raise ValueError('independent diagnosis evidence required')
        if r['status']=='active' and r.get('condition') not in OLID_CONDITIONS:
            raise ValueError('unsupported active model condition')
        if r['status']!='active' and not r.get('exclusion_reason'):
            raise ValueError('excluded records need a reason')
        with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
        if r.get('sha256')!=digest: raise ValueError('inventory SHA256 mismatch')
        hashes.setdefault(digest,[]).append(r)
    for same in hashes.values():
        if len({r['source_class'] for r in same})>1 and any(r['status']!='quarantined' for r in same):
            raise ValueError('all cross-label exact duplicates must remain quarantined')
        if sum(r['status']=='active' for r in same)>1:
            raise ValueError('duplicate content cannot have multiple active records')
    return rows
