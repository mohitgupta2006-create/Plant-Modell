"""Read actual split metadata and export distributions and eligibility; never invent counts."""
import argparse
import json
from pathlib import Path
from research_inputs import read_csv, split_audit

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--splits', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    if a.out.exists():
        ap.error('output exists; choose a new path')
    counts, missing = split_audit(read_csv(a.splits))
    report = {'distribution': [dict(zip(('split','source','acquisition','condition','cause'), k), n=v)
                               for k,v in sorted(counts.items())],
              'missing_tomato_field_cells': missing,
              'biotic_abiotic_field_evaluation': 'BLOCKED' if missing else 'eligible; residual source confounding remains',
              'warning': 'Metadata checks do not establish physical plant independence or eliminate capture/source bias.'}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(report['biotic_abiotic_field_evaluation'])

if __name__ == '__main__':
    main()
