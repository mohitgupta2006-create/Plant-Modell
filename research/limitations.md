# Remaining limitations

- Raw PlantVillage, PlantDoc and OLID I datasets, capture records, reviewed masks, real paired environmental
  measurements and .pt/.pth model checkpoints are absent in this clone. No new training or scientific experiment ran.
- Manuscript and evaluation PDF are absent; only explicit concerns in the master prompt were reviewed.
- Manifest flags are investigator attestations, not independent expert validation or evidence of correct diagnosis.
- Physical plant/session independence cannot be established from pHash/MD5 alone. Missing capture groups block OLID
  ingestion. Stratification does not remove dataset-source confounding; field examples from different sources retain bias.
- Heuristic damage labels are not ground truth. Severity training/evaluation remain blocked after annotation tooling.
- No scientifically justified threshold policy is provided. No environmental/date/location evidence is provided.
- New training/evaluation is not runtime validated with torch; syntax and lightweight contracts passed only.
- New cause-first decoder can abstain when predicted crop/health/cause has no supported condition. Conditional
  softmax confidences are uncalibrated and may increase after gating. No calibration is reused from legacy runs.
- Flat comparison, domain shift, stage-specific error files and foreground evaluation are implemented but unexecuted.
- SHAP/LIME, adjudicated severity training, expert interpretation and publication-specific edits remain blocked.
- Existing historical output metrics are retained, not reproduced; no publication-readiness claim is made.
