# Rebuild the v030 fitted-stores candidate

Restore v029 source from fixed Git commit `d753ba032b1d3138a1d0c34e13b0caee40b3d92f` in a separate archive. Its SHA256 is `4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5`. Use existing official Blender 5.2.3; this recipe installs nothing.

```sh
blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python build_fittings.py -- --source /absolute/castle_v029.blend --output /absolute/new/castle_v030.blend --report /absolute/new/build.json
```

Parents must already exist and outputs must not. The source cannot be overwritten. Opening a model does not run this script; construction is explicit. The model is additive: two racks and four body/lid bin objects, 78 closed components, 2,184 triangles, one local material. No original geometry, lighting, camera or route is changed.

Different .blend serialization hashes are expected across builds; use the independent QA runner with restored accepted model to verify complete semantic equivalence. Frozen plan paths are historical provenance, not external runtime dependencies. Actual geometry/material outputs and source hashes are recorded.

`test_builder.py` has 15 pure tests. Native Linux replay is separately recorded; Windows command execution is not claimed.
