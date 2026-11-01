# Local path conformance rebuild (v023 candidate)

Explicit opt-in rebuild from the byte-exact accepted v022 source. This is not a new path, stair connector, or an engineering-scale claim. Units are scene coordinate units; global real-world calibration is not established.

Source SHA256: `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`.
Restore v022 from fixed Git commit `a80fdd6bc589f03159c23cc3cfaea1cfbdb2adc3` using its `checkpoints/v022/MANIFEST.json`, restore script and referenced `model_chunks`. No private candidate or survey export is an input.

Tested runtime for the original candidate: official Blender 5.2.3 Linux. No Windows or other-version runtime claim. The frozen recipe has not yet undergone its separate clean rebuild; see external execution receipts when available.

```sh
python3 -B test_preflight.py
python3 -B test_plan.py
/path/to/blender -b -t 8 --disable-autoexec --python-exit-code 1 \
  --python-expr 'import sys; sys.dont_write_bytecode=True' \
  --python scripts/build.py -- \
  --source '/path with spaces/castle_v022.blend' --plan plan.json \
  --output '/new result/candidate.blend' --report '/new result/build.json' \
  --source-snapshot '/new result/source_snapshot.json'
```

All three output paths must be new and distinct; source/plan aliases and direct symlinks are refused. Do not run Python with `-O`. Failures are nonzero with `--python-exit-code 1`. Inspect every report gate, not only process exit. No automatic rendering, publishing, installation or source save.

The original 120 triangles remain in the raw path mesh. A 63-vertex inverted Mask suppresses only their evaluated faces. The separate 800-triangle patch reuses the original materials and follows actual terrain triangle overlays. Rows 95/105 retain their original cross-seam vertices and polylines; lateral Z may conform. Rollback requires disabling this owned Mask AND hiding the new patch in viewport/render together.

Original 14 seam vertices are bit-exact. Inserted intersections are float32 geometry: XY-domain and seam collinearity residuals must be measured, not described as exact zero. Independent saved-mesh overlay checks are authoritative for full-face clearance and partition residuals. The declared gap bound is [0.016,0.030], nominal interior offset 0.021 coordinate units. Original winding remains downward: this is an open decal, not a closed structural solid.

These pure tests exercise eight preflight refusals and plan/overlay arithmetic only, not Blender execution, saved attributes, actual terrain partition, clearance, or visual acceptance. Saved .blend bytes may differ between reproductions; compare persistent/evaluated semantics independently.
