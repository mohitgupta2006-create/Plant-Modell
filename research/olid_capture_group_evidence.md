# OLID I capture-group evidence and proposed evaluation protocol

## Status

Physical plant/leaf/session-group evidence is UNAVAILABLE in the checked release materials. Strict model-data
loading and group-based splitting remain BLOCKED. No new split, training, label correction or metadata substitution
was performed. All ten disputed records retain quarantine. The external manifest is byte-for-byte unchanged.

## Materials actually inspected

- [Original OLID I paper](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1251888/full),
  especially collection, labeling, and data-description sections. It describes acquisition procedures and both
  leaf surfaces, but does not supply a filename-to-physical-leaf/plant/session map.
- [Official Zenodo version 1.1.0 release](https://zenodo.org/records/8105154), including available file inventory.
  The release advertises crop archives and a class-count workbook, not an image-level capture log.
- The original tomato archives, previously verified against published MD5: 359 and 439 file entries respectively.
  This audit confirmed they contain only image files, no embedded CSV/JSON/XML capture ledger, and no ZIP comments.
- Extracted directories, filenames and the current 798-record inventory. The three external CSVs are generated
  manifests/backups, not independently supplied acquisition records.
- The supplied class_distribution.xlsx: one main_dataset sheet, 58 rows, four columns (Crop, Class Abbrv.,
  Class Full Form, Sample Size). It contains class totals, not physical specimen/capture IDs.
- Standard EXIF fields and EXIF/GPS IFDs of all 798 default image frames. Proprietary MakerNotes were detected
  but not decoded or treated as authenticated specimen records. No authors were contacted.

## Verified metadata findings

| Evidence | Observed result | What it establishes / does not establish |
|---|---|---|
| Folder structure | Seven class-labelled image folders | Source class membership; not specimen groups |
| Filenames | All 798 follow source-class plus numeric-suffix naming | Renamed file identifiers only; 207 suffix values recur across classes |
| Plant/leaf/session ledger | No such record found in checked archives/workbook/release | Physical grouping remains unknown; absence in checked files is not proof authors lack private records |
| ImageUniqueID / BodySerialNumber / LensSerialNumber | 0 images with these inspected standard fields | No standard per-image/device identifier useful for group provenance |
| Original capture timestamp field | Present in 735 images, absent in 63; 729 distinct timestamp strings | Source EXIF observations; not validated session boundaries or plant identity |
| GPS IFD | Present in 735 images | Location metadata exists; accuracy/site assignments were not independently verified; not plant identity |
| Make/Model | Present in 735 images, one distinct value for each | Common capture device description; cannot distinguish physical plants |
| Description/comment/XP title/keywords/subject | None found in inspected standard fields | No readable free-text specimen mapping in those fields |
| Opaque MakerNote | Present in 735 images | Unparsed proprietary data; an author-supported decoding/mapping may be investigated later |
| Manifest capture groups | unknown in all 798 records; zero nonempty group-evidence records | Current mandatory split contract cannot be satisfied |
| ZIP entry timestamps | Include dates different from embedded image dates | File/packaging metadata, not authenticated acquisition groups |

### Timestamp distribution: useful audit clue, not session identity

| EXIF original date | Images |
|---|---:|
| 2022-03-17 | 409 |
| 2022-08-16 | 286 |
| 2022-04-25 | 40 |
| Missing | 63 |

Dates are unevenly associated with source labels: all 207 leaf-miner files have one date, while all 200 mite files
have another. Other classes span dates and some have missing timestamps. Thus date holdouts can change class
support or measure a class/acquisition correlation rather than independent generalization. This observation does
not infer sessions or prove that one plant was or was not photographed on multiple dates. Missing timestamps
must not be backfilled from filenames, adjacent files, ZIP dates or source labels.

The canonical manifest's capture fields remain unknown because the EXIF observations have not been validated
as the acquisition ledger required by the protocol. Observed EXIF values are kept separately in the local audit.
The paper's inclusion of both leaf surfaces is a reason to request view/leaf mapping; it does not prove that every
specimen has multiple views, or identify which files share a specimen.

## Can duplicate grouping provide partial protection?

Yes, against repeated or visually similar image content. It cannot establish independent physical specimens,
sessions, sites or plants. A distinct leaf surface, different crop, lighting change or repeated plant can escape
perceptual detection; similar silhouettes on a dark background can also be falsely linked.

Existing src/split_data.py already combines MD5 and 64-bit pHash at Hamming distance <=6 AFTER enforcing the
OLID capture-group contract. This investigation did not remove that guard or produce synthetic capture IDs.
The five previously established SHA256 duplicate pairs remain quarantined; they are not rehabilitated as groups.

### Executed exploratory similarity diagnostic

The diagnostic used the original default RGB frame, converted to grayscale, resized to 32x32 with Lanczos,
unnormalized 2-D DCT-II, the low-frequency 8x8 block, and above-median bits including DC. No SciPy/ImageHash
package was available in the audit interpreter; this was a separately implemented diagnostic DCT pHash, not a
runtime equivalence test of the repository's ImageHash implementation. Results are unadjudicated similarity
candidates, NOT confirmed near-duplicates or physical capture groups. No threshold was selected using accuracy.

There are 788 nonquarantined inventory records, including the 318 healthy/N/NK target candidates. No exact-byte
duplicate pairs remain within either of these scopes. Candidate counts and transitive components were inspected
at several thresholds to expose how grouping assumptions affect the effective sample size.

| Scope | Threshold | Candidate pairs (nonidentical bytes) | Diagnostic components | Largest component |
|---|---:|---:|---:|---:|
| 788 nonquarantined records | 0 | 7 | 782 | 3 |
| 788 nonquarantined records | 2 | 61 | 743 | 7 |
| 788 nonquarantined records | 4 | 340 | 613 | 59 |
| 788 nonquarantined records | 6 | 1096 | 399 | 262 |
| 788 nonquarantined records | 8 | 2892 | 214 | 522 |
| 318 target candidates | 0 | 2 | 316 | 2 |
| 318 target candidates | 2 | 11 | 308 | 3 |
| 318 target candidates | 4 | 62 | 266 | 14 |
| 318 target candidates | 6 | 207 | 186 | 74 |
| 318 target candidates | 8 | 597 | 99 | 182 |

At threshold 6, the target-only diagnostic has 207 candidate pairs and a 74-image component. The full
nonquarantined pool has 1,096 candidate pairs and a 262-image component. Such large components require manual
review; blindly applying the inherited threshold is not a validated OLID grouping policy. Hash distance zero
is also not proof of identical image content or physical identity. The candidate CSV is only a review aid.

## Proposed alternative evaluation: limited exploratory claim, not a guard bypass

This is a proposed methodology only. It has NOT been implemented as a permissive splitter or executed. The
current strict pipeline remains blocked until its evidence contract is met.

1. Preserve the ten-record quarantine and original source labels. Freeze a content-hashed inventory before
   selecting evaluation cohorts. Keep generated augmentations, recompressions and derived crops with their source.
2. Review exact and candidate near-duplicate links across the whole available nonquarantined corpus, including
   source-only records and any additional datasets used later. Build conservative connected components of reviewed
   image-content relationships before filtering target classes; indirect links can cross otherwise excluded images.
   Use a separately named image-content cluster identifier, NEVER plant_id/leaf_id/capture_group evidence.
3. If a separate exploratory study is adopted, hold entire reviewed image-content components out together and
   document all component sizes, class support, excluded ambiguous links and thresholds in advance. Use only
   training/validation for fitting, threshold choice and checkpoint selection; inspect the final test once.
4. Characterize that result as within-dataset image-content-cluster holdout. Report sample/class/component support,
   per-class and macro metrics, and abstentions. Explicitly state that repeated plants, opposite leaf surfaces,
   sessions and sites may cross partitions despite this control. Do not call it plant-independent or leakage-free.
   Component-resampling intervals would be conditional on provisional clusters; they do not resolve unknown
   biological dependence. Seed variability is descriptive, not evidence that independence was achieved.
5. Report sensitivity across prespecified similarity thresholds and manual-review choices; do not choose the best
   test score. Infeasible/oversized components or insufficient minority-class support make a split unavailable,
   not grounds to break components. Do not assume a 20-fold/70:15:15 scheme is feasible for the effective groups.
6. Date-held-out analysis can be an additional acquisition-shift stress test on supported classes, with missing-date
   records explicitly handled and counts disclosed. A date is not an authenticated session and cannot certify
   plant independence. Do not construct session IDs from arbitrary time gaps or GPS rounding.
7. Prefer a prospectively collected, independently annotated test cohort with tracked physical plants/leaves,
   views, sites and sessions, disjoint from the development specimens. This is the appropriate basis for stronger
   biological or cross-acquisition generalization claims. No such cohort was supplied or evaluated here.

Similarity clustering is therefore defensible only as a stated partial content-leakage control, not a substitute
for the strict capture evidence required by this repository. This document does not authorize implementation
that bypasses that distinction.

## Exact evidence needed to unblock the strict protocol

Request from the original curators an image-level ledger keyed by original member path AND preferably SHA256,
with stable physical plant ID, leaf/specimen ID, view/orientation and parent-original relationships, plus capture
session/date/site records where available. It must explain ID scope and reuse, whether a leaf or plant appears
in several sessions/sites, and which fields are verified versus unknown. Supply the responsible curator or
record provenance, annotation/acquisition method and the coverage of the released images.

For plant-independent evaluation, all leaves/views/visits of the same plant must be held together. Reliable leaf
IDs alone support only a leaf-level claim, not plant independence. Reliable session IDs support an acquisition
holdout only; author evidence must address repeated specimens across sessions. Per-image unique identifiers,
device IDs or timestamps alone do not establish any of these disjointness claims.

If records cannot be recovered, leave strict splitting BLOCKED and state that limitation. The alternative is a
different, explicitly limited exploratory protocol or newly collected provenance-rich data—not invented IDs.

## Verification and unchanged state

- All 798 images inspected for the stated EXIF fields; both original ZIP inventories and the workbook structure inspected.
- The external manifest SHA256 was unchanged before/after the audit; all 798 group_id values remain unknown.
- All ten quarantined records remain quarantined and no labels were changed.
- The real target candidate records were passed to validate_olid_capture_groups: BLOCKED as expected.
- Existing capture/quarantine contract tests: 11/11 passed. No model test or training was started in this task.
- No split assignment, inferred identity field, GPS-derived site, or session ledger was written.
- Local metadata and candidate-pair CSVs are inspection artifacts only and are not committed.


## Additional XMP inspection

Eight images contained embedded XMP packets; all eight parsed successfully with XML entity/DOCTYPE declarations rejected. No identifier-like plant, leaf, specimen, session, burst, ID or UUID fields were found in those packets. ExifTool, exifread and piexif were unavailable; proprietary MakerNotes remain uninterpreted. No claim is made that private curator records or undocumented proprietary fields cannot exist. This limitation does not satisfy or relax the capture-group evidence requirement.
