# Independent optional-inspection copy review

Final reviewed export: `viewer-validated.blend`, SHA6f0973123b5d27a9685b67c5c43b6cc8f50c5e24e7cdcec8c6698014d274193d. Canonical v023c4 remains unchanged. This is a derived inspection copy, not a new accepted modeling checkpoint.

## Result

Actual Linux export/reopen/manual-Python/operator API QA passes. The full snapshot contains13checked categories, including explicit per-viewlayer original-object visibility and selection. All source raw/evaluated geometry, existing deformation weights/modifiers, materials/world/lights/render quality and old camera data remain exact after removing only11owned cameras/datablocks, one collection, manualText and scene provenance marker. Default original hero remains unchanged. All12bookmarks tested twice, with operator calls and full roundtrip preservation; register twice/unregister twice now work. Second reopen with scripts disabled retains valid ownership and does not auto-register.

Twenty actual in-memory negative cases reject canonical/foreign/partial ownership, export collisions, modified unselected lens/DOF/delta, hidden parent/excluded layer, autoexecText, unknown bookmark, foreign scene context, hidden originalhero parent and foreign registry. Rejected operations do not alter active camera. Twenty-four independent standard-Python tests cover version discovery, source/catalog/path guards and atomic exclusive publication behavior. They include exact first-destination substitution immediately after link, before publication bookkeeping, followed by failure.

## Meaningful bugs found and fixed

* Initial UI verified only the selected camera, allowing partial/foreign ownership elsewhere; final UI verifies all reviewed cameras before mutation.
* Original hero ancestor visibility and foreign scene context now fail closed; no automatic unhide/reset.
* Parent identified publication rollback race: recording destination inode after linking could adopt a foreign replacement. Final code pins temporary inode before linking; independent exact race fixture preserves foreign data.
* Actual first QA caught registration idempotence failure: Python class name did not match Blender RNA operator name. Final class is CASTLE23_INSPECTION_OT_bookmark, matching bl_idname; fresh embeddedText export and complete recheck pass. Earlier failed export/validation.log remain historical evidence, not accepted outputs.

## Scope and limitations

No native Windows machine or interactive desktop clicking was available. Filesystem-error mocks are not a native Windows claim. No rendering, quality/LOD changes, model save to canonical path, software installation or automatic load handler. Manual Text has use_moduleFalse; user explicitly runs it to register the sidebar. Export provenance marker is not proof that later user edits preserve geometry.

Bookmarks intentionally leave current render aspect/settings unchanged. Returned metadata/sidebar guidance tells the user to set historical reference aspect manually in this copy for exact framing. Source and historical v018 navigation/v019 quality tools remain separate and untouched. No unknown future manifest is silently treated as reviewed.
