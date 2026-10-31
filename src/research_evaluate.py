"""Evaluate reviewer runs separately from historical tables. No overwrite, no fabricated metrics."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, balanced_accuracy_score, confusion_matrix
import config as C
from dataset import build_table, LeafDataset
from infer import get_device, load_variant, predict_loader
from reconcile import reconcile
from evaluate import acc_stat

from research_annotations import masked_image

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--variant',default='image',choices=['image','env','fusion','fusion_shuffled_env'])
    ap.add_argument('--run',required=True)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--masks',type=Path,help='reviewed leaf masks CSV: path,leaf_mask,verified,review_evidence')
    a=ap.parse_args()
    if a.out.exists(): ap.error('output already exists; choose a new directory')
    model,maps,cfg=load_variant(a.variant,dev=get_device(),run=a.run)
    if cfg.get('research_protocol')!='reviewer_revision_v1': ap.error('requires reviewer checkpoint')
    fingerprint=(C.DATA_PROCESSED/'splits.csv').read_bytes()
    if a.variant!='image': fingerprint+=(C.DATA_PROCESSED/'env_real.csv').read_bytes()
    if hashlib.sha256(fingerprint).hexdigest()!=cfg['dataset_sha256']:
        ap.error('split manifest differs from training')
    df,_=build_table(research=True,variant=a.variant)
    test=df[df['split']=='test'].reset_index(drop=True)
    excluded_unseen = 0
    if cfg.get('lab_only'):
        test=test[test['acquisition']=='field'].reset_index(drop=True)
        excluded_unseen=int((~test['condition'].isin(maps['condition'])).sum())
        test=test[test['condition'].isin(maps['condition'])].reset_index(drop=True)
    if not len(test): ap.error('no eligible test images')
    ds=LeafDataset(test,maps,maps['research_env_stats'],False,load_image=a.variant!='env')
    if a.masks:
        if a.variant=='env': ap.error('background intervention requires image branch')
        masks=pd.read_csv(a.masks,keep_default_na=False)
        if masks['path'].duplicated().any(): ap.error('duplicate mask path')
        masks=masks.set_index('path')
        class Removed(LeafDataset):
            def __getitem__(self,i):
                item=super().__getitem__(i)
                r=masks.loc[self.df.loc[i,'path']].to_dict()
                if str(r.get('verified')).lower()!='true' or not r.get('review_evidence'):
                    raise ValueError('mask review evidence required')
                r['path']=self.df.loc[i,'path']
                item['image']=self.tf(masked_image(C.ROOT,r))
                return item
        ds=Removed(test,maps,maps['research_env_stats'],False)
    logits=predict_loader(model,DataLoader(ds,batch_size=32),get_device())
    arrays={k:v.numpy() for k,v in logits.items()}
    # Unsupported diagnostic branches are abstentions, retained in all denominators.
    decoded=[]
    for i in range(len(test)):
        try: decoded.extend(reconcile({k:v[i:i+1] for k,v in arrays.items()},maps,maps['cause_trained_classes']))
        except ValueError as exc:
            if 'unsupported diagnostic branch' not in str(exc): raise
            decoded.append(dict(crop='unavailable',health='unavailable',cause='unavailable',condition='unavailable',severity='unavailable'))
    pred=pd.DataFrame(decoded)
    result=test.copy()
    for k in ('crop','health','cause','condition'):
        result['pred_'+k]=pred[k].values
        result['raw_'+k]=[maps[k][int(j)] for j in arrays[k].argmax(1)]
    report={'run':a.run,'test_n':len(test),'background_removed':bool(a.masks),'excluded_field_conditions_absent_from_lab_training':excluded_unseen,'metrics':{},
            'severity':'BLOCKED: no adjudicated ground truth',
            'interpretation':'mixed-source test is not a source-held-out validation; segmentation is an intervention, not proof of causal reasoning'}
    a.out.mkdir(parents=True)
    result.to_csv(a.out/'predictions.csv',index=False)
    scopes=[('all',np.ones(len(test),bool))]+[(f'source_{s}',(test['source']==s).values) for s in sorted(test['source'].unique())]
    for scope,base in scopes:
        for h in ('health','cause','condition'):
            mask=base.copy()
            if h=='cause':
                mask &= test['health'].eq('Unhealthy').values
                if set(maps['cause_trained_classes'])!={'Biotic','Abiotic'}:
                    report['metrics'][scope+'/'+h]={'status':'BLOCKED: both training causes required'}; continue
            if not mask.any(): continue
            yt,yp=test.loc[mask,h],result.loc[mask,'pred_'+h]
            labels=sorted(set(yt)|set(yp))
            stats=acc_stat(test['group_id'].values,mask,(test[h]==result['pred_'+h]).values)
            report['metrics'][scope+'/'+h]={'classification':classification_report(yt,yp,labels=labels,output_dict=True,zero_division=0),
                'balanced_accuracy':float(balanced_accuracy_score(yt,yp)),
                'accuracy':stats[0], 'accuracy_ci95':list(stats[1:3]) if np.isfinite(stats[1]) else None,
                'n':stats[3],'groups':stats[4]}
            pd.DataFrame(confusion_matrix(yt,yp,labels=labels),index=labels,columns=labels).to_csv(a.out/f'{scope}_{h}_confusion.csv')
    # Required disease/N/NK comparison restricted to unhealthy tomato field images.
    subset=result[(result['crop']=='Tomato')&(result['acquisition']=='field')&(result['health']=='Unhealthy')]
    def coarse(c):
        if c=='Tomato___N_Deficiency': return 'N_Deficiency'
        if c=='Tomato___NK_Deficiency': return 'NK_Deficiency'
        return 'Disease' if c in maps['condition'] and c.startswith('Tomato___') and not c.endswith('___healthy') else 'other_or_abstain'
    truth=subset['condition'].map(coarse); prediction=subset['pred_condition'].map(coarse)
    if set(truth)>={'Disease','N_Deficiency','NK_Deficiency'}:
        pd.crosstab(truth,prediction).to_csv(a.out/'tomato_field_disease_N_NK_confusion.csv')
        report['tomato_field_confusion']='executed; source confounding remains'
    else: report['tomato_field_confusion']='BLOCKED: missing required tomato field classes'
    (a.out/'metrics.json').write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')

if __name__=='__main__': main()
