# Independent central-pier surface cleanup proof

Accepted source SHA673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614 was loaded read-only. `PROOF.json` independently checks the actual evaluated vertices, all six face planes/outward normals, flat shading, material slots and exact box corners against the mapper's records. Fraction arithmetic proves each pair's occupied union is exactly one box; this is not a bounding-box approximation.

## Bounded replacement specification

1. V007 western stonework: hide only raw vertices15882–15889 and15956–15963 (16 vertices,12 complete faces). Replace their union with one closed8vertex/6face box bounded X[−41.5,−38.5], actual Y[34.79999923706055,41.20000076293945], Z[6,26.399999618530273]. Reuse existing `West_Cool weathered limestone`, DATA slot0, flat shading and identity world transform.
2. V012 legacy ashlar: hide only raw vertices5144–5159 (16 vertices,12 complete faces). Replace union with one closed8vertex/6face box bounded X[−41.92499923706055,−38.07500076293945], actual Y[34.29999923706055,41.70000076293945], Z[5.699999809265137,8.100000381469727]. Reuse existing `West_Ashlar stone variation`, DATA slot0, flat shading and identity transform.

Both source objects have one mesh user, no modifiers, vertex groups, existing weights, shape keys, parents, constraints or animation. Both material graphs explicitly feed Geometry.Position into Noise.Vector; neither uses Generated coordinates or Object Info randomness. A separate identity-transform union box therefore does not introduce a new generated-coordinate scale or object-random material mapping. Node graphs and all source materials must remain unchanged.

## Reversible method

Prefer two uniquely owned inverted16vertex Mask modifiers/groups plus two new union objects, not large duplicated replacement mesh objects. Keep every original raw coordinate/topology/material/attribute and all non-target components intact. Each Mask must be VERTEX_GROUP, invertTrue, threshold0.5, smoothingFalse, enabled in viewport/render, native other defaults explicitly verified. No changes to existing forest masks or quality-helper artifacts.

Rollback is paired: disable the two owned masks and hide their corresponding two union objects, in viewport AND render. Keeping both representations visible recreates the artifact; keeping neither leaves a hole. Never delete raw originals or modify the accepted source file.

## Required acceptance gates

- Full original persistent scene/material/light/world/camera/collection preservation except exact two groups,32owned weights, twoMask stacks and explicitly named additions.
- Independently map both evaluated target complements to original kept vertex/edge/face/corner IDs and compare every attribute, topology, normal and material field. If Mask drops unselected degree-zero vertices, prove that exact isolated set; no unrelated faced geometry may disappear. No broad attribute waiver.
- Two new boxes must have exactly the measured corners, six outward faces, closed oriented positive volume and identical material mapping. Exact occupied-set equality preserves all original intrados/route/silhouette occupancy, rather than adding material to a supposed opening.
- Verify same-facing exposed duplicate front patches disappear in the measured pier/plinth regions. Opposite-facing shared support contacts are not duplicate exposed skins. The mapper's all-visible front audit found only the four intended original faces; this does not certify every remote surface in the castle.
- Rollback and repeated setup/collision guards must leave source hashes unchanged. Restore the original evaluated scene when masks are disabled and added boxes hidden.
- Negative fixtures: wrong/unselected weight; source hidden-forest vertex mutation; union corner displaced into a new volume or narrowed to create a gap; flipped/open union face; wrong material/world mapping; deliberately mixed original/new visibility. Require intended invariant failures, not setup errors.

## Visual evidence boundary

The actual baseline image shows a dark narrow central-pier strip and fork-like foot. Mapper ray hits and the independently verified occupied-box intersections show these pixels are not an empty aperture. Duplicate front areas are12.239968643m² for the shaft and3.479993505m² for the plinth; their projected regions align with the visible strip/foot. This supports one union-only trial. It does not establish original author intent or guarantee the rendered improvement: use the identical practical camera/settings for the final comparison. No new structural-support or engineering claim.
