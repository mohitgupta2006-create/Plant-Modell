# Reviewer response work log — not a final rebuttal

Based only on explicit master-prompt concerns, not an unseen report. No concern is silently marked complete.

| Reviewer concern | Status | Implementation / remaining limitation |
|---|---|---|
| Missing experimental results | PARTIALLY FIXED | Separate evaluator, seeded/flat/lab-only run options and commands; raw data, checkpoints and torch absent. No new metrics. |
| Dataset-source confounding | PARTIALLY FIXED | Reviewed OLID ingestion, explicit cause labels, distribution/coverage audit, common-condition source probe, reviewed-mask intervention. Data/source independence unverified. |
| Simulated environmental features | PARTIALLY FIXED | Revised training requires real exact path/location/date pairing; image-only independent of env.csv; legacy --all blocked. Real paired measurements absent. |
| Missing severity ground truth | BLOCKED | Reviewed binary masks, policy provenance and multi-annotator kappa tooling added. No reviewed annotations/adjudication/scientific thresholds; severity masked. |
| Title/scope mismatch | BLOCKED | Scope/title recommendation in manuscript guide; original manuscript absent. |
| Unsupported novelty | BLOCKED | Guide limits claims to implemented comparisons; comparisons not executed. |
| Missing architecture diagram | PARTIALLY FIXED | Mermaid diagram in guide reflects shared backbone and parallel heads with conditional decoding; manuscript insertion pending. |
| Training/methodological details | PARTIALLY FIXED | Protocol records losses/weights/hyperparameters and checkpoint isolation. Actual hardware and experiments unavailable. |
| Dataset imbalance | PARTIALLY FIXED | Existing train-only condition weighting retained; distributions and support metrics exported from real manifests only; actual data absent. |
| Hierarchical consistency | PARTIALLY FIXED | Legacy regression preserved; new checkpoint-specific health/cause gating, metadata, abstention and severity suppression tested. Torch training/inference untested. |
| Writing/repetition | BLOCKED | Section guide supplied; no manuscript for line edits. |
| Reference inconsistencies | BLOCKED | No bibliography/evaluation PDF; no citations invented. |
| Broken tables/presentation | BLOCKED | New outputs separated; no manuscript tables/layout to verify. |
| Affiliations/publication declarations | BLOCKED | Guide lists required declarations; author identities, institutions and policies not supplied. |

Evidence: repository_audit.md lists inspected files; tests/test_research_inputs.py covers input contracts,
cause mapping, leakage, masks, agreement and new hierarchy. Existing tests/test_reconcile.py and
test_saved_predictions.py cover backward compatibility on saved outputs. See results_summary.md for actual results.
All rows requiring model execution remain unverified until raw datasets/checkpoints/dependencies are supplied.
