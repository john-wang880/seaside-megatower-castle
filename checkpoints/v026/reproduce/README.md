# V026 guarded reproducible recipe

The guard-only wrapper runs the exact successful candidate builder, not a rewritten geometry algorithm. Initial candidate `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee` was built directly, not retroactively relabeled wrapper-built. `scripts/` includes all sibling dependencies, including a byte-exact pinned SCOPE copy. `RUNTIME.json` and wrapper constants pin builder/helper/plan/bothSCOPE files.

Exact historical input: V025 SHA `8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2`,47,663,562bytes. Use fixed history, because superseded checkpoint manifests may be removed from latest tree:

```sh
git -C /path/to/repository worktree add --detach /path/to/new-v025-history 06cf897ea73fa105ba27cb7dd79af6df18587c9a
python /path/to/new-v025-history/checkpoints/v025/restore_checkpoint.py --repository-root /path/to/new-v025-history --output /path/to/new-input/castle_v025.blend
python /path/to/recipe/rebuild.py --preflight-only --source /path/to/new-input/castle_v025.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python /path/to/recipe/rebuild.py --blender /path/to/existing/blender --source /path/to/new-input/castle_v025.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python -B /path/to/recipe/test_guards.py -v
```

Existing Blender5.2.3, ordinary non-optimized Python and new output paths in existing parents are required. Quote spaces/Unicode paths. No nativeWindows claim, installation, network or render. Local filesystem must support hardlinks; no fallback overwrite. Run one Blender worker externally. Private temporary staging contains builder output; source/runtime identities are rechecked after child/save and before exclusive paired publication. Rollback only removes an inode captured from the owned temporary before linking; a foreign replacement survives. Crashes can leave one completed output, so choose new paths rather than silently replacing it.

Nineteen pure tests pass, including source bytes/hash, scope/runtime/material/16-vertex mapping, shared-user delta, inherited contact scope, UTF-8 length, missing siblingSCOPE, aliases/overwrite/symlink, optimizedPython and foreign-inode rollback. These do not claim native injected collision or geometry negatives.

Only two actual box solids are unioned. Visible shaft gets an identical single-user mesh derivative before16deform weights/Mask; original shared mesh and hiddenV004 stay unchanged. Effective calibrated OBJECT material differs from preserved raw deep-slate slot. Existing top contacts with original polygons13/28 remain; no broader cleanup. Independent exact geometry/contacts/source proof, actual views and fresh semantic rebuild remain separate gates. Differently saved .blend files can differ in bytes; never replace accepted bytes solely because a rebuild saves successfully.

## Later completed gates

All three actual views passed owner review; lateral was also accepted by parent/art director. Fresh Git-only guarded rebuild `2dfc901717c43cc3ec3bbfc62b0eca27914cdc6524caf78f22e310a4a13ebfd6` passed semantic equivalence to original candidate `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee` and full public independent QA:5geometry negatives,4native model negatives,7convex controls and9coplanar controls. Hidden shared original, effective OBJECT material, nativeLOW and full-pointer rollback remain valid; two inherited top contacts remain. Source,11-file executed recipe inventory and QA bundle stayed unchanged; no caches or renders. This later prose note does not overwrite the earlier executed README/hash chronology. Historical adjacency corrections are separately archived; no global coplanar-free or remote-publication claim.
