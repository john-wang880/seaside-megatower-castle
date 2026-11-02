# V030 fittings builder — code review stage

No Blender execution, candidate save or render has occurred. Baseline is exact accepted V0294f838529…; parent publication receipt d753ba032b1d3138a1d0c34e13b0caee40b3d92f. Source geometry/lights/camera/materials remain immutable.

Inputs: sibling PLAN.json byte-exact from74-part reviewed plan, and copied frozen snapshot_support.py. build_fittings.py pins both and source; checks runtime/source/helper/plan hashes before/after. No private helper imports. Requires original Linux Blender5.2.3; Windows untested. CLI explicit --source --output NEW.blend --report NEW.json; no automatic render. Exclusive hardlink publication prevents overwrite and rolls back only files it created on publication failure. Optimized Python, symlinks/aliases, existing outputs and namespace collisions fail closed.

## Geometry and ABI

Six meshes/objects in `V030 | reversible stores fittings`: `V030 | south three-bay rack`, `V030 | north three-bay rack`, and four `V030 | {south|north} supply bin {0|2}`. Each rack has35 connected components (8posts+9boards+18rails). Each bin has2 components (body+lid):78 closed positive components total,2184 triangles. There are no modifiers, masks, duplicate source meshes or new lights. No back braces; geometry support connectivity is not an engineering stability certificate.

All74 original primitive envelopes remain bounds. Each profile has0.008 XY corner cuts on vertical edges only: eight-sided ring extruded between exactly original Z planes. No top/bottom chamfer, so all foot/bearing planes stay flat. Planned foot area reduces from0.0144 to0.014272, wholly inside the proven original foot domain; actual post/rail/board contacts must be independently rechecked after rounding. No original source material/mesh is changed.

Bins: original envelope is partitioned at maxZ−0.04. Body XY is inset0.006 from the original bin bounds, with0.008 corner cuts; lid uses full original XY bounds and same cuts. Lid bottom rests directly on body top, leaving a restrained0.006 rim, no gap/floating lid. Bin body bottom remains exact shelf Z. Opposite-facing bearing interfaces are intentional; exposed same-facing coincident patches must be excluded independently.

`report.new_meshes[]` contains actual native vertices/faces/loop triangles, identity matrix/material, and `components[]`: unique ID, source_primitive name/role, part(body/lid/whole), half-open vertex_range/face_range, bounds, chamfer, bottom/topZ and analytic volume. Thus QA can recover exact part-to-source-plan mapping, compare containment and reconstruct every bearing. Do not infer saved volume from analytic double values; actual native vertices are authoritative.

One local material `V030 | subdued stores timber`: world Geometry.Position→Noise(scale2/detail1)→muted brown ramp→Principled, roughness0.82. No textures, external coordinates, material copies with hidden users, or shared-wall changes. The isotropic noise is subdued mottling, not authored directional wood grain. This is an initial restrained material, subject to original-light actual-view art review, not a license to brighten lamps.

Full original snapshot categories/collections and selection/active state must match before save; only6mesh/objects+1material+1collection are added. The report includes semantic geometry/material hashes and all input hashes. Independent saved geometry/source/fixture/door/body/coplanarity tests and same-camera visual gates remain mandatory.

## Run only after owner's native grant

```
PYTHONDONTWRITEBYTECODE=1 /path/to/blender-5.2.3 -b --factory-startup -t 8 --disable-autoexec --python-exit-code 1 --python-expr 'import sys;sys.dont_write_bytecode=True' --python /absolute/build_fittings.py -- --source /absolute/castle_v029.blend --output /NEW/candidate.blend --report /NEW/build.json
```

Pure tests: `PYTHONDONTWRITEBYTECODE=1 python test_builder.py` (15 methods). No native run claimed by these tests. Saved .blend bytes may vary between builds; semantic equivalence and source preservation need actual native QA.
