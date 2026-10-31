"""Synthetic allocation contracts only; no fabricated real specimen metadata or training."""
import copy
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'/'tools'))
from assess_olid_holdout import build_components, propose, assess, search, CLASSES

def row(path,cls='tomato__healthy',status='active',digest=None):
    return dict(path=path,source_class=cls,status=status,sha256=digest or hashlib.sha256(path.encode()).hexdigest(),
                group_id='unknown',group_evidence='')
def edge(a,b,d=6):return dict(path_a=a,path_b=b,distance=str(d),scope='all_files_diagnostic_only')
def review(a,b):return dict(path_a=a,path_b=b,decision='retain_atomic_component_or_exclude_component_from_evaluation')
def cohort():
    rows=[row(f'{c}/{i}.jpg',c) for c,n in zip(CLASSES,(120,45,45)) for i in range(n)]
    return rows,{r['path']:f'fixture_component_{i}' for i,r in enumerate(rows)}

class ExploratoryTests(unittest.TestCase):
    def test_constructive_allocation_meets_counts_and_components(self):
        rows,m=cohort();a=propose(rows,m,15);r=assess(rows,m,a)
        self.assertTrue(r['meets_allocation_criteria'])
        self.assertEqual(r['class_counts']['test'],dict(zip(CLASSES,(30,15,15))))
        self.assertEqual(r['class_counts']['val'],dict(zip(CLASSES,(15,5,5))))
    def test_deterministic_without_changing_unknown_metadata(self):
        rows,m=cohort();before=copy.deepcopy(rows)
        self.assertEqual(propose(rows,m,15),propose(rows,m,15))
        self.assertEqual(rows,before)
        self.assertTrue(all(r['group_id']=='unknown' and 'split' not in r for r in rows))
    def test_too_small_test_rejected(self):
        rows,m=cohort();r=assess(rows,m,propose(rows,m,12))
        self.assertFalse(r['meets_allocation_criteria'])
        self.assertTrue(any('insufficient test support' in e for e in r['errors']))
    def test_source_only_bridge_cannot_cross_partitions(self):
        rows=[row('a'),row('b','tomato__N'),row('context',status='source_only')]
        m=build_components(rows,[edge('a','context'),edge('context','b')],[])
        self.assertEqual(m['a'],m['b'])
        r=assess(rows,m,{'a':'train','b':'test'})
        self.assertTrue(any('crosses partitions' in e for e in r['errors']))
    def test_quarantined_context_forbids_holdout(self):
        rows=[row('a'),row('q',status='quarantined')]
        m=build_components(rows,[edge('a','q')],[])
        r=assess(rows,m,{'a':'test'})
        self.assertTrue(any('quarantine-connected' in e for e in r['errors']))
    def test_exact_duplicate_union_survives_missing_similarity_edge(self):
        rows=[row('a',digest='same'),row('b','tomato__N',digest='same'),row('c',status='source_only')]
        m=build_components(rows,[edge('a','c')],[])
        self.assertEqual(m['a'],m['b'])
    def test_missing_direct_target_review_rejected(self):
        with self.assertRaisesRegex(ValueError,'review decision missing'):
            build_components([row('a'),row('b')],[edge('a','b')],[])
    def test_review_cannot_drop_a_link_automatically(self):
        with self.assertRaises(ValueError):
            build_components([row('a'),row('b')],[edge('a','b')],[dict(review('a','b'),decision='discard_to_improve_counts')])
    def test_wider_unresolved_bridge_is_retained(self):
        rows=[row('a'),row('b'),row('c',status='source_only')]
        m=build_components(rows,[edge('a','c',8),edge('c','b',8)],[],max_distance=8)
        self.assertEqual(m['a'],m['b'])
    def test_conservative_graph_can_remove_all_apparent_feasibility(self):
        rows,m=cohort();n=[r['path'] for r in rows if r['source_class']=='tomato__N']
        for p in n[:33]:m[p]='fixture_large_N_component'
        trials,accepted=search(rows,m)
        self.assertEqual(accepted,[])
        self.assertTrue(all(not r['meets_allocation_criteria'] for r in trials))
    def test_context_records_never_get_assigned(self):
        rows,m=cohort()
        for p,status in [('q','quarantined'),('c','source_only')]:rows.append(row(p,status=status));m[p]=p
        a=propose(rows,m,15)
        self.assertNotIn('q',a);self.assertNotIn('c',a)
    def test_invalid_partition_or_incomplete_cohort_rejected(self):
        rows,m=cohort();a=propose(rows,m,15)
        with self.assertRaises(ValueError):assess(rows,m,dict(a,unexpected='test'))
        a[next(iter(a))]='invalid'
        with self.assertRaises(ValueError):assess(rows,m,a)
    def test_foreign_similarity_path_rejected(self):
        with self.assertRaises(ValueError):build_components([row('a')],[edge('a','outside')],[])

if __name__=='__main__':unittest.main(verbosity=2)
