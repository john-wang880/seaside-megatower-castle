# Independent bounded QA plan: one complete lowest-tier western rib

Status: planning only, no candidate acceptance; no Blender run. Canonical source is v021 SHA256 `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`. Evidence: source `work/west_lower_tier_v021/survey.json`, FEASIBILITY.md and camera_preflight.json. Builder owns candidate and sole Blender slot until explicit release.

## 1. Bind actual authored scope

Target is `V012 | retained west rib facade with buried-route clearance`, original component56/vertices56–63,8vertices/6faces, world-identity, one mesh user and no existing modifiers/groups according to survey. Confirm from actual source, not a stale assumption. Its original88m prism has constant XY section and mildly tilted top/bottom. Approximate visible tier79.43–103.19 is NOT a replacement for actual authored boundaries or a license to flatten original seats.

After candidate exists, obtain exact names/owned Mask/group, selected vertex IDs, course/backing/continuation component ranges and physical joint limits from builder. Check all input hashes; no implicit access to intermediate/private models. Freeze expected names/parameters only after explicit candidate schema is supplied. No count-driven acceptance if real pieces differ.

## 2. Strict preservation / reversible state

Adapt the proven v021 public snapshot/complement code, as NEW files, with explicit --source/--candidate/--report and a bundled input specification. Preserve the existing v019 tree weights/Mask, both v021 pier Masks, v020 threshold geometry, every hidden original and all materials/world/lights/cameras/scene/collection data.

Verify exactly8 owned weight1 vertices, one uniquely owned group and inverted Mask, exact mode/threshold and native remaining flags. No broad weight-ignore: normalize only this explicit new group on this target; all previous deformation weights remain byte-exact. Source target raw topology/attributes/normals/material indices remain exact. Map all kept POINT/EDGE/FACE/CORNER indices and compare every evaluated attribute, normal/material and topology field; enumerate any unexpected isolated-vertex changes instead of suppressing them.

All non-target evaluated render geometry and source object properties remain exact. New meshes use explicit existing material slots and identity transforms; verify no new material/datablock overrides or changed world-coordinate mapping. Paired rollback disables only the owned Mask and hides all replacements in viewport/render; its evaluated scene must equal canonical source after separately checking the retained owned nonrendering weight records. Repeated LOW/HIGH/LOW/HIGH must be idempotent. Mixed states are not valid rollback.

## 3. Actual geometric acceptance

* Decompose actual evaluated replacement meshes into connected components. Check every intended solid edge incidence2, consistent orientation, positive signed volume, no degenerate face triangles, and unexpected nonadjacent triangle crossings. Do not infer geometric embedding merely from closed topology.
* Use authoritative `calc_loop_triangles`, with local coordinates/double precision where needed. Source tiny nonplanarity must not be flattened by arbitrary quad tessellation.
* Check all new vertices/face interiors remain inside original source volume/envelope. For convex shell halfspaces, first establish convex eligibility from actual source triangles; otherwise use solid-angle winding and explicit triangle intersection. No enlarged XY envelope or modified distant upper/lower geometry.
* Original tilted end face coordinates and normals must remain exact in continuations. Prove the untouched upper/lower occupied sections equal source—not just shared endpoint bounds. Verify each continuation/course/backing transition has an intentional contact, not accidental face-area duplication or open seam.
* Derive all joint intervals from actual geometry. Prove backing covers every interval continuously and is contained in the original rib. Test positive closed overlap or exact shared contact area between courses/backing/continuations, recording actual finite margins. Check exposed same-facing coplanar patches separately from opposite-facing support interfaces and intentional buried intersections. No blanket new-new collision whitelist.
* Cornice seats: use actual source lower/upper components and candidate pieces. Original witnesses around(-120.44,85.3,79.3) and(-120.44,85.3,103.4) are starting evidence, not sufficient final gate. Confirm actual retained contact at both ends, with double-precision winding on authoritative triangles where float parity disagrees. State only bounded geometric contact, not load capacity.
* Neighbor/window clearance follows source containment if exact no-enlargement holds. Still inspect actual nearby evaluated triangle intersections for unintended exposed crossings; broadphase uses evaluated bounds. Existing source intersections may remain only if explicitly identified by geometry; do not exempt whole objects. Preserve existing lancet glazing and all non-target geometry.

## 4. Backed joints are not universal opacity

Recessed backing inside the old section cannot occlude every possible grazing ray at its outer silhouette. Thus do not claim the replacement exactly preserves every original occupied point or all-angle opaque silhouette. Prove continuous backing and bounded practical-camera coverage separately. At each actual joint, cast rays from the frozen practical camera across the visible inset joint patch, including near-edge probes; classify hits on backing/courses versus unrelated architecture/background and measure witness margins. Any visible transparent slit, extreme dark gap or ladder effect is a hold for actual same-camera review, not fixed by increasing sampling tolerance.

If all replacement geometry stays within source rib, no new route/intrados occupancy can be introduced; full unrelated navigation rerun is unnecessary. Removal of material for joints is an intentional artistic change, not exact occupied-union equivalence like v021 pier cleanup.

## 5. Decisive negative controls

In-memory only, no saves: (a) extra Mask weight on non-target vertex; (b) mutate hidden original/previous forest weight; (c) expand a course vertex outside original envelope; (d) reverse/open a replacement face; (e) create one backing gap at an actual joint or shift a seat off its host. Each must fail its intended invariant, not setup/CLI validation. Add a mixed-state rejection test only if a toggle API is supplied; otherwise document required paired state and test evaluator equality directly.

## 6. Execution / stopping condition

No Blender until builder/owner releases slot and exact candidate hash is known. Technical gate first; then owner schedules identical-camera actual before/after review. Aesthetic improvement is not established by polygon count, closedness or a valid backing. Stop at rejected visual gain; no broad forest/rib replication, new materials or arbitrary tolerances. If accepted, copy only portable QA code/spec/README with hashes; rerun isolated restored-source/candidate gates before publication. Historical executed validators remain untouched.
