# v021 western tower — one complete lowest shaft tier, read-only art gate

Source `work/v021/castle_v021.blend`, SHA256 `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`, unchanged. No model edit/save, material edit or render. This is possible stone-craft enrichment, **not a newly diagnosed defect**.

## Actual member and tier

Camera-facing outer-right pale rib: `V012 | retained west rib facade with buried-route clearance`, connected component seed56, source vertices56–63,8vertices/6faces, material slot0 `West_Sunlit ivory carved stone`. Bounds X[−121.0373993,−119.8506012],Y[84.57499695,85.625],Z[78.2057419,166.9610443]. ItsXY section is constant1.1867981×1.0500031m: **no taper**. Bottom/top retain small authored tilt; bottom corners78.2057…78.2570, top166.9097…166.9610. Original prism is continuous through multiple tiers, not already an independent lowest-tier object.

Lowest tall shaft tier lies between lower arcade crown cornice stack seeds88/96/104 (Z78.49…80.13) and next cornice stack192/200/208 (Z103.18…104.83). Near this rib, the front visible run is approximatelyZ79.43…103.19, but rear seat cap geometry differs; these approximate levels are **not approved flat cuts**. Any future treatment must cover the coherent full visible lowest run while preserving original tilted geometry and all lower/upper continuations—not retile the entire88m source prism and not add another five-block sample.

Original source contact witnesses: (−120.44,85.3,79.3) is inside rib56 and lower cornice96; (−120.44,85.3,103.4) inside rib56 and upper cornice192. Actual source face-triangle signed solid-angle winding is1 for all four tests. This establishes original contacts, not final candidate seats/overlap clearance. Initial floatBVH parity disagreed on one upper-rib ray; source cornice has tiny quad nonplanarity. Diagnostic logs/votes are retained rather than silently relaxing tolerances; double-precision winding on exact source triangles resolves the interior test without flattening geometry. This is not a structural capacity claim.

## Neighboring windows and excluded sample

Existing V004 lower front lancets centeredX−137 and−128.9: bottom85.8,shoulder92.0,apex94.5,width2.8,frontY86,recessdepth2.2. Sparse window arrangement is deliberate and stays unchanged. Both center-view rays reach `V004 | varied facade groups deep muted glazing` behind front plane.

Existing V006 west sample lies on a **different inner rib** centeredX−126.12,Y84.575…85.625,Z137.95…147.45. It is excluded. Source recipe `work/gallery_arcade_audit_v018/original_refine_v006.py` uses five1.9m courses,18mm joints,10mm one-segment bevel, backingXY inset28/35mm, and preserved tilted original continuations. Its copied stone reduces bump and backing is a separate subdued material. These are historical construction language, **not automatic instructions to repeat parameters or materials** on the new full-tier member.

## Dependencies / existing articulation

Current merged pale-facade mesh has one user, identity world matrix, no modifiers and noUV layers in this survey. Its existing three material slots are original pale stone, V006 sampled-rib stone, and V006 recessed backing. Target56 uses only original slot0. Original `West_Sunlit ivory carved stone` has3users and world Geometry.Position→Noise→ColorRamp plus Noise→Bump; no Brick/joint shader or UV/Generated-coordinate mapping. Full graphs/material users are in `survey.json`.

Target prism itself has no physical course joints/bevel subdivisions; current full-tier image may nevertheless have sufficient articulation through cornices, adjacent windows and subtle stone variation. Aesthetic sufficiency remains an actual-image judgment, not something inferred from six-face topology. Shared original graphs/palette and tower silhouette must remain unchanged in any future candidate. No duplicate whole-facade mesh or new material is justified at this feasibility stage.

## Single practical baseline proposal

Location(−98.25,3.5,98.5) → target(−132,86,91),55mm,1200×866,original world/lights/exposure. Whole front-tier bounds X[−148,−117],Y[83.5,91],Z[76,107] fit with9.655%minimum margin. Seven target front samplesZ80…102.8 hit the intended rib; both lower lancet centers reach their recessed glazing. Includes both seats, neighboring ribs and windows rather than a joint macro. Exact camera matrix/data and finite ray/contact evidence: `camera_preflight.json`. Initial mathematical framing was slightly cropped, corrected before any render by increasing distance25%; no rendered camera-search batch occurred. Slot released for one owner-approved actual source image.

## Stop / acceptance gate

Baseline first. If existing articulation is already sufficient or proposed course detail would only make a stripe ladder, close negative. If owner/art director see meaningful room for crafted stone, a subsequent bounded full-run concept could use restrained physical joints/edge relief within the existing section, with continuous recessed backing and unchanged continuations/contacts. It must not brighten the outline, introduce black slits, enlarge the rib, flatten tilted seats, disturb window clearance or mechanically spread to other ribs. No prototype recipe, count, new material or cutting plane is approved by this survey; future geometry/contact QA remains separate.
