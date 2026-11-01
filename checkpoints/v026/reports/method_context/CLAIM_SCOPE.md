# Coplanar broadphase limitation — read-only claim inventory

2026-11-01. Discovered before any v026 build: Blender BVHTree.overlap returned zero for a known positive-area coplanar shaft contact. A triangle-BVH overlap API is not a conservative all-coplanar candidate generator. Explicit evaluated triangle AABB and plane/polygon clipping, with known positive and negative controls, is required for that claim.

## Affected assurance
- `checkpoints/v024/qa/adjacent.py` and `checkpoints/v025/qa/adjacent.py`: source uses `ub.overlap(bv)` before actual plane/polygon checks. Their recorded zero adjacent positive-area contacts is limited by that missed-candidate method, not a universal exclusion proof. Independent replacement scans are pending; no new defect inferred solely from this method limitation.
- Actual individual-union occupied boundary/volume proofs, source preservation, actual visual comparisons and exact recovery are separate. These must not be discarded wholesale or retroactively represented as adjacency proofs.

## Other reviewed usages and distinct scope
- v024/v025 `reproduce/scripts/build.py` self-BVH scan explicitly tests strictly transverse crossings, not coplanar exclusion. Complete independent oriented boundary coverage separately checks missing/doubled surfaces. Do not conflate these predicates.
- v018 `scripts/build_western_cap.py` has a preliminary finial BVH check. Its independent `scripts/validate_geometry.py` lines48–60 uses full convex SAT face/edge-axis separation and treats mere touching as not-separated. Accepted finial exclusion therefore has an independent non-BVH basis; no reason to invalidate it from this specific discovery.
- v020 `gs.overlap` is an ordinary bounds helper, not `BVHTree.overlap`.

Frozen historical reports/scripts remain unchanged as evidence. Corrections must explicitly supersede the incomplete adjacency assurance, cite new reports and preserve old hashes; do not silently relabel the old result. No model mutation or new geometric cleanup is authorized by this inventory alone.

## First corrected result (classification still under review)
Accepted v024 has same-facing contacts: ashlar underside −Z atZ46.2000007629, pairwisearea0.8262736374; terrace-ledges UPPER +Z atZ66.3000030518, pairwisearea767.2619807511. These are distinct planes. Do not infer the upper contact is underside/hidden. Original source-boundary linkage and finite practical exposure remain under independent review; no new model edit from this finding alone.
