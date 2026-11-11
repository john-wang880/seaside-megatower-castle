# S25 segmented shallow-arch stone facing

Baseline: 13462353c42f2628cacfab4df43543b2e9927914 on backup/shallow-arch-rebuilt-20261111. Added 17 discreet stone facing blocks per side of the shallow arch, exposing narrow joints and a shallow projection for legible masonry detail. Original arch, original scene and lighting unchanged. Decorative facing only, not load-bearing wedge construction.

Reproduce with official Blender 5.2.3 LTS Linux portable (SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec). Restore baseline via its study restore.py, then:
blender -b --python build.py -- /path/to/baseline/candidate.blend
blender -b --python check_saved.py -- /path/to/baseline/candidate.blend
python check_geometry.py
blender -b --python render_after.py
blender -b --python render.py
Numpy required for independent checks. Preview camera changes are not saved in the model.

Validate CHECKSUMS.json after restoring. Before/after and reverse previews demonstrate unchanged original lighting. Checks cover closed oriented meshes, strict overlap, spacing and the specified central crossing, not full circulation or engineering safety. Continue from output/candidate.blend; next candidate should address another localized useful detail rather than adding more repetitive layers to this doorway. Preserve history and verify remote backup before retiring current-tree payloads.
