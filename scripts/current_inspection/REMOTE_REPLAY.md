> Local v028 three-mode native validation passed. This is the separate fresh Git-only remote replay recipe; no remote pass is implied by local results.

# Current v028 three-mode independent QA

Runtime five files and executed independent QA Python are byte-identical to the successful local run. `qa/reports/SUMMARY.json`/`qa/reports/modes.json` record13 source categories,27 native negatives,18 bookmarks in each ofOFF/HIGH/LOW, and8 pure controls. This entrypoint supersedes inspection-only QA for quality acceptance. It does not export, render, save or publish models.

Use only a fresh repository archive/tool, exact restored v028 model SHA `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096` and independently restored historicalc46 target-lineage model. Historical c46 is QA-only, never required by user buttons. Paths need quoting; outputs must be new and outside tool/QA trees. Set environment `PYTHONDONTWRITEBYTECODE=1` for **all subprocesses**, not only host`-B`. No input caches accepted.

```sh
export PYTHONDONTWRITEBYTECODE=1
tool="$repo/scripts/current_inspection"
mkdir "$out"
for mode in OFF HIGH LOW; do
  extra=()
  if [ "$mode" != OFF ]; then extra=(--tree-mode "$mode"); fi
  "$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys;sys.dont_write_bytecode=True' --python "$tool/export_inspection.py" -- --repository-root "$repo" --source "$source" --output "$out/$mode viewer.blend" --report "$out/$mode receipt.json" "${extra[@]}" || exit 1
done
python -B "$tool/qa/run_qa.py" --source "$source" --baseline "$historical_c46" --tool "$tool" --off "$out/OFF viewer.blend" --high "$out/HIGH viewer.blend" --low "$out/LOW viewer.blend" --off-receipt "$out/OFF receipt.json" --high-receipt "$out/HIGH receipt.json" --low-receipt "$out/LOW receipt.json" --blender "$blender" --output-dir "$out/qa"
```

These are bash commands (no native Windows claim). Require terminal success AND fresh SUMMARY.json.pass; no stale reports. Independent runner fingerprints entire tool and QA trees before/after; do not change docs or inventories during tests. Optional pure checks:
```sh
python -B "$tool/test_preflight.py"
python -B "$tool/test_tree_pure.py"
python -B "$tool/tests/test_preflight_independent.py" --tool "$tool" --source "$source"
```

Historicalv018 source fixed Git `89cce41edf648eef6487d54ee1ce2a46bbb0ae17`, `checkpoints/v018/MANIFEST.json`; restore through that historical checkpoint recipe. ExpectedSHA `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`. Retain recovery receipts. Do not overwrite current checkpoints or use the entire historical scene as current-model comparison.
