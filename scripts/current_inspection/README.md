# v030 inspection copy — 20 unchanged manual bookmarks

**Local native export/reopen, model visual acceptance and complete independent controls passed; fresh remote replay also passed.** Source pin `9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35`,47,842,841bytes. Only a genuine latest v030 manifest is accepted; none is fabricated here.

All20 existing camera records remain byte-equivalent as JSON values, including historical recipe/receipt hashes and camera names. Runtime ownership uses CASTLE30/INSPECT30; old camera datablock labels inside those unchanged records are intentional. No new viewpoint, quality mode, automatic execution or visibility mutation.

Optional `--editing-index` now offers6groups/51targets. The existing5groups/45targets are unchanged; the new group selects exactly two racks and four supply bins. **Freestanding fittings only; source architecture unchanged.** Local timber material is shared by these six objects. The index is a manual selection aid for an unedited derived copy, not post-edit certification. It never unhides objects, toggles masks, enters Edit Mode or modifies geometry. Hidden/unselectable/stale targets fail closed; selection/active state rolls back on failure.

`--tree-mode` remains absent=OFF or explicit HIGH/LOW. The same HIGH tree group is unavailable while LOW/hidden; the new fittings group does not alter quality. Exactly20 current bookmarks remain the authority; no count increase in this upgrade.

Existing historical reports/QA paths are retained, **not relabeled v030 proof**. Prior v029 tool/receipt provenance is fixed at Git `d753ba032b1d3138a1d0c34e13b0caee40b3d92f`; copied baseline documentation lives in `provenance/v029_upgrade_baseline`. The current independent entry point is `qa/v030_current/run_qa.py`; older QA paths remain historical. Linux Blender5.2.3 is the reviewed environment; Windows remains untested. No file-size or speed claim.

CPU checks: test_preflight.py(18),test_tree_pure.py(9),test_edit_index.py(10),test_index_panel.py(4),test_v030_catalog.py(6),tests/test_preflight_independent.py(24) with inherited PYTHONDONTWRITEBYTECODE=1. Last test requires `--tool` and explicit candidate `--source`. The historical test_v029_catalog.py is retained for chronology, not a current-source test.

## Create an explicit copy

Restore the latest canonical model, then use NEW output/report paths with existing Blender5.2.3:

```sh
blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python scripts/current_inspection/export_inspection.py -- --repository-root /absolute/repository --source /absolute/castle_v030.blend --output /absolute/new/inspection.blend --report /absolute/new/inspection.json --editing-index --tree-mode HIGH
```

Omit both optional switches for bookmarks only. To inspect manually, open the derived copy with auto-run disabled and explicitly run Text Editor text `INSPECT30 | Run manually for bookmarks.py`; the sidebar controls are then registered. Save only when you choose. Camera selection never changes lighting/quality or renders.

Current native evidence: `qa/v030_current/provenance/` and VALIDATION.json. See `qa/v030_current/README.md` for four-copy replay with pinned historical v018 tree baseline.84 distinct CPU methods (47 runtime,24 independent preflight,13 comparison/scope) passed; historical tests are not current acceptance.

### Current test scope

Do not recursively discover every historical test in this archival repository. Current runtime tests are the five explicitly listed files above (47 methods); `test_v029_catalog.py` remains byte-exact historical evidence and intentionally describes the earlier five-group/current-source assumptions. Run those five files explicitly, then the24- method independent preflight CLI and13-method `qa/v030_current` suite. This preserves old evidence without treating it as current acceptance.

Remote additive facb336b3bec7c36608f06ab9788ca06eda3257b passed fresh four-copy native replay and84 current pure methods. Source/runtime/archive unchanged; [project record](../../checkpoints/v030/reports/remote/VERIFIED.json).
