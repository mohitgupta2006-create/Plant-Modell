# OLID image-content similarity review and draft holdout protocol

## Finding and scope

The saved diagnostic pHash<=6 graph for 318 active target candidates has 207 links, 186 connected components,
25 multi-image components and 161 isolated vertices. All 25 multi-image components were visually screened on
contact sheets. All 67 cross-label links were additionally screened side-by-side. Within-label links were reviewed
at component level, not all individually adjudicated. Singletons were only checked for graph isolation.

This is AI-assisted image-content screening with source labels visible, not an independent/blinded expert review,
diagnostic verification, or proof of physical plant identity. No model training, split assignment or permissive
splitter was implemented. Strict physical-group requirements remain BLOCKED.

## Contact-sheet and evidence artifacts

Generated locally: four pages for the 74-image component; individual sheets for all multi-image components;
four consolidated small-component pages; six cross-label pair pages covering all 67 links; and a larger C025
comparison. The local contact_sheets.zip contains preview derivatives only, not original source images. No image
or review CSV was committed. link_review_decisions.csv has all 207 links with relative paths, source hashes,
distance, review level, evidence sheet, uncertainty and disposition. group_review_decisions.csv covers all 186
components, including the 161 unreviewed isolated vertices. Node IDs I001 etc are contact-sheet references,
not specimen/plant IDs. Component IDs C001 etc are image-similarity graph references only.

The saved analysis used a separately implemented 64-bit grayscale DCT pHash on a 32x32 resize, with the low 8x8
block thresholded above its median including DC. It was not a runtime equivalence test of the repository's
ImageHash implementation. These candidate links are not authenticated near-duplicate relationships.

## Exact content, visual similarity and unresolved relationships

- Zero byte-identical pairs exist among these 318 candidates. The five original conflicting-label pairs remain
  outside this cohort as ten unchanged quarantined records.
- Full default-frame RGB pixel hashes, including dimensions, found zero pixel-identical groups among the 318.
- C025 (healthy 38/40) has especially similar composition, vein pattern and stem/background layout. Larger
  previews were reviewed. The originals are not pixel-identical; mean absolute channel difference without
  alignment is 18.29/255. Common capture or derivation is not established. Keep together conservatively.
- The other distance-zero pHash pair (healthy 205/210 in C005) is also not pixel-identical; its mean absolute
  channel difference is 24.49/255. Equal pHash does not establish equal content or specimen identity.
- Many components contain visibly different outlines, stems, folds, orientations and colours against a shared
  dark background. Such low-frequency resemblance is not sufficient to call a duplicate family.
- No cross-label link was promoted to a confirmed duplicate or diagnosis error. All source labels remain intact.
  All 25 multi-image components retain unresolved origin/relationship status and stay atomic in the draft graph;
  alternatively, exclude the entire uncertain component from a future evaluation cohort. No link was silently cut.

## Group-level review register

H=source healthy, N=source nitrogen deficiency, NK=source combined nitrogen-potassium deficiency.
Every multi-image group below was contact-sheet screened. Disposition for each is retain atomic component or
exclude the whole component from evaluation; no physical identity claim is made.

