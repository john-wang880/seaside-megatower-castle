# Independent local path-conformance QA — rows95→105 only

Source v02299156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2. Planning and pure-JSON proof only; no model writes/render/Blender. Target is an intentionally open road surface, not a closed/manifold solid.

## Proven source defect and clean cuts

Actual path polygons are already triangles: faceID=row*12+2*crossCell+triangle. Approved local strip is faces1140–1259 (120triangles), between rows95 and105 of127×7vertices. Independent Python-double polygon overlay against actual evaluated terrain triangles proves plan-area57.5677229202, buried area12.7278484323 (22.1093484%), worst clearance−0.0842474309 atface1257/material0. This is a face-interior result, not the older sampled−0.0665 approximation and not camera-pixel coverage. The wider180-face diagnostic is preserved separately, not the final fix scope.

Independent full-segment clipping confirms all end-row seams clean: row95 gap[0.0170178482,0.0227116917], row105 gap[0.0215625888,0.0256551650]. Their entire polylines must retain source XYZ, including inserted collinear interpolants. Lateral source edges are partly buried (minimum−0.0363607124); preserve exact XY footprint but permit their Z to conform. Freezing all four boundaries would preserve a real defect.

Proof files: source_overlay.json, boundary_and_subset.json and their pure-Python scripts. Per-path-face terrain overlay coverage is complete to~2e−14area and pairwise overlap negligible~1e−14, establishing the exported single-heightfield partition locally. This uses double-precision arithmetic, not a formal exact-rational proof. Actual candidate scene terrain must later be hash/semantic-bound to the export.

## Reversible implementation expectation

Owner's refined topology avoids masking shared seam rows: select ONLY interior rows96–104, vertices672…734 inclusive (63vertices), retaining rows95/105. Independent raw-face incidence confirms that exactly120faces1140–1259 touch this set and1392otherfaces do not. Thus one precisely owned inverted vertex Mask plus a separate replacement patch is feasible; the earlier general warning about masking all boundary vertices does not prohibit this refined selection. Native evaluated complement remains to be verified; if unexpected topology/attribute behavior occurs, stop rather than broaden exemptions.

Original path raw vertices/faces/attributes remain untouched except63owned deform weights and one owned group/Mask. No whole-path copy is necessary unless actual evaluator behavior blocks the minimal approach. Preserve all earlier forest/pier/rib Masks and hidden baselines exactly. The source path has no pre-existing groups/modifiers/UV in the current inventory.

Allowed deltas must be explicit: exactly those63weight1entries and one uniquely owned invertedMask/group; one new patchmesh/object and ownedcollection/metadata if needed. No original visibility/material/world/terrain changes. Compare all unrelated persisted/evaluated state against source, including every earlier deform weight/modifier. Rollback disables only this Mask and hides the replacement; repeated states must reproduce source/active evaluation. The retained raw path remains recoverable without relying on a separately hidden copy.

## Full planar domain and material partition proof

Use actual evaluated candidate loop triangles. Project both original selected120triangles and new patch toXY. Clip intersections and prove:
* each original face's entire XY domain is covered, no holes;
* no new area outside that exact original patch;
* no overlapping positive-area triangles/double surfaces;
* per-original-face material assignment retained, including the moss verge partitions; no redefining moss as paving or adding edge borders;
* triangle orientation follows the original surface convention (original normals are downward); do not silently flip or demand positive solid volume.

The original per-face material/smoothing/selection/sharp fields need explicit new-face inheritance. New vertices/loops require declared interpolation/mapping rules for all existing attributes. No broad attribute drops. Unaffected face coordinate/topology/material/normal records remain exact. If seam triangulation is needed to eliminate T-junctions, explicitly identify the minimal adjacent faces and prove their XYZ occupied surface/material domain unchanged; do not silently expand height modification beyond selected strip. Geometrically collinear edge subdivision is distinct from raw-topology equality.

## Terrain overlay clearance over ENTIRE faces

For every new triangle, intersect its XY polygon with every relevant evaluated terrain triangle. On each intersection polygon, pathZ−terrainZ is affine. Its extrema occur at polygon vertices; checking all these vertices proves the whole piece, unlike sampling only candidate vertices/centroids. Verify full coverage and no positive-area terrain-overlap ambiguities before interpreting a minimum.

The intended interior offset is approximately0.021coordinate units. Fixed end seams impose the inherited positive range above. Predeclare a local offset/blending field and its numerical bounds before accepting output. A nominal0.021interior plus preserved end seams should produce an overall envelope no worse than roughly[0.0170178482,0.0256551650] before quantified float32 rounding; do not accept an unbounded raised road merely because it clears terrain. Compute and report actual min/max gaps independently. Derive allowed saved-coordinate rounding from local float32 ULP and actual affine interpolation, not a broad post-hoc tolerance.

Also intersect new/source path triangles to prove bounded Z displacement across the whole patch, not only matching vertices. Report maximum positive/negative displacement and location. Determine maximum actual surface gradient/grade, gap-field gradient and end-seam continuity; a local surface offset must not create vertical steps, spikes or extremely steep sliver triangles. Compare to original and actual terrain grades and to the predeclared blend field. Do not claim accessibility/engineering compliance or globally calibrated metres.

Actual ground support here is a small controlled visual road/terrain clearance, not closed-volume load-bearing contact. Retain open-surface semantics; never call terrain/path sheets enclosing solids. Exclude no other visible geometry merely by name without inspecting its role.

## Seams / exposed edges / topology

Both end polylines must be identical inXYZ as geometric sets, even with split points. Require every new boundary point lie on the exact old edge with matching interpolatedZ; require full edge-length coverage/no duplicate segments. At old/new joins, prove zero geometric gap and no positive-area doubled triangles. Assess combinatorial T-junctions separately and prefer compatible splits; any minimal unchanged adjacent retessellation must be declared.

Lateral XY outline remains exact and its full new segment-to-terrain clearance is bounded, so no floating side lip or buried sawtooth survives. No new bridge/arrival connector, route widening, grade stair or wall strip is in scope. New outer side faces are not authorized; this remains a surface mesh.

## Negative controls and delivery

Actual in-memory fixtures should reject: lower one new interior point to create terrain burial; lift one point beyond allowed support gap; move a lateral point off originalXY footprint; alter a moss material partition; break an end seam/introduce a hole or duplicate triangle; mutate hidden original/previous Mask. Include an overlay fixture whose vertices clear terrain but interior crosses a terrain ridge, proving full-face logic catches the original mechanism.

Critical full-face/domain/seam/source gate first; actual identical-camera view then decides whether the sawtooth intrusion is visibly resolved without a raised patch. No material/weathering redesign. If accepted, complete rollback/negative/rebuild/public-adapter checks with explicit paths/hashes and fresh Git restoration. Source991 and any candidate never saved by QA. Stop if a clean bounded construction cannot be proved; do not enlarge the patch or tolerance silently.
