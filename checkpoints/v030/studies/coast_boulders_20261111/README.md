# S28 southwest intertidal shore articulation

Baseline 5052d672e0dd51233a71e8ea61855ecf18b23d2d on backup/rack-braces-20261111. Overall review found the southwest foreground rock shoreline visually bare and abrupt. Add 13 irregular low boulders traced from the actual western-headland Z=0 contour, partly submerged and embedded into the existing solid shore. No change to old terrain, ocean, paths, trees, castle or illumination. Source material reused.

Reproduce from restored baseline with official Blender 5.2.3 LTS portable (SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec):
blender -b --python build.py -- /path/to/baseline/candidate.blend
blender -b --python check_saved.py -- /path/to/baseline/candidate.blend
python check_geometry.py
blender -b --python render.py -- /path/to/baseline/candidate.blend
Numpy required. Survey.py is exploratory only; build derives shoreline directly from baseline. Render cameras/settings do not save back into candidate.

Verify CHECKSUMS.json after restore. Exported mesh validation checks topology, interior-ball overlap with closed headland, pairwise separation and southwestern/intertidal limits; original-data comparison protects existing routes and geometry. Six deliberate invalid mutations are detected. This is a visual terrain-detail study, not geology, hydrodynamics or engineering certification.

Continue from output/candidate.blend. Use overview and coastal detail together to assess scale, silhouette and unnatural repetitions before extending the coastline. Prefer a scene-wide assessment next, not endless rock scattering. Persist complete recovery pack before GitHub calls; independently restore/check remote before retirement; retain history and old branches.