| Component | Images | H / N / NK | Links / cross-label links | Visual evidence and remaining uncertainty |
|---|---:|---|---|---|
| C001 | 74 | 53 / 13 / 8 | 134 / 45 | Heterogeneous lobed and oval outlines, different stems, folds, colours and positions; transitive silhouette/background links do not establish a duplicate family. |
| C002 | 7 | 6 / 1 / 0 | 7 / 1 | Mixture of upright lobed and diagonal narrow leaves; visible orientation and outline differences. |
| C003 | 6 | 5 / 0 / 1 | 5 / 1 | Upright NK image and differently oriented healthy outlines; shared low-frequency shape is insufficient evidence of duplicate capture. |
| C004 | 6 | 5 / 0 / 1 | 8 / 4 | Lobed and oval outlines with differing stems and folds; heterogeneous content. |
| C005 | 5 | 4 / 1 / 0 | 7 / 2 | One upright lobed N image and four diagonal narrow healthy images. Healthy 205/210 have equal pHash but nonidentical pixels; origin unresolved. |
| C006 | 5 | 3 / 1 / 1 | 5 / 4 | Lobed upright images mixed with heart-like outline; texture, colour and folding differ. |
| C007 | 5 | 4 / 1 / 0 | 6 / 3 | Diagonal elongated silhouettes resemble one another, but tips, stems and outlines differ. |
| C008 | 5 | 5 / 0 / 0 | 4 / 0 | Different lobed/oval healthy silhouettes; similar central placement on dark cloth. |
| C009 | 4 | 3 / 1 / 0 | 4 / 2 | Upright lobed shapes; stem, venation and leaf-edge differences remain visible. |
| C010 | 4 | 2 / 1 / 1 | 3 / 3 | Three labels; leaf size, colour and folding differ. Cross-label similarity is not a diagnosis correction. |
| C011 | 4 | 4 / 0 / 0 | 4 / 0 | Similar upright silhouette with different folds, stems and visible veins. |
| C012 | 3 | 2 / 0 / 1 | 2 / 1 | Different orientations and outlines; no confirmed common capture. |
| C013 | 3 | 3 / 0 / 0 | 3 / 0 | Similar general outline but different margins and texture. |
| C014 | 3 | 3 / 0 / 0 | 3 / 0 | Lobed and oval/curled outlines; heterogeneous content. |
| C015 | 3 | 3 / 0 / 0 | 2 / 0 | Diagonal elongated leaves with different tips and stems. |
| C016 | 2 | 0 / 0 / 2 | 1 / 0 | Broad lobed NK image versus narrow NK image; silhouette collision candidate, not confirmed duplicate. |
| C017 | 2 | 1 / 0 / 1 | 1 / 1 | Bright lobed NK outline versus healthy oval outline; source labels retained. |
| C018 | 2 | 2 / 0 / 0 | 1 / 0 | Narrow diagonal silhouettes with differing stem/edge details. |
| C019 | 2 | 2 / 0 / 0 | 1 / 0 | Similar oval silhouette and veins, with different outline/position details; common origin not verified. |
| C020 | 2 | 2 / 0 / 0 | 1 / 0 | Curled/lobed silhouettes with visible fold differences. |
| C021 | 2 | 2 / 0 / 0 | 1 / 0 | Diagonal silhouettes with different outlines and stem lengths. |
| C022 | 2 | 2 / 0 / 0 | 1 / 0 | Lobed upright shapes; stem, margin and folding differences. |
| C023 | 2 | 2 / 0 / 0 | 1 / 0 | Different lobes and stems despite similar upright placement. |
| C024 | 2 | 2 / 0 / 0 | 1 / 0 | Similar pointed upright outlines but different curling and venation details. |
| C025 | 2 | 2 / 0 / 0 | 1 / 0 | Especially similar vein pattern, stem and composition in healthy 38/40; larger detail sheet reviewed. Pixels differ; possible near-duplicate content, not confirmed common capture. |

### Priority component C001

C001 has 74 images (53 H, 13 N, 8 NK), 134 candidate links and 45 cross-label links. Four contact sheets show
heterogeneous leaf contours, sizes, colour and folding, linked transitively through shared silhouette/position.
It is not a confirmed 74-image duplicate set. The conservative draft retains the entire unresolved component;
splitting it opportunistically to fit a ratio would undercut the proposed content-leakage control.

It occupies 23.3% of the target cohort and contains 31.0% of N examples and 20.0% of NK examples. A nominal
15% holdout is about 48 images; placing C001 in it already exceeds that budget. Placing it entirely in development
is arithmetically possible but changes the distribution represented by the holdout; that choice needs predefinition.

### Cross-pool bridge warning

As a structural check only, saved nonquarantined-inventory links were projected onto the 318 targets, allowing
paths through source-only images. Target component count falls from 186 to 160; the largest projected target
component grows to 115 (85 H, 19 N, 11 NK). Non-target bridge images were not visually adjudicated in this task.
Those additional relationships therefore remain unresolved and must be conservatively retained or reviewed
before a target-only graph can support an evaluation design. The target-only counts are not final independent units.

## Imbalance and feasibility assessment

