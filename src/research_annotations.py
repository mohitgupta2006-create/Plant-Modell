"""Measure investigator-reviewed binary leaf/damage masks from multiple annotators.

Does not train severity or declare thresholds scientifically valid. Investigators must
pre-specify and justify thresholds and adjudicate disagreements before training is enabled.
"""
import argparse
import csv
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import numpy as np
from PIL import Image
from research_inputs import local_file, read_csv

def masked_image(root, row):
    from PIL import Image
    from research_inputs import local_file
    mask=np.asarray(Image.open(local_file(root,row['leaf_mask'])))
    with Image.open(local_file(root,row['path'])) as im:
        image=np.asarray(im.convert('RGB')).copy()
    if mask.ndim!=2 or mask.shape!=image.shape[:2] or not set(np.unique(mask))<={0,255} or not (mask>0).any():
        raise ValueError('invalid aligned binary leaf mask')
    image[mask==0]=127
    return Image.fromarray(image)


def affected_fraction(leaf, damage):
    leaf, damage = np.asarray(leaf), np.asarray(damage)
    if leaf.ndim != 2 or leaf.shape != damage.shape:
        raise ValueError('masks must be aligned single-channel arrays')
    if not set(np.unique(leaf)) <= {0,255} or not set(np.unique(damage)) <= {0,255}:
        raise ValueError('masks must be binary 0/255')
    a,b = leaf>0,damage>0
    if not a.any() or np.any(b & ~a):
        raise ValueError('empty leaf or damage outside leaf')
    return float(b.sum()/a.sum())

def weighted_kappa(pairs):
    # Quadratic weighted Cohen kappa for ordinal classes 0,1,2.
    cm=np.zeros((3,3))
    for a,b in pairs: cm[a,b]+=1
    if cm.sum()==0: return None
    expected=np.outer(cm.sum(1),cm.sum(0))/cm.sum()
    w=(np.arange(3)[:,None]-np.arange(3)[None,:])**2/4
    den=float((w*expected).sum())
    return None if den==0 else 1-float((w*cm).sum())/den

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--annotations', required=True, type=Path)
    p.add_argument('--policy', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a=p.parse_args()
    if a.out.exists(): p.error('existing output preserved')
    policy=json.loads(a.policy.read_text())
    if not all(policy.get(k) for k in ('rationale','reference_or_protocol','preregistered_at')):
        p.error('threshold policy must contain justification and preregistration evidence')
    t=policy['thresholds_fraction']
    if len(t)!=2 or not 0<t[0]<t[1]<1: p.error('invalid thresholds')
    root=Path(__file__).resolve().parent.parent
    by=defaultdict(dict); measured=[]
    for r in read_csv(a.annotations):
        if r.get('verified')!='true' or not r.get('review_evidence') or not r.get('annotator_id'):
            p.error('manual verification, review evidence, and annotator identity required')
        image=local_file(root,r['path'])
        leaf=Image.open(local_file(root,r['leaf_mask']))
        damage=Image.open(local_file(root,r['damage_mask']))
        with Image.open(image) as im:
            if leaf.size!=im.size or damage.size!=im.size: p.error('mask/image size mismatch')
        f=affected_fraction(leaf,damage)
        c=int(f>=t[0])+int(f>=t[1])
        if r['annotator_id'] in by[r['path']]: p.error('duplicate annotator/image')
        by[r['path']][r['annotator_id']]=(f,c)
        measured.append(dict(path=r['path'],annotator=r['annotator_id'],fraction=f,ordinal_class=c))
    agreement=defaultdict(list)
    for annotators in by.values():
        for a1,a2 in combinations(sorted(annotators),2):
            agreement[a1,a2].append((annotators[a1][1],annotators[a2][1]))
    report={'measurements':measured, 'agreement':[dict(annotators=list(k),n=len(v),quadratic_kappa=weighted_kappa(v)) for k,v in agreement.items()],
            'training_status':'BLOCKED: investigator adjudication and threshold validation required', 'policy':policy}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()
