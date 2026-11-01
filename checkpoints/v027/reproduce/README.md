# Guarded first-hall bay recipe — candidate, not yet a checkpoint

This wrapper runs the byte-exact executed builder in `scripts/`, including its pinned sibling plan, support envelope and snapshot helper. The initial candidate `37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255` was built directly, not by this later wrapper. Its successful runtime is not rewritten or retroactively relabeled.

Use exact historical source v026, SHA `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee`, 47,680,699 bytes. Fixed history remains usable even after a later checkpoint removes the current source manifest:

```sh
git -C /path/to/repository worktree add --detach /path/to/new-v026-history 054bc322fed3ad54080471901566c3b1c96d8e8e
python -B /path/to/new-v026-history/checkpoints/v026/restore_checkpoint.py --repository-root /path/to/new-v026-history --output /path/to/new-input/castle_v026.blend
python -B /path/to/recipe/rebuild.py --preflight-only --source /path/to/new-input/castle_v026.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python -B /path/to/recipe/rebuild.py --blender /path/to/existing/blender --source /path/to/new-input/castle_v026.blend --output /path/to/new-output/rebuilt.blend --report /path/to/new-output/rebuilt.json
python -B /path/to/recipe/test_guards.py -v
```

Existing Blender 5.2.3 and ordinary non-optimized Python are required; output parents must exist, outputs must not. Quote paths containing spaces or Unicode. No installation, network or rendering occurs. No native Windows runtime claim is made. The wrapper inherits `PYTHONDONTWRITEBYTECODE=1`, explicitly disables auto-execution, sets no-bytecode before the script, and uses a nonzero Blender Python exit code. Run only one Blender job externally.

The original source and every frozen dependency are checked before/after the child and before publication. Temporary output stays in a fresh private directory. Exclusive hardlinks publish the pair, capturing the owned temporary inode BEFORE linking; foreign replacement inodes are never adopted/deleted during rollback. Unsupported hardlinks fail without overwrite. A crash may leave a completed output: use new paths rather than silently overwriting. There is no automatic source save, current-version promotion or checkpoint publication.

Seventeen pure test methods pass, covering scope/material/profile edits, wrong source bytes/hash, runtime/sibling dependency corruption, UTF-8 native name limits, spaces/Unicode, aliases/symlinks/dangling links/overwrite, optimized Python refusal and both owned/foreign-inode publication rollback. Native injected name collisions and fresh saved semantic equivalence are separate checks, not claimed by these fixtures.

## Meaning and limits

Three shallow pointed twin-curve arches and two high wall bands are new-only EXACT-unioned. Seven course sectors per arch are shallow backed articulation in a continuous solid, not flying detached blocks or overlapping backer skins. Original geometry, shader graph, fixtures, lighting, routes and cameras stay unchanged. The material actually uses Geometry.Position, not per-object Generated coordinates. Source and candidate geometry/support QA and actual image acceptance remain separately recorded evidence.

The old downward walking-camera cadence failed to reveal repeated arches. The revised purpose is inspectable 3D ceiling detail in a separate +8-degree standing-eye view; acceptance of that image does not erase the earlier failure or claim three complete arches are visible in the walk. This workspace is unrelated to the rejected far-cliff v027 study.

Fresh wrapper rebuild and independent semantic comparison are pending an owner-granted native slot. Different Blender saves can legitimately differ in file bytes; compare all source/owned geometry/material/settings semantics against the original candidate and rerun independent public QA. Never weaken a source/hash guard or replace the accepted candidate solely because a rebuild saves successfully.

## Later completed isolated rebuild

The guarded recipe subsequently rebuilt the model from fixed-commit Git-extracted v026 bytes in fresh spaces/Unicode paths. New save SHA `3aca0f43eb9c27f5e7c4194587920db30abf17b7af5b3515950c452986527a10` passed independent semantic equality to original `37c0…`: all 12 compared categories match. The portable full QA then passed source preservation, topology, station support, clearance, crown-contact evidence and negative controls. Extracted historical source files, executed recipe inventory and input source hash remained unchanged; no bytecode caches or new renders were produced. The earlier pending-status files record their original chronology and are not silently rewritten. This does not claim remote publication.
