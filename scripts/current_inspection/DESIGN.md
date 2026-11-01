# Bounded design and failure policy

Purpose: restore an exact accepted checkpoint, then produce a separate inspection-only Blender copy whose12 bookmark recipes are independently traceable. This does not migrate/rewrite historical navigation, film or quality-mode tools and does not create a model version.

1. Import-safe standard Python preflight resolves highest numeric existing checkpoint manifest; only reviewedv023/sourcec4/catalog-bytes50db598… is accepted. No unknownfuture fallback. Full source byte count and streamingSHA checked before Blender load.
2. Blender starts factory-empty with autoexec disabled. It opens canonical bytes itself using `use_scripts=False`, rechecks source/catalog/latestmanifest/runtime bindings, and preflights every reserved name before adding anything. Existing datablocks are never adopted.
3. Add only11 camera objects+data in one directly linked owned collection, one manual-onlyText, and one scene provenance marker. Original hero camera remains default; original geometry/material/light/world/renderquality and visibility remain unchanged. Existing rollback forest data stays hidden.
4. Embedded UI registers only on explicit RunText. Full camera inventory and effective collection/view-layer visibility is verified before each bookmark mutation. Re-registration does not duplicate classes. Changed/foreign ownership, pose/gate/delta transforms or Textcode causes refusal rather than silent repair. Allowed UI mutation: scene.camera and saved3Dview camera/use_local_camera/view_perspective; no samples/aspect/frame/unhiding.
5. Save a temporary sibling copy. Recheck all source/manifest/runtime bindings before publication. Publish viewer/report with atomic exclusive hardlinks (samefilesystem); failure removes only a still-owned inode captured from the temporary file **before** linking. Never adopt destination identity after publication. Unsupported hardlinks fail closed. Two-file crash atomicity is not claimed: a crash can leave a complete firstfile without report; choose new filenames after inspecting, never auto-clean unknown outputs.
6. Marker describes export provenance, not certification after user edits. No LOD geometry switch or performance promise. Solid/MaterialPreview/Rendered guidance is manual and copy-local.

Testing is bounded to purePython/negativefixtures and actual Linux Blender5.2.3 export/reopen/headlessUIAPI. NativeWindows/UI interaction and arbitrary futureBlender builds are not claimed. Exact camera matrices come from historical actual receipts and three existing detail recipes; no unreviewed crown pose added.

## Recoverable issues caught before acceptance

- Publication race identified in code review: destination stat after link could adopt a foreign replacement. Fixed to pin temporary inode before link, with immediate-postlink replacement/secondpublishfailure fixture proving foreign file survives.
- Actual Blender repeat-registration revealed RNA operator classname differs from an inconsistent Python classname. Aligned `CASTLE23_INSPECTION_OT_bookmark` with `castle23_inspection.bookmark`; fresh distinct copy/receipt produced, old failedAPI copy not relabelled. Static regression checks class/id correspondence.

These preliminary outputs remain scratch-only, not accepted deliverables or proof of the final runtime. Final reports identify the tested source/output/runtime hashes.
