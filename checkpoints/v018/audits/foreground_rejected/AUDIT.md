# Foreground woodland fidelity audit — read-only v017

Canonical `work/v017/castle_v017.blend`, SHA `9ed12e2dd4e21ee91ff65848d3c11601332a690ea80a880fb31bf41f1d7dd943`,35,671,703 bytes. Hash unchanged after inspection. No model save, Git changes, prototype or new render. `audit.py` created a temporary camera in memory only for pixel-ray identification.

## Visual finding and priority

Viewed the actual1200×866 `checkpoints/v017/navigation/renders/west_approach.png` (clearly documented v016 source, forest unchanged in v017) and current `checkpoints/v017/previews/hero_after_v017.png`.

The dominant tree immediately left of the stair reads as stacked large tapered spindle/pear-shaped green solids; individual lobes span tens of pixels and the tree occupies hundreds of pixels vertically. Several smaller right-side trees have similarly polygonal bough silhouettes. This is a meaningful **navigation-close-view asset-fidelity weakness**, not a scene-wide defect. The hero's forest mass remains coherent and small; increasing distant-tree density or photoreal individual needles would have little demonstrated hero benefit.

All307,650 visible foliage polygons are already smooth-shaded. Bump/noise is already present. The coarse outline comes from simplified geometry, not disabled smoothing or absent surface texture. No further baseline render is needed to establish this case; existing image is sufficiently revealing.

The intended visual language remains stylized dark conifers and clustered boughs. A modest spray/lobed silhouette pass could improve the closest tree without making it photorealistic or changing species/massing. Prototype approval remains with owner.

## Representative local assets

Exact ray-hit component IDs and contiguous spatial group evidence are in `candidate_groups.json` and `audit.json`. These are **spatially corroborated groups**, not an assumed original generator index or a promise to restore unavailable pre-decimation geometry. Visible meshes retain original vertex indexing, including unused vertices from prior face removals.

1. **Primary left tree:** nearest tall trunk component seed26760, centerXY(−82.09366,42.23069), trunk z23.63609…33.40089. Foliage group vertices[90395,90693),25 disconnected bough solids,298 vertices/496 faces, bounds x−83.73939…−80.68923,y40.63627…43.64584,z23.65438…34.13936. Pixel rays(250,450),(270,300),(300,620) hit group components90493,90573,90429. Adjacent groups' centers are57.19m and10.07m away from the associated trunk, giving a clear spatial boundary. This is the best first candidate.
2. **Right gate-side tree:** trunk seed27710, XY(−79.00246,35.14120), height7.67729. Foliage[91262,91479),25 boughs,217 vertices/334 faces; bounds x−80.12985…−77.99047,y34.16153…36.25011,z23.52490…31.11649. Ray(770,480) hits91356. Its northmost foliage is already near the route margin, so no outward expansion toward the stairs.
3. **Very near right-edge tree, optional later:** trunk125560, XY(−89.51857,32.75514), height9.32586. Foliage[196527,196938),40 boughs,411 vertices/662 faces. Cropped by the frame and partly shadowed; lower priority than the legible left tree.

Do not modify neighboring trees merely because their crowns overlap in image space. Keep all actual trunk/branch meshes and their transforms unchanged. Before any replacement, check whole target polygons are selected by the exact group ID set and no unrelated face straddles the vertex selection.

## Source, materials and dependencies

Hidden recoverable baseline objects:
- `Dense western woodland | irregular three-dimensional needle boughs`:204,154 vertices/311,872 faces.
- `Woodland tree trunks`:130,530 vertices/65,265 faces.

Visible current objects:
- `V010 | woodland boughs with gate exit clearance`:204,154 vertices/307,650 faces/23,827 faced components;2,675 extra isolated vertices are not extra branches.
- `V010 | woodland trunks with gate exit clearance`:130,530 vertices/63,855 faces/12,771 faced components;2,820 isolated vertices.

All four meshes have one object user, no modifiers, no constraints/parents/animation, and no detected child/modifier-object references. This is a bounded dependency inventory, not authorization to delete baseline data. The received full baseline forest was already needle-decimated; its retention does not recover the unavailable earlier high-detail original.

Four shared opaque foliage shaders: `Cypress needles — deep blue green`, `Fir needles — forest green`, `Sunlit needle tips`, `Distant sea pines`. All use existing Geometry/Noise/colour-ramp/Bump graphs, noise scale3.7, bump strength0.66/distance0.1, roughness1, metallic0, alpha1. `Pine bark` is the plain trunk material. Keep these unchanged initially: stronger bump or smoothing alone cannot create needle silhouette, and global material edits would touch the whole forest.

## Bounded candidate strategy, not implemented

Start with **one complete left-tree foliage group only**. Preserve trunk/branch axes, total height, canopy envelope, material assignment, forest positions and route clearance. Replace broad solid bough shapes with a small reusable family of stylized tapered sprays/lobes; express some branching and small internal negative spaces, not hundreds of thousands of literal needles. Constrain new vertices to the original tree/component envelope unless a tiny outward allowance is explicitly measured and approved. Do not just overlay needles on unchanged solid blobs, uniformly subdivide every tree, add alpha-card dependencies, or increase forest count.