These are descriptive cohort scenarios, NOT generated train/test partitions or adopted exclusions. Group counts
below refer to the target-only graph and do not establish physical independence.

| Scenario | Images | Provisional components | Healthy | N | NK | Largest/smallest class ratio |
|---|---:|---:|---:|---:|---:|---:|
| Retain all targets | 318 | 186 | 236 | 42 | 40 | 5.90 |
| Exclude entire C001 | 244 | 185 | 183 | 29 | 32 | 6.31 |
| Exclude every cross-label component | 197 | 175 | 148 | 23 | 26 | 6.43 |
| Only graph-isolated targets | 161 | 161 | 114 | 23 | 24 | 4.96 |

All scenarios retain each source class, so grouping does not arithmetically erase a class or prove that all pilot
evaluation is impossible. However, even the full cohort has only 42 N and 40 NK cases: a nominal 15% test set
would contain about six cases per deficiency before component constraints. A single classification change could
shift recall by about 17 percentage points at that support. Excluding uncertain groups further reduces support
and changes the evaluation population. Singletons-only selection does NOT certify plant independence.

Conclusion: a narrowly described exploratory pilot may be conceivable after bridge review and prespecified
precision/cohort decisions, but a defensible representative holdout has NOT been finalized. Current evidence
does not support a precise publication-level performance claim or a plant-wise evaluation. No feasibility of an
exact 70/15/15 or 20-fold arrangement has been demonstrated.

## Draft image-content-cluster holdout protocol (not executable authorization)

1. Freeze a hash-addressed inventory, current labels and the ten-record quarantine. Cluster original images before
   augmentations; derived versions must stay with their original. Do not infer plant IDs from this process.
2. Retain unresolved candidate relationships conservatively. Start with whole C001-C025 components. Review
   source-only bridges across the complete development/evaluation corpus; merge unresolved connected content
   groups across that corpus. Record every accepted/rejected edge and reason. No cross-label relabeling occurs.
3. Define the scientific cohort and a precision/sample-support requirement BEFORE selecting held-out cases.
   Record giant-component policy in advance: keep atomic or exclude the entire component from the evaluation
   population. If an evaluation exclusion has connections to development data, retain the full connected unit
   in development or exclude that unit entirely; never release linked members across partitions.
4. Only if the separate exploratory methodology is formally adopted, allocate whole reviewed content components
   once using a prespecified seed/procedure, preserving class support where feasible. Do not break components,
   oversample held-out cases or try seeds until performance improves. Block metrics whose required support or
   precision cannot be achieved. This task creates no partition or permissive code path.
5. Use training/validation only for model choice, thresholds and preprocessing choices. Reserve an untouched
   test cohort for the final descriptive comparison. Predefine sensitivity analyses for candidate-link thresholds
   and ambiguous-link decisions instead of choosing the best test outcome.
6. Report per-class precision/recall/F1/support, macro measures and full component/source counts, with all cohort
   exclusions. Repeated-seed variation and cluster-bootstrap intervals are conditional on provisional clusters;
   they cannot establish unknown biological independence or guarantee correctly calibrated uncertainty.
7. Describe any result as exploratory within-dataset image-content holdout. Do not claim plant-wise, leaf-wise,
   session-independent or leakage-free validation. Stronger evaluation needs authenticated specimen/capture
   mapping or a separately collected, tracked independent cohort.

The repository's strict capture-group gate remains unchanged and blocked. No provisional Cxxx identifier is
written to group_id/group_evidence or used to bypass that gate. No study result or train/test split is produced.

## Verification

- Real manifest/source SHA256 validation passed for the complete 798-record inventory before review bookkeeping.
- Artifact assertions passed: exactly 318 target paths, one component per path, 186 components, 207 recorded
  links, all links internal to their component, 67 cross-label screens, 25 multi-image group reviews, and referenced
  group contact sheets present. No exact decoded-pixel groups were found.
- The real strict capture-group guard remained blocked as expected.
- The manifest remains byte-for-byte unchanged; the original ten quarantined records and all source labels remain
  unchanged. No production/model/split code was edited in this task.
- This is a first-pass AI-assisted contact-sheet review. It is not a second-reviewer consensus or expert validation.
