# v022 approach-side midground conifer stand — read-only inventory

Source `work/v022/castle_v022.blend`, SHA256 `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`, unchanged. No model edits/save/render. Existing square exhibitionA is v020 imagery, valid only as unchanged forest context; current geometry was loaded from v022 for the actual ray/projection/dependency checks.

## Exact bounded stand and locator

Art-directed A locator X0.30–0.35,Y0.555–0.59 includes overlapping foreground/background foliage. Finite rays through the exact shifted A camera locate three coherent upslope trees immediately below the west tower, left of the bridgehead. Actual hits(730,1335),(765,1360),(765,1385) correspond to the three groups below; other locator pixels hit architecture, path or unrelated foreground trees. Those are **not** automatically included.

| Associated trunk component | Crown raw vertex range (end exclusive) | Crown bounds XYZ | Vertices / triangles / faced clumps | Crown height |
|---|---|---|---|---|
|90130,XY(−113.7075,44.2637)|159318…159634|X−114.9496…−111.9531;Y42.3144…45.7843;Z31.0825…40.5118|316 /480 /38|9.4293|
|54140,XY(−109.9923,50.0850)|122118…122433|X−111.5378…−108.5360;Y48.6155…51.5863;Z31.4634…39.5721|315 /470 /40|8.1086|
|3350,XY(−106.5564,43.9566)|15211…15589|X−109.3484…−104.1992;Y41.1043…46.3404;Z29.4401…37.4304|378 /608 /37|7.9903|

All dimensions/distances here are **coordinate units**, not asserted real-world metres. Current settings are METRIC,scale_length1.0,length_unitMETERS; these UI settings do not establish global calibration. CrownAABB volumes98.0413,72.3108,215.4302 coordinate-units³ are envelope measures, **not actual union volume**. The115 disconnected bough masses overlap; occupied crown union volume was not measured or approximated as a summed solid volume. Total stand1009vertices/1558triangles is the useful confirmed resource baseline.

Groups are contiguous spatially corroborated source components around actual ray hits, associated with nearby tall stems; not recovered original generator tree IDs. Adjacent source-group boundaries are spatially separated by at least7.94coordinateunits. No selected face straddles a range, no selected vertex has v019 weights, and every selected raw coordinate is present in current evaluated mesh. Crown-to-each-woody-carrier attachment is not certified by this inventory; a later implementation would need actual tree/component ownership and attachment evidence.

The existing v019 dense hero tree(X−83.55…−80.72,Y40.83…43.62,Z23.86…34.11) is excluded and far away. Early near-gate provisional alternatives are explicitly retained only as `excluded_near_gate_groups.json`, **not scope**.

## Existing mass, palette and dependencies

Two crowns are predominantly Fir green:90130=426Fir/42Cypress/12Sunlit triangles;54140=446Fir/16Cypress/8Sunlit. The broader3350 crown is deliberately lighter:566Sunlit/32Fir/10Cypress. This already supplies height, breadth and color rhythm. All selected faces smooth-shaded; facets are geometric silhouette, not simply disabled smoothing. Do not homogenize the palette or add bump/noise as a substitute for canopy design.

Visible source `V010 | woodland boughs with gate exit clearance` is one merged mesh,204154rawvertices/307650rawpolygons, not tree instances; existing v019Mask/VG must remain exact. Visible woody source `V010 | woodland trunks with gate exit clearance`130530vertices/63855faces stays unchanged. Both source-hidden originals (`Dense western woodland | irregular three-dimensional needle boughs`,204154vertices/311872faces; `Woodland tree trunks`,130530vertices/65265faces) remain separately recoverable. Allfourmeshes single-user, instance_typeNONE, no collection instancing, shape keys, parenting, constraints or animation; detailed dependencies/material slots in `inventory.json`.

Historical material audit establishes existing worldPosition/Noise/ColorRamp/Bump foliage language; subsequent accepted checkpoints preserved those graphs. No texture downloads, material replacement, new tree density or unavailable pre-decimation restoration claim. The accepted v019 specialist asset is~420206triangles for one near hero tree and **must not be copied into this stand**.

## Visibility and path context

At exact2400² A camera, projected crown envelopes are approximately19×61,21×52 and34×52pixels, camera distances453.59/457.29/450.15coordinateunits. These are bounding envelopes, not opaque-pixel counts. Broad stand silhouette/mass differences could register; microscopic needles cannot justify their cost. Existing A view alone does not prove the current palette/spacing is deficient.

All three crowns are **behind** the existing west-approach camera(−99,38,32)→(−79,38,26.5). Negative projected depths−16.62…−4.78 mean their raw perspective coordinates are not meaningful visible coverage. Do not claim visibility in that historical route frame or move the selected stand to fit it.

Actual nearest path-surface samples from three stem-root references are10.4357,4.9258,3.5842coordinateunits away. Local path mesh vertices within the studyX/Y window occupyX−106.079…−101.146,Y40.685…53.970,Z28.096…30.762. Thus the broad/lighter3350 tree is nearest the path; preserve its footprint and path readability. These nearest-point samples are **not route clearance certification** or grounds to remove branches. No bridge opening/floor is selected.

## One honest practical source-view proposal

Camera(−87.8,−9.6,38)→target(−109.5,45,34.5),48mm,1200×866,original world/lights/exposure. Whole study context boundsX[−117,−101],Y[32,54],Z[26,42] have10.72%minimum margin. Current crown envelopes~79×253,80×203,139×233pixels. It includes whole selected stand and neighboring path context, not a needle macro. Exact matrix/data/projections are in `inventory.json`→`proposed_camera`; use only after owner render approval.

Finite centerline rays meet actual foliage/trunks, with normal canopy gaps sometimes reaching other trees behind; they are not complete per-pixel visibility/ownership tests. Initial nonrender framing was too tight for the broader path bounds and was corrected by increasing distance40%; no rendered camera-search batch. No render was performed here.

## Bounded art/resource gate

This is a plausible **artistic opportunity**, not an established defect: current two dark narrow crowns plus one light broad crown may already be the right stand rhythm. Inspect one actual source context still before authoring. If no concrete grouped-silhouette weakness is readable, close negative. If a coherent improvement is identified, preserve exactly these three tree locations, stem/roots, overall envelope/mass, palette differences, path and architecture visibility. No new trees or density increase.

A proposed resource ceiling for an eventual simplified stand asset is **6000triangles total for all three replacement crowns**, not a target and not a performance benchmark (~3.85×current1558, far below420k hero asset). Favor fewer well-shaped, opaque branch-tier masses with meaningful irregular outer gaps over tiny needles; do not repeat rejected pears/collars/ladders/fans. Actual source crown union/occupancy and branch ownership would need measurement before a volume-preservation claim. Accept only a visible practical-view gain with coherent A-scale massing and no route/hero regression; counts alone do not establish benefit. No model version or implementation is authorized by this report.
