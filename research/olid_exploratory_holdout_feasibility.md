# Conservative exploratory OLID holdout: feasibility assessment

> Follow-up: all 59 crossing distance-8 candidates have now been screened. Fourteen direct candidates
> were removed on content evidence and 45 remain unresolved. The exploratory holdout remains BLOCKED.
> See [the bounded pair review](olid_distance8_crossing_review.md) and its per-pair evidence table.
> The assessment below records the earlier, unadjudicated sensitivity analysis.

## Decision

No defensible draft split manifest is issued under the declared conservative policy. A distance-6 mathematical
allocation passed support/known-link checks, but failed the wider, unresolved distance-8 sensitivity screen.
Its provisional CSV was withdrawn from deliverable outputs and retained only as a rejected audit artifact.
The final offline tool emitted NO draft manifest. Strict plant-wise splitting remains BLOCKED.

This is not proof that all possible exploratory studies are impossible. Distance 8 is an analysis-time conservative
sensitivity choice, not a scientifically validated boundary between duplicate and independent images. The new
links are unresolved candidates, not confirmed leakage or physical identities. Under the requested policy of
retaining unresolved relationships, they cannot simply be discarded to obtain a more convenient allocation.

## Protocol and operational acceptance criteria

The assessment uses the existing component review decisions: no retained link is cut, no source label changes,
and no disputed image is admitted. All 798 records enter the connectivity audit, including source-only records
and the ten quarantined records as CONTEXT ONLY. Exact duplicate content is unioned as well as saved pHash
links. Only the 318 active Healthy/N/NK records could be candidate model examples; quarantine/context rows are
never allocated as examples. Content components are never written as plant IDs or capture-group evidence.

Declared pilot support floors were chosen within this analysis before training or performance observation;
they are operational design choices, not externally preregistered or universal statistical sufficiency criteria:

- Training: >=60 Healthy and >=15 each N/NK; >=20 Healthy and >=3 N/NK provisional content components.
- Validation: >=15 Healthy, >=5 N, >=5 NK, in distinct provisional components within each class.
- Test: >=30 Healthy, >=15 N, >=15 NK, in distinct provisional components within each class.
- Heldouts draw from components containing one target record and no quarantine records. All unresolved
  multi-target or quarantine-connected components stay wholly in development or are excluded from evaluation.
- One deterministic order (seed 42, content-component hash order), no model outputs, accuracy-driven seed
  selection, oversampling, or ratio-driven component breaking. Output is draft-only proposed_partition, not split.

The finite quota search varied N/NK test targets over 6, 10, 12, 15 and 20 with fixed validation and Healthy quotas.
This is a stated search family, not a claim of exhaustive combinatorial search over every possible protocol.

## Actual baseline allocations examined

Counts below are image counts in Healthy / N / NK order. No model was trained on any proposal.

| N/NK test target | Train H / N / NK | Validation H / N / NK | Test H / N / NK | Disposition |
|---|---|---|---|---|
| 6 | 191 / 31 / 29 | 15 / 5 / 5 | 30 / 6 / 6 | Rejected: minority test support below the declared floor. |
| 10 | 191 / 27 / 25 | 15 / 5 / 5 | 30 / 10 / 10 | Rejected: minority test support below the declared floor. |
| 12 | 191 / 25 / 23 | 15 / 5 / 5 | 30 / 12 / 12 | Rejected: minority test support below the declared floor. |
| 15 | 191 / 22 / 20 | 15 / 5 / 5 | 30 / 15 / 15 | Support and distance-6 graph checks pass; REJECTED by wider unresolved-link sensitivity. |
| 20 | Not allocated | Requested 15 / 5 / 5 | Requested 30 / 20 / 20 | Rejected: only 20 eligible N components, but 25 needed for validation+test. |

The baseline 15-case proposal contained 233 train, 25 validation and 60 test images. Its largest 115-target
component (85 H, 19 N, 11 NK) stayed entirely in development. No saved distance<=6 relationship crossed its
partitions, even through source-only/quarantine context. The 22 training N images represented only four
content components, with 19 in one component: image counts overstate development diversity.

## Source-only bridge negative control

A target-only construction produced the SAME apparent class counts as the baseline 15-case proposal but was
rejected against the complete graph: three full-corpus components crossed partitions, including an unresolved
quarantine-connected component. Adequate-looking class counts alone therefore do not validate a holdout.

## Wider unresolved-link sensitivity

The saved distance-6 diagnostic graph was recomputed from all original default image frames and reproduced
exactly. The same diagnostic DCT pHash was then evaluated at distance<=8, a sensitivity threshold already
considered in the preceding evidence audit. This is not an equivalence test of the repository ImageHash package.
All wider-screen candidates were conservatively retained; none was declared a confirmed duplicate or a plant ID.

| Diagnostic graph | Target-containing components | Largest target component H / N / NK | Direct target links crossing baseline proposal | Full components crossing proposal |
|---|---:|---|---:|---:|
| <= 6 | 160 | 85 / 19 / 11 | 0 | 0 |
| <= 8 | 72 | 179 / 33 / 20 | 59 | 4 |

