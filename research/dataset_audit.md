# Dataset audit and reviewed inputs

Current raw-data availability: BLOCKED. There is no data/raw or data/processed directory in this clone.
Physical images, labels, capture records, leaf masks, licenses/access records must be supplied by the investigator.
The planned 18,160/544 counts are not verified actual counts. logs/split_full.txt records historical mixed-source
counts: PlantVillage train 15,574 / val 3,249 / test 3,258; PlantDoc 1,061 / 211 / 206. OLID I absent.

## OLID manifest

CSV columns: path,condition,source,acquisition,label_verified,label_evidence,group_id,group_evidence,sha256.
By default, path identifies an existing image relative to the repository (normally ignored data/raw/olid_i/).
For an external dataset, explicitly set OLID_DATA_ROOT to an existing absolute dataset directory in the shell
running preparation. Do not commit a local path or credentials. Example using a user-supplied variable:

```powershell
$env:OLID_DATA_ROOT = $YourAbsoluteDatasetDirectory
python src/prepare_data.py --olid-manifest $YourReviewedManifestPath --out data/processed/index_reviewer.csv
```

With this setting, each manifest `path` is relative to OLID_DATA_ROOT, e.g. `tomato__N/<original filename>.JPG`.
The manifest location does not change the image root. Unset the environment variable to restore legacy
repository-relative behavior. Empty/relative/missing/file/filesystem-root configurations are rejected.
Manifest absolute paths, drive-relative paths, parent traversal, alternate data streams and resolved symlink/junction
escapes are rejected. Access remains confined to the explicitly selected root; do not configure a broad shared directory.
No dataset is copied. Preparation exports native absolute OLID image paths into the ignored local index when images
are external, so existing pathlib image readers can open them. These generated indices are machine-local: recreate
them when moving the dataset. This change does not add external-path support to independent annotation/source-control
tools that impose their own repository-only contracts. Other datasets and labels are unchanged.
Reviewed label evidence, capture-group evidence and SHA256 are still mandatory; the setting is not an ingestion bypass.
PlantVillage/PlantDoc are still required by the combined preparation command. No real ingestion is claimed without them.
source=OLID_I; acquisition=field; label_verified=true only after investigator inspection.
Use canonical conditions Tomato___N_Deficiency, Tomato___NK_Deficiency, Tomato___healthy ONLY where
dataset documentation/manual review actually supports them. These identifiers come from the master prompt;
they are NOT claims that the raw folders or diagnoses have been verified. No sample dataset records are provided.
label_evidence should identify original annotation, reviewer, and provenance; group_evidence identifies capture
records establishing shared leaf/plant/session identity. If those records are unavailable, ingestion stays BLOCKED
rather than guessing plant identity from filenames. sha256 must match the actual file bytes. Never label healthy Abiotic.

prepare_data.py appends reviewed records before label assignment, preserving original source/group/evidence/hash.
It still requires existing PlantVillage and PlantDoc inputs. It validates readability/minimum dimensions. Existing
index output is never overwritten. Full sampling retains field examples first within the configured condition cap;
inspect audit counts for any truncation. No oversampling is applied to validation/test.

## Splits and residual confounding

Existing MD5/pHash grouping remains. Condition stratification does not guarantee source/cause balance or physical
plant independence. Run audit_research_data.py on actual splits; require tomato FIELD Biotic AND Abiotic examples
in each split before the corresponding cause evaluation. Audit reports missing cells as BLOCKED.
Groups must remain intact across source duplicates. Near-duplicate threshold 6/64 is inherited, not revalidated here.
20-fold grouping requires sufficient independent groups/class. Small OLID strata may require a separately justified
split design; do not clone/oversample groups to satisfy counts.

PlantDoc tomato mapping already contains healthy and 8 disease/pest classes; Target_Spot has no PlantDoc mapping.
Images and labels have NOT been visually checked here. Web images, watermarks, crop framing and acquisition
practices can identify source even when both causes have field images. Common-condition source controls and
reviewed-mask interventions cannot alone establish source invariance. Seek independent sites/captures containing
both causes. Source-held-out testing is not valid for a cause absent from the held-out/training domain.

## Real environmental records

CSV: path,capture_location,capture_date,measurement_origin,measurement_evidence,units,temperature,rainfall,humidity,soil_moisture.
The split manifest must independently contain capture_location and ISO capture_date for EXACT matching.
measurement_origin=real; units=C;mm/day;RH%;VWC%. Document sensor calibration and observation window in evidence.
No generated weather, means imputation, label-derived values or nearest-date matching. Current images have no
verified capture dates/locations: all environmental experiments BLOCKED. Train-only normalization is checkpoint-local.

## Severity and leaf masks

Annotation CSV: path,annotator_id,leaf_mask,damage_mask,verified,review_evidence. Masks must be binary 0/255,
same image dimensions, damage entirely inside a nonempty leaf. Collect independent lesion/chlorosis masks from
at least two annotators, review segmentation, then adjudicate disagreements. Policy JSON must supply
thresholds_fraction (two ascending values), rationale, reference_or_protocol, preregistered_at. No default clinical
threshold is invented. Tool reports per-annotator affected fraction and pairwise quadratic Cohen kappa; undefined
kappa is null. Review/adjudication and scientific validation remain mandatory; training is deliberately blocked.
For background evaluation use path,leaf_mask,verified,review_evidence CSV; verify every test image's mask.
