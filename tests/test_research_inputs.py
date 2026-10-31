"""Synthetic fixtures test contracts only; these are not research images or experiment results."""
import csv
import hashlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from research_inputs import olid_rows, condition_cause, paired_environment, split_audit
from research_annotations import affected_fraction, weighted_kappa, masked_image
from prepare_data import label, PV_MAP, PD_MAP
from reconcile import reconcile

class Inputs(unittest.TestCase):
    def setUp(self):
        env=patch.dict(os.environ);env.start();self.addCleanup(env.stop)
        os.environ.pop("OLID_DATA_ROOT", None)  # fixtures must not access a user dataset
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.image=self.root/'leaf.png'; Image.new('RGB',(40,40),'green').save(self.image)
        self.row=dict(path='leaf.png',condition='Tomato___N_Deficiency',source='OLID_I',acquisition='field',
                      label_verified='true',label_evidence='TEST FIXTURE ONLY',group_id='plant1',group_evidence='fixture record',
                      sha256=hashlib.sha256(self.image.read_bytes()).hexdigest())
    def tearDown(self): self.tmp.cleanup()
    def load(self,rows=None):
        p=self.root/'manifest.csv'
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(self.row));w.writeheader();w.writerows(rows or [self.row])
        return olid_rows(p,self.root)
    def test_explicit_olid_label(self):
        r=self.load()[0];self.assertEqual(label(r)['cause'],'Abiotic');self.assertEqual(r['group_id'],'OLID_I:plant1')
    def test_NK_label(self):
        self.row['condition']='Tomato___NK_Deficiency';self.assertEqual(label(self.load()[0])['cause'],'Abiotic')
    def test_healthy_none(self):
        self.row['condition']='Tomato___healthy';r=label(self.load()[0]);self.assertEqual((r['health'],r['cause']),('Healthy','None'))
    def test_existing_mappings(self):
        for c,k in list(PV_MAP.values())+list(PD_MAP.values()):
            r=label(dict(condition=f'{c}___{k}'));self.assertEqual(r['cause'],'None' if k=='healthy' else 'Biotic')
    def test_unknown_label_rejected(self):
        self.row['condition']='guessed_N';self.assertRaises(ValueError,self.load)
    def test_missing_review_rejected(self):
        self.row['label_verified']='false';self.assertRaises(ValueError,self.load)
    def test_hash_mismatch(self):
        self.row['sha256']='0'*64;self.assertRaises(ValueError,self.load)
    def test_duplicate_path(self): self.assertRaises(ValueError,self.load,[self.row,self.row])
    def test_escape_rejected(self):
        self.row['path']='../outside.png';self.assertRaises(ValueError,self.load)
    def test_missing_group(self):
        self.row['group_id']='';self.assertRaises(ValueError,self.load)
    def test_environment_exact_pairing(self):
        s=dict(path='leaf.png',capture_date='2026-10-01',capture_location='fixture plot')
        r=dict(s,measurement_origin='real',measurement_evidence='TEST ONLY',temperature='25',rainfall='1',humidity='50',soil_moisture='30',units='C;mm/day;RH%;VWC%')
        self.assertEqual(len(paired_environment([s],[r])),1)
        for key,val in [('capture_date','2026-10-02'),('capture_location','different'),('temperature','nan'),('measurement_origin','simulated'),('units','unknown')]:
            with self.subTest(key=key): self.assertRaises(ValueError,paired_environment,[s],[dict(r,**{key:val})])
    def test_missing_environment(self): self.assertRaises(ValueError,paired_environment,[dict(path='a')],[])
    def test_split_group_leak(self):
        r=dict(path='a',group_id='same',split='train',crop='Tomato',condition='Tomato___N_Deficiency',health='Unhealthy',cause='Abiotic',source='OLID_I',acquisition='field')
        self.assertRaises(ValueError,split_audit,[r,dict(r,path='b',split='test')])
    def test_confusion_not_declared_solved(self):
        r=dict(path='a',group_id='g',split='train',crop='Tomato',condition='Tomato___N_Deficiency',health='Unhealthy',cause='Abiotic',source='OLID_I',acquisition='field')
        counts,missing=split_audit([r]);self.assertEqual(len(missing),5);self.assertEqual(sum(counts.values()),1)
    def test_inconsistent_label(self):
        r=dict(path='a',group_id='g',split='train',crop='Tomato',condition='Tomato___N_Deficiency',health='Unhealthy',cause='Biotic',source='OLID_I',acquisition='field')
        self.assertRaises(ValueError,split_audit,[r])
    def test_affected_area(self):
        self.assertEqual(affected_fraction([[255,255],[0,0]],[[255,0],[0,0]]),.5)
        self.assertRaises(ValueError,affected_fraction,[[255,0]],[[0,255]])
        self.assertRaises(ValueError,affected_fraction,[[0]],[[0]])
        self.assertRaises(ValueError,affected_fraction,[[1]],[[0]])
    def test_background_intervention(self):
        mask=np.zeros((40,40),dtype=np.uint8);mask[10:30,10:30]=255
        Image.fromarray(mask).save(self.root/'mask.png')
        output=np.asarray(masked_image(self.root,dict(path='leaf.png',leaf_mask='mask.png')))
        original=np.asarray(Image.open(self.image))
        self.assertTrue(np.all(output[mask==0]==127))
        self.assertTrue(np.array_equal(output[mask>0],original[mask>0]))
    def test_agreement(self):
        self.assertAlmostEqual(weighted_kappa([(0,0),(1,1),(2,2)]),1)
        self.assertIsNone(weighted_kappa([]))
    def test_hierarchy(self):
        maps=dict(crop=['Tomato'],health=['Healthy','Unhealthy'],cause=['Biotic','Abiotic'],
            condition=['Tomato___healthy','Tomato___Early_blight','Tomato___N_Deficiency','Tomato___NK_Deficiency'],
            condition_meta={'Tomato___healthy':['Tomato',True],'Tomato___Early_blight':['Tomato',False],
                'Tomato___N_Deficiency':['Tomato',False],'Tomato___NK_Deficiency':['Tomato',False]},
            cause_trained_classes=['Biotic','Abiotic'],decoder='cause_first',severity_trained=False)
        lg=dict(crop=np.array([[1]]),health=np.array([[0,5]]),cause=np.array([[0,5]]),condition=np.array([[20,30,10,0]]),severity=np.array([[5,5]]))
        out=reconcile(lg,maps,maps['cause_trained_classes'])[0]
        self.assertEqual((out['condition'],out['cause'],out['severity']),('Tomato___N_Deficiency','Abiotic','unavailable'))
        lg['health']=np.array([[5,0]])
        out=reconcile(lg,maps,maps['cause_trained_classes'])[0]
        self.assertEqual((out['condition'],out['cause'],out['severity']),('Tomato___healthy','None','None'))
    def test_unrepresented_branch_abstains(self):
        from research_hierarchy import gated_logits
        m=dict(crop=['Tomato'],health=['Healthy','Unhealthy'],cause=['Biotic','Abiotic'],condition=['Tomato___Early_blight'],condition_meta={'Tomato___Early_blight':['Tomato',False]},cause_trained_classes=['Biotic','Abiotic'])
        lg=dict(crop=[[1]],health=[[5,0]],cause=[[5,0]],condition=[[1]])
        self.assertRaises(ValueError,gated_logits,lg,m)

if __name__=='__main__':unittest.main(verbosity=2)
