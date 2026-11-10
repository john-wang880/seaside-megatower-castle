# Meadow blade silhouette study

Source: verified receiving-alcove checkpoint `5050dbc8dea19b06ec4f485fe506bafa0aae175f`, branch `backup/receiving-alcove-20261110` in john-wang880/seaside-megatower-castle. Source model SHA256: `8713c396cc14c7b793955375409740348fd0b343346ff38e9569d122898f385e`.

Only the existing `Fine meadow grass blades` mesh is changed. Broad triangular spikes become narrower, shorter, gently bending segmented leaf silhouettes. No blades, furniture or lights are added. The 11,965 original root midpoints, individual material assignments and original light setup remain. Other meshes, transforms, materials, cameras, scene settings and collections are unchanged under the recorded snapshot checks.

Each original triangle becomes seven vertices and five triangles. The result has 83,755 vertices and 59,825 triangles, an increase of 47,860 triangles. This is a silhouette-quality improvement, not a performance optimization. Base width is 24% and longitudinal height 72% of the old blade. Blade count is unchanged, but apparent leaf coverage is intentionally reduced. The original full base edge is shortened, not preserved. The geometry remains planar, not volumetric foliage.

The new surfaces lie within their original triangles within the reported floating-point tolerances. This does not certify or repair pre-existing floating roots or path/terrain overlaps. No real-world units or structural claims are made.

## Reproduce

Use official Blender 5.2.3 LTS and Python with NumPy. Restore the preceding checkpoint to obtain its exact `candidate.blend`, then run from this directory:

    blender -b -t 4 --python-exit-code 1 --python build.py -- SOURCE.blend output
    blender -b -t 4 --python-exit-code 1 --python check_saved.py -- output
    python check_geometry.py output
    blender -b -t 4 --python-exit-code 1 --python render.py -- SOURCE.blend output
    blender -b -t 4 --python-exit-code 1 --python render_full.py -- SOURCE.blend output

Use a fresh output directory. The build pins the source file hash, compares non-target scene data, saves and reopens the model. The separate saved-file exporter and NumPy checker check component topology, exact material assignment, original root midpoint, monotonic sections, face winding, source-triangle containment and four deliberately invalid controls. Snapshot coverage is bounded by snapshot_support.py, not a claim of byte-for-byte serialization of every Blender property. Reproduction is checked semantically; Blender file bytes may differ between saves.

The supplied previews are actual Cycles renders with unchanged original lighting, 40 samples: matched ground camera (960x694) and original full-scene camera (1200x800). Render settings and temporary inspection camera are not saved into the delivered model. Before images are verified copies from renders of the exact source model; receipts record hashes and settings.

## Continue

Start future modeling only from this version if its ART_ACCEPTANCE and REMOTE_VERIFIED reports pass. Retain the source branch and all Git history. Do not restore the rejected coastal-inlet geometry from evidence commit 186c5e3, add furniture/lights merely to create another version, or revive the unbuilt dark gate-pull study. Inspect an actual rendered view for a meaningful issue before changing geometry. These leaves remain single-sided thin surfaces; further densification or a new vegetation style needs an actual visual case rather than automatic escalation. Never claim the complete meadow has solved terrain contacts.
