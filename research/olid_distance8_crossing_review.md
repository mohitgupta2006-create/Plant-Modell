# OLID I: review of the 59 distance-8 crossing candidates

## Decision: exploratory holdout remains BLOCKED

This bounded review concerns the 59 direct pHash distance-8 links crossing the previously rejected distance-6 allocation. It does not review or delete the other full-corpus relationships. No training, new split manifest, source-label change, identity inference or quarantine change was made. Strict plant-wise splitting remains BLOCKED because authoritative plant/leaf/capture-group evidence is unavailable.

The review is an AI-assisted image-content screen, not independent expert adjudication or diagnostic verification. Different-looking images are not evidence of different biological plants, leaves or capture sessions.

## Pair review and evidence

- Reviewed all 59 pairs (81 distinct real files) on eight labeled side-by-side contact sheets. Fourteen larger detail sheets are also supplied locally; the ledger specifies observations and original sheet references for every pair.
- SHA-256 of each reviewed file matched the source manifest. No byte-identical or default-RGB decoded-pixel-identical pair was found among these 59 candidates. This finding does not negate the five known conflicting-label exact pairs elsewhere in the inventory.
- No pair was confirmed as a clear near-duplicate with high confidence. This is not evidence that none exists. Forty-five pairs remain inconclusive and their links are retained.
- Fourteen direct content candidates were classified as visually similar but distinguishable using differences in the full blade contour, lateral incisions and leaflet/stalk structure. Different colour, source class, filename, EXIF date, background or file size was never sufficient to remove a link.
- A removed link means only that this direct photographic-match candidate was rejected in this screen. It makes no biological independence claim. A related specimen or acquisition session remains possible even for distinguishable photographs.

Removed direct candidates: R03, R04, R06, R07, R18, R20, R27, R35, R37, R39, R45, R49, R52, R56.

The complete review table is `olid_distance8_link_decisions.csv` in the repository and `review_decisions.csv` in the local deliverables. Each row includes both relative paths, SHA-256 values, source-provided labels, timestamps when available, exact-match checks, classification, decision, content explanation and sheet reference. All biological identities remain `unknown`. The original timestamp evidence remains contextual only; source labels are not independently verified diagnoses.

The local image-only sheets are `pair_page1.jpg` through `pair_page8.jpg`; the ZIP contains all eight pages and fourteen larger detail comparisons. They are excluded from Git. The rendered sheets were checked to contain all 118 nonblank image cells.

## Recalculated graph

| Quantity | Before this review | After this review |
| --- | ---: | ---: |
| Full-corpus distance <=8 edges | 2,949 | 2,935 |
| All-inventory content components | 212 | 215 |
| Components containing active targets | 72 | 75 |
| Largest component: active targets | 232 | 230 |
| Largest component: Healthy / Nitrogen / N+K | 179 / 33 / 20 | 177 / 33 / 20 |
| Direct links crossing the prior rejected proposal | 59 | 45 |

All 798 inventory records remain graph context: 318 active targets, 470 source-only records and ten quarantined records. All nonreviewed similarity edges, all baseline distance <=6 edges, all 207 earlier retained target links and exact-SHA unions remain intact. Source-only and quarantine bridge paths were retained; those records are never held-out examples. Ten of the fourteen removed edges still connect their endpoints transitively through other retained links. Four removed edges no longer do so; no physical identity is inferred from this change.

## Feasibility rerun

The existing offline assessor was rerun using the revised full-corpus graph and the unchanged earlier 207-link review. Its five predefined trial targets (minority test sizes 6, 10, 12, 15 and 20) all failed. The single-target/no-quarantine holdout rule yields only 44 eligible Healthy components, below the fixed 45 required for Healthy validation plus test. No thresholds, class floors, grouping safeguards or production loaders were relaxed.

There is a stronger, seed-independent Nitrogen count obstruction. The largest indivisible content component contains 33 Nitrogen images; only nine Nitrogen images remain outside it. With unchanged minimum Nitrogen support train=15, validation=5 and test=15:

