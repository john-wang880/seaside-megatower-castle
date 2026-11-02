# V029 independent read-only QA

Requires Blender **5.2.3**, Python 3 with numpy (already installed in the validated environment). No installs, rendering or saving. Canonical source is v028 `f0d135…`; accepted v029 is `4f838529…`. Restored source must be hash-exact; a rebuilt candidate may have different bytes only when `--accepted` supplies the exact published accepted file for semantic comparison first.

```
PYTHONDONTWRITEBYTECODE=1 python -B /absolute/qa/run_qa.py \
  --blender /absolute/blender-5.2.3-linux-x64/blender \
  --source /absolute/source/castle_v028.blend \
  --candidate /absolute/rebuilt/rebuilt.blend --candidate-sha FULL_SHA256 \
  --accepted /absolute/accepted/castle_v029.blend \
  --output-dir /absolute/new-external-report-directory
```

For exact accepted-byte replay omit `--accepted`. `--preflight-only` checks identities, complete inventory, decoded export and Blender version, creating no output. Inputs and output must be canonical nonsymlink paths; output must be new and outside bundle/model input directories. No overwrite, `..` traversal, role inode alias or optimized Python. Inherited no-bytecode propagates to every child; a private output cache is used. All bundle/data/models/executable hashes are checked after every stage.

Full chain: **3 native calls with semantic repeat (2 without)** and **9 Python calls**. Native: optional full persistent/evaluated comparator, source→simulated exact Masks→candidate HIGH/rollback/repeat and fixture identity/export, four focused mutation controls. Python: nominal guard, saved-coordinate payload, 7 guard controls, 8 exported-payload/math controls, quantized floor/routes, fixture/camera plan, saved native-parent coverage and actual seats/body/nearplanes, explicit local neighbors, 50 finite saved visibility rays. Inspect `SUMMARY.json` and individual JSON predicates, not only exit codes.

The public adapter changes only runtime path plumbing; original executed scripts and reports remain in `provenance/`. `data/native.json.gz` decodes to pinned actual full source export. No ignored/private workspace imports. Original parent-mapping/volume harness setup failures are described in the retained verdict; native report-serialization failure is retained separately, superseded by the successful identical-predicate run.

Precision: partition-only bottom is 28.900001525878906; all other new guard/cavity coordinates nearest float32. Exact Fraction source-domain/cap/local boundary checks have separate uncovered/outside/multiple area predicates. Native triangles with exactly zero area are excluded only after their positive parent coverage is independently proven. Native fixture rotation bound is 8 float32 eps scaled by matrix magnitude; translation bound is two coordinate ULPs; actual positive seat boxes are independently tested. No globally calibrated physical units.

Twelve emitted snapshot categories include collections and scene custom state. Only separately reported derived UI-selection fields of the three named pre-existing subdivided traveler garments are normalized; all raw deformation weights preserved. Remote268polygon records stay exact; affected11source domains may be retriangulated. Guard interfaces are buried opposite-facing contacts, not an assertion that all original overlapping solids are globally disjoint. No structural, whole-scene manifold, global accessibility or whole-pixel visibility certification. Artistic acceptance is separate.
