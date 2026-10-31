# Repository audit — 31 October 2026

Audited baseline a64fc6aeb4c8aa008f7a4febfed5dbed6c8b4599. Source: actual local checkout of
mohitgupta2006-create/Plant-Modell on existing fix/olid-data-loading. Upstream is read-only.
The manuscript and evaluation PDF were not supplied. This audit uses only the pasted master prompt's concerns.

| Component | Existing implementation inspected | Revision / remaining evidence |
|---|---|---|
| Architecture | src/model.py: EfficientNet-B0, optional 4→32→32 environmental MLP, 5 parallel heads | Backbone preserved; cause-first gated decoder for new checkpoints and flat condition-only comparison |
| PlantVillage | src/prepare_data.py PV_MAP and leaf-map lookup | Existing aliases preserved; no raw images available for visual validation |
| PlantDoc | PD_MAP, excluded ambiguous labels, train/test pooling | Already integrated; re-split by groups, NOT untouched official PlantDoc test evaluation |
| OLID I | No ingestion; unhealthy labels always Biotic | Optional manually reviewed manifest ingestion; explicit N/NK cause mapping; actual loading BLOCKED by absent data |
| Splits | src/split_data.py: leaf IDs, MD5 and pHash union-find, stratified 20 folds | Existing split files preserved; distribution/field-cause eligibility audit added; not source-held-out |
| Training | src/train.py: AdamW, cosine decay, AMP, early stop, inverse condition frequency weighting | Revised runs isolated; missing severity masked; one-class cause masked; image-only does not require env/severity CSV |
| Environment | src/env_features.py: crop-dependent baselines and path-seeded noise | Historical script retained as explicitly simulated; normal training uses real pairing or image-only placeholders |
| Severity | src/severity.py: heuristic GrabCut/HSV damage ratio; experiments/severity_v2 | Not expert ground truth; reviewed masks/threshold-policy/annotator agreement workflow added; severity training BLOCKED |
| Evaluation | src/evaluate.py: group bootstrap, confusion, lab/field comparison | Historical evaluator retained; new research_evaluate.py separates new outputs and reports abstentions |
| Source controls | src/sanity.py: blurred thumbnails and border probes, nearest pHash check | New condition-matched tomato source control supplements existing generic probe |
| Explainability | infer.GradCAM, explain.py, environment permutation | Explicit stage/target selection added to predictor; SHAP/LIME on real environment BLOCKED |
| Inference | predict.py default image model; reconcile.py condition-first legacy reconciliation | Legacy decoder remains compatible; checkpoint-local new metadata supports deficiency labels; no validated severity displayed |
| Artifacts | logs/, outputs/, models/* metadata/history exist | No .pt/.pth checkpoints or raw/processed datasets present in this clone |
| Requirements | Pinned requirements.txt and HOW_TO_RUN.md inspected | No dependency versions changed; available interpreter Python 3.14.3 lacks torch; original pinned environment not validated here |

The data design in the master prompt is tomato-only (18,160 + 544 planned images). Existing recorded execution
instead covers 8 crops, 27 conditions, with 22,081 PlantVillage + 1,478 PlantDoc images. These are historical log
counts, not current raw-data counts or a reproduced experiment. No manuscripts were edited or fabricated.
