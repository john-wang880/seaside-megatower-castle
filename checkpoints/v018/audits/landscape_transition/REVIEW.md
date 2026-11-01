# v018 grass–rock transition audit — useful negative

## Decision
Retain accepted v018. No sufficiently clear **hero-readable grass–rock boundary defect** was established to justify a local modeling or shader prototype. This does not declare the wider landscape brief completed. Its remaining “systematic deepening” language is an art-direction opportunity, not evidence that a missing material, edge strip, or scatter pass must be added.

Reviewed the actual 1200×866 current hero first (`work/v018_navigation/current_hero/image.png`), then one actual-light, same-camera crop rendered at 3× linear resolution. The crop diagnoses mechanics; it is not the acceptance scale. At delivered hero scale the main south slope is only roughly 360×120 pixels. Grass occupies upper ledges and fades into the lower, steeper exposed substrate; the rock blades keep an angular graphic language. No conspicuous straight grass cutoff, detached turf sheet, bare unassigned patch, or UV-scale discontinuity was seen in this bounded region.

## Original goal, faithfully bounded
- Fixed original `V002_STAGE_REVIEW.md` line20 explicitly says slope materials already existed. Line54 calls for systematic development of the main rock platform, remote land silhouette, rock-strata direction, grass–rock junctions and coastal foam.
- `V006_STAGE_REVIEW.md` line40 calls for staged main-slope/coast naturalness after entrance, clearance and foundation work.
- Neither source specifies a new vegetation species, an erosion pattern, universal rounded rocks, added random stones, or a different biome. Those should not be invented to manufacture a version.

## What the closer view actually shows
`hero_slope_detail.png` is the same hero perspective, crop original pixels x620…980, y575…695, rendered at 3600×2598 full-frame equivalent (about1080×360 cropped). Original Cycles80 samples, max bounces8, world, lights, exposure0.2 and AgX remain. The terrain's soft slope-based colour edge is visible between hard separate slate blades. There is a stylistic contrast between smooth underlying hill and sharply fractured rocks, but that contrast is already part of the established design. Replacing it would be a broader landform/strata decision, not a narrowly supported grass-edge repair. The crop does not justify smoothing the angular rocks or adding more noise/grass tufts.

## Exact dependencies and sampled area
- Visible main substrate: `V010 | headland with local stair-edge clearance`, same-name mesh, single user,16,385 vertices/32,512 smooth faces, no modifiers/groups. Full bounds x−28.280…101.251,y−46.978…102.605,z−0.780…29.015.
- Exposed separate rocks: `V008 | coastal rock blades locally excavated for approach`, same-name mesh, single user,18,047 vertices/23,027 flat faces, no modifiers/groups, material `Fractured coastal grey-blue slate`. Its complete merged object spans both headlands; do not globally change it to address this crop.
- Existing grass geometry: `Fine meadow grass blades`, single-user mesh,35,895 vertices/11,965 faces, three existing olive/sunlight/dark-green materials. Not evidence that more scatter is needed.
- Main and western substrates share `Meadow and slate | slope-based procedural strata` (four datablock users). A direct material edit could change both visible landmasses and hidden baseline resources. Do not treat it as local.
- Exact hero rays in `audit.json` identify the south-slope sample envelope: nearest hits x8.178…86.468,y−28.728…−13.163,z12.427…27.711. These are representative samples, **not exhaustive patch boundaries or a proposed edit region**. Points include terrain at(16.312,−27.898,19.023), (47.184,−24.669,20.502), (61.541,−15.720,24.763), and rock blades around(8.178,−20.526,24.781), (35.948,−13.163,27.711). Raw ray normals are geometric ray-cast normals, not a measured shader result; no shading defect is inferred from their sign.

## Existing transition implementation
Actual current material links use Geometry **Position** for colour noise (scales0.16 and0.027) and fine bump(scale2.8, strength0.56,distance0.28). Grass/stone mixing uses Geometry **Normal.Z** through `Grass clings to slanting ledges above bare sheer rock`, a continuous black-to-white ramp0.40…0.78. There is already low-altitude damp modulation. No UV/image mapping is required by this graph. Do not describe the transition, macrocolour breakup, or wetness as absent.

## If the broader brief is revisited later
A coherent landscape redesign would first need a reference/composition direction: e.g. whether the smooth substrate/hard-blade contrast should remain graphic or become more continuously stratified. That is broader than this narrowly authorized patch audit and risks changing rock strata, coast silhouette, foundation contacts and existing paths. No specific local change currently clears the visible-benefit gate. Do not substitute microscopic grass detail, foam normals, or wetness tweaks merely to keep a version counter moving.

## Verification / limits
Canonical source `work/v018/castle_v018.blend` SHA256 `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd` verified unchanged before/after. Blender5.2.3 with autoexec disabled; one read-only load, one render, no saves, no geometry/material mutations, no Git changes. Render59.08s. `audit_original_executed.py`, `audit.json`, `render_receipt.json`, and `audit.log` preserve the executed procedure/evidence. Portable `audit.py` is a later CLI wrapper; see README.md for its validation status. This is a visual/material dependency audit, not all-rock contact, navigation, geology, erosion or structural certification. No new v019 scene was produced.
