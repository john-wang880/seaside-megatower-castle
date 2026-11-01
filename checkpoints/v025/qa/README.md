# Independent v025 four-return-frame QA

Read-only, self-contained QA for four separate unions of actual evaluated chamfered frame solids. No render, model save, network access or installation. The original v024 six-solid union and both existing target modifiers remain protected source data, not part of this batch.

## Inputs and invocation

Historical v024 source SHA: `89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856`.
Reviewed v025 candidate SHA: `8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2`.
Restore these using their public checkpoint manifests/history; the runtime does not require an old private workspace, standalone asset or intermediate model.

```sh
python -B run_qa.py \
  --source '/absolute/history/castle_v024.blend' \
  --candidate '/absolute/restored/castle_v025.blend' \
  --output-dir '/absolute/existing-parent/new QA reports' \
  --blender '/absolute/compatible/blender'
```

Actual tested executable: official Blender5.2.3. Output directory must be new and outside frozen QA/checkpoint trees. Existing outputs, symlinks, parent traversal, wrong source, changed/extra payload files and optimized Python are refused. Every Blender command disables autoexec and explicitly disables Python bytecode before script loading. Full payload inventory and all model hashes are checked again at the end. Failure evidence remains for diagnosis; no model is overwritten.

A separately saved rebuild may have different file bytes. Supply `--accepted '/absolute/restored/castle_v025.blend'`; that reference must have the reviewed SHA above. Full persistent/evaluated semantic equality runs **first**, and only then is the rebuilt SHA admitted to the geometry chain. A caller-provided arbitrary SHA is not an alternative acceptance gate.

Check `SUMMARY.json` and its referenced JSON gates, not just exit status. Normal chain has11 Blender calls: preservation/export, exact-zero triangulation audit, four in-memory model negative fixtures, native LOW, and four adjacent scans. Rebuild adds one semantic-comparison call. Pure checks run the four-boundary/cross-interface proof, nine geometry negatives, six partition controls and the compensating-area control.

## Protected scope

`SCOPE.json` pins four groups of five source components at rear planes Y56,57,58,59.20000076293945. Exactly160 new raw weight-1 assignments are added as a uniquely owned group, followed by a third Mask **after** the existing BEVEL and V024 Mask. Exactly480 evaluated vertices are removed. All retained point/edge/face/corner attributes, normals and deform weights remain exact; original48weights, old modifier primitives, standalone V024 union, hidden originals and every other scene datablock remain exact.

Each saved output must independently preserve its five-solid occupied boundary, real recesses, original single-face surfaces, chamfers, world-coordinate material and silhouette. Do not use raw-box unions or convex hulls. Four separate unions deliberately retain three pre-existing inter-frame volume overlaps (~773.96384,553.67966,427.21009 coordinate-unit³). Non-neighbor groups remain disjoint. This is not a claim that all four objects form a globally disjoint or self-intersection-free collection.

## Independent geometric proof and tolerances

Actual source convex face polygons are clipped by all other source halfspaces. Equal same-facing overlaps receive one owner. Saved triangles are compared to that independently constructed boundary in both orientations/directions. Coverage is a **set** calculation: uncovered area and multiply covered area are measured separately, so an equal-area hole and duplicate cannot cancel in a signed total. Signed-volume and cross-frame intersection comparisons are additional checks, not substitutes for boundary coverage.

Before measuring residuals, each group declares a distance budget of four maximum float32 source-coordinate ULPs. This is1.52587890625e-5 for the first two groups and3.0517578125e-5 for the upper two. Per-face area budget is `4*perimeter*distance_budget + 16*distance_budget²`; volume budget is `2*saved_surface_area*distance_budget`. Reports expose per-face residuals and budgets. Accepted run: uncovered area0 in every group, numerical duplicate residual1.05e-11…2.36e-11, maximum plane displacement2.70e-6, maximum individual volume difference6.25e-8. Existing cross-frame intersection differences are below2.25e-9. These are saved-float numerical bounds, not exact-rational whole-model claims.

The four adjacent scans use evaluated bounds before culling and actual triangle/BVH plus oriented coplanar polygon checks. Actual run examined17/18/16/14 neighboring surface objects and found no positive-area coplanar contacts with the new unions. Opposite-facing interfaces are distinguished from same-facing skins. This is bounded to the complete four union bounds, not the whole castle.

### Exactly zero derived tessellation triangle

Group3 has one **exact-zero-area loop triangle45**, not a zero-area saved polygon. Its parent polygon21 is positive-area0.0991015341126256, planar and convex, with one collinear boundary vertex. Exact rational arithmetic on the saved float32 coordinates proves collinearity/planarity. Actual nonzero triangle44 exactly covers the parent convex hull; no positive-area overlap/hole exists. All saved polygons remain positive and closed/oriented.

Only exact-rational-zero derived triangles are omitted from normal/area integration; no epsilon-based near-zero filtering is used. The runtime audit requires the known single case and proves the actual parent/triangle coverage. The model is not modified to work around an undefined zero-triangle normal. Other small Boolean coordinate rounding remains subject to the same predeclared boundary budget.

## State and negative controls

Native LOW disables only the new Mask and hides only the four new objects, returning to current v024. Inherited new-group values are compared bit-exactly to independent original-chain propagation of the160 raw assignments. Only proven group1 values are normalized for LOW render-semantic comparison; all old group0 values remain strict. Repeated state assignments and exact raw rollback are checked.

Nine **exported actual-geometry** negatives: translation, missing triangle, duplicate triangle, reversed orientation, raw-box union losing chamfers, and filled genuine recess for each of the four frames. Four **actual Blender in-memory** negatives: extra new Mask weight, changed old V024 weight, changed old V024 union vertex, unrelated hidden original mutation. No fixture saves a model.

Seven mathematical controls: six convex-partition arrangements, plus equal missing/doubled half-face areas. The last has unchanged signed area/volume but must report0.5 uncovered and0.5 duplicated and reject. `python -B test_runner.py` adds13 orchestration guard tests using temporary fixtures/mocks. Linux paths with spaces/Unicode tested; no native Windows/desktop interaction claim.

Only the established three Traveler SUBSURF objects' derived evaluated edge-selection UI fields are separately normalized by the snapshot helper. Raw selection, geometry, other attributes, old masks/deform weights and materials stay exact.

## Superseded evidence

The earlier `bd2f…` candidate is **not** this accepted identity. Its proposed65-character new Mask name was truncated natively. `reports/mask_diagnostic.log` and `preservation_superseded_name.log` document this; the corrected exact50-character name is in SCOPE and asserted by the final recipe. No geometry was redesigned. `triangulation_initial.log` records an initial all-polygons area-comparison assumption; the final audit distinguishes exact-zero parent proof from unrelated saved-coordinate rounding, while the geometric budgets remain unchanged.

Historical reports may contain original execution paths as provenance. No runtime import depends on those paths. Visual same-camera acceptance, structural/load safety, general navigation and waterproofing are not certified by this tool.
