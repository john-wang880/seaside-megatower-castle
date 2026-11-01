# Bounded coplanar-neighbor methodology correction

Status: corrected predicate and both native historical rechecks completed; the historical zero-adjacent-contact conclusions are superseded. No accepted model was edited.

The v024/v025 adjacent-surface scripts used `BVHTree.overlap` as a triangle broadphase. A current-source positive control proves that method can omit coplanar area: a known 140-unit² top-face overlap was absent from its candidate pairs. Consequently the historical adjacent reports do **not** establish absence of coplanar neighboring surfaces. Their original files and hashes are retained in `historical_inputs.json`.

The replacement filter explicitly considers overlapping triangle AABBs and all-vertex plane distance, then clips oriented polygons. Nine controls include the actual 140-area contact, same/opposite orientations, separated parallel planes, disjoint coplanar triangles with overlapping bounds, zero-area contact, and a separately labeled tolerance-only near-plane contact. Reported areas are pairwise, not union areas, and do not by themselves prove exposure or a newly introduced defect.

Recheck scope is one accepted v024 union plus four accepted v025 frame unions against actual evaluated render-visible neighboring surface meshes. Each model is pinned and unchanged; all its evaluated object bounds are used before culling. Results will distinguish same-facing duplicate candidates from opposite-facing interfaces. Existing occupied-boundary/volume, source-complement, rollback and negative-control proofs are separate and are not invalidated by this adjacency-filter limitation.

This correction is not a blanket statement about every use of BVH: the builders' strict transverse-crossing checks are differently scoped; v018 final finial clearance also has an independent full convex SAT test; v020 `gs.overlap` is a bounds helper rather than Blender BVH. No unrelated cleanup is authorized.

## Corrected findings and consequence

- v024 has same-facing contacts with unchanged ashlar (pairwise area0.8262736374, underside Z46.2000007629) and terrace ledges (767.2619807511, upward Z66.3000030518). These are different plane classes; the upper contacts cannot be dismissed as underside contacts.
- v025 has both same-facing and opposite-facing contacts for every return frame, chiefly with retained gallery geometry. Full per-object/plane records are in `plane_summary.json`; pairwise sums are **not** unique exposed areas.
- `v024_original_boundary.json` and `v025_original_boundary.json` link every affected saved triangle to its original independently clipped operand-union boundary; the separately bound source-preservation reports prove neighboring geometry unchanged. These are inherited contacts, not union enlargement.
- Actual recorded hero camera Z24, rear Z210, and v025 lateral Z180 were used, not assumed heights. Finite stratified rays found2 same-facing first-surface samples for v024 and53 for v025; all were inside the corresponding camera frame. Therefore remaining contacts cannot all be called buried. These counts are samples, not unique regions or pixels; they do not prove visible flicker or quantify its severity. No opposite-facing first-surface sample was found in this bounded sample set.
- Practical scope: previous targeted black-strip/frame cleanup remains supported by its occupied-boundary/source/actual-image evidence, but **zero neighboring coplanar surfaces** is withdrawn. Remaining inherited exposed contact candidates are explicitly deferred for visual prioritization, not automatically repaired or silently exempted. V026 is separately confined to its two mainshaft components.

The old reports/scripts and accepted models remain byte-exact. No renders, canonical saves, or publication occurred in this recheck.
