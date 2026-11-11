# S26 receiving alcove bench backrest

Baseline: 7d5c4383024cc29585ba9c07ca7688d01d203669, backup/segmented-arch-20261111. Add three timber backrest rails on two uprights to existing S22 bench; reuse existing seat timber material. Original bench and all other original object/material/light/camera/world/scene data unchanged per snapshot. This improves alcove furnishing without further layering the doorway.

Restore baseline from its study restore.py. Reproduce using official Blender 5.2.3 LTS Linux portable (SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec):
blender -b --python build.py -- /path/to/baseline/candidate.blend
blender -b --python check_saved.py -- /path/to/baseline/candidate.blend
python check_geometry.py
blender -b --python render_before.py -- /path/to/baseline/candidate.blend
blender -b --python render.py
Numpy required for independent mesh checker. Render scripts do not save cameras into candidate.

Validate CHECKSUMS.json after restore. Geometry checks bound to backrest topology, positive support overlap, wall clearance and fixed local aisle limit; not ergonomic certification, structural engineering or proof of entire-route clearance. No new lamps or exposure changes. Continue from output/candidate.blend; next work should review a different room or exterior feature rather than continually embellishing the alcove. Preserve history, maintain persistent full artifact copy, verify remote restore before retiring previous current-tree payload.
