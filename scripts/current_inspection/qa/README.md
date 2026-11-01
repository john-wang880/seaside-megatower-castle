# Independent QA for the current-inspection copy tool

This is a self-contained review bundle for the optional derived-copy tool, not a new castle model. Runtime files live separately in `scripts/current_inspection` after publication. Historical v018 navigation and v019 quality tools are not imported or edited.

## Inputs / one command

First create a NEW viewer and export receipt using the reviewed exporter from the fresh repository. Then run this independent checker on those existing artifacts:

```sh
python -B run_qa.py --repository-root "FRESH_REPOSITORY" --tool "FRESH_REPOSITORY/scripts/current_inspection" --source "RESTORED_V025.blend" --viewer "NEW_VIEWER.blend" --receipt "NEW_EXPORT.json" --output-dir "NEW_QA_DIRECTORY" --blender "BLENDER_5_2_3_EXECUTABLE"
```

All paths are explicit; spaces/Unicode are supported in the tested Linux environment. The output directory must not exist and its parent must exist. Reports cannot be inside immutable checkpoints, the tool or this QA bundle. The runner never exports, saves, renders or modifies a model. It verifies the current highest numeric live MANIFEST, reviewed catalog, exact source SHA/bytes, exported-viewer SHA and runtime/manifest receipt identity before testing.

The runner executes24pure tests and one Blender headless deep/UI API check. Blender is launched with factory startup, automatic scripts disabled, Python-error exit code1 and explicit sys.dont_write_bytecode=True before the checker. Use `python -B`; do not use `-O`. No software installation or network is required.

## Gates and artifacts

Require output `SUMMARY.json`→pass; inspect `validation.json`, not only exit status. The report records actual category names/count rather than assuming a fixed count. The historical v023 tested snapshot had13categories including explicit per-viewlayer original-object visibility/selection. All pre-existing geometry/raw attributes/deform weights/modifiers/evaluated geometry/materials/world/lights/render settings and old camera data remain exact after removing only12owned new cameras, onecollection, manualText and provenance marker.

All13bookmarks are chosen repeatedly and exercised through operators. Registration/unregistration is idempotent, source scene settings remain unchanged through a hero roundtrip, and a second disabled-script reopen is valid.20negative API cases verify canonical/foreign/partial ownership, export collisions, changed camera gate/DOF/delta, parent/layer visibility, autoexecText, unknown bookmark, foreign scene context and foreign registry. Rejection must not switch active camera.

The24pure tests include highest reviewed/unknown future/stale/ambiguous numeric manifests, wrong source size/SHA, altered catalog, source/output aliases, immutable checkpoint destinations, Unicode, symlinks, nooverwrite and optimized-mode refusal. Publication fixtures verify second-file failure rollback deletes only an owned first inode and preserves a foreign destination even if swapped immediately after the first link, before bookkeeping. Filesystem unsupported-error mocking is explicitly not a native Windows test.

The complete QA directory inventory, runtime files and both model hashes must remain unchanged; no caches are allowed in the bundle. Report files are only created under the new output directory. The runner binds the exported model to its receipt but does not claim any future user edit remains validated.

## Platform / UI limits

Historical v023 tests were executed on Linux using actual Blender file reopen/manual Python/operator APIs; this v025 adapter passed actual Blender 5.2.3 Linux export/reopen, preservation and manual operator API checks. No desktop mouse-click or native Windows machine was tested. Do not describe mock filesystem failures as native Windows compatibility. Symlink/hardlink fixture support may differ on Windows; a Linux runner is the validated independent-QA environment. The actual tool fails closed when exclusive hardlinks are unsupported rather than overwriting or using a weaker fallback.

Manual Text has use_moduleFalse. Nothing auto-registers on file load. The user explicitly runs the Text to enable the sidebar. Bookmarks do not change render aspect, lighting, exposure, quality, LOD or object visibility; reference aspect metadata is guidance for manual changes in the derived copy. A provenance marker is not certification after user edits.


## Actual v025 validation status
Fresh export and full QA passed for exact source8a359 and derived viewer e9253a2. All13bookmarks,13original state categories and20negativeAPI cases passed. Existing raw/evaluated meshes, weights and modifiers remain exact. Snapshot helper remains fixed-v024 exact; runner has the explicit13-bookmark expectation.

The first wrapper run found a stale12-bookmark assertion only after Blender had passed13bookmarks. That failed wrapper evidence remains local, its old runner/inventory archived under provenance. The one-line assertion was corrected and the complete pipeline rerun into a fresh output directory. No runtime, catalog or viewer changed. Executed QA inventory and pre-publication README are archived; packaging changes only docs/reports/inventory, not tested Python.
