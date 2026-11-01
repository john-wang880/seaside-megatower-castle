# V024 bounded rear-surface union — reproducible wrapper

This wrapper is separate from the **byte-exact successfully executed** builder in `scripts/build.py`. It does not claim the initial candidate was produced by the wrapper. `RUNTIME.json` records the executed builder/helper/plan and independent SCOPE bytes; `rebuild.py` pins those hashes in code and checks them before and after the child process, before publishing new outputs.

Input must be the exact accepted V023 file,47,628,324bytes, SHA `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51`. Restore it from the pinned historical Git commit below, not the latest branch: superseded checkpoint manifests may be removed from the current tree. The local checkout must already contain that commit and its objects. The restore/build tools do not install software, access the network or render.

```sh
git -C /path/to/repository worktree add --detach /path/to/new-historical-v023 4a7cd90ceb9d545de67951cae536e2c4604a547a
python /path/to/new-historical-v023/checkpoints/v023/restore_checkpoint.py --repository-root /path/to/new-historical-v023 --output /path/to/new-input/castle_v023.blend
python checkpoints/v024/reproduce/rebuild.py --preflight-only --source /path/to/new-input/castle_v023.blend --output /path/to/new-output/candidate.blend --report /path/to/new-output/build.json
python checkpoints/v024/reproduce/rebuild.py --blender /path/to/existing/blender --source /path/to/new-input/castle_v023.blend --output /path/to/new-output/candidate.blend --report /path/to/new-output/build.json
```

Output parents must exist; output/report must not. Use ordinary non-optimized Python and existing Blender5.2.3. Quoted paths with spaces/Unicode are supported by argument arrays. No nativeWindows execution is claimed. Hardlink publication must be supported by the local filesystem; it fails closed otherwise. The builder runs in a private temporary output directory, so its publication cannot overwrite final destinations. The wrapper verifies source/runtime/plan identities after save, then exclusively links final model/report. Handled failures remove only a still-owned inode captured **before** linking; a foreign replacement is never adopted. A crash between final links can leave one complete output; choose new paths rather than silently replacing/deleting it. Run one Blender worker at a time; this bounded wrapper is not a global process scheduler.

## Exact geometric scope

Source object `V008 | gallery with genuine eastern approach portal`. Only six actual evaluated chamfered solids56/80/104/128/152/176, corresponding to48rawvertices16…63, are replaced by their sequential BlenderEXACT union. Original global clamp-overlapBEVEL stays fully unchanged; an owned invertedMask follows it and removes exactly144evaluated vertices. The source raw topology remains as rollback; one union object/mesh/collection is added. Same existing GeometryPosition material and original object matrix, no smoothing/style/material redesign. The other20affected components are explicitly deferred.

Builder guards cover selected mapping, closed/oriented topology, positive signedvolume, exact duplicate polygons, basic nonadjacent transverse triangle crossings, exact evaluated complement facecoords/material/smoothing, raw mesh rollback attributes, originalBEVEL primitive and originalmaterial. They are **not** a substitute for independent full-attribute complement, occupied-set/exterior boundary coverage, broader self-intersection and actual-camera visual acceptance.

Appending theMask initially changed only BEVEL.is_active UIstate; two pre-save attempts stopped. Successful builder restores that original UIflag and requires complete primitive equality—no setting exclusion, altered bevelwidth or tolerance creep. Those failed attempts produced no accepted model. Native save's unavailable thumbnail-cache warning does not indicate source/model write failure; source hash was verified unchanged.

## Verification

`test_guards.py`:14stdlib tests pass, including wrongsource bytes/hash, pinned runtime, altered scope/material/tolerances, output collisions, Unicode/space paths, aliases/dangling symlinks, optimizedPython and foreign-inode rollback. Existing Blender-name collisions are checked by the immutable builder; pure tests do not claim native injected-name testing. Fresh guarded execution from a Git-only restored input passed: rebuilt SHA `dae21a80556a1ba6104ca268401a76e3a3522318f67b9d4b52a40f452a938260` is semantically equivalent to accepted SHA `89f9f6a8a57103d99100935b96624469ddf1fd52b9703e0d9177a352e735c856` across all12 emitted snapshot categories, with the independent helper’s explicitly documented derived traveler UI-edge normalization. Full independent boundary/preservation/rollback checks,5geometry negatives,2model negatives and6math controls passed. Source,10-file historical recipe inventory and QA bundle remained unchanged; no Python caches were created. See the archived rebuild receipts and independent QA reports for exact identities. Saving metadata may change .blend SHA; do not replace accepted bytes merely because a rebuild succeeded.

## Publication documentation clarification

The public README now pins historical restoration to commit `4a7cd90ceb9d545de67951cae536e2c4604a547a`. This is a prose/command clarification after the isolated rebuild recipe was staged. Its earlier README hash remains in that run’s input inventory; all executable builder/wrapper/helper, plan and SCOPE bytes are unchanged. Do not overwrite the historical run inventory with this later documentation hash.
