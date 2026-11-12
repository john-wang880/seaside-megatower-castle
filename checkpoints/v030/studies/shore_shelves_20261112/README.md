# S29 visible southern shoreline bedrock shelves

Baseline 4bbeb1fde4aaaab0393e75a1346f705aa4dcffca, backup/coast-boulders-20261111. Exterior review identified the southern mainland shore as a thin nearly uniform rim. Two broad, low, irregular bedrock outcrops articulate the visible shoreline, partly submerged and embedded in the original closed headland. This is a local terrain-silhouette refinement, not a rebuild of the castle. Existing terrain, structures, routes, vegetation, water, materials and lighting are unchanged.

Reproduce using Blender 5.2.3 LTS portable, official binary SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec:
blender -b --python build.py -- /path/to/baseline/candidate.blend
blender -b --python check_saved.py -- /path/to/baseline/candidate.blend
python check_geometry.py
blender -b --python render.py -- /path/to/baseline/candidate.blend
Independent second implementation: python independent_review.py, verifying full-surface distance and winding for strict overlaps. Python checkers require numpy. Random seed 29 fixes vertex variations. Shoreline is derived from actual baseline triangle intersections with Z=0, not guessed from an image. Preview camera settings are temporary, never written to saved model.

Restore and verify CHECKSUMS.json before use. Native comparison checks original snapshot-supported data unchanged. Geometry checker validates closed oriented components, strict positive-volume terrain contact using a 0.015 interior ball, pair separation, coastal bounds and six deliberate invalid mutations. No engineering load, geology, hydrodynamics or navigation safety certification is implied.

Continue from output/candidate.blend. Assess both overview and detail. Stop extending rocks merely to add objects; future work should prioritize functional circulation or a purposeful broader visual improvement. Persist entire recovery archive before repository writes. Independently fetch, restore, hash and reopen the remote model before retiring prior current-tree study payloads. Preserve earlier branches and history.
