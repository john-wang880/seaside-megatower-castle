# Compact stores guard / interface PLAN — no candidate

Pinned accepted v028 source f0d135…; full actual evaluated triangles from `../native.json`. This pass is CPU-only: no Blender, model save, CSG mesh, new light or render.

## Frozen nominal scope
- Clear stores: [16.4,34,29]…[23.4,38.5,32.05].
- Clear connector: [15,35.5,29]…[16.4,36.9,31.45].
- Room guard: [16.3,33.9,28.9]…[23.5,38.6,32.15].
- Connector guard: [14.8,35.4,28.9]…[16.5,37,31.55].
- No sleeve, added source volume, new retained pier or ceiling band.

The highest guard plane32.15 remains .1450019836 below the preserved terrace's actual bottom32.2950019836. Guard is a local replacement partition, NOT permission to remove its whole occupied volume. Existing source above/below/lateral to the cavity stays; prior .30 source-cover proof is not reduced to guard thickness or an engineering assertion.

## Actual planes / face-domain preservation
Three current V028 complex host components, eachseed0,335 unique raw vertices total. Current no-modifier/raw=evaluated mappings are bound, not old V012 IDs. Owner's `../attributes/inventory.json` separately records native attributes/material graph and source stability; final integration must preserve those records.

| Host | Exact remote parent faces | Affected parent IDs / actual planes |
|---|---:|---|
| foundation outside chamber guard |122|85,86: Z31.440000534057617;112: X15.100000381469727|
| ashlar outside chamber guard |76|56,57: Z30;72: X15.100000381469727|
| local receiving chamber shell |70|24:X15;25:X15.100000381469727;57,61,63:Z29|

All11 affected parent faces are exactly axis-planar;268 wholly remote parent polygons remain exact, including inherited source interfaces. Their actual loop-triangle clipped domains, oriented original polygons and raw IDs are in PLAN.json. A first diagnostic inferred triangle-parent membership from vertex subsets; collinear triangles can share vertex domains. Final code uses authoritative ordered n−2 parent slices with membership/count assertions. This correction leaves the classification/result unchanged; initial script/report retained honestly.

## Uniform-cell result and old-air interfaces
All actual intersecting host planes plus guard/cavity planes partition G into241 connected open coordinate cells. No boundary crosses a cell interior. Solid-angle witnesses classify whole cells, not an arbitrary sampled grid or convex/AABB host assumption. Maximum winding residual1.80e−14.

Within G: source union115.524; expected retained union14.647; removed100.877; added0 coordinate-units³. Removed volume equals7×4.5×3.05 +1.4×1.4×2.45. These are analytical expected sets, not saved-mesh measurements.

Every guard interface cell retains original occupancy. **Not all guard boundaries are solid.** Old receiving-room air occupies westX14.8 aboveZ29, and short portions of connector sideY35.4/Y37 and topZ31.55 forX14.8…15. All23 air-interface cells are explicitly classified as unchanged pre-existing receiving void. They must not be capped as solid or “fixed” with a sleeve. Remaining interface cells are occupied source, so retained-side/local-side caps can meet only in buried material; final oriented interface-domain equality remains a saved-geometry gate.

## Continuous old-to-new floor
PLAN.json floor cells extend across **X14.8→15→15.100000381469727→16.4→23.4**, not merely the new room. For all footprint intervals, immediately belowZ29 is retained source and immediately aboveZ29 is old or newly cut air. Thus no extra threshold plug/sleeve is indicated.

At westG planeX14.8, the source-floor strip Y35.4…37,Z28.9…29 remains occupied on the partition side and connects to the unchanged old room floor. Its planar area is.16; the actual doorway-width substrip is.14. `floor_witness.json` additionally proves an actual positive-volume source box X14.7…14.9/Y35.4…37/Z28.91…28.99 across BOTH sides of westG, using all-triangle exclusion plus solid-angle inclusion. This is a positive occupied interface, not an unsupported new floor plane. Existing receiving floor polygons57/61/63 are locally clipped only; their outside-G domains and all other original room surfaces/piers/band remain.

## Implementation contract / stop gate
Preserve all335 original raw target vertices/meshes with explicit owned reversible controls. Do not alter existing V012 masks or the fourth V028 east-lining complement. Independently copy/clip the268 remote and11 affected source domains, close only matched buried cut interfaces, and construct one common local union-minus-cavity boundary. Never run a global union on all remote host surfaces or independently subtract each overlapping host and retain duplicate room skins.

Architecture planning cap3–8k triangles, counted over all visible replacement pieces including remote retained portions; no fixtures in this first shell milestone. Potential later storage stays INSIDE the clear room; no new recess excavation. Existing20 fixture meshes/2lights and all old routes protected. Current owner attribute inventory must be hash-bound before implementation. Final float32 output, closedness/orientation/domain coverage, duplicate-skin/floor/route/fixture negatives and art gates are still required. Independent CPU proof requested before parent construction approval.
