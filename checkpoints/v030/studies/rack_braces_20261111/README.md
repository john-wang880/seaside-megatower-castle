# S27 north storeroom rack rear diagonals

Baseline cb8bcb5330a220b1fb63b72e16b49db35d34c44e, backup/bench-backrest-20261111. Three alternating timber rear diagonals articulate the three-bay north rack's support geometry. Reuse rack timber material. Original rack, shelves, objects, lights and scene data unchanged. Not an engineering load-rating or claim of structural safety.

Restore baseline study first. Reproduce with official Blender 5.2.3 LTS portable (SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec):
blender -b --python build.py -- /path/to/baseline/candidate.blend
blender -b --python check_saved.py -- /path/to/baseline/candidate.blend
python check_geometry.py
blender -b --python render_before.py -- /path/to/baseline/candidate.blend
blender -b --python render.py
Independent geometry checks require numpy. Render cameras are temporary and not saved into the candidate.

Validate CHECKSUMS.json. Check scope is topology, endpoint engagement, specified rear wall/aisle bounds, not full-route or load analysis. Next work should assess room-level composition or exterior rather than making repeated tiny timber additions. Persist full recovery pack and independently verify remote before retiring old current-tree payload. Preserve history and previous branch.
