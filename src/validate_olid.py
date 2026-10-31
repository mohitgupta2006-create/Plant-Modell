"""Audit real OLID files against supplied class_distribution.xlsx; write an inspection inventory.

Requires Pillow and openpyxl for the supplied workbook. No training or capture IDs generated.
Images remain untouched. Quarantine is enforced by manifest status, not destructive file moves.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
from config import ROOT
from research_inputs import olid_data_root, olid_image_file, olid_rows
from olid_inventory import validate_inventory

TARGET={'healthy':'Tomato___healthy','N':'Tomato___N_Deficiency','N_K':'Tomato___NK_Deficiency'}

def workbook_classes(path):
    try: import openpyxl
    except ImportError as exc: raise RuntimeError('Workbook inspection requires openpyxl in this interpreter') from exc
    wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
    result={}
    try:
        for sheet in wb:
            rows=sheet.iter_rows(values_only=True)
            header=next(rows,())
            if tuple(header[:4])!=('Crop','Class Abbrv.','Class Full Form','Sample Size'): continue
            crop=None
            for n,row in enumerate(rows,2):
                if row[0]: crop=row[0]
                if crop!='Tomato': continue
                abbr=str(row[1] or 'healthy')
                folder='tomato__'+abbr
                if folder in result: raise ValueError('duplicate tomato class in workbook')
                result[folder]={'abbr':abbr,'label':str(row[2]),'expected':int(row[3]),
                                'evidence':f'{path.name}!{sheet.title}!A{n}:D{n}'}
    finally: wb.close()
    if not result: raise ValueError('no tomato class distribution found in workbook')
    return result

def inspect_file(p,root,classes,workbook_hash):
    rel=p.relative_to(root).as_posix()
    resolved=olid_image_file(ROOT,rel)
    if p.parent.name not in classes: raise ValueError(f'unmapped image directory: {rel}')
    cls=classes[p.parent.name]
    with resolved.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    row=dict(path=rel,source='OLID_I',source_class=p.parent.name,source_label=cls['label'],
        condition=TARGET.get(cls['abbr'],''),acquisition='field',
        capture_protocol='source describes detached leaves on dark cloth in natural light',
        source_label_checked='true',label_verified='true',label_review_scope='source_folder_to_spreadsheet_only',
        label_evidence=cls['evidence']+'; workbook_sha256='+workbook_hash,
        diagnosis_verification='not_independently_verified',diagnosis_evidence='',
        plant_id='unknown',leaf_id='unknown',group_id='unknown',group_evidence='',
        capture_date='unknown',capture_location='unknown',sha256=digest,
        status='active' if cls['abbr'] in TARGET else 'source_only',
        exclusion_reason='' if cls['abbr'] in TARGET else 'source class not mapped to current model targets',
        bytes=p.stat().st_size)
    try:
        with Image.open(resolved) as im: im.verify()
        with Image.open(resolved) as im:
            row.update(width=im.width,height=im.height,format=im.format,frames=getattr(im,'n_frames',1))
            im.convert('RGB').load()
        if min(row['width'],row['height'])<32: raise ValueError('image smaller than 32px')
        row['readable']='true'
    except Exception as exc:
        row.update(readable='false',status='quarantined',exclusion_reason=f'unreadable: {type(exc).__name__}: {exc}')
    return row

def write_csv(path,rows,fields):
    with path.open('x',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--workbook',required=True,type=Path)
    ap.add_argument('--manifest',required=True,type=Path)
    ap.add_argument('--report-dir',required=True,type=Path)
    ap.add_argument('--workers',type=int,default=4)
    a=ap.parse_args()
    if a.manifest.exists() or a.report_dir.exists(): ap.error('existing manifest/report preserved; use new output paths')
    if a.workers<1: ap.error('workers must be positive')
    root=olid_data_root(ROOT)
    classes=workbook_classes(a.workbook)
    whash=hashlib.sha256(a.workbook.read_bytes()).hexdigest()
    files=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.jpg','.jpeg','.png'})
    if not files: ap.error('no real images found')
    print(f'Checking {len(files)} real files with full default-frame decoding',flush=True)
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        rows=list(pool.map(lambda p:inspect_file(p,root,classes,whash),files))
    hashes=defaultdict(list)
    for r in rows: hashes[r['sha256']].append(r)
    duplicates=[]
    for digest,same in hashes.items():
        if len(same)<2: continue
        conflict=len({r['source_class'] for r in same})>1
        duplicates.append(dict(sha256=digest,conflicting_labels=conflict,paths=[r['path'] for r in same]))
        if conflict:
            for r in same: r.update(status='quarantined',exclusion_reason='unresolved exact duplicate with conflicting source labels')
        else:
            for r in same[1:]:
                if r['status']!='quarantined': r.update(status='excluded_duplicate',exclusion_reason='same-source-label exact duplicate; first path retained')
    counts=Counter(r['source_class'] for r in rows)
    distributions=[dict(folder=k,source_label=v['label'],expected=v['expected'],actual=counts[k],
                        status='MATCH' if counts[k]==v['expected'] else 'MISMATCH') for k,v in classes.items()]
    for r in rows:
        cls=classes[r['source_class']]
        if counts[r['source_class']]!=cls['expected'] and r['status']=='active':
            r.update(status='quarantined',exclusion_reason='source folder count differs from workbook; review required')
    a.manifest.parent.mkdir(parents=True,exist_ok=True)
    a.report_dir.mkdir(parents=True)
    fields=list(dict.fromkeys(k for r in rows for k in r))
    write_csv(a.manifest,rows,fields)
    excluded=[r for r in rows if r['status']=='quarantined']
    write_csv(a.report_dir/'quarantine.csv',excluded,fields)
    checked=validate_inventory(a.manifest,ROOT)
    try:
        olid_rows(a.manifest,ROOT)
        strict='PASS'
    except ValueError as exc: strict='BLOCKED: '+str(exc)
    report=dict(scope='Both extracted tomato parts; source-label and file validation only; not research-ready',
        root=str(root),manifest=str(a.manifest),workbook=str(a.workbook),workbook_sha256=whash,
        image_files=len(rows),readable=sum(r['readable']=='true' for r in rows),
        unique_sha256=len(hashes),class_distribution=distributions,duplicates=duplicates,
        status_counts=dict(Counter(r['status'] for r in rows)),
        active_class_counts=dict(Counter(r['source_class'] for r in rows if r['status']=='active')),
        formats=dict(Counter(r.get('format','unreadable') for r in rows)),
        dimensions=dict(Counter(f"{r.get('width')}x{r.get('height')}" for r in rows)),
        inventory_smoke=f'PASS: {len(checked)} source-labelled real records verified against files and SHA256',
        strict_model_loading=strict,
        blockers=['Physical plant/leaf/capture groups unknown for all images; leakage-safe splitting blocked.',
                  'Conflicting source labels require adjudication; quarantined records cannot enter model data.',
                  'No independent diagnosis verification; no training performed.'],
        quarantine_policy='Logical quarantine enforced through manifest status; original images untouched.',
        frame_scope='Default RGB frame decoded, matching existing loader; extra MPO frames not separate samples.')
    (a.report_dir/'validation_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__': main()
