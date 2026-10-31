# Experimental protocol (implementation available, execution BLOCKED)

Use an isolated supported Python/PyTorch installation for this project; original pinned requirements are not
validated on Python 3.14. Install a mutually compatible PyTorch/torchvision build for the actual CPU/GPU and
remaining requirements. Do not change pins or claim installation success without checking it.

Commands below are from the repository root with the project interpreter named python. Input files are real
investigator-supplied records. Data files are ignored by Git. Choose unused output paths; never replace legacy tables.

```powershell
python -m pip install -r requirements.txt
python -I tests/run_tests.py
python src/prepare_data.py --olid-manifest data/raw/olid_i/manifest.csv --out data/processed/index_reviewer.csv
python src/split_data.py --index data/processed/index_reviewer.csv --out data/processed/splits.csv
python src/audit_research_data.py --splits data/processed/splits.csv --out research/generated/dataset_audit.json
python src/train.py --variant image --seed 42
python src/train.py --variant image --flat --seed 42
python src/train.py --variant image --lab-only --seed 42
python src/research_evaluate.py --run image_reviewer_seed42 --out research/generated/image_seed42
python src/research_evaluate.py --run image_reviewer_flat_seed42 --out research/generated/flat_seed42
python src/research_evaluate.py --run image_reviewer_lab_seed42 --out research/generated/lab_to_field_seed42
python src/research_source_control.py --splits data/processed/splits.csv --out research/generated/source_control.json
python src/research_evaluate.py --run image_reviewer_seed42 --masks data/annotations/test_leaf_masks.csv --out research/generated/masked_seed42
python src/prepare_real_env.py --splits data/processed/splits.csv --measurements data/measurements.csv --out data/processed/env_real.csv
python src/train.py --variant env --seed 42
python src/train.py --variant fusion --seed 42
python src/research_annotations.py --annotations data/annotations/masks.csv --policy data/annotations/threshold_policy.json --out research/generated/annotation_review.json
python src/predict.py --image YOUR_REAL_IMAGE_PATH --run image_reviewer_seed42 --cam-head condition
```

If splits.csv already exists, STOP: its original content must be retained. These instructions do not authorize
overwriting it. Establish a separate local research dataset workspace/configuration before switching the active
split manifest. New training hashes split/env inputs and refuses incompatible resumes; existing completed runs
are preserved. Never run legacy train --all: it is blocked because it generated synthetic/heuristic targets.

1. Image-only: primary valid baseline; health/crop/condition CE, cause CE only if both training causes exist,
   severity masked. One-class cause accuracy is not a meaningful result.
2. Environment-only: BLOCKED until exact location/date paired real measurements for every eligible image.
3. Fusion: same real pairing requirement; image-only comparison on identical groups is mandatory.
4. Lab-to-field: --lab-only trains/validates on lab acquisition; evaluation restricted to field. It cannot learn
   abiotic if lab training lacks deficiencies. Exclude field conditions absent from lab training and report the
   excluded count explicitly; report cause unavailable for one-class lab training. Report class support and source/crop mix; do not call it causal validation.
5. Tomato Disease/N/NK: evaluator requires all three unhealthy tomato field categories, retains other/abstain errors.
6. Severity: BLOCKED; annotation report is not adjudicated ground truth and no severity training switch is exposed.

Additional comparisons: --flat applies condition-only loss, compared with the same-backbone multi-task/cause-first
decoder. It is not a separately branched neural hierarchy. Evaluate raw versus gated predictions (saved CSV),
per-source metrics and abstentions. Strict unsupported branches abstain in evaluator and stop interactive prediction
with an explicit error. Healthy output has no disease/severity; unsupported severity is unavailable.

Source control uses common tomato conditions across ALL sources and train-only inverse source-condition weights;
if no overlapping conditions exist, BLOCKED rather than testing class/source correlation as source invariance.
Background evaluation replaces reviewed non-leaf pixels with neutral gray. Compare EXACT same test cohort/checkpoint
with and without masks. This is test-time intervention, not a retrained foreground-only model; mask errors remain.

Repeat seeds 42,1,2,3 on a fixed group split using the same commands; each seed uses its own reviewer folder.
research_evaluate reuses existing 1,000 group-bootstrap accuracy CIs when n>=30 and groups>=10. It also exports
macro-F1, per-class precision/recall/F1/support, balanced accuracy and confusion matrices. No unexecuted run gets a
result. Report mean/std and design before claiming seed repeatability; no new repetitions ran here.

Training defaults inherited from config.py: 224px, batch16, 8 epochs, seed42, AdamW head3e-4/backbone1e-4,
weight decay1e-4, label smoothing0.1, clipping1, patience3, cosine LR, AMP on CUDA. Loss weights are 1 for supported
crop/health/cause/condition and 0 severity; flat uses only condition. Inverse condition-frequency weights fit TRAIN
only. Actual device/config/input digest saved per checkpoint. Claimed RTX3050 in historical configuration is not
proof of the current machine. Record actual hardware before experiments. No checkpoints present here.

Grad-CAM: predictor --cam-head health/cause/condition selects displayed target class; unsupported cause skipped.
Masks/attention and CAM do not prove causal reasoning. SHAP/LIME for real environment remains BLOCKED; historical
permutation scripts operate on simulated features and cannot support agronomic claims.


## OLID capture-group evidence status

See [olid_capture_group_evidence.md](olid_capture_group_evidence.md). Readable EXIF timestamps/GPS were found
in 735/798 files, but no authoritative plant/leaf/session ledger was found in checked release materials. Strict
splitting remains blocked. The exploratory similarity-cluster protocol is a proposal only, with explicit unknown
biological dependence; no guard was relaxed and no split/training run was performed.
