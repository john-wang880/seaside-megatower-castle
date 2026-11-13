# S31 · Connected two-berth guard rest room

A new bounded rest/readiness destination south of the existing reception room. This is a deliberate new architectural use, not a repair of a supposedly incomplete reception room. The original reception/checking station, visitor bench, cloak stand, connected stores and staircase remain.

## Scope
- Room clear envelope X7..14, Y27.8..32.4, floor Z29 and ceiling Z32.05, in uncalibrated scene units.
- One 1.4-wide, 2.45-high opening at X8..9.4 connects northward to reception. No exterior opening, new circulation loop or full-tower interior.
- Two full low timber berths aligned end-to-end along the south wall, with feet, rails, bedboards, mattresses, restrained covers and pillows. No extra clutter.
- Two local source-style 36-energy warm lanterns, east and southwest walls. Original lamps, world, exposure and cameras unchanged. The southwest lamp is deliberately away from bedding; this is not fire/structural/ergonomic certification.
- Three original host meshes retained behind owned reversible masks. Four bounded replacement meshes: 1,114 triangles equivalent. Bed/fixture additions: 58 mesh objects, 3,440 triangles; two new point lights. This is not a global boolean cleanup.

## Evidence
Finite 450-cell occupancy, complete local host/instance scope, single-door route and floor coverage, preserved original pier/band boxes, closed oriented positive meshes, 346 unchanged remote polygon cycles, and clipped source-domain coverage have independent reports. Maximum clipped-domain float32 area difference is 0.000031808; do not call these domains bit-exact. Saved native geometry matches reviewed JSON, and saved source complement plus rollback pass the supported snapshot categories.

Eight bed feet have complete real floor-face coverage. Sixty support connections use mesh interior points or actual coplanar contact area rather than bounding boxes alone. Beds/lamps remain outside the protected route; both light mounting plates engage actual walls. These are static scene-geometry checks, not physical safety certifications or general self-intersection guarantees.

A fresh pinned-S30 rebuild produced a different file hash but passed full supported scene/data semantic and collection comparison. Original S30 source SHA256: a6c9715064ae0ea8ee58f369f46ceb3352bfc84fb53687b30bffd35bf38bd9ce. Current candidate SHA256: a9ececee22e0cb9295698e8baed6e60b7c7fabe2df5b55ca1f3cb545e4bfb9d6 (49,219,971 bytes).

## Files / replay
Open native/candidate.blend in Blender 5.2.3 with automatic script execution disabled. Native final previews are room.png and return_v2.png, at ordinary eye height without wall removal; unlit_entry.png is the earlier rejected unlit stage, not the finished lighting.

To rebuild from the preserved S30 source in a fresh directory:
`python rebuild.py /path/to/blender /path/to/S30.blend /new/output/directory`
Then compare using compare_rebuild.py in Blender with rebuilt native/candidate.blend as its final argument. Original source and output directories must remain separate. Full large intermediary source exports are reproducible from export_all.py, not duplicated in this package. CHECKSUMS.json binds packaged files. Geometry/independent check scripts and saved reports document their exact scope.

## Continue / avoid regressions
Do not add more berth accessories or enlarge this room for incremental versions. Review an independently useful next architectural target before altering the accepted arrangement. Do not extend room cuts into the original piers, top band, route, facade or stores. Preserve old branch/history. Remote restore and checks must pass before withdrawing the former current payload; no history purge or force push.

The initial oblique return.png is retained as an inadequate review-camera study, not an accepted connection view. return_v2.png uses a normal standing position within the protected route, aimed through the actual north doorway. No wall hiding or source lighting change was used to obtain this view.
