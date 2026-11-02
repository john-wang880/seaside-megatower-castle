# B0: wooded shoulder, open approach, asymmetric rocky coast

Status: **read-only art brief; no prototype, render or geometry authority**. The user explicitly selected both purposeful interior exploration and whole woodland/coast redesign on 2026-11-02. Earlier rejected isolated trees/cliff wedges inform the design, but do not prohibit this newly authorized holistic direction.

## Evidence and intent

Reviewed current v028 hero and `current_inventory/REVIEW.md` / `spatial_map.png`. The scene's strengths are the unequal monumental towers, pale stone against dark shafts, the bridge connection, and contrasting grassy western headland / rocky main pedestal. The new aim is a coherent wind-shaped coastal pine landscape, not a claim that these existing features are defective.

Inventory confirms merged forest geometry, not instances. Its 693 tall woody-component references are **not tree identities or proven roots**. Terrain/path rectangles are broad vertex bounds, **not actual shoreline, occupied surfaces or safe planting footprints**. Existing HIGH tree alone is 420,206 evaluated triangles; do not propagate its needle-level construction across the island.

## One composition, four interdependent zones

All coordinate bands below are **conceptual influence masks only**, in scene-coordinate units. Clip them to actual terrain and subtract verified architecture, root/support and route exclusions before any placement. No rectangular forest boundaries should appear in the model.

| Zone | Conceptual influence | Massing and distribution |
|---|---|---|
| Wooded western shoulder | Primarily X -200..-135, Y 15..115; taper toward X -135..-85, Y 65..125 only outside actual tower/support exclusions | One connected scalloped grove: three unequal overlapping crown-mass lobes, with two shallow grassy bites. Core apparent crown-area mix about 55% tall sheltered, 35% broad mature, 10% low wind-pruned. Unequal heights, occasional visible trunks, no hedge edge. |
| Open approach | Actual winding path and its bridge/tower connection, not its bounding rectangle | Hard exclusion for the verified route/body envelope; wider view openings determined by actual hero and standing-route rays. Trees approach in groups on one side, retreat at bends and the bridge reveal. Do not turn the route into a straight formal avenue. |
| Exposed foreground transition | Broad provisional X -215..-125, Y -55..15 | Predominantly open grass/rock. Sparse linked crowns, approximately 70% low wind-pruned, 25% broad, 5% tall by apparent crown area. Broad gradual transition to the grove, no abrupt old/new or LOD boundary. |
| Main castle pedestal | Actual supported platform, not broad terrain bounds | Predominantly bare rock. Vegetation only as subordinate, proven-supported accents that do not mask the gothic base, bridge or shoreline relationship. |

Percentages describe intended visual mass, not prescribed tree counts. Actual source topography may shift the influence bands while preserving this composition. The accepted near HIGH tree can remain an anchor if it fits the new canopy language; do not preserve every old planting position mechanically or copy its mesh density.

## Coast as a continuous landform

Keep the recognizable two-headland composition and channel/bridge separation. On the western exposed outer/rear reach, compose **two unequal broad shoulders enclosing one concave bay**, with continuous oblique fractured slopes from rim to foot. Change the whole curtain-like reading, not one triangular fin attached to it. The front approach shore remains lower and quieter.

Preserve exact castle/path support cores pending independent proof. Main-castle upper support silhouette remains; the lower exposed rock should read as fewer broad primary planes with subordinate broken fragments, rather than equally weighted blades everywhere. The marker rock and its stairs are a separate protected architectural support, not incidental scatter.

Actual shoreline relocation and peripheral terrain redesign are allowed by the new user brief, but must be explicitly recorded and tested. No assumptions that the old broad terrain bounds locate the rim or that a new lower rock mass automatically preserves every contact.

## Shared style

- Restrained naturalism with legible sculpted masses, compatible with the existing castle rather than a photoreal needle forest beside stylized stone.
- Three related coastal-conifer growth forms: tall sheltered, broad mature and low wind-pruned. Use asymmetric interlocking bough masses; avoid stacked cones, horizontal collars and exposed artificial shelf gaps.
- A modest conceptual NW-to-SE wind tendency can unify exposed crown bias. This is an art choice, not a local meteorological claim.
- Rock: one dominant oblique fracture family with limited crossing planes. Avoid a single flat slab, horizontal terrace stripes or a necklace of equal boulders.
- Cool muted grey rock, olive ground and dark blue-green crowns. Pale castle ribs remain the strongest fine light accents. Original lighting/exposure stays fixed for first comparison; no wetness/glow retuning to sell geometry.

## B0 build target, only after parent approval

Create one disposable, reversible whole-scene proxy composition. In the test copy, replace woodland masses coherently rather than layering proxies over every old tree. Keep originals recoverable and protected support cores exact.

Planning ceiling: **2–4k coast-plane triangles + 2–4k grove-envelope/simple asymmetric crown-proxy triangles; at most 8k combined**. This is a low-cost composition test, not production tree modeling, final geological topology or a triangle target to fill. Retained existing geometry must be reported separately from this new proxy budget.

Required before prototype: actual faced rim/shore trace, actual route footprint/centerline, source support/exclusion domains, and clear old/new ownership. CPU extraction from existing data is preferred. If existing exports are insufficient, request the owner's sole native slot; do not infer missing traces from inventory rectangles.

## Acceptance and stop gate

One original-light hero and one existing opposite-side view should establish the joint composition. Only after that whole-view gate, inspect one standing approach context. No angle search to conceal a weak massing result.

Pass only if:
1. Grove, clearing and exposed fringe read as one landscape system rather than random tree scatter or unrelated patch upgrades.
2. Both towers remain dominant and distinguishable; bridge/path connection and main architectural base stay legible.
3. Coast reads as attached, continuous geology from both sides; no isolated fin, collar, terrace stripe or conspicuous old/new seam.
4. Shoreline changes are intentional and source support/route preservation is independently proven.
5. Whole-scene resource cost is measured, not inferred from unique prototype size.

If the unified massing is weak, stop before production foliage/material work and reassess the composition. Do not rescue it with denser needles, brighter materials or repeated small camera changes.

Later production planning ceilings remain coast 10–25k triangles and three crown archetypes 15–30k unique triangles with lighter far variants. Evaluated instance totals and native memory/render cost need independent budgets. Aim for no more than 15% paired-view cost growth over accepted baseline; larger costs require an explicit benefit/cost decision. These are planning targets, not measured performance guarantees.
