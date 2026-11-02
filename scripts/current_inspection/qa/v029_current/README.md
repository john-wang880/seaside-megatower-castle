# Independent v029 inspection / optional quality / selection-index QA

This validator tests derived inspection copies, never updates the canonical model. It needs four freshly exported copies with matching receipts from the frozen tool: `default` (no index, no tree mode), `off` (index enabled, no tree mode), `high` (index plus HIGH), and `low` (index plus LOW). Native Blender 5.2.3 is required; no rendering or model saving is performed.

```
PYTHONDONTWRITEBYTECODE=1 python -B /absolute/qa/edit_index/run_qa.py \
 --source /absolute/castle_v029.blend \
 --baseline /absolute/castle_v018.blend \
 --tool /absolute/scripts/current_inspection \
 --default /absolute/viewers/default.blend --default-receipt /absolute/viewers/default.json \
 --off /absolute/viewers/off.blend --off-receipt /absolute/viewers/off.json \
 --high /absolute/viewers/high.blend --high-receipt /absolute/viewers/high.json \
 --low /absolute/viewers/low.blend --low-receipt /absolute/viewers/low.json \
 --blender /absolute/blender-5.2.3-linux-x64/blender \
 --output-dir /absolute/new-external-results
```

The current source SHA is `4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5`. Historical v018 baseline SHA is `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`; restore its manifest/chunks using the immutable fixed v018 commit `89cce41` lineage. The baseline is used solely for original near-tree geometry/material/transform/wood lineage, not to claim the whole current scene equals v018. No historical helper is imported at runtime.

The runner refuses optimized Python, existing output, symlinks and parent traversal; source/baseline/receipts/entire QA and tool inventories are checked. Inherited no-bytecode prevents subprocess caches. Output and cache must remain outside frozen payloads. Reusable API code is manual Text only; no autoexec, handler, install, render, unhide or geometry change.

Three sequential native phases preserve the proven RNA-reacquisition safeguards: four-mode exact source/reopen tests; repeated manual registration/index/20bookmark/HIGH-LOW actions;37selection negatives plus6 direct native `Panel.draw` recording-layout cases. Eight pure comparison tests run first. Target expectations are fixed in `expected_scope.py`:20bookmarks,19derived cameras,five groups/45entries,13snapshot categories,27quality negatives,37selection negatives,64repeated LOW refusals;56positive bookmark/index action records across OFF/HIGH/LOW. Valid panel has five buttons; foreign/unmarked/stale opt-in states show ERROR and no accepted buttons. This is native background API evidence, not desktop GUI or Windows interaction evidence.

The five accepted groups are two connected-room local-shell pieces,20old receiving lantern meshes,one ceiling-bay mesh,two HIGH tree meshes and20stores lantern meshes. No light sources or large foundation/ashlar replacements are indexed. Existing historical names saying `candidate`, `study` or `UNACCEPTED` remain provenance. No rejected far-cliff geometry is included. Index labels are not shared-material-graph or edited-scene certification; target edits fail closed until a fresh canonical export. LOW hides the high-tree objects and restores only the original target foliage via the existing owned mask; it does not alter source wood or save file size.

Exact non-selection preservation is tested after restoring only test-owned selection and bookmark camera/viewport fields. Every index action independently leaves camera/view/quality state unchanged. Failure injection must restore full selected set and active object without undo. The known three traveler-derived UI selection fields are individually recorded, never a blanket attribute/weight exclusion.

Prior v028 harness/RNA crash chronology remains historical provenance in earlier public QA reports. This v029 adapter changes source/catalog/index pins, namespace, expected counts and the negative fixture's current shell identity only; it does not weaken predicates or treat earlier test reports as current acceptance.
