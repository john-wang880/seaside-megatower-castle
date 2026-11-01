# Targeted interpretation of rear stepped black shapes

## Result

The conspicuous black staircase contains a **demonstrable exposed same-facing duplicate-surface family**. It is not adequately explained as an empty passage, missing rear wall, or ordinary broad exterior shadow. This is a narrow technical finding, **not permission to fill the apparent recesses or redesign the rear**. Other dark regions in the same picture remain ordinary occlusion/shadow and are not diagnosed wholesale.

Source accepted v023 SHA `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51` stayed unchanged. Exact actual source image/camera: `actual/image.png`, `actual/receipt.json`, `views.json`. No additional render or model save.

## Exact source family

Object **`V008 | gallery with genuine eastern approach portal`**, material slot0 **`Citadel • aged gallery grey`**, preserved modifier **`Soft carved stone arrises` (BEVEL)**. All measurements below use the **actual evaluated mesh**, not raw-box AABBs as proof. Evaluated component seeds may differ from raw-source indices.

The long stepped black family lies on identical north-facing plane **Y65.5**, normals(0,+1,0):

| Evaluated component | Bounds X | Bounds Z | Relevant north face |
|---|---|---|---|
|56|−0.5…28.5|56.10…66.30|10032|
|80|−6.5…0.5|46.20…52.20|10038|
|104|−2.3…4.7|50.40…56.40|10044|
|128|1.9…8.9|54.60…60.60|10050|
|152|6.1…13.1|58.80…64.80|10056|
|176|see exact JSON|see exact JSON|10062|

The steps overlap each other; several also overlap broad upper component56. Double-precision clipping of their **actual beveled planar face polygons** proves positive coplanar overlap:56/128=31.3550;56/152=41.8361;80/104=4.9821;104/128=4.9821 square coordinate units. These are face areas, not pixels. No additive area total is claimed because triple intersections can double-count.

The return-frame family repeats at **Y56,57,58,59.20000076**: broad body components200/3896/7000/9560 and their narrow side/top/bottom members. The bounded selected family contains40 pairwise positive coplanar intersections across26 evaluated components;19 overlap-centroid rays reach that gallery plane first. This is finite exposure evidence, not a claim every square unit of all40 overlaps is visible.

## Direct image correlation and controls

Exact rays reconstructed from the actual camera, with same pixel centers:

- Black pixel **(452,579)** intersects faces10032/10056 at **identical distance463.18664**.
- **(465,591)** intersects10032/10050 at identical463.94203.
- **(490,610)** intersects10038/10044 at identical465.12393.
- Return corner **(505,565)** intersects **three** north faces11004/11010/11028 at identical468.87247.
- Controls **(477,600)** and **(498,590)** each encounter a single nearest north face before deeper geometry. They demonstrate that not all nearby dark areas should be labeled duplicate surfaces.

These coincidences plus actual shared +Y polygons establish the surface ambiguity directly. The sampled components have two uses of every mesh edge (closed evaluated boundaries), and rays hit their front surfaces before deeper geometry. Thus the apparent black notches are not evidence of missing faces or new openings. Material assignment is identical within the family; no separate black material accounts for those duplicate zones. Lighting/shadow can still contribute to their appearance. No structural/load-capacity claim follows.

## Small pale pointed rear ornament

At image~(395,465), the pale shaft is **`V012 | ashlar with bounded entrance and north stairwell`**, evaluated component12328, weathered-limestone material, boundsX26.1501–27.8499,Y62.1726–63.8274,Z90–100.2600. Its cap is **`Citadel | oxidized spire roofs`**, component380, blue-green-roof material, boundsX26.0169–27.9831,Y62.0650–63.9350,Z100.4700–108.2100. It sits visually against the main north wall. This is an authored small pinnacle assembly, not a window, visual hole, or newly proposed decoration. Hidden support/contact was not audited and is not nominated for repair.

## Boundary for any next work

Only the demonstrated gallery plane-overlap family warrants independent review. Do not fill black shapes with new masonry, alter stairs/entrance routes, remove bevels globally, or infer the whole rear is defective. A future technical correction would need actual occupied-set/exterior-outline preservation and source rollback, with careful treatment of the existing bevel modifier; simple box unions are **not automatically equivalent** to these evaluated beveled components. Scope/repair strategy must be separately approved. Original V008 recipe identifies its source as `Citadel | secondary keep and galleries`; actual historical identity of each affected component can be verified in that later independent pass rather than assumed from names.

Evidence: `target_probe.json` (80 actual-camera rays and hit-component topology), `coplanar_targets.json` (all selected face polygons, pair intersections, camera exposure, exact coincident-ray controls), executed `.py`/logs. No render, model save, or material edit. Blender released.
