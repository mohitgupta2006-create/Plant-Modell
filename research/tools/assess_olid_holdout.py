"""Offline allocation feasibility ONLY. Never used by model training or strict splitting.

Retains all saved similarity edges including paths through excluded source-only/quarantine
records. Content components are not physical capture groups. Outputs have proposed_partition,
not split; original unknown capture metadata remains unchanged. No production guard is relaxed.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
CLASSES=('tomato__healthy','tomato__N','tomato__N_K')
PARTITIONS=('train','val','test')
POLICY='exploratory_content_pilot_v2_conservative_sensitivity'

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def build_components(rows,edges,reviewed,max_distance=6):
    if max_distance not in (6,8):raise ValueError('only reviewed baseline 6 and conservative stress 8 are supported')
    by={r['path']:r for r in rows}
    if len(by)!=len(rows):raise ValueError('duplicate input path')
    parent={p:p for p in by}
    def find(p):
        while parent[p]!=p:parent[p]=parent[parent[p]];p=parent[p]
        return p
    def union(a,b):parent[find(a)]=find(b)
    retained=set()
    for e in edges:
        if e.get('scope')!='all_files_diagnostic_only':continue
        a,b=e['path_a'],e['path_b']
        if a not in by or b not in by:raise ValueError('similarity path absent from inventory')
        if not 0<=int(e['distance'])<=max_distance:raise ValueError('edge outside reviewed threshold')
        retained.add(frozenset((a,b)));union(a,b)
    if not retained:raise ValueError('full-corpus similarity links required')
    reviewed_pairs=set()
    for e in reviewed:
        pair=frozenset((e['path_a'],e['path_b']))
        if pair not in retained:raise ValueError('review refers to absent retained link')
        if e.get('decision')!='retain_atomic_component_or_exclude_component_from_evaluation':
            raise ValueError('unsupported review decision; no automatic link rejection')
        reviewed_pairs.add(pair)
    target_edges={frozenset((e['path_a'],e['path_b'])) for e in edges
                  if e.get('scope')=='all_files_diagnostic_only' and int(e['distance'])<=6
                  and by[e['path_a']]['status']=='active' and by[e['path_b']]['status']=='active'}
    if not target_edges<=reviewed_pairs:raise ValueError('target-target review decision missing')
    exact={}
    for r in rows:
        if r['sha256'] in exact:union(r['path'],exact[r['sha256']])
        else:exact[r['sha256']]=r['path']
    groups=defaultdict(list)
    for p in sorted(by):groups[find(p)].append(p)
    membership={}
    for paths in groups.values():
        # A stable content-component reference, NEVER a plant/leaf/capture ID.
        cid='IC_'+hashlib.sha256('\n'.join(paths).encode()).hexdigest()[:20]
        for p in paths:membership[p]=cid
    return membership

def component_records(rows,membership):
    result=defaultdict(list)
    for r in rows:result[membership[r['path']]].append(r)
    return result

def ordered(items,seed):
    return sorted(items,key=lambda x:hashlib.sha256(f'{seed}|{x}'.encode()).hexdigest())

def propose(rows,membership,test_minority,seed=42):
    """Construct exact quotas from single-target components, without partitioning any group.

    All multi-target components and every quarantine-connected component stay in development.
    Source-only nodes are never examples; they remain graph context to prevent hidden bridges.
    """
    groups=component_records(rows,membership)
    assignment={r['path']:'train' for r in rows if r['status']=='active'}
    quotas={'tomato__healthy':(30,15),'tomato__N':(test_minority,5),'tomato__N_K':(test_minority,5)}
    for cls,(nt,nv) in quotas.items():
        eligible=[]
        for cid,context in groups.items():
            active=[r for r in context if r['status']=='active']
            if len(active)==1 and active[0]['source_class']==cls and not any(r['status']=='quarantined' for r in context):
                eligible.append((cid,active[0]['path']))
        eligible=sorted(eligible,key=lambda x:hashlib.sha256(f'{seed}|{x[0]}'.encode()).hexdigest())
        if len(eligible)<nt+nv:
            raise ValueError(f'{cls}: {len(eligible)} eligible components, need {nt+nv} for test+val')
        for _,p in eligible[:nt]:assignment[p]='test'
        for _,p in eligible[nt:nt+nv]:assignment[p]='val'
    return assignment

def assess(rows,membership,assignment):
    by={r['path']:r for r in rows};active={p for p,r in by.items() if r['status']=='active'}
    if set(assignment)!=active:raise ValueError('proposal must contain active targets only, once each')
    if any(p not in PARTITIONS for p in assignment.values()):raise ValueError('invalid proposed partition')
    if any(by[p]['source_class'] not in CLASSES for p in active):raise ValueError('unknown active class')
    groups=component_records(rows,membership)
    errors=[]
    for cid,context in groups.items():
        target=[r for r in context if r['path'] in assignment]
        parts={assignment[r['path']] for r in target}
        if len(parts)>1:errors.append('full-corpus component crosses partitions: '+cid)
        if parts & {'val','test'}:
            if len(target)!=1:errors.append('heldout component has multiple targets: '+cid)
            if any(r['status']=='quarantined' for r in context):errors.append('quarantine-connected heldout component: '+cid)
    counts={p:Counter(by[x]['source_class'] for x,v in assignment.items() if v==p) for p in PARTITIONS}
    component_counts={p:{c:len({membership[x] for x,v in assignment.items() if v==p and by[x]['source_class']==c}) for c in CLASSES} for p in PARTITIONS}
    minima={'train':{'tomato__healthy':60,'tomato__N':15,'tomato__N_K':15},
            'val':{'tomato__healthy':15,'tomato__N':5,'tomato__N_K':5},
            'test':{'tomato__healthy':30,'tomato__N':15,'tomato__N_K':15}}
    for p in PARTITIONS:
        for c in CLASSES:
            if counts[p][c]<minima[p][c]:errors.append(f'insufficient {p} support: {c}={counts[p][c]}, need {minima[p][c]}')
            min_components=(20 if c=='tomato__healthy' else 3) if p=='train' else minima[p][c]
            if component_counts[p][c]<min_components:errors.append(f'insufficient {p} content components: {c}')
    return dict(meets_allocation_criteria=not errors,errors=errors,
                class_counts={p:{c:counts[p][c] for c in CLASSES} for p in PARTITIONS},
                content_component_counts=component_counts,
                sizes={p:sum(counts[p].values()) for p in PARTITIONS})

def wilson_illustration(n,k,z=1.959963984540054):
    p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den
    half=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/den
    return [center-half,center+half]

def search(rows,membership):
    trials=[];accepted=[]
    for n in (6,10,12,15,20):
        try:
            assignment=propose(rows,membership,n)
            result=assess(rows,membership,assignment)
            trials.append(dict(minority_test_target=n,**result))
            if result['meets_allocation_criteria']:accepted.append((n,assignment,result))
        except ValueError as exc:trials.append(dict(minority_test_target=n,meets_allocation_criteria=False,errors=[str(exc)]))
    return trials,accepted

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',required=True,type=Path)
    ap.add_argument('--similarity-links',required=True,type=Path)
    ap.add_argument('--conservative-links',required=True,type=Path,help='complete distance<=8 graph; unresolved extra edges are retained')
    ap.add_argument('--reviewed-links',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args()
    if a.out.exists():ap.error('existing output preserved; choose a new directory')
    from olid_inventory import validate_inventory
    from research_inputs import validate_olid_capture_groups
    before=hashlib.sha256(a.manifest.read_bytes()).hexdigest()
    rows=validate_inventory(a.manifest,ROOT)
    edges=read_csv(a.similarity_links);stress=read_csv(a.conservative_links);reviewed=read_csv(a.reviewed_links)
    basepairs={frozenset((e['path_a'],e['path_b'])) for e in edges if e.get('scope')=='all_files_diagnostic_only'}
    widerpairs={frozenset((e['path_a'],e['path_b'])) for e in stress if e.get('scope')=='all_files_diagnostic_only'}
    if not basepairs<=widerpairs:ap.error('stress graph omitted known baseline relationships')
    baseline=build_components(rows,edges,reviewed)
    conservative=build_components(rows,stress,reviewed,max_distance=8)
    base_trials,base_accepted=search(rows,baseline)
    stress_trials,accepted=search(rows,conservative)
    selected=max(accepted,key=lambda x:x[0]) if accepted else None
    groups=component_records(rows,conservative)
    active=[r for r in rows if r['status']=='active']
    try:validate_olid_capture_groups(active)
    except ValueError as exc:strict='BLOCKED: '+str(exc)
    else:raise ValueError('strict evidence status unexpectedly changed; review protocol')
    report=dict(policy=POLICY,scope='offline feasibility; biological independence NOT established',seed=42,
        manifest_sha256=before,input_fingerprints={str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (a.manifest,a.similarity_links,a.conservative_links,a.reviewed_links)},
        all_inventory_records=len(rows),active_targets=len(active),quarantined=sum(r['status']=='quarantined' for r in rows),
        baseline_target_components=len({baseline[r['path']] for r in active}),
        conservative_target_components=len({conservative[r['path']] for r in active}),
        baseline_trials=base_trials,conservative_trials=stress_trials,
        strict_plantwise_splitting=strict,draft_manifest_emitted=bool(selected),
        precision_illustrations={'assumption':'independent Bernoulli outcomes assumed for illustration ONLY; not established; no predictions were made',
           'n15_7_correct_wilson95':wilson_illustration(15,7),'n15_15_correct_wilson95':wilson_illustration(15,15),
           'minority_recall_one_error_percentage_points':100/15},
        limitations=['All wider-screen edges are unresolved similarity candidates, NOT verified duplicates or plant identities.',
                     'Failure under conservative grouping is policy-dependent, not proof that no scientifically valid future pilot can exist.',
                     'No strict gate is relaxed. Draft-only proposed_partition is never consumed by model training.'])
    if base_accepted:
        _,candidate,base_result=max(base_accepted,key=lambda x:x[0])
        report['baseline_best_mathematical_proposal']=base_result
        report['baseline_proposal_under_conservative_graph']=assess(rows,conservative,candidate)
        target_edges=[dict(e,scope='all_files_diagnostic_only') for e in edges if e.get('scope')=='target_candidates']
        naive_membership=build_components(active,target_edges,reviewed)
        try:report['target_only_negative_control']=assess(rows,baseline,propose(active,naive_membership,15))
        except ValueError as exc:report['target_only_negative_control']={'meets_allocation_criteria':False,'errors':[str(exc)]}
    biggest=max(groups.values(),key=lambda g:sum(r['status']=='active' for r in g))
    report['largest_conservative_target_component']=dict(targets=sum(r['status']=='active' for r in biggest),
        class_counts=dict(Counter(r['source_class'] for r in biggest if r['status']=='active')))
    total_n=sum(r['source_class']=='tomato__N' for r in active)
    giant_n=sum(r['status']=='active' and r['source_class']=='tomato__N' for r in biggest)
    report['nitrogen_capacity_bound']={'total':total_n,'in_largest_component':giant_n,'outside_largest_component':total_n-giant_n,
        'outside_needed_if_largest_in_train':20,'outside_needed_if_largest_in_val':30,
        'outside_needed_if_largest_in_test':20,'needed_if_largest_excluded':35,
        'interpretation':'Necessary count bound for min train15/val5/test15 N; no partition search or random seed can overcome it.'}
    assert before==hashlib.sha256(a.manifest.read_bytes()).hexdigest(),'source manifest changed'
    report['source_manifest_unchanged']=True
    a.out.mkdir(parents=True)
    if selected:
        _,assignment,result=selected
        fields=list(rows[0])+['content_component_id','proposed_partition','proposal_policy','biological_independence']
        with (a.out/'draft_exploratory_holdout.csv').open('x',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for r in active:w.writerow(dict(r,content_component_id=conservative[r['path']],
                proposed_partition=assignment[r['path']],proposal_policy=POLICY,biological_independence='not_established'))
        report['selected_allocation']=result
    (a.out/'feasibility_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
