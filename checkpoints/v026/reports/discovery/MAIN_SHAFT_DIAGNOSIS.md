# Main shaft black strip — targeted read-only diagnosis

Source v025 SHA8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2 unchanged. Actual unchanged-light frame: `actual/image.png`. West tower flank is a coherent negative finding; this report concerns only the conspicuous main-shaft strip.

## Actual geometry and image correlation

Visible object: `V005 | main tower calibrated stone surface`. No modifiers. Raw/evaluated720vertices,413polygons. Two closed eight-vertex box components:

| component seed / vertices | bounds | overlapping west face |
|---|---|---|
|0 /0…7|X17.5…47.5,Y31.5…62.5,Z39.599998…180|face4, vertices3,0,4,7|
|16 /16…23|X17.5…27.5,Y31…43,Z42…180|face18, vertices19,16,20,23|

Each component has6faces/12edges, every edge usedtwice. Both relevant polygons have normal(−1,0,0), common planeX17.5, slot0. Exact rectangle intersectionY31.5…43 × Z42…180 has area**1,587 coordinate units squared**. This is geometric overlap, not the exposed/pixel area: ledges and other architecture cover some portions. Closedness alone is not a support certification.

All24samples at imageX670/680/690 acrossY200/225/250/300/340/375/420/450 intersect both actual loop-triangle faces at the same nearest depth (within reported float ray precision). Their first opaque scene hits are on this shaft. Representative pixelsX680 atY200/300/420 are RGB(0,0,0).

Genuine shade controls on the same west face4, X640/660 atthoseheights, hit onlyface4 and retain visible slate RGB values~14…36. X700 samples hit a single adjoining face18 or15 and remain dark-but-readable. Thus the strip correlates with a proven duplicate coincident skin, not an empty recess or merely a deliberately black material. `pixel_surface_evidence.json` records all56probes and first-hit normals; `coincident_rays.json` independently intersects every actual evaluated shaft triangle. This is targeted evidence, not a blanket all-shaft intersection audit.

## Critical dependency and correct effective material

The mesh has**two users**: visibleV005 and hidden `V004 | main shaft selective front and east-facing windows`. The hiddenV004 is hide_render/hide_viewportTrue. There are no vertex groups/modifiers/parent/constraints/animation/shape keys on visibleV005; identity transform. Shared raw-mesh writes, including added deform weights, would affect hidden rollback data and are **not automatically safe**.

The raw mesh slot refers to `Citadel • deep slate ashlar`, but visibleV005 uses an **OBJECT-linked override**: `V005 | main large ashlar calibrated world units`. Both faces share that effective material. Early raw-slot labels in geometric exports are not the rendered assignment; `shaft_dependencies.json` is authoritative for effective material mapping. Its graph uses world Geometry Position / true-normal projection and calibrated masonry/noise; no separate pure-black strip material exists.

Historical `original_refine_v005.py`, retrieved read-only from fixed Git91f2c7d, explicitly creates a linked object copy and object material override (lines75–85), hidesV004 and asserts the shared mesh. Its stated scope is material calibration, no geometry changes. Therefore this assembly was inherited, not created byv025rear repairs. We do not infer missing access or intentional recess from object names.

## Bounded next decision

There is a demonstrable same-facing duplicate-surface issue at the practical visible strip. An independent exact source/component review is appropriate before any remedy. If a later union/surface cleanup is authorized, it must preserve the actual occupied union, existing window apertures in other components, world-mapped effective material, exposed outline, all cornices and original hiddenV004 data. No wall fill, new supports, lighting change, thickness alteration or broader cleanup is justified by this survey. No candidate or render was created; Blender slot released.
