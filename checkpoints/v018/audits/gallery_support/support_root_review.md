# Independent root selection for the430-component support graph

This is a semantic/data review of the validator's evaluated export, not a second graph implementation or Blender run. Canonical v018 SHA remains `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`.

## Exact approved initial roots

| Current visible object | Evaluated seed | Architectural basis |
|---|---:|---|
| V005 main tower calibrated stone surface |8|Massive main-shaft body, x42.5…51.5,y30.5…59.5,z42…180|
| Same |24|Deep front wall with actual recessed-window cuts, x28.05…42.55,y28.8…32.8,z51.6…180|
| V008 gallery with genuine eastern approach portal |8|Secondary keep/gallery body, x5.5…34.5,y27…63,z35.1…69.3|
| V012 ashlar with bounded entrance and north stairwell |24|Broad lower base platform, x9…69,y2.5…65.5,z32.4…36|
| Same |576|Substantial pier/tower body, x16…24,y19.5…28.5,z34.8…61.2|
| Same |2064|Front gallery body, x36.41…60.19,y1.5…21.5,z33.6…59.4|
| V008 gallery with genuine eastern approach portal |12020|Companion front gallery body, x27…35.8,y1.5…21.5,z33.6…59.4|

Full exact names, bounds, evaluated signatures and export hash are in `support_root_review.json`. These are primary wall/building-volume semantics, not every component in objects with architectural names. The V005 body lineage is an unchanged-mesh object-material copy of the v004 recessed-window main tower, ultimately original `Citadel | monumental shadowed tower`. The V008 body comes from `Citadel | secondary keep and galleries`. V012 ashlar/terrace copies bake source modifiers and apply bounded lower passage cuts. Thus hidden baseline objects are not used as phantom support.

Terrace ledge seeds24/48/72 are broad slabs, but should remain **intermediary nodes** until contact to a nominated body is established. Arbitrary nearby sculpture, glass, decorations, individual corbels and rails are not independently rooted merely because they are large or closed. Other substantial tower bodies may be legitimate contextual roots if needed, but start with this narrower reviewed set; no root inflation to force a pass.

## Mapping and scope trap
All430 source component seeds, bounds and vertex counts match the evaluated targets in the export. This limited correspondence is not itself a full mesh-equality proof; the validator owns evaluated signatures and triangulated geometry. The initial x10…65,y8…35,z48…80 box selects **whole connected components by intersection**. Their full evaluated union is x8.819…65.938,y0.65…62.5,z35.4…180. Long ribs must not be cut atz80. A chain unresolved by neighborhood selection is inconclusive, not automatically floating.

A graph pass means the430 sampled components connect geometrically to these established primary architectural masses under the validator's disclosed contact tolerances. It does **not** certify structural loading, foundational grounding of every root, all facades, hidden interiors or dynamic traversal. Closedness alone never proves attachment.

No model/Git changes, no render and no simultaneous Blender process were used by this reviewer. Stop this bounded question if the graph resolves it; do not expand into unrelated defect hunting.
