# OLID I tomato integration validation

Both extracted tomato parts were inspected. This validates files and publisher-provided folder labels,
not independent diagnoses or research readiness. No training or train/validation/test split was run.
The external dataset stayed outside Git; no images were moved, copied, relabelled, or committed.

## Actual file and class counts

The supplied class_distribution.xlsx, main_dataset!A52:D58, was read without modification.
Every discovered image directory matched a tomato class named by the workbook. No class-directory names were
assumed for discovery; the audit scans actual image paths and compares their parent directories with the workbook.

| Folder | Spreadsheet count | Actual files | Result |
|---|---:|---:|---|
| tomato__healthy | 236 | 236 | MATCH |
| tomato__LM | 207 | 207 | MATCH |
| tomato__MIT | 200 | 200 | MATCH |
| tomato__JAS_MIT | 32 | 32 | MATCH |
| tomato__K | 36 | 36 | MATCH |
| tomato__N | 47 | 47 | MATCH |
| tomato__N_K | 40 | 40 | MATCH |

Total: 798 files, all readable via verification and full default-frame RGB decoding. There are 793 unique file
contents. 533 containers identify as JPEG and 265 as MPO despite .JPG names. Only default image frames were
decoded, matching the existing loader; extra MPO frames are not additional training samples. 790 images are
3024x3024; eight have other valid dimensions. Full dimensions are in the machine-readable local report.

## Unresolved duplicate labels and quarantine

Five cross-label duplicate pairs were found using SHA256 and independently compared byte-for-byte. The first
three pairs reproduce the previously disputed cases. The final two appear across the newly available mite class
and nitrogen class. No attempt was made to guess the correct diagnosis.

| Source-labelled image | Identical source-labelled image |
|---|---|
| tomato__K/tomato__K (12).JPG | tomato__N/tomato__N (16).JPG |
| tomato__K/tomato__K (27).JPG | tomato__N/tomato__N (13).JPG |
| tomato__K/tomato__K (31).JPG | tomato__N/tomato__N (25).JPG |
| tomato__MIT/tomato__MIT (1).JPG | tomato__N/tomato__N (21).JPG |
| tomato__MIT/tomato__MIT (8).JPG | tomato__N/tomato__N (26).JPG |

All 10 conflicting files are logically quarantined: their manifest status is `quarantined` and the reason identifies
the unresolved source-label conflict. Both sides are excluded, not just the extra copy. Originals remain untouched.
The local quarantine.csv records all exclusions. Strict OLID loading skips quarantined/source-only records, and
inventory validation rejects any cross-label exact-duplicate pair not fully quarantined.

No additional same-class exact duplicate groups were found. Perceptual near-duplicate discovery and physical
leaf/plant independence were not established by this audit; exact-byte deduplication does not substitute for either.

## Manifest semantics and real loading

An external manifest.csv now records all 798 real file paths and hashes, source folders/labels, workbook evidence,
readability and exclusion status. It contains 318 target candidates (236 healthy, 42 N, 40 NK), 470 source-only
records outside current model targets, and 10 quarantined records. These 318 are inspection candidates, not
training-ready examples. Potassium-only, mite, leaf-miner and combined-jassid/mite labels remain source labels;
no equivalence to existing PlantVillage/PlantDoc conditions was invented.

`source_label_checked=true` and `label_verified=true` mean only that folder labels were reconciled against the
source spreadsheet, as recorded by `label_review_scope=source_folder_to_spreadsheet_only`. Every diagnosis is
explicitly `not_independently_verified`, with no fabricated diagnosis evidence. `plant_id`, `leaf_id`, `group_id`,
capture date and capture location remain `unknown`; group evidence is empty. Source acquisition is accompanied
by its dark-cloth/natural-light protocol, not represented as complex outdoor scene imagery.

The real inventory smoke passed for all 798 records: safe root containment, existence, SHA256 and source metadata
were checked, and each image was decoded during the audit. The final code rechecked every manifest hash.
Strict model-data loading and leakage-safe splitting are BLOCKED because reliable capture groups and evidence
are absent. The literal value `unknown` (including prefixed OLID_I:unknown) cannot satisfy the group guard.
No attempt was made to infer identities from filenames or substitute perceptual groups for mandatory evidence.
The combined PlantVillage/PlantDoc preparation pipeline was not executed; this report claims OLID inventory
validation only. It does not claim other datasets have become available.

## Reproduction

Set OLID_DATA_ROOT explicitly in the shell to the actual external absolute dataset directory. The existing safe
root implementation is retained: relative manifest entries, absolute configured directory, path traversal/ADS/
symlink/junction escape rejection. No machine-specific path is hardcoded in repository code or persisted settings.

For a NEW manifest/report destination (existing files are deliberately preserved):

```powershell
$env:OLID_DATA_ROOT = $YourAbsoluteDatasetDirectory
python -m pip install openpyxl
python src/validate_olid.py --workbook $YourSpreadsheetPath --manifest $NewManifestPath --report-dir $NewReportDirectory
python -I tests/run_tests.py
```

Pillow is also required (already a project dependency). The actual audit used the available bundled Python 3.12
runtime with Pillow/openpyxl. Contracts were executed under installed Python 3.14.3. No dependency installation
or model-runtime availability is implied by these commands. Manifest/report outputs are not committed.

## Executed checks

- New inventory/quarantine/group contracts: 11 passed.
- External-root tests: 14 passed, 1 symlink test skipped due to Windows privilege. Windows junction escape passed.
- Existing research input contracts: 20 passed.
- Existing reconciliation checks: 32 passed.
- Existing saved-prediction checks: 7 passed (historical CSVs, not new model inference).
- Syntax compilation and git diff whitespace checks: passed.
- Historical hash audit: FAILED, 24 expected historical artifacts absent; 2 metadata files unchanged, 0 changed.
- Torch/checkpoint inference integration: SKIPPED because torch is not installed in the test interpreter.
- Therefore the overall existing test runner exits 1. It is not reported as a fully passing suite.

## Remaining blockers

Obtain reliable physical capture grouping evidence before splitting or strict model-data loading. Ask the source
authors or an appropriate expert to adjudicate all five conflicting-label pairs; retain quarantine until then.
Independent diagnostic verification has not been performed. Review near-duplicates and split design only after
group metadata is available. Missing historical artifacts/ML dependencies still limit unrelated integration tests.
No research-ready, model-performance or publication-readiness claim is made.
