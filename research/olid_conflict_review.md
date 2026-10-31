# Five OLID I conflicting-label pairs: evidence review

## Decision

All five cases remain unresolved. Both records in every pair remain quarantined from model data and hence
from training/evaluation. No source labels or diagnoses were changed. This review was limited to these five pairs.

The conflict mechanism is established: identical images already appear under different labelled folders in the
published source archives. This is not a local extraction mix-up or manifest mapping error. The correct diagnosis
cannot be determined from those contradictory assignments, general labeling statements, or visual appearance.

## Review table

Each SHA256 applies to BOTH files in the corresponding row. Paths are relative to the configured OLID root.

| Pair | Relative path A | Source label A | Relative path B | Source label B | SHA256 (both files) | Conflict and disposition |
|---|---|---|---|---|---|---|
| OLID-C01 | `tomato__K/tomato__K (12).JPG` | Potassium Deficiency | `tomato__N/tomato__N (16).JPG` | Nitrogen Deficiency | `28511586e038610e38771eac56f22fc3d44e51495e2ae7bab3dd645a3891db89` | Identical original bytes; inconsistent original folder labels; both quarantined, diagnosis unresolved. |
| OLID-C02 | `tomato__K/tomato__K (27).JPG` | Potassium Deficiency | `tomato__N/tomato__N (13).JPG` | Nitrogen Deficiency | `b35feddb65008fd76748a4bb9e35ca47da9bb51ef9bdb6924a1ca39916d98a3e` | Identical original bytes; inconsistent original folder labels; both quarantined, diagnosis unresolved. |
| OLID-C03 | `tomato__K/tomato__K (31).JPG` | Potassium Deficiency | `tomato__N/tomato__N (25).JPG` | Nitrogen Deficiency | `9a5cff1927054f31858963cd77f5f0b2a5a1548fb539035199a22f29982ae62f` | Identical original bytes; inconsistent original folder labels; both quarantined, diagnosis unresolved. |
| OLID-C04 | `tomato__MIT/tomato__MIT (1).JPG` | Mite | `tomato__N/tomato__N (21).JPG` | Nitrogen Deficiency | `6923e80a8a9b0e8a5e44724228765ccae4ccadc82b293528841d0d1dc0238e8b` | Identical original bytes; inconsistent original folder labels; both quarantined, diagnosis unresolved. |
| OLID-C05 | `tomato__MIT/tomato__MIT (8).JPG` | Mite | `tomato__N/tomato__N (26).JPG` | Nitrogen Deficiency | `5c05ae81e5345f790f6df2bfc305232f1eadd02356f05de836fb29226f13f2fb` | Identical original bytes; inconsistent original folder labels; both quarantined, diagnosis unresolved. |

## Authoritative provenance checks

The official [Zenodo version 1.1.0 record](https://zenodo.org/records/8105154) lists the original archives and
their checksums. Both downloaded archives matched those published checksums:

| Archive | Published and locally calculated MD5 | Result |
|---|---|---|
| tomato__part_1.zip | 35607a338f08a0f2fe64406a48b5d5ef | Match |
| tomato__part_2.zip | 83730955bfd6b1628cd9a582e993a75b | Match |

The supplied class_distribution.xlsx also matches the record's MD5, 4e7fb219f2bdffebce5be0b67e9c931f.
Its relevant entries are main_dataset!A54:D54 (Mite), A56:D56 (Potassium Deficiency), A57:D57 (Nitrogen Deficiency).
The workbook supplies aggregate class definitions/counts, not per-image corrected diagnoses.

All ten disputed files were read directly from the checksum-matched ZIPs without extracting/replacing images.
ZIP member CRC verification succeeded, each member was byte-identical to its local image, and both files within
each pair shared the reported SHA256. Original member paths preserve the same conflicting folder assignments.
Each existing manifest source_class/source_label matches that original folder and its workbook definition.

The [original dataset paper](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1251888/full)
describes expert labeling and adjudication generally. The checked article and release record provide no case-level
adjudication for these ten files. None of the ten files contained diagnostic annotations in the checked EXIF fields
(ImageDescription, UserComment, XPKeywords, XPSubject, XPTitle). Missing EXIF fields are not evidence of a diagnosis.
No unpublished author correspondence or laboratory records were available, and no one was contacted.

This establishes original-source duplication and inconsistent labels; it does not select the scientifically correct
label. No authoritative evidence available in this review resolves any pair. A future author-issued per-image
correction or documented expert adjudication is needed before either record can be reconsidered.

## Draft manifest and quarantine

The external active manifest.csv was regenerated only after the reviewed draft passed inventory validation.
The previous manifest was preserved as manifest.before_conflict_review.csv; the reviewed draft is
manifest.conflict_review.csv. All three remain external and uncommitted. Original images are untouched.

New provenance columns record the conflict review ID, evidence and decision for the ten affected records.
Their status remains quarantined, with explicit exclusion from training and evaluation. No paths, source labels,
model condition labels, hashes, identities, group evidence or diagnosis-verification fields were changed.
Unknown plant/leaf/capture identities remain unknown; no filename-derived grouping was introduced.

Inventory counts remain 798 records: 318 target candidates, 470 source-only records and 10 quarantined records.
These counts do not establish training readiness. Strict model loading and leakage-safe splitting still reject
the missing physical capture-group evidence.

## Checks actually executed

- Both official archive checksum comparisons passed; source workbook checksum passed.
- Ten original archive members matched the local images byte-for-byte; five pair-identity comparisons passed.
- Ten manifest source-label mappings matched original source folders and the supplied workbook.
- The regenerated 798-record manifest passed path containment, SHA256 and quarantine inventory validation.
- Preservation checks passed for original labels, paths, hashes and unknown identity/group/diagnosis fields.
- Strict model loading and split eligibility were exercised and remained BLOCKED by missing capture groups.
- Existing inventory/quarantine tests: 11 passed.
- Existing root tests: 14 passed, 1 symlink test skipped due to Windows privilege. Junction escape test passed.
- Existing input contracts: 20 passed; reconciliation checks: 32 passed; saved-prediction checks: 7 passed.
- Overall runner exited 1: historical hash audit found 24 expected artifacts missing (0 changed); torch inference
  integration was skipped because torch is unavailable. This is not reported as an all-passing suite.

No training, diagnostic relabeling, dataset-image commit or capture-group bypass occurred.
