# S33 · Guard equipment and changing station

A single functional furnishing ensemble completes the empty north-side wall of the two-berth guard room: an open shoe/small-item shelf (three structural bays, the middle bay divided by its support leg into two accessible openings), slatted sitting bench, floor-supported tall uprights, six raised-stop equipment pegs, and three upper cubbies. No doors swing into the aisle. This is an empty station ready for equipment, not a claim that coats/helmets have been modeled.

The original beds, lamps, doorway, floors, walls, reception room, seven refined S32 trees and all other source content are preserved. No illumination, world, exposure or original-camera changes. The review camera is temporary and not saved into the model. This is geometric architectural modeling; dimensions are scene units, not calibrated furniture or structural engineering certification.

## Reproduce
Required source: accepted S32 `candidate.blend`, SHA256 `96347578d286b3d898fd8c9f9b7e9393807da20cd4cb89b853fb1500118d0c8f`, from commit `01a61eb775d398f741271d286b3ca8d7c4a7204d`, `checkpoints/v032/restore.py` plus its manifest/archive directory. All old payload remains recoverable from Git history.

Copy `build.py` and `snapshot_support.py` to a clean output folder and run Blender 5.2.3 LTS with scripts disabled:
```
BLENDER -b -t 2 --disable-autoexec --python-exit-code 1 --python NEW/build.py -- ABS_S32_SOURCE.blend
```
Compare both models using `compare_rebuild.py -- ACCEPTED.blend REBUILT.blend`. Native validation uses `check_native.py -- ABS_S32_SOURCE.blend ABS_S33.blend`. Tests never save source models. `GEOMETRY.json` contains reviewed actual mesh arrays.

## Validation boundary
Native snapshot, saved-array equality and removal of the entire owned delta prove source preservation/rollback in supported categories, not every possible Blender API field. Mesh checks and floor-support contact certify the finite predicates in the independent reports, not engineering load capacity, material strength or global self-intersection freedom. Adjacent furniture pieces deliberately meet or overlap to form joinery.

## Continue
Do not populate this station with successive trivial props just to create versions. Choose a new useful architectural or landscape improvement with explicit source-preservation and route boundaries. Before retiring an older current payload, reconstruct the complete new archive from the actual remote commit, verify all checksums and rerun relevant checks. Preserve history; never force push. Stop new iterations at 2026-11-30 12:24:59 UTC.

## Rejected prototype and correction
The first prototype's low front apron obstructed most of the low shelf opening. Independent visual/geometry review rejected its open-cubby claim. The front apron was narrowed and raised beneath the seat while preserving the rear apron and all floor-supported uprights. Final geometry, native/rebuild and image checks were rerun. Low cubbies are for shoes/small items, not asserted to fit tall boots or certified anthropometric sizes.

Final access check establishes four clear insertion corridors from Y31.55 to32.14: height0.22999954, widths approximately1.0/0.48/0.48/1.0 scene units. A negative control correctly rejects the old blocked front apron. These are empty geometric access envelopes, not full-object insertion simulation or guaranteed footwear compatibility.
