# V028 independent saved-model QA

Read-only, non-render validation of the reversible receiving chamber. Source v027 SHA `37c0db0e...a255`; accepted v028 SHA `f0d135e0...8096`. No old unlit binary is needed. No historical source or canonical file is saved.

```
PYTHONDONTWRITEBYTECODE=1 python -B run_qa.py \
 --blender /absolute/path/to/blender \
 --source /fresh/v027.blend \
 --candidate /fresh/v028.blend \
 --candidate-sha FULL_SHA256 \
 --reference-export /public/reproduce/native.json.gz \
 --output-dir /new/external/qa_results
```

For a fresh rebuilt candidate whose save bytes differ, add `--accepted /restored/accepted_v028.blend`. The accepted file must have the fixed SHA above; full persistent/evaluated semantics are checked first. This does not waive subsequent boundary/source checks. `--preflight-only` validates inputs without creating output.

The shared reproduction `native.json.gz` must decode to exact export SHA `83593439fc128700af9302eb1e53185b3f782b00f39e1b7cb972a72823dc362e`. A byte-exact raw JSON is also accepted. The runner decompresses into its own external output, not the immutable bundle. All 29 full actual components and complete visibility/instance metadata remain available; no private workspace imports or reference model cache is required.

Run with the tested Blender 5.2.3 build and host Python with NumPy available. No install is performed. Linux background execution is tested; no native Windows or GUI claim. The runner rejects `-O`, malformed identities, symlink/traversal/role aliases, occupied output and output inside immutable/input directories. Every child inherits no-bytecode; Blender also sets it explicitly. `FILES.json` inventories all payload files. Inputs and bundle must remain byte-exact throughout.

## Gates and counts

Normal accepted-byte run: **2 native calls**, **13 Python calls**. Rebuild comparison adds **1 native call**. Native calls are source/mask/rollback/export and four focused mutation controls, not renders.

CPU gates include independent quantized-cell boundary, eight outside source domains and112 exact remote polygons, exact per-host volume conservation, actual native parent triangulation coverage, finite positive seats, continuous body/near-plane boxes, explicit coplanar scans, saved fixture geometry and contacts. Six altered actual geometry controls, ten exact-boundary math controls and nine explicit-coplanar controls run. Fourteen runner controls are separate pure orchestration tests (`python -B test_runner.py`).

The final validator compares direct baseline→final candidate with exactly four architecture meshes, twenty fixture meshes, two point lights, three owned Masks/148weights and two collections allowed. It verifies both original-template fixture copies without a private unlit file. Added new mesh uniform flags/absence of extra custom layers are explicitly checked. Existing source attributes and all earlier controls remain strict. Only the documented derived evaluated edge-selection UI of three historical SUBSURF traveler objects is normalized; raw data is not waived.

## Scope and numerical honesty

Saved float32 geometry is compared using exact rational area/volume arithmetic where applicable. Nominal decimal planes are not claimed exact: 1,038 nominal cells coalesce to948 saved-coordinate cells. Three exactly collinear native derived triangles are recorded after proving their positive parent polygons are completely covered without overlap. No epsilon near-zero triangle deletion is allowed.

Separate outside hosts retain their inherited overlaps and remote polygon records. Guard caps are opposite-facing internal partitions; this is not a globally welded solid or a global zero-coplanar claim. Seating/body tests do not establish engineering capacity, human gait or full-floor accessibility. Camera checks establish near-plane/body geometry, not appearance. Actual image acceptance remains separate.

`provenance/` preserves the earlier executed reports/scripts and the rejected matrix-assignment placement diagnostic. The public adapter combines stages and replaces paths, so it must pass its own isolated full execution before publication; it is not retroactively described as the earlier executed code. The first lamp placement had a tiny but real orientation-matrix drift and was rejected, then corrected using location-only translation without tolerance relaxation.

The camera-complete revision reruns the single corrected reverse pose’s continuous inset-aperture pyramid clipping,221 finite rays, body/near-plane proxies and actual saved pier footprints. It does not search poses or require both complete piers in frame.

Decoded/copied source-reference and frozen-plan data are also inventoried after every child. They are derived read-only inputs despite residing under the new report directory.
