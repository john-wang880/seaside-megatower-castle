# v027 hall inspection copy

Fresh local actual export/reopen QA passed; remote publication is separate. No live checkpoint manifest has been fabricated. Reviewed source is `castle_v027.blend`,47,773,404bytes, SHA256 `37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255`.

16 manual bookmarks /15 added cameras. Original15 camera records remain exact except owned INSPECT27 namespace. Only `ceiling_inspection` is new: standing eye(−3,38,30.65), original first-leg yaw/lens26/aspect960×694, pitch+8°. This is a separate architectural inspection; the historical downward walk is unchanged. Exact original proposal and actual candidate recipe/receipt are archived under provenance. The unrelated rejected cliff trial is not part of this model/tool.

## Explicit opt-in export, with the real accepted checkpoint manifest

Use existing Blender5.2.3, ordinary Python (not `-O`):
```sh
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys; sys.dont_write_bytecode=True' --python "$tool/export_inspection.py" -- --repository-root "$repo" --source "$source" --output "$new_viewer" --report "$new_report"
```
The highest numeric real checkpoint manifest must be reviewed v027. Unknown v028, stale v026, ambiguous v27/v027, wrong source bytes/hash/catalog, aliases/symlinks and existing destinations are refused. Source is never saved. Output/report must be new, outside immutable checkpoints. Exclusive hardlink publication has no overwrite fallback; handled rollback removes only invocation-owned inodes. A crash may leave a viewer without its report: choose a fresh pair, do not adopt/delete it blindly.

Open the derived file with autoexec disabled. In Text Editor explicitly run `INSPECT27 | Run manually for bookmarks.py`; then N-sidebar → Castle检查. No handlers/addon installation/automatic registration. Existing hero remains saved default. Buttons change camera/viewport only, not model/quality/LOD/light/material/frame/resolution. Reference aspect is advisory, not automatically set. Repeated registration is idempotent; foreign or modified ownership fails closed. Provenance certifies export, not arbitrary later edits.

18 implementation +24 independent pure tests are required; fresh native gate passed13 original-state categories,16 bookmark operations,20 negative API cases, repeated registration and disabled-script reopen. No native Windows/desktop click claim. Historical15-view v026 tool remains fixed at Git054bc322; all historical camera provenance hashes remain unchanged.
