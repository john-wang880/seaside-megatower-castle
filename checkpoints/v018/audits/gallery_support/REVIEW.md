# Bounded gallery connected-support graph — v018, read-only

## Result, not a blanket clearance claim
- **301 of430 sampled gallery components** have explicit geometric-contact chains to three independently justified visible primary bodies.
- **129 components** are not connected to those roots in the examined graph; they form22 local contact islands. These are predominantly repeated ornamental assemblies, not129 distinct structural failures.
-12 islands/112 target components have complete direct-contact-neighbor coverage under the export-selection test and are geometrically separated from surrounding exported visible structure at the stated numerical tolerance.10 islands/17 targets contain extended non-target members beyond the guaranteed neighborhood; their ultimate attachment remains unresolved, not certified floating.
- No engineering, gravity, bearing capacity, whole-castle connectivity or aesthetic failure is asserted. No model change or new render was made.

## Scope and root provenance
Original ROI x10…65,y8…35,z48…80 selected430 components of `V006 | main facade with one short jointed rib sample`. Their FULL evaluated geometry actually spans x8.819…65.938,y0.65…62.5,z35.4…180. No component was clipped to the ROI. Source has no modifiers on this target; source seeds/bounds/vertexcounts match all430 evaluated components, independently confirmed by root reviewer.

Other visible evaluated objects are broadphase-culled using evaluated object bounds, then full component bounds queried against every full target box plus2m. All target-object components retained as possible intermediary chains.5,237 components exported. Hidden historical originals and named atmosphere/ocean objects do not count as support.

Three roots, chosen for primary wall/body semantics, not merely large AABBs:
1. `V005 | main tower calibrated stone surface`, seed8: main shaft body x42.5…51.5,y30.5…59.5,z42…180.
2. `V008 | gallery with genuine eastern approach portal`, evaluated seed8: gallery mass x5.5…34.5,y27…63,z35.1…69.3.
3. `V012 | ashlar with bounded entrance and north stairwell`, seed576: substantial tower/pier mass x16…24,y19.5…28.5,z34.8…61.2.

Independent lineage/root review: `work/gallery_arcade_audit_v018/support_root_review.json`. Four additional nominated primary bodies (mainshaft24, ashlar24/2064, gallery12020) already lie in the connected graph; relabeling them roots cannot artificially resolve the129. Terrace ledges remain intermediary nodes, not assumed roots.

## Predicates and controls
2,922 actual pair tests; full convex-polyhedron SAT only after every actual face is verified supporting all actual vertices of a closed component. Nonconvex cases use actual triangulated-surface SAT (including coplanar in-plane separating axes) and three-direction ray containment/interior witnesses. No boundary crossings is not automatically separation: nested solids are tested explicitly. AABBs only select candidates/prune distance bounds.

Contact epsilon1e−7m is a NUMERICAL tolerance, not mathematical exact-zero certification. Gaps up to2e−5 are uncertain, not silently bridged. This run found no near/open/parity-uncertain edges in the root exploration. Stored tree edges include1,987 convex-solid contacts,402 actual-triangle contacts and178 interior-witness contacts; explicit chains are in `support_graph.json`.

Controls pass: overlapping AABBs but disjoint coplanar triangles reject; same triangle contact accepts; fully contained tetrahedron with no boundary crossings accepts; translated tetrahedron rejects; broken graph bridge loses root reachability. Separate nearest-surface controls verify triangle-interior projection, segment crossing, known0.25m separation and symmetry.

## Repeated separated ornament families
`unresolved_islands.json` groups rather than prescribing129 tweaks. Nearest external distances are measured on actual triangles via point–triangle and edge–edge minimization, with AABB lower bounds used only for pruning.
- Five floral medallion assemblies: seven target parts each plus a local non-target part; nearest small bronze fitting gap≈0.022413m; those fittings are themselves NOT root-connected. The nearest root-connected actual surface is0.100000m away (separate measured result). A separate front-host ledge AABB gap≈0.19m is **not** substituted for that nearest actual-surface result.
- Two trefoil-loop assemblies:36 target segments each; nearest external actual-surface gap≈0.009056m.
- Four shallow diamond appliques: nearest actual-surface gaps≈0.320123m,0.420000m and0.610001m (two). These are ornaments, not bearing corbels.
- Remaining collars/caps/frame pieces show repeated≈0.03m gaps, many in the17-target neighborhood-limited category. Do not extrapolate their top-cap attachment from a local ring gap.

Actual semantic taxonomy is independently supplied by `west_approach_survey`; large AABB distance to a ROOT is not used as a floating-piece diagnosis. No rendering was requested here, so visible importance and intended decorative reading remain separate from geometric gaps.

## Recommended stopping point
Keep the accepted v018 model unchanged. This audit closes301 contact chains and identifies bounded repeated ornament separation without inventing a load defect. If owner elects a visual follow-up, inspect ONE representative ornament family at practical camera scale before any repair; do not add bridges to all129 pieces automatically. The17 targets with export-neighborhood limits may receive one explicit neighbor expansion only if an attachment verdict is needed. Otherwise retain that uncertainty and return to stable maintenance rather than indefinite detail hunting.

## Visibility and nearest-neighbor reconciliation
A second lightweight read-only Blender visibility query found **zero render-enabled mesh objects omitted solely by viewport hiding or layer visibility** (`visibility_audit.json`). All29 hidden mesh originals also hide_render; no hidden support object was silently excluded by a viewport-only flag. No new geometry export/render/save occurred.

`connected_gap_comparison.json` explicitly separates nearest ANY exported external surface from nearest ROOT-CONNECTED surface for every island. The five rosettes have0.022413m to disconnected brass versus0.100000m to connected structure. Some limited pinnacle cap islands have≈0.03m to another disconnected trim but several metres to a connected root component; the latter does not by itself establish floating, given their documented unexamined extended-neighbor limits. Trefoil/diamond nearest surfaces are already root-connected.

Exact129 component taxonomy, based on repeated geometry rather than asserted author intent: `work/gallery_arcade_audit_v018/unresolved_classification.json` and matching Markdown. No original generator establishing intent was found in the inspected history; labels such as rosette/diamond/pinnacle are geometric interpretations.
