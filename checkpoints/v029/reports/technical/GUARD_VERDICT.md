# Frozen east-program guard — independent pre-cut PASS

**The frozen plan passes the independent CPU pre-cut gate.** This authorizes no saved geometry by itself: parent geometry authority, a declared budget, actual local partition output, saved-coordinate boundary/material/rollback validation and visual review remain separate. No model/Boolean/native/render operation was performed.

## Exact scope checked

Source f0d135…a8096, current three V028 complex hosts, 335 raw vertices. Plan manifest `work/v029_interior_program/guard_plan/MANIFEST.json` (148ed81…19802).

- Room guard: [16.3,33.9,28.9]–[23.5,38.6,32.15].
- Connector guard: [14.8,35.4,28.9]–[16.5,37,31.55].
- Room cavity: [16.4,34,29]–[23.4,38.5,32.05].
- Connector cavity: [15,35.5,29]–[16.4,36.9,31.45].
- No sleeve/addition. Minimum nominal changed-domain guard buffer approximately .1 coordinate unit.

The checker reads only these input boxes/identities from the mapper plan; it independently derives affected planes, occupancy, interfaces, floors, routes and seats from actual exported triangles. It then cross-checks the mapper's exact raw/remote/affected IDs, rather than accepting its computed cells.

## Actual boundary and occupancy result

Exact rational clipping of each nonzero source triangle against the guard independently identifies **268 untouched remote parent polygons and 11 affected parents**:

- Foundation: remote122; affected source85,86 at Z31.440000534057617 and112 at X15.100000381469727.
- Ashlar: remote76; affected56,57 at Z30 and72 at X15.100000381469727.
- Existing room shell: remote70; affected24 at X15,25 at X15.100000381469727,57/61/63 at Z29.

Every positive-area intersecting parent is exactly axis-planar. Collinear exact-zero derived triangles contribute no area; canonical saved topology remains untouched. No raw-box approximation or BVH coplanar exclusion is used.

The independent partition has **570 cells**, versus mapper241 because it also inserts floor-air/body planes. All actual intersecting source planes are present, making each connected open cell boundary-disjoint; a solid-angle witness classifies the entire cell, not a finite sample approximation. Maximum winding residual 1.80e−14. Source union in guard115.524; after common cut14.647; removed100.877; added0 (nominal-coordinate volume values).

**Zero changed guard-interface cells.** The refined partition explicitly records47 existing-air interface rectangles, on west X14.8, both connector sides Y35.4/Y37, and topZ31.55 where X14.8–15 is the original receiving-room void. They are not missing seats and must not be capped. Occupied interfaces require paired opposite-facing buried partition caps; old-air interfaces require no cap.

The expected local union has235 unique oriented interior solid/air rectangles. This resolves overlapping-host cavity walls into one boundary and therefore avoids *expected* duplicate skins. It does not claim an unbuilt mesh is duplicate-free: output must match this oriented reference in both directions with separate missing/extra/multiply-covered area checks. Preserve all remote inherited surfaces and actual clipped source domains, not a global host-union cleanup.

## Floor, routes, lamps and retained seats

- Full connector floor from X14.8 through old X15/15.100000381 interfaces into the stores, and the entire proposed room floor, have33 refined positive occupied cells in Z28.95–29; the33 corresponding open cells Z29–29.025 are clear. These are continuous domain proofs, not spot checks.
- A positive old-room floor box X14.7–14.9/Y35.4–37/Z28.91–28.99 independently crosses both sides of the west guard interface inside the actual original shell.
- Continuous new body prism X14.8–23.3/Y35.6–36.8/Z29.025–31.1 is clear in the predicted result. Its adjoining old-room prism X7.1–14.8 with the same Y/Z is already clear of every actual exported source component. It intersects both existing longitudinal aisles, connecting to the accepted receiving-room network; no forced return loop.
- All29 non-target components (including the20 lamp meshes and actual open terrain surface) are independently disjoint from the interiors of cavities/floor-air/body domains. No fixture movement is allowed. Lights/world/material graphs must remain exact during native integration.
- Six finite positive-volume retained seats beside/above the new doorway pass actual closed-source containment: two jamb sides on each side of X15.1, plus local-shell/ashlar lintel seats. These supplement, not replace, full floor/source-cover proof.
- Pure subtraction cannot add an obstruction to old clear body lanes. The complete old receiving-room geometry outside the declared opening/guard, its piers/band, floor, fixtures and prior native mask chains remain strict preservation requirements. No claim covers arbitrary future furniture, every destination floor point or human/engineering capacity.

## Seven negative controls passed

1. Guard ending on the cavity rather than enclosing it.
2. Omitted raw target vertex.
3. Missing actual foundation top plane.
4. Actual room cut extended below intended floor.
5. Source solid retained in the doorway body lane.
6. Duplicate expected oriented boundary rectangle.
7. Actual old lamp geometry intruded by a changed volume.

These are CPU plan/exported-geometry controls, not injected saved-model tests.

## Closed dependency omission / remaining implementation conditions

Owner's exact `attributes/inventory.json` closes the earlier probe omission: all three targets have no UV/color layers, custom normals, shape keys or object/mesh animation; eleven expected topology/position/select/sharp/seam/material-index attributes are recorded, as are exact material graphs/slots. Preserve that inventory and all original source raw data, not merely these summarized absences.

Before build: freeze explicit architecture/fixture budgets and ownership. During build: no global Boolean shortcut; exact outside-domain preservation, consistent float32 registry and shared guard seams. The current proof is nominal pre-cut geometry; saved quantization must be measured and compared to an independently quantized reference, not called exact decimal geometry. Validate original masks, all raw weights, materials/lights, source rollback, complete actual replacement boundary, route/floor and fixtures on the saved result.
