# Actual validation — 31 October 2026

No new training, full dataset loading, model accuracy experiment or model inference executed. No raw datasets,
reviewed OLID records, real environmental pairs, expert severity annotations or .pt checkpoints exist in this clone.
Available interpreter: Python 3.14.3 with NumPy, pandas and Pillow; torch absent. Pinned requirements not installed.

Executed so far:
- compileall src/tests: passed syntax compilation (not runtime ML validation).
- tests/test_research_inputs.py: 20/20 passed using explicitly synthetic temporary fixtures, never research data.
- Existing tests/test_reconcile.py: 32/32 passed.
- Existing tests/test_saved_predictions.py: 7/7 passed on committed historical prediction CSVs; no new inference.
- tests/check_hashes.py: FAILED: 26 expected files, 2 metadata files unchanged, 24 absent, 0 changed.
- tests/test_venv_inference.py: SKIPPED by runner because torch is unavailable.
- Full tests/run_tests.py: FAILED due to missing historical artifacts. Do not report full suite as passed.

Saved-prediction tests rechecked historical condition accuracy: image 0.967, fusion 0.969, on 3,464 recorded rows.
These numbers are derived from existing saved CSVs, not a reproduced training/evaluation experiment and do not
validate the new branch's cause-first decoder or any abiotic class. No new research accuracy is reported.

Six manuscript experiments plus source/background/flat comparisons: BLOCKED for real execution by absent inputs,
checkpoints and ML runtime. Severity and environmental validity additionally need investigator evidence.