- Largest component in train: validation plus test need 20 outside, but only nine exist.
- Largest component in validation: train plus test need 30 outside.
- Largest component in test: train plus validation need 20 outside.
- Largest component excluded: 35 are needed outside, but only nine exist.

Thus no intact allocation can meet these fixed count minima on the currently retained graph, even with a broader search or a different random seed. This is a conclusion about the current conservative protocol and evidence, not proof that every future exploratory protocol is impossible.

For reference, the prior distance-6 proposal remains invalid despite its nominal counts:

| Rejected proposal only | Healthy | Nitrogen | N+K |
| --- | ---: | ---: | ---: |
| Train | 191 | 22 | 20 |
| Validation | 15 | 5 | 5 |
| Test | 30 | 15 | 15 |

It still crosses three full-corpus components, including a quarantine-connected component, and has inadequate independent content-component support. Its 45 retained direct crossing links are listed locally in `remaining_cross_partition_candidates.csv`. It is not an accepted split and must not be used for training or evaluation.

## Actual validation

- Real inventory validation: 798 records accepted for inspection, including 318 active / 470 source-only / ten quarantined. This does not authorize ingestion for training.
- Existing offline feasibility CLI: completed successfully, rejected every trial, emitted no draft split manifest; its explicit capture-group check remains BLOCKED.
- `tests/test_exploratory_holdout.py`: 13 passed.
- `tests/test_olid_inventory.py`: 11 passed.
- `tests/test_olid_root.py`: 14 passed, one skipped (Windows symlink privilege unavailable).
- `tests/test_research_inputs.py`: 20 passed.
- Total relevant contracts: 58 passed, one skipped. The full unrelated artifact/checkpoint suite was not rerun for this documentation-only review.
- Source manifest SHA-256 is unchanged: `c3b66a80536cae2a7176248b094e7d5a169882a14950e6b25330150778997d37`. Consequently the ten quarantined rows, source labels and unknown identities are unchanged.

## Reproduction and provenance

Start from the complete saved all-files distance <=8 graph and the unchanged source manifest. Match the 59 candidate pairs by unordered relative-path pairs; require exact one-to-one review coverage, matching per-file hashes, active status, distance exactly eight and no byte/pixel equality before any removal. Remove only rows whose ledger decision is `remove_direct_content_candidate`; retain every other edge and all exact-content unions. Rebuild full-inventory components before considering targets. Rerun `research/tools/assess_olid_holdout.py` with the same baseline and earlier 207-link review, using the adjudicated graph as `--conservative-links`. The original production split gate is unchanged.

Input/output graph fingerprints:

These fingerprints identify the local audit files. Git may normalize line endings in the versioned CSV; its parsed rows remain identical.

- Original full graph (`all_distance8_links.csv`): `147463b578dc84b6a7dded5f1342166838e293fd0e615375c65e9d97004bdfb6`.
- New review ledger (`review_decisions.csv`, identical to the versioned decision table): `4a82a7aaa508c6c9ea15c5e3d0cc647090194cb65688ae7926ac06e01e0ae416`.
- Adjudicated graph (`adjudicated_distance8_links.csv`): `f067f4f439c527542182f5ca11a1fabb76b17e361c0a7398532b868385d145d8`.

Local machine-readable evidence includes `review_results.json`, `reassessment/feasibility_results.json` and `component_membership.csv`. Membership IDs represent image-content components only, never plants or capture groups. Contact sheets, full graph copies and membership exports are local artifacts, not committed datasets. The small versioned results summary and decision table preserve this bounded review without local absolute paths.

## Remaining evidence gap

Forty-five reviewed relationships remain unresolved, and other unreviewed full-corpus bridge relationships remain conservatively retained. Reliable further photographic provenance/adjudication would be needed to justify changing those relationships; relaxing the distance threshold or discarding links to make counts work is not evidence. Even resolving content ambiguity would not establish biological independence. Authoritative specimen/acquisition mappings would still be needed to unblock strict plant-wise splitting. No other reviewer issue is addressed here.
