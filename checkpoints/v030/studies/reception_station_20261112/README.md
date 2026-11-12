# S30: reception checking and registration station

Source: S29 on backup/shore-shelves-20261112, reviewed at ff82e7cff5d02f1b6cfce66c69b8ec1c8a48c79d. Source native file SHA256 740efdecdc3a7b081b44c244d8113b678a03aeb7cc377764195354588c00bbd6.

The current S29 scene has a receiving alcove/bench, cloak stand and stores, but no reception table. The historical receiving_table_r01 package is a separate research candidate, not an object already in S29. This study reuses its precisely bounded, previously reviewed table recipe at x12..13, y34.9..35.5, z29..29.9 and tests it again in the newer scene. An open unmarked register, closed spare register and small ink-tray/filled inkpot form a coherent checking station, rather than repeating hidden box hardware. The props remain entirely over the table; no additional chair occupies the aisle. The table surface and supports are static geometry; the objects are not rigged or physically operable. Scene units are not certified physical metres.

All old model geometry, lighting, cameras, materials and world settings are preserved. New paper, binding and ink materials are restricted to new props. The actual original lighting is used in doorway and detail reviews; only temporary review camera/render settings are changed, never saved into the model. This does not certify human ergonomics, simultaneous passage with an operator, load capacity or all-route navigability.

Reproduce with official Blender 5.2.3 LTS portable (archive SHA256 78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec):
1. Verify CHECKSUMS.json, restore the pinned S29 source from its historical branch.
2. In a writable copied package: blender -b -t 4 --python build.py -- /path/to/S29/candidate.blend
3. blender -b -t 4 --python check_saved.py -- /path/to/S29/candidate.blend
4. blender -b -t 4 --python export_environment.py -- /path/to/S29/candidate.blend
5. python independent_review_s30.py && python independent_environment_s30.py (NumPy required).
6. blender -b -t 4 --python render.py -- /path/to/S29/candidate.blend

Native output is output/candidate.blend. Do not equate a new local candidate with a verified release: publish only after independent geometry and visual acceptance, complete archive backup and separate remote reconstruction. Preserve old history and branch; retire predecessor payload only after successful remote verification.

Next: assess actual spatial/use benefits before adding more props. Do not add four-box hardware rejected by stores_retrieval_20261112, more coast stones, or repeatedly re-render unchanged views as fictitious model progress.

Acceptance: output/VISUAL_REVIEW.json accepts a bounded local improvement only. Native preservation, independent component/support checks, current-source environment test and fresh recipe reproduction passed. The inkpot is a static closed-cylinder representation; pages are blank solid blocks. No real vessel, writing or opening function is claimed.
