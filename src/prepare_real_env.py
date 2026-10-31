"""Validate exact image/location/date paired real measurements; no synthetic fallback."""
import argparse
import csv
from pathlib import Path
from research_inputs import read_csv, paired_environment

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--splits', required=True, type=Path)
    p.add_argument('--measurements', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    if a.out.exists():
        p.error('existing output preserved')
    rows = paired_environment(read_csv(a.splits), read_csv(a.measurements))
    if not rows:
        p.error('no measurements')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    main()
