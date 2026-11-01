# One bounded midground canopy prototype — rejected at isolated preflight

## Decision
Do not integrate. The one authored concept produces shelf-like polygonal rims and exposed vertical tier gaps in the isolated diagnostic. It does not meet the requested overlapping full-canopy language well enough to justify whole-scene render/QA cost. No artistic parameter search or second prototype was run.

## Scope and preservation
Only the three mapped crowns were authored. Source SHA and source per-component polygon IDs/bounds/triangle counts were checked; trunk ownership was verified by exact connected-component traversal and bounds. Original foliage/trunks, hidden full forest, existing v019 Mask and weights were never edited. The source was never saved. Source SHA rechecked after render. Asset is a standalone collection library, not an integrated castle checkpoint.

Source SHA256: `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`
Asset SHA256: `a806609799c9d9dc2e9792694649f50dc18b7c938d639140435334ebc7d3b673`
Generator SHA256: `ea840120de69e00c3484ed0ce88127bcf4c9b174fe4345b178cfde00060ade5f`

## Exact costs and bounds (coordinate units)
- Trunk 90130: 686 vertices, 1208 triangles; source 316 vertices/480 triangles. Bounds [[-114.94964599609375, 42.31443786621094, 31.08250617980957], [-111.95314025878906, 45.78433609008789, 40.51176071166992]].
- Trunk 54140: 686 vertices, 1208 triangles; source 315 vertices/470 triangles. Bounds [[-111.53778839111328, 48.61549377441406, 31.46342658996582], [-108.53599548339844, 51.5863037109375, 39.57206344604492]].
- Trunk 3350: 686 vertices, 1208 triangles; source 378 vertices/608 triangles. Bounds [[-109.34844207763672, 41.10434341430664, 29.440134048461914], [-104.19918060302734, 46.340354919433594, 37.430397033691406]].

Total: 3624 triangles / 2058 vertices across 3 new crown objects; original 1558 triangles. 40 fan solids plus 1 continuous foliage core per tree; 123 authored disconnected closed components overall. No new woody supports; original stems retained.

## Construction and evidence
Seven unequal-phase radial tiers of convex folded fans, tapering to a continuous pointed foliage core. Each fan has a thick embedded heel on the original trunk XY axis; adjacent shoulder and tier overlap was intended. All convex components verified closed manifold and positive oriented signed volume before exact envelope fitting. Flat shading and original foliage material datablocks/graphs are reused at original world positions. Manifest maps every component vertex/triangle interval and material slot.

The isolated render reveals insufficient continuity/fullness: mid/upper dark-tree gaps and blocky rim faces are too pronounced. The broad sunlit tree has layered shelf-like edges. Neighbor compatibility cannot be asserted because isolated rendering is not scene-context acceptance.

## Explicit limitations
- Convexity, closed manifold topology and positive signed volume checked before envelope fit. Post-fit independent self-intersection/contact certification not performed.
- Per-tree source AABB matched exactly; new occupied volume outside old canopy solids not quantified. Occupancy preservation and route clearance NOT certified.
- Core intended to intersect original woody carrier and all fan heels; actual intersection/contact independently unverified.
- No baseline/A whole-scene comparison performed: rejected at isolated design preflight.

## Files
- `build.py`: deterministic reproducible generator; includes isolated-only diagnostic render.
- `midground_canopy_asset.blend`: standalone STUDY collection, original materials; no original forest.
- `manifest.json`: exact source/object/component/material/ownership maps and checks.
- `isolated_preflight.png`: original world/lights, transparent background; source trunk component copies only.
- `build.log`: Blender 5.2.3 completion record.

Blender slot released immediately after the single preflight. No canonical integration, Git changes, publication or full-scene renders performed.
