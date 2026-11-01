# Independent QA — one western lowest-tier rib

Portable read-only Blender5.2.3 scripts; bundled NumPy only, no installation/render/model save. Source accepted v021 SHA256 `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`. Candidate SHA256 `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`. Restore the historical source from the project's recorded v021 checkpoint; input hashes, not arbitrary local filenames, bind the test. All required plan/build-range/camera data are bundled and SHA-pinned in common.py.

## Run sequentially

Use absolute quoted paths. Each report must be new and its parent must exist. Never use optimized Python. Every call must include both the error-exit flag and the explicit no-bytecode setting; Blender can ignore PYTHONDONTWRITEBYTECODE from the host environment.

```sh
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python-expr "import sys; sys.dont_write_bytecode=True" --python "$QA/critical.py" -- --source "$SOURCE" --candidate "$CANDIDATE" --report "$OUT/critical.json"
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python-expr "import sys; sys.dont_write_bytecode=True" --python "$QA/deeper.py" -- --source "$SOURCE" --candidate "$CANDIDATE" --report "$OUT/deeper.json"
```

Then invoke `negative.py` five times with the same input options, unique report paths and `--case mask`, `hidden_original`, `enlargement`, `orientation`, `backing_gap` respectively. The hidden-original fixture may additionally create a `*_mutation_full.json` failed-preservation record; this is expected diagnostic evidence, not a positive result. Never overwrite an existing fixture report.

Check process exits AND JSON:
* critical: `pass`, `source_unchanged`, `candidate_unchanged`, all `full_source_checks` values true; complement exact,16 positive closed parts, both seats,15 core contact witnesses and60 normal-view joint probes.
* deeper: `pass`, source/candidate unchanged, active non-target equality, repeated paired rollback; `nonadjacent_self_crossings` and `same_facing_new_new_coplanar_patches` empty; practical ray classifications55backing/5unchanged-original-occluder for this exact camera.
* five negatives: `rejected` true, exact input hashes, intended actual assertion—not a malformed setup rejection. Extra weight / hidden original mutation / enlarged course / reversed face / shortened backing must fail their actual invariant.

## Rebuild with different save bytes

First run `validate_repeat.py --accepted "$ACCEPTED_991" --rebuilt "$REBUILT" --report "$OUT/repeat.json"` with the same Blender safety flags. Require `pass`, `inputs_unchanged`, and every category check true. Only after this pinned accepted-model comparison may the other scripts use `--candidate-sha256 "$EXACT_REBUILT_SHA"`. Supplying an arbitrary hash alone is not acceptance.

## What is proved

Exact source persisted attributes, topology, normals, existing deformation weights/Mask modifiers, materials/nodegraphs, world, lights, cameras, scene and collections survive after normalizing only this new owned8-vertex group/Mask plus replacement object/mesh/collection. Full target complement POINT/EDGE/FACE/CORNER attribute mapping is explicit. Earlier v019 forest, v020 threshold and v021 pier work is not broadly exempted.

The replacement comprises13beveled courses, continuous inset core and two original-end continuations. Actual component topology/orientation/positive volumes are checked; savedfloat32 cut rings follow original four vertical edges, original tilted terminal faces remain exact, backing28/35mm insets and10mm end overlap are exact. The actual source cornice loop triangles contain all8cut corners; finite interior witnesses connect core to courses/continuations. These are geometric contact witnesses, not a load calculation.

All new geometry stays inside the old prism; no enlarged occupied envelope or new window/navigation encroachment is introduced. Joints/bevels intentionally remove narrow material. **This is not exact occupied-volume equality like the earlier bridge-pier cleanup.** No unrelated whole-castle navigation certification is implied.

No strict interior crossings were found between nonadjacent triangles of each piece. Shared-vertex or coplanar degeneracies are outside that narrow predicate; positive-area near-coplanar new-new interfaces are checked separately with2µm plane bound and1e-8m²reporting floor. Same-facing positive patches fail; opposite-facing support contacts are recorded separately. Source-neighbor occupied intersections cannot enlarge because replacement lies inside source envelope; this is not a global manifold or zero-intersection claim.

All12joints have five inset normal-view backing probes. At the frozen practical camera55rays hit replacement backing. Five uppermost-joint rays first hit nearer unchanged diagonal bracket component288 (source faces220/221); these are legitimate occlusions, not transparent holes. No broad original-object whitelist: exact component, joint12, and shorter hit distance are required. Recessed backing does not prove opacity for every possible grazing silhouette ray.

Paired rollback disables only this Mask and hides the new object in viewport/render; repeated HIGH/LOW states are checked. Precisely8owned stored deform weights are separately verified then normalized only for rollback render-semantic equality. The historical three explicit Traveler SUBSURF evaluated UI edge-selection fields are narrowly schema-checked; persisted selection and all other attributes remain exact.

## Provenance and limits

PROVENANCE.json binds the executed local checks and adapter hashes. The adapter additionally combines the separately tested exact-profile/native-Mask checks into critical.py. Original executed scripts/reports remain unchanged. This bundle must pass a fresh isolated full run before publication. Actual practical visual acceptance and hero review are separate artistic gates; mesh QA alone does not prove aesthetic gain. No source edits, renders, new materials, whole-forest/rib expansion or engineering certification occur here.
