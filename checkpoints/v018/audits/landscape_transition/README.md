# v018 landscape audit — report only

This is a useful-negative audit of accepted v018, **not an accepted v019 model**. No prototype, new scene archive, or model change is included. See `REVIEW.md` and `decision.json`.

## Evidence and portability

`audit_original_executed.py` is the exact workspace-specific script that generated `audit.json`, `hero_slope_detail.png`, the original render receipt and `audit.log`. Its relative paths are historical, not portable instructions. `audit.json` preserves its original local source path as provenance; this path is not needed to use the portable CLI.

`audit.py` is a dependency-free portable wrapper of that procedure, requiring only Blender's bundled Python. It accepts a user-supplied source path but pins its SHA256 to accepted v018. It creates a new, nonexistent output directory and refuses existing output directories or mismatched sources. It opens with scripts disabled and never saves a .blend. Render settings are changed only in memory. No scene asset, material, light or world is modified.

```
/path/to/blender --background --disable-autoexec --python audit.py -- \
  --source /path/to/castle_v018.blend \
  --output-dir /path/to/new_landscape_evidence
```

For cheaper geometry/material inspection without the crop render:

```
/path/to/blender --background --disable-autoexec --python audit.py -- \
  --source /path/to/castle_v018.blend \
  --output-dir /path/to/new_landscape_inspection --skip-render
```

The output parent directory must exist. Do not point the command at this archive directory; it correctly refuses overwriting evidence. Successful inspection writes `audit.json` plus `inspection_receipt.json`; full mode also renders `hero_slope_detail.png` and writes `render_receipt.json` with source/image hashes. Use Blender5.2.3 for comparability. The code has no workspace helper imports.

**Validation status:** portable script passed compilation, help and refusal guards, then an actual Blender5.2.3 `--skip-render` run on exact v018. Geometry/material/sample payloads match the original audit exactly; source unchanged. See `portable_blender_recheck.json` and `portable_inspection_receipt.json`. The original crop was not rerendered for packaging; the full-render branch retains its recorded original evidence.

The crop is diagnostic enlargement only; the negative decision is based on the actual delivered hero scale. It is not a new preferred hero image.
