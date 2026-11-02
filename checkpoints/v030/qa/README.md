# v030 fittings independent QA

Requires Blender 5.2.3 and Python with existing numpy. No installation, render or model save. Source is exact v029 `4f838529…882df5`; accepted v030 is `9f020b7e…feda35`. Rebuilt candidate bytes may differ only after full saved semantic equality against the supplied accepted file. The source .blend is an explicit external historical dependency; no workspace-relative imports or hidden model files are used.

```sh
PYTHONDONTWRITEBYTECODE=1 python -B /absolute/qa/run_qa.py \
 --blender /absolute/blender-5.2.3-linux-x64/blender \
 --source /absolute/source/castle_v029.blend \
 --candidate /absolute/candidate/rebuilt.blend --candidate-sha FULL_SHA256 \
 --accepted /absolute/accepted/castle_v030.blend \
 --output-dir /absolute/new_external_results
```

For exact accepted bytes, omit `--accepted`; the candidate must then match the accepted pin. Output must not exist, must have an existing parent, and must be outside the bundle and all model input directories. Paths with symlink ancestors or `..` are refused. Optimized runner/native Python is refused. The runner checks the complete frozen inventory, compressed input hashes, decompressed inputs and model hashes before/after. It uses inherited no-bytecode and an output-local cache.

Sequence: two sequential native processes (semantic repeat plus two focused in-memory snapshot controls; full source preservation/export/additive rollback), then four Python processes (actual bearing, clearance, material, geometry/math controls). Do not run concurrently with another authorized native job. Every JSON pass gate is inspected, not just exit codes. The derived expected geometry contract changes only the runtime candidate hash in a copy of the frozen original builder receipt; it is explicitly not represented as a receipt produced by the rebuilt file's builder.

## Scope and limits

Six objects, 78 closed convex components, 2,184 triangles, one local timber material and one collection. All 13 original persistent/evaluated categories preserved with only named traveler derived edge-selection normalization. Whole actual octagonal foot coverage, rail/post positive intersections, shelf/rail bearing, full bin/body/lid seats and a rooted contact graph are checked. Intentional volumetric post/rail joints and opposite-facing bearing interfaces remain; this is not a globally welded/nonintersecting assembly or structural capacity certification.

Explicit exact-plane clipping finds no same-facing positive-area coincident new skins; finite actual camera/light rays and protected body clearance are checked against 53 source/fixture components. This does not claim universal near-plane depth separation, full emitter visibility or visual acceptance.

Six exported geometry mutations are caught first by prescribed profile/topology/ownership predicates; they are **not** claims of downstream bearing-predicate injection. A separate equal-area missing-plus-duplicated coverage control directly checks that missing and multiple coverage cannot cancel. Two native snapshot controls mutate and restore unrelated original geometry/material in memory. `test_runner.py` adds five lightweight orchestration/path controls.

`provenance/` retains original local executed results and hashes. Portable script diffs change only input/output resolution; original equations and tests remain. Original local technical results do not themselves certify the portable wrapper: a fresh isolated complete run is required and will produce a separate SUMMARY.json. Art remains a separate actual-image gate.
