"""Dataset-root isolation tests. All metadata/images are synthetic temporary fixtures."""
import csv
import hashlib
import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from research_inputs import olid_data_root, olid_image_file, olid_rows, index_image_path


class OLIDRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'; self.repo.mkdir()
        self.external = self.base / 'external dataset'; self.external.mkdir()
        self.image = self.external / 'tomato__N' / 'leaf.JPG'
        self.image.parent.mkdir(); self.image.write_bytes(b'SYNTHETIC PATH FIXTURE ONLY')
        self.other = self.base / 'external dataset sibling'; self.other.mkdir()
        (self.other / 'outside.JPG').write_bytes(b'outside selected root')
        self.env = patch.dict(os.environ, {}, clear=False); self.env.start()
        self.addCleanup(self.env.stop)
        os.environ.pop('OLID_DATA_ROOT', None)
        self.manifest = self.base / 'manifest.csv'
        self.row = dict(path='tomato__N/leaf.JPG',condition='Tomato___N_Deficiency',
                        source='OLID_I',acquisition='field',label_verified='true',
                        label_evidence='SYNTHETIC TEST ONLY',group_id='fixture',
                        group_evidence='SYNTHETIC TEST ONLY',
                        sha256=hashlib.sha256(self.image.read_bytes()).hexdigest())

    def selected(self): os.environ['OLID_DATA_ROOT'] = str(self.external)
    def load(self):
        with self.manifest.open('w', newline='', encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(self.row));w.writeheader();w.writerow(self.row)
        return olid_rows(self.manifest, self.repo)

    def test_unset_preserves_repository_root(self):
        self.assertEqual(olid_data_root(self.repo), self.repo.resolve())
        p=self.repo/'leaf.JPG';p.write_bytes(b'legacy')
        self.assertEqual(olid_image_file(self.repo,'leaf.JPG'),p.resolve())

    def test_explicit_absolute_root_with_spaces(self):
        self.selected()
        self.assertEqual(olid_data_root(self.repo),self.external.resolve())
        self.assertEqual(olid_image_file(self.repo,self.row['path']),self.image.resolve())

    def test_invalid_configurations(self):
        for value in ('', '   ', 'relative/path', str(self.base/'missing'), str(self.image), self.external.anchor):
            with self.subTest(value=value):
                os.environ['OLID_DATA_ROOT']=value
                with self.assertRaises(ValueError): olid_data_root(self.repo)

    def test_absolute_manifest_entries_rejected(self):
        self.selected()
        for value in (str(self.image),'C:\\unrelated\\file.jpg','C:relative.jpg',r'\\host\share\image.jpg',r'\image.jpg'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): olid_image_file(self.repo,value)

    def test_traversal_and_alternate_streams_rejected(self):
        self.selected()
        for value in ('../external dataset sibling/outside.JPG',r'..\external dataset sibling\outside.JPG',
                      'tomato__N/../tomato__N/leaf.JPG','tomato__N/leaf.JPG:secret','', '   ', 'bad\x00name'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): olid_image_file(self.repo,value)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction test')
    def test_junction_escape_rejected(self):
        self.selected()
        link=self.external/'junction'
        result=subprocess.run(['cmd.exe','/c','mklink','/J',str(link),str(self.other)],
                              capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
        self.addCleanup(link.rmdir)
        with self.assertRaises(ValueError): olid_image_file(self.repo,'junction/outside.JPG')
        self.assertTrue((self.other/'outside.JPG').is_file())

    def test_invalid_path_types(self):
        self.selected()
        for value in (None, 42):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): olid_image_file(self.repo,value)

    def test_missing_image_rejected(self):
        self.selected()
        with self.assertRaises(ValueError): olid_image_file(self.repo,'tomato__N/missing.JPG')

    def test_symlink_escape_rejected(self):
        self.selected()
        link=self.external/'escape'
        try: link.symlink_to(self.other,target_is_directory=True)
        except OSError as exc: self.skipTest(f'host cannot create symlink: {exc}')
        with self.assertRaises(ValueError): olid_image_file(self.repo,'escape/outside.JPG')

    def test_external_index_requires_explicit_root(self):
        with self.assertRaises(ValueError): index_image_path(self.image,'OLID_I',self.repo)
        self.selected()
        exported=index_image_path(self.image,'OLID_I',self.repo)
        self.assertEqual((self.repo / exported).resolve(),self.image.resolve())

    def test_external_index_rejects_other_source_and_sibling(self):
        self.selected()
        with self.assertRaises(ValueError): index_image_path(self.image,'PlantVillage',self.repo)
        with self.assertRaises(ValueError): index_image_path(self.other/'outside.JPG','OLID_I',self.repo)

    def test_internal_index_remains_relative(self):
        p=self.repo/'internal.JPG';p.write_bytes(b'internal')
        self.assertEqual(index_image_path(p,'PlantVillage',self.repo),'internal.JPG')

    def test_full_fixture_manifest_uses_configured_root(self):
        self.selected()
        self.assertEqual(self.load()[0]['path'],self.image.resolve())

    def test_review_and_group_guards_remain_required(self):
        self.selected()
        for key,value in (('label_verified','false'),('label_evidence',''),('group_id',''),('group_evidence','')):
            with self.subTest(key=key):
                original=self.row[key];self.row[key]=value
                with self.assertRaises(ValueError): self.load()
                self.row[key]=original

    def test_hash_guard_remains_required(self):
        self.selected();self.row['sha256']='0'*64
        with self.assertRaises(ValueError): self.load()


if __name__=='__main__': unittest.main(verbosity=2)
