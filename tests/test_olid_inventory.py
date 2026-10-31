"""Synthetic inventory contracts: inspection never authorizes unsafe splitting."""
import csv, hashlib, os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from olid_inventory import validate_inventory
from research_inputs import olid_rows, validate_olid_capture_groups

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'a.JPG').write_bytes(b'SYNTHETIC TEST ONLY')
        self.manifest=self.root/'manifest.csv'
        env=patch.dict(os.environ,{'OLID_DATA_ROOT':str(self.root)});env.start();self.addCleanup(env.stop)
        self.row=dict(path='a.JPG',source='OLID_I',source_class='tomato__N',source_label='Nitrogen Deficiency',
            source_label_checked='true',label_evidence='SYNTHETIC TEST ONLY',condition='Tomato___N_Deficiency',
            acquisition='field',label_verified='true',diagnosis_verification='not_independently_verified',
            diagnosis_evidence='',group_id='unknown',group_evidence='',status='active',exclusion_reason='',
            sha256=hashlib.sha256((self.root/'a.JPG').read_bytes()).hexdigest())
    def write(self,rows=None):
        with self.manifest.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(self.row));w.writeheader();w.writerows(rows or [self.row])
    def test_inventory_accepts_honest_unknowns_but_strict_loading_blocks(self):
        self.write();self.assertEqual(len(validate_inventory(self.manifest,self.root)),1)
        with self.assertRaisesRegex(ValueError,'capture group'):olid_rows(self.manifest,self.root)
    def test_unknown_tokens_cannot_bypass_strict_group_guard(self):
        for token in ('unknown','UNKNOWN','none','n/a','na','null',''):
            self.row['group_id']=token;self.row['group_evidence']='unknown';self.write()
            with self.subTest(token=token),self.assertRaisesRegex(ValueError,'capture group'):olid_rows(self.manifest,self.root)
    def test_false_independent_diagnosis_requires_evidence(self):
        self.row['diagnosis_verification']='independently_verified';self.write()
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
    def test_modified_file_rejected(self):
        self.write();(self.root/'a.JPG').write_bytes(b'changed')
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
    def test_path_traversal_rejected(self):
        self.row['path']='../outside.JPG';self.write()
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
    def test_conflicting_duplicates_must_both_be_quarantined(self):
        (self.root/'b.JPG').write_bytes((self.root/'a.JPG').read_bytes())
        other=dict(self.row,path='b.JPG',source_class='tomato__K',source_label='Potassium Deficiency')
        self.write([self.row,other])
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
        self.row.update(status='quarantined',exclusion_reason='fixture conflict')
        other.update(status='quarantined',exclusion_reason='fixture conflict')
        self.write([self.row,other]);self.assertEqual(len(validate_inventory(self.manifest,self.root)),2)
        with self.assertRaisesRegex(ValueError,'empty OLID'):olid_rows(self.manifest,self.root)
    def test_quarantine_requires_reason(self):
        self.row.update(status='quarantined');self.write()
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
    def test_duplicate_active_content_rejected(self):
        (self.root/'b.JPG').write_bytes((self.root/'a.JPG').read_bytes());self.write([self.row,dict(self.row,path='b.JPG')])
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
    def test_split_guard_rejects_unknown_capture_groups(self):
        with self.assertRaisesRegex(ValueError,'capture group'):validate_olid_capture_groups([self.row])
        self.row.update(group_id='OLID_I:unknown',group_evidence='unknown')
        with self.assertRaisesRegex(ValueError,'capture group'):validate_olid_capture_groups([self.row])
    def test_split_guard_rejects_quarantine_even_with_groups(self):
        self.row.update(group_id='fixture',group_evidence='SYNTHETIC TEST ONLY',status='quarantined')
        with self.assertRaises(ValueError):validate_olid_capture_groups([self.row])
    def test_invalid_status_rejected_by_both_readers(self):
        self.row['status']='approved_by_guess';self.write()
        with self.assertRaises(ValueError):validate_inventory(self.manifest,self.root)
        with self.assertRaises(ValueError):olid_rows(self.manifest,self.root)

if __name__=='__main__':unittest.main(verbosity=2)
