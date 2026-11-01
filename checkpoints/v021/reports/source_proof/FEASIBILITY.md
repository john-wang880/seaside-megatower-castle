# v020 central bridge pier: duplicate surfaces, not an opening

Read-only source `work/v020/castle_v020.blend`, SHA256 `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`, unchanged. No render/model save/edit. The prior ring-articulation proposal is closed without prototype; this is a distinct conspicuous source-surface issue.

## Actual image correlation

Baseline `work/bridge_ring_feasibility_v020/visual/baseline/image.png`, original-light receipt alongside. Rays through black strip pixels(344,210),(344,350),(344,550),(350,700) all hit existing front limestone at Y34.8, normal(0,−1,0), not an opening/background. The widened black foot(350,775) hits existing ashlar atY34.3. Dark and adjacent lighter samples use the same material within each object; no black material slot is assigned.

Exact evaluated source corners show overlapping closed axis-aligned boxes:

| Pair | Component seeds | X intervals | Equal Y/Z extents | Material/slot |
|---|---|---|---|---|
| `V007 \| western stonework with actual bridgehead passage` |15882 /15956|[−41.5,−39.7] /[−40.3,−38.5]|Y34.8…41.2;Z6…26.4|`West_Cool weathered limestone`,0|
| `V012 \| legacy ashlar with buried-route clearance` |5144 /5152|[−41.925,−39.275] /[−40.725,−38.075]|Y34.3…41.7;Z5.7…8.1|`West_Ashlar stone variation`,0|

All four are8vertices/6faces with outward normals. Pier frontfaces11897/11938 duplicate12.2399686m² in X−40.3…−39.7; foot frontfaces3860/3866 duplicate3.4799935m² in X−40.725…−39.275. Both pairs also duplicate back/top/bottom surface strips and retain internal side faces. Their occupied intersections are78.335818m³ and25.751957m³, respectively. This is not a gap requiring an infill block.

The duplicated pier-front rectangle projects to roughlyX332…360,Y190…799 in the1200×866 baseline; foot duplicate projectsX329…373,Y740…813, aligning with the long narrow black strip and widened fork-like black foot. This makes coincident exposed surfaces a strong localized rendering-artifact diagnosis; exact elimination/cause must still be tested with an otherwise identical cleanup render, not assumed from geometry alone.

## Scope completeness and dependencies

`coplanar_scope.json` clips **all visible evaluated triangle faces** to the two union-front rectangles at actual Y planes (1e−5 coordinate tolerance, positive clipped area>1e−8). Only the four listed frontfaces contribute: no enclosing bridge-body/other ornament face adds a third coplanar layer there. This does not certify every back/top surface or whole bridge.

`probe.json` records exact source IDs, all four component corners/faces, actual pixel-ray hit chains and materials. Pier combined occupied volume is a single box X−41.5…−38.5,Y34.8…41.2,Z6…26.4. Plinth combined occupied volume is a single box X−41.925…−38.075,Y34.3…41.7,Z5.7…8.1. Equality of Y/Z bounds plus overlapping X intervals and exact8corner checks proves these unions analytically (`section_evidence.json`). Pier and plinth still intersect at Z6…8.1; their external relationship need not change. Existing arch bodies, intrados, trim legs, deck, terrain and foundation are unrelated preservation targets, not redesign candidates.

Right-hand dark line is **not automatically the same case**: its sampled ray hits an X-normal side of the neighboring pier atX−21.3 after traveling behind the front plane. Do not extend a central-overlap remedy to it without a separate justified scope. Apex notch is explicitly excluded.

Original pre-v002 construction generator is not present in the inspected historical script inventory; canonical file contains no embedded Text. Existing geometry's repeated per-span end-pier construction is consistent with assembled overlapping boxes, but authored intention cannot be claimed from naming. No intentional structural slot or load-capacity conclusion is supported.

## Minimal candidate, only after independent approval

Replace each pair's visible evaluated surface with its exact analytic box union, preserving occupied volume and all outer faces/coordinates/materials. Retain source records recoverably; no widening, filling an alleged void, new support, or arch intrusion. This four-component technical cleanup is bounded and has a specific practical visual target. Independent QA must verify occupied-set equality, exact non-target source/material preservation, no newly exposed coplanar duplicates, unchanged route/intrados and source hash. Same-camera actual before/after must confirm disappearance of the black artifacts without changing arch/bridge silhouette or lighting. No implementation has been done in this survey.
