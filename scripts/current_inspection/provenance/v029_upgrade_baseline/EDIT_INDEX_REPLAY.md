# Optional selection index — explicit replay

Use existing Blender 5.2.3 (Linux tested; Windows untested), the current repository and byte-exact restored v028 source `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096`. Use fresh output paths. No downloads, installations, automatic UI execution or rendering occur.

```bash
export PYTHONDONTWRITEBYTECODE=1
# Set absolute paths (spaces and Unicode are supported).
ROOT=/absolute/repository
SOURCE=/absolute/castle_v028.blend
BLENDER=/absolute/blender
OUT=/absolute/new-output-directory
mkdir "$OUT"
TOOL="$ROOT/scripts/current_inspection"
for MODE in default off high low; do
  EXTRA=()
  case "$MODE" in
    off) EXTRA=(--editing-index);;
    high) EXTRA=(--editing-index --tree-mode HIGH);;
    low) EXTRA=(--editing-index --tree-mode LOW);;
  esac
  "$BLENDER" -b --factory-startup -t 8 --disable-autoexec --python-exit-code 1 \
    --python-expr 'import sys;sys.dont_write_bytecode=True' \
    --python "$TOOL/export_inspection.py" -- --repository-root "$ROOT" \
    --source "$SOURCE" --output "$OUT/$MODE.blend" --report "$OUT/$MODE.json" "${EXTRA[@]}" || exit 1
done
# QA-only historical original tree source c46b581a… from fixed Git
# 89cce41edf648eef6487d54ee1ce2a46bbb0ae17; see qa/edit_index/README.md.
BASELINE=/absolute/castle_v018.blend
python -B "$TOOL/qa/edit_index/run_qa.py" --source "$SOURCE" --baseline "$BASELINE" \
  --tool "$TOOL" --default "$OUT/default.blend" --off "$OUT/off.blend" \
  --high "$OUT/high.blend" --low "$OUT/low.blend" \
  --default-receipt "$OUT/default.json" --off-receipt "$OUT/off.json" \
  --high-receipt "$OUT/high.json" --low-receipt "$OUT/low.json" \
  --blender "$BLENDER" --output-dir "$OUT/independent-qa"
```

The baseline is independent lineage QA input, not a runtime dependency of the exported manual tool. `default` leaves editing index and tree quality OFF; `off` enables only selection index. HIGH/LOW alter only the pre-existing paired tree flags. All four retain the same 18 camera records and canonical source.

Current public QA is `qa/edit_index/run_qa.py`; old `qa/run_qa.py` and prior reports remain as historical pre-index evidence, not substitutes. Current success requires all JSON gates and successful process exit. Native crash/provisional harness history is disclosed in the new QA provenance; tested runtime was not changed to hide those failures.