The 59 distance-8 crossing pairs are exported for targeted review. They are reasons to withhold acceptance while
unresolved, not proof that 59 actual duplicated captures exist. Shared backgrounds/silhouettes can create false
positives; a documented review could potentially reject some links later. Dropping them merely because they
prevent a convenient allocation would not be a defensible resolution.

### Necessary-count infeasibility bound under the conservative graph

The 232-target component contains 33 of all 42 N images, leaving only nine N images outside it. Keeping it atomic:

| Giant component disposition | N images required outside it | Available outside | Result |
|---|---:|---:|---|
| Training/development | 5 validation + 15 test = 20 | 9 | Insufficient |
| Validation | 15 training + 15 test = 30 | 9 | Insufficient |
| Test | 15 training + 5 validation = 20 | 9 | Insufficient |
| Excluded entirely | 15 training + 5 validation + 15 test = 35 | 9 | Insufficient |

This count bound rules out any intact-component allocation satisfying those support floors, not just the
implemented single-target holdout search. Seeds cannot repair it. With the component in development and five N
cases reserved for validation, at most four N cases remain for testing; one error would move recall by 25 points.
That is rejected as too fragile for the proposed exploratory metric report. No source labels were changed.

## Are 15 minority test cases sufficient?

They would allow coarse descriptive metrics with a 6.67-percentage-point recall step per error, not precise model
comparisons or biological generalization. As a hypothetical precision illustration ONLY, under an independent
Bernoulli assumption, 7 correct out of 15 gives a Wilson 95% interval about 24.8%-69.9%; even 15/15 gives a lower
bound about 79.6%. These are not model results, and biological independence has NOT been established here.
Five validation examples per deficiency are also too fragile for extensive hyperparameter selection.

Thus the operational floor is deliberately modest and does not establish statistical adequacy. The actual
conservative graph cannot even satisfy that floor. Class-balanced test quotas also select a different population
from OLID's original 236/42/40 target distribution; aggregate accuracy would not estimate full-dataset prevalence
performance. The development-only giant components further restrict what any future test could represent.

## Artifacts, safeguards and reproducibility

research/tools/assess_olid_holdout.py is an isolated OFFLINE feasibility tool. It does not modify src/train.py,
src/split_data.py, capture-group gates, labels, manifests or checkpoints. It emits a draft only when support and
the supplied conservative graph both pass. Here no draft was emitted. Input fingerprints are recorded in the local
feasibility JSON; local paths and per-image proposal records are not committed.

```powershell
$env:OLID_DATA_ROOT = $YourAbsoluteDatasetDirectory
python research/tools/assess_olid_holdout.py --manifest $SourceManifest --similarity-links $ReviewedDistance6Links --conservative-links $CompleteDistance8Links --reviewed-links $ReviewDecisions --out $NewOutputDirectory
python -I tests/test_exploratory_holdout.py
python -I tests/run_tests.py
```

The supplied graphs must be complete frozen diagnostic outputs for the inventory; the tool checks that the
stress graph retains all baseline links and fingerprints its inputs. In this run completeness/method consistency
was additionally checked by recomputing all 798 hashes before supplying the graphs. Do not substitute a hand-picked
edge subset or present this tool as a production splitter. No speculative plant/session evidence is generated.

## Actual verification

- Source manifest/file SHA256 inventory validation passed; source manifest remained byte-for-byte unchanged.
- Ten quarantined records remain excluded and labels/unknown physical identities are unchanged.
- All exact and saved similarity relationships across both parts and source-only/quarantine contexts were retained.
- The target-only negative control failed the full-corpus bridge check as intended.
- The distance-6 graph was reproduced; distance-8 stress rejected the otherwise count-feasible proposal.
- Final no-draft assertion passed: no accepted draft CSV exists in the final output directory.
- New feasibility tests: 13 passed, covering intact groups, hidden bridges, quarantine, low support, review
  coverage, conservative infeasibility, determinism and unchanged unknown metadata.
- Existing tests: inventory 11 passed; roots 14 passed/1 symlink test skipped; research contracts 20 passed;
  reconciliation 32 passed; saved-prediction checks 7 passed. Syntax and whitespace checks passed.
- Full runner still exits 1: historical hash audit has 24 expected artifacts missing (0 changed), and torch
  inference integration is skipped because torch is unavailable. No full-suite success is claimed.

## What could change this decision without fabricating metadata?

Review the wider-screen crossing candidates and critical source-only bridges using explicit image-content
evidence, not diagnoses or desired split counts. Reject an edge only with documented support; retain or exclude
remaining unresolved connected units. Lock that revised graph and rerun the same support/bridge checks.
Alternatively obtain additional appropriately documented images for a genuinely separate exploratory cohort.
Neither route requires inventing plant IDs, but neither has been completed here. Lowering the content threshold
or sample floor after seeing this failure must be a separately justified protocol change, not a silent workaround.

Current conclusion: a conditional distance-6 mathematical pilot exists, but a conservatively robust limited pilot
is NOT yet defensible under the inspected evidence and stated support policy. Strict plant-wise splitting stays
BLOCKED, and no exploratory result could establish biological independence even if future content-only checks pass.
