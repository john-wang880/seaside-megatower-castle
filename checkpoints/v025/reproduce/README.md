# V025 guarded reproducibility wrapper

This guard-only wrapper executes the byte-exact successful identity-corrected builder under `scripts/`. It does not relabel the original candidate as wrapper-built. `rebuild.py` pins source SHA/bytes, plan/SCOPE/helper/builder bytes, four frame memberships,160raw/480evaluated IDs, prior V024 chain/group and native UTF-8 name lengths. It validates before and after the child, then publishes only new output/report via exclusive hardlinks with pre-link owned-inode rollback. Run one Blender worker externally; this is not a process scheduler. No installs/network/render.

Historical input must come from fixed V024 commit, not a mutable latest manifest:

```sh
git -C /path/to/repository worktree add --detach /path/to/new-v024-history 0d332990a252bbb2d51f73e69bdefd34e2931c19
python /path/to/new-v024-history/checkpoints/v024/restore_checkpoint.py --repository-root /path/to/new-v024-history --output /path/to/new-input/castle_v024.blend
python /path/to/recipe/rebuild.py --preflight-only --source /path/to/new-input/castle_v024.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python /path/to/recipe/rebuild.py --blender /path/to/existing/blender --source /path/to/new-input/castle_v024.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python -B /path/to/recipe/test_guards.py -v
```

Use existing Blender5.2.3, ordinary non-optimized Python and new output paths in existing parents; quote paths containing spaces. Source is exact89f9…/47,631,759bytes. No nativeWindows execution claim. Filesystem hardlinks must be supported; no overwrite fallback. A crash between paired publications may leave one complete output; choose new paths rather than deleting/replacing foreign content.

Fifteen pure guard tests pass, including source bytes/hash, plan/scope/runtime mutation, Unicode/spaces, aliases/dangling symlinks/overwrite, optimizedPython, UTF-8 overlong-name refusal and foreign-inode rollback. Native builder name assertions are not claimed as a separately injected Blender negative. The earlier65-byte-name candidate is superseded and retained; this corrected runtime uses the shorter actual Mask name, unchanged geometry.

Four separate evaluated five-solid unions preserve original chamfers, voids and inherited neighboring overlaps. Never globally merge20solids or claim disjoint new objects. Existing V024 union,48weightgroup and entire prior modifier chain remain unchanged. Independent geometry/visual acceptance and fresh semantic rebuild equivalence remain separate pending gates at this recipe staging time.

The first isolated wrapper attempt stopped before source loading because the relocated immutable builder required sibling `scripts/SCOPE.json`. The corrected package includes that byte-exact additional pinned copy. No successful builder/runtime geometry logic changed; the failed input inventory/log remain historical evidence. Fresh run uses a new directory.

## Completed validation (later evidence)

Owner, parent and independent art director accepted the rear comparison; hero showed no visible regression (not pixel identity). Fresh Git-only guarded rebuild SHA `48f1270189ab16598ff709188a03a057efe608488ecdc6c60d1922fb88059160` passed independent semantic equivalence to accepted `8a3590082c99a69d50d444f77165fae57fb611cf069cecda03fdf0c6c17cadd2`, all boundary/void/intersection/preservation/native rollback gates,9geometry and4model negatives plus7math controls. Exact source,11-file executed recipe inventory and independent QA bundle remained unchanged. No caches or renders. The executed recipe retains its earlier README/provenance chronology; this later prose update does not rewrite those recorded hashes. Remote publication is parent-owned and not claimed here.
