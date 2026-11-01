# v021 independent, read-only QA

Requires Blender 5.2.3 with bundled NumPy. No pip installation, rendering, model saving, private asset, workspace path or cached model is used. Run scripts from any current directory. Keep assertions enabled; `-O` is explicitly rejected.

## Inputs

* Historical source v020: restore from Git commit `23fd4aa`, SHA256 `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`.
* Accepted candidate: SHA256 `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`.
* Local `data/plan.json` is pinned to SHA256 `660d847827193a6624d6f9ab91e51d1621cac34bc28bb0cdf19e06c94ba3361a`.

The models are explicit CLI inputs. No historical intermediate .blend is required. The source and candidate must be distinct files; reports must be new paths in an existing directory. Every Blender invocation must include `--python-exit-code 1`; inspect report gates as well as process exit status.

## Complete gate

Shell variables below stand for absolute paths; quote all paths, including Windows paths with spaces or Unicode. Execute sequentially (one Blender process at a time):

```sh
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python "$QA/validate.py" -- --source "$SOURCE" --candidate "$CANDIDATE" --report "$OUT/preservation_geometry.json"
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python "$QA/planes.py" -- --source "$SOURCE" --candidate "$CANDIDATE" --report "$OUT/planes.json"
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python "$QA/state.py" -- --source "$SOURCE" --candidate "$CANDIDATE" --report "$OUT/state.json"
```

Then run `negative.py` five times with the same source/candidate inputs, unique reports and `--case` respectively `bounds`, `orientation`, `material`, `mask`, `unrelated_source`. Each opens the real model and mutates only memory, never saves.

Required JSON gates:
* preservation: `pass`, `source_unchanged`, `candidate_unchanged`; every `checks.normalized_full_source` value true.
* planes: `unchanged`, `source_unchanged`, `all_six_planes`, `evaluated_bounds_before_cull`; `exposed_same_facing_patches == 0`.
* state: `pass`, `active_non_target_evaluated_exact`, `repeated_high_low_high_exact`.
* each negative: `rejected == true`, correct case, expected assertion (not an input/setup failure), exact input SHA256 values.

## Rebuilt save with different bytes

Before allowing a rebuilt candidate into the gate, prove full semantic equality to the pinned accepted model:

```sh
"$BLENDER" -b --factory-startup --disable-autoexec --python-exit-code 1 --python "$QA/validate_repeat.py" -- --accepted "$ACCEPTED" --rebuilt "$REBUILT" --report "$OUT/repeat.json"
```

Require `pass`, `inputs_unchanged`, every `category_checks` value true. Then run the complete gate with `--candidate "$REBUILT" --candidate-sha256 "$EXACT_REBUILT_SHA256"`. An arbitrary caller-supplied SHA is **not** acceptance: the prior comparison against pinned accepted457 is mandatory. Preserve both receipts. Different compressed .blend save bytes alone do not indicate geometry drift.

## Scope and numerical boundaries

See SCOPE.md. Exact occupied-set union, all source raw attributes/deform weights and non-target evaluated semantics are checked. Only the two new groups/modifiers/objects/meshes/collection are normalized. The existing v019 tree and v020 threshold remain strict.

The six-plane audit separates opposite-facing support interfaces from same-facing duplicate patches. Three same-facing shaft-bottom triangles remain strictly buried inside the foot, with minimum margins X0.424999237m/Y0.5m/below0.300000191m/above2.100000381m. This is not a global zero-coplanars assertion. Plane tolerance1e-6m and reporting floor1e-8m² are numerical bounds, not physical tolerances.

Rollback is a paired operation: disable the two owned Masks and hide both new union objects in viewport/render. Disabled modifiers leave the precisely checked owned deform weights stored; only these records are removed for rollback render-semantic comparison. Never enable both original and union surfaces simultaneously or hide both. Repeated paired LOW/HIGH transitions are tested in memory.

The only historical derived UI exception is evaluated `.select_edge` plus duplicate edges.select on the three explicitly named Traveler SUBSURF meshes. Schema/count agreement is required; persisted selection/geometry/other attributes remain exact. No full-castle navigation, manifoldness, original author-intent, structural load or engineering certification is claimed. Practical same-camera before/after visual review remains separate.

## Provenance / test status

This is a portable adaptation of the executed independent candidate QA, not a claim that the adapter has already run. `PROVENANCE.json` binds original executed code/reports and adapted code. The executed originals remain unchanged in the owner's audit history. Before publication, run this copied bundle in an isolated directory on restored source/candidate and inspect all gates above.