Provisional cost ceiling for the first local experiment: roughly2,000–4,000 foliage faces for this tree versus496 now, not a whole-forest multiplier. This is a practical visual-test budget, not a target to fill. Reuse original material slots; no new world/light/exposure changes. If judged useful, consider the one right gate-side tree separately; do not mechanically propagate to all trees.

Preserve original hidden full forest exactly. Source-preserving prototype copies are acceptable locally, but a permanent second entire V010 copy just to replace298 vertices would duplicate about21MB of core uncompressed foliage arrays. For accepted organization, owner should choose a documented complement+local replacement arrangement and retire superseded intermediate only after archival verification/approval, retaining full baseline and latest visible forest. This audit does not perform or authorize cleanup.

## Resource baseline and acceptance gate

- Visible forest371,505 faces combined; foliage307,650 plus trunks63,855.
- Estimated core arrays: visible foliage20,908,848 bytes, trunks6,674,760 bytes. This excludes Blender runtime/attribute overhead and is not compressed file cost. Original+visible forest arrays together≈55.5MB decimal.
- Current v017 file35,671,703 bytes. Read-only audit peakRSS760,016KiB includes Python component dictionaries/material capture; not a pure render memory measurement.
- Existing west-approach v016 receipt:1200×866,80 samples,8 threads,78.31s render,617.92 CPU seconds,peakRSS1,930,672KiB. Historical contextual baseline, not a controlled current-v017 performance pair.

Acceptance requires identical actual-light west-approach before/after and unchanged hero, with close-tree silhouette becoming less bulbous while remaining stylistically consistent and forest mass unchanged. No relight to manufacture visibility. Compare new shadow shapes, branch/trunk contact, route occupancy, preserved non-target faces/materials/transforms and source hash. Reopen/repeatability, no external dependencies, count/file-size/runtime/RSS checks apply. Reject if merely denser, noisy, soft melted cones, too transparent, or only discernible in an artificial detail crop.

If the one-tree experiment fails this gate, retain v017 and proceed to another genuine original-roadmap feature (e.g. west crown assessment), rather than escalating forest scope.

### Material/selection follow-up

`group_materials.json` confirms zero straddling faces for all three candidate ranges. Primary left group:420 Fir-green faces,54 Sunlit-tip faces,22 Cypress-blue-green faces. Right gate group:318 Cypress,8 Sunlit,8 Fir; near right-edge group:590 Distant-sea-pine,64 Cypress,8 Fir. Names are palette/intent clues, not botanical identification. This strengthens the choice to test the Fir-dominant left tree first and **not** automatically apply the same spray design to the slender Cypress-dominant right tree. Preserve each component's original material assignment rather than homogenizing all foliage.

## Owner-requested Mask/carrier compatibility audit

`mask_carriers.json` supersedes the earlier full-complement-copy suggestion as the preferred low-memory prototype route. All four baseline/visible forest objects have **zero vertex groups, zero assigned vertex weights, zero modifiers, no shape keys or libraries**, and distinct single-user meshes. No prior armature/group binding needs preservation.

A uniquely named new vertex group on the visible V010 foliage, weights1 on the selected complete clumps, with an inverted vertex-group Mask modifier and explicit threshold, can hide only those clumps in evaluated geometry while retaining all source positions/faces/materials and original hidden full forest. Keep ownership/name collision checks and no arbitrary deletion. **New group weights are additional mesh deform data**; source-preservation validation must allow exactly those owned additions plus the modifier, not misleadingly claim all original mesh data is byte-identical. Existing coords, edges, face topology, UV/colour/material data and non-target evaluated geometry must remain exact. Original hidden forest and visible trunks stay wholly unchanged. Inspect mask visibility in render and viewport and repeat-install idempotence before acceptance.

Three clearly mapped front clumps are enough for a *decision prototype*:

| Foliage vertices | Faces | Material | Verified wooden carrier contact |
|---|---:|---|---|
|[90429,90446)|30|Sunlit needle tips|Five end-ring vertices26795–26799 of woody component26790 lie inside foliage by all three oblique ray parity tests|
|[90493,90508)|26|Fir needles — forest green|All ten vertices26830–26839 plus adjacent stem vertices lie inside|
|[90573,90588)|26|Fir needles — forest green|Five end-ring vertices26895–26899 of woody component26890 lie inside|

Each original clump is closed (every edge has two incident faces), already smooth-shaded, and has no crossing polygons at its selection boundary. Preserve actual woody carriers rather than invent branch attachments from nearest trunk-center guesses. Left tree's contiguous woody group is[26760,27010),25 components; it includes the tall trunk and branch parts, and is **not** a one-to-one ordinal match to the25 foliage clumps. The final accepted asset, if the three-clump trial visibly succeeds, should coherently finish the one tree rather than publish a permanent three-clump sample.
