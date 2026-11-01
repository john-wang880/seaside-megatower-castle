# Dense left-tree experiment — unaccepted

Canonical source v018 SHA `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`. This is a local decision experiment, not a new accepted checkpoint. No source file, Git, original palette or lighting edits.

## Distinct shape hypothesis
The25 received clumps each span approximately2.18–2.51m vertically, while XY widths narrow from~1.5m in lower branches to~0.4m above. The repeated long spindle dominates the close approach. This trial replaces each with **three overlapping broad closed masses**, not thin carriers with individual spray arms. Their centers are24%,49%,73% up the old bough bbox; vertical semiextents34%,34%,29%; horizontal scale98%,100%,83%. The low half of each volume leans slightly outward/downward from the trunk. Staggered shoulders and shallow edge notches separate the lobes without opening the entire canopy. Each volume has26 vertices/48 triangles;75 components total3,600 triangles. Original material per clump is reused unchanged.

New geometry stays within each original bough bbox, hence whole crown envelope. Radial clipping toward the original closed source surface prevents gross outward expansion, but edges interpolate between clipped points; this is not a proof every surface point lies within the original faceted solid. Independent validation should test the actual result. Overall silhouette may lose the old spindle outline; exact silhouette preservation is not the artistic objective.

## Pre-render measurements (not visual acceptance)
`source_components.json` contains exact source vertex/face groups. `design_metrics.json` and `build_manifest.json` record13 horizontal section samples per bough using13×13 midpoint occupancy. Each new section is the union of its three lobes, so overlapping lobe volume is not summed. Combined per-clump estimate: source18.6085, new15.1164 world-unit³, ratio81.23%. Intersections between different bough groups are counted separately in both totals; this is **not exact whole-tree union volume**. That independent measurement is pending. A provisional≥80% bulk gate prevents repeating the sparse recipe; it is not a claim of beauty or perceptual equivalence.

Each bough retains one or more actual original woody vertices inside new solids; exact IDs before/after are reported. Not all original enclosed wood vertices remain enclosed; the checks prove continuing local overlap, not comprehensive woody containment or physical botanical attachment. Trunks/branches themselves remain exact. Original full hidden forest and all non-target meshes/materials remain unchanged. The target raw mesh changes only by298 explicit weights and an owned Mask modifier; complete raw snapshots match when the new group is temporarily removed. Non-target evaluated face positions/order-within-face, material indices and smooth flags match exactly in the builder. Independent full-attribute verification is pending.

## Allowed local delta
- Collection `EXPERIMENT | dense foreground tree`.
-25 new mesh/objects `DENSE TRIAL | bough {first_source_vertex}`.
- Source foliage group `DENSE TRIAL | left tree source canopy`, weights1 on[90395,90693).
- Inverted Mask `DENSE TRIAL | reversible source canopy mask`, threshold0.5, native other defaults.
- No new materials/custom properties, no original object deletion.

Candidate `dense_candidate.blend` SHA `3da5a6ac692767b2b726fa417b1f2ac39aebdd289d5aed503e7583e8524364cd`,36,004,914 bytes. Exact source35,962,496 bytes: +42,418 bytes. Blender's thumbnail-cache write warning did not prevent saving; saved candidate and unchanged source hashes were verified.

## Decision gate
Same actual1200×866/80-sample west camera before/after and candidate hero will determine whether broad mass remains while the vertical pear dominance decreases. Original source hero is already available at `work/v018_navigation/current_hero/image.png`. Independent visual review must reject a marginal difference, noisy blobs, excessive holes/mass loss, or effects apparent only at magnification. No relighting, automatic expansion to other trees, or iterative ladder tuning. Independent geometry/source/occupancy results and comparable resource receipts are required before any acceptance/publication decision. All files here remain local prototype evidence.
