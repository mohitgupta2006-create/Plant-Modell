"""Source prediction using border pixels, condition-matched tomato cohorts, group splits.

Run without torch. Failure to predict source does NOT prove absence of confounding.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report
from research_inputs import split_audit, local_file

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--splits',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    if a.out.exists(): p.error('existing output preserved')
    df=pd.read_csv(a.splits,keep_default_na=False)
    split_audit(df.to_dict('records'))
    df=df[df['crop']=='Tomato']
    sources=sorted(df['source'].unique())
    if len(sources)<2: p.error('BLOCKED: at least two sources required')
    common=set.intersection(*(set(df[df['source']==s]['condition']) for s in sources))
    df=df[df['condition'].isin(common)]
    if df.empty: p.error('BLOCKED: no common tomato conditions across sources; unmatched source control is confounded by class')
    root=Path(__file__).resolve().parent.parent
    features=[]
    for path in df['path']:
        with Image.open(local_file(root,path)) as im:
            x=np.asarray(im.convert('RGB').resize((32,32)),dtype=float)/255
        border=np.ones((32,32),bool);border[4:-4,4:-4]=False
        features.append(x[border].ravel())
    x=np.stack(features); tr=df['split'].eq('train').values;te=df['split'].eq('test').values
    if set(df.loc[tr,'source'])!=set(sources) or set(df.loc[te,'source'])!=set(sources):
        p.error('BLOCKED: missing source in train or test')
    # Fit on train only; balance train source-condition cells without altering test distribution.
    cells=df.loc[tr].groupby(['source','condition'])['path'].transform('size').to_numpy()
    clf=HistGradientBoostingClassifier(max_iter=150,random_state=42)
    clf.fit(x[tr],df.loc[tr,'source'],sample_weight=1/cells)
    pred=clf.predict(x[te]);truth=df.loc[te,'source']
    report={'status':'EXECUTED','common_conditions':sorted(common),'sources':sources,'n_train':int(tr.sum()),'n_test':int(te.sum()),
            'accuracy':float(accuracy_score(truth,pred)),'balanced_accuracy':float(balanced_accuracy_score(truth,pred)),
            'classification':classification_report(truth,pred,output_dict=True,zero_division=0),
            'limitations':'Border pixels may contain leaf tissue. Capture/location/source bias and symptom differences remain.'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':main()
