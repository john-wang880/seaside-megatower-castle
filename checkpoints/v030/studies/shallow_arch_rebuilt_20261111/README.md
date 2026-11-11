# S24 reconstructed shallow receiving arch

Rebuilt from verified meadow-ribbons commit 618e19d35b3129a790da8255b108a209d7c0476f. This is NOT recovery of the lost original shallow-arch candidate. Only one weathered limestone arch-shoulder mesh added; original scene data preserved per UNCHANGED.json. No lighting change.

## Reproduce
Blender 5.2.3 LTS, official Linux portable SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec.
Restore baseline study meadow_ribbons_20261110 at the parent commit with its restore.py. Then:
`blender -b --python build.py -- /path/to/baseline/candidate.blend`
`blender -b --python check_saved.py -- /path/to/baseline/candidate.blend`
`python check_geometry.py` (numpy required)
`blender -b --python render.py` produces reverse preview.
Preview scripts do not save scene changes.

## Verified scope
Closed oriented single-component added mesh; positive overlaps at piers and beam; 1.2-wide 2.1-high central crossing clear; six deliberate negative mutations detected. All preexisting snapshot-supported data unchanged. This is a decorative modeling review, not boolean fusion or structural certification.

## Continue
Start from output/candidate.blend after verifying CHECKSUMS.json. Evaluate wider circulation and alternate views before any next modeling change. Retain source history. Do not claim old approval succeeded or original lost candidate was recovered. Do not clean old payloads before remote roundtrip validation.
