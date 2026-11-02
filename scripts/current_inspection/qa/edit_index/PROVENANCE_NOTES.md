# Independent QA provenance and limits

The staged exporter and all four exported viewers are immutable during this audit. No canonical saves or renders are made.

## Superseded QA setup attempts (not product failures)
- The first expected embedded-Text reconstruction placed the CONFIG index-enabled key before the runtime-identity key, while the exporter emitted the reverse insertion order. Dictionary values agreed, but repr bytes did not. The retained initial script/log records this strict setup refusal; the corrected checker matches actual literal assembly without changing runtime.
- The first selection checker tried to restore pre-test viewport state by selecting the hero bookmark. A bookmark intentionally selects camera perspective and does not restore an arbitrary original perspective. The corrected checker restores only the precise fields changed by its own bookmark calls: scene camera and each VIEW_3D space camera, use_local_camera and region_3d.view_perspective. Every individual index action still compares current camera/viewport state directly, with no normalization.
- A subsequent test cleanup exposed Blender's coupling between a VIEW_3D non-local camera setter and scene.camera. The final cleanup restores the scene camera last; the intermediate setup failure remains archived. No runtime or direct per-action invariance check changed.
- The first pure comparator invocation preceded creation of its imported runner and failed one import. The runner was then staged and all eight methods rerun.
- A combined unittest discovery invocation lacked the independent path-test script's required CLI parameters. The scripts were subsequently invoked using their respective APIs; no test predicate was changed.

## Scope
Thirteen actual snapshot categories are meshes, objects, materials, lights, cameras, worlds, visible_evaluated, scene, libraries, texts, collections, scene_custom and visibility. Raw data stays strict. The inherited derived-only SUBSURF traveler selection-edge exception is recorded explicitly by the modes report; it is not a generic attribute waiver.

Selection is not isolation, edit permission or shared material-graph certification. The optional tool intentionally rejects stale target geometry/transform fingerprints after edits. LOW lineage is target-only against the exact v018 c46 baseline, not whole-scene equivalence to v018. Native tests use Linux background Blender API, not desktop GUI or native Windows.

## Native mutation-fixture diagnosis
The original combined selection stress run terminated with exit 139, with no Python backtrace. A fresh split negative run later localized a second crash after a smoothing/material-index mutation fixture. Per-fixture exact fingerprint restoration isolated the first drift to a MeshPolygon RNA wrapper retained across dependency-graph updates. The final checker reacquires the polygon from its mesh for every setter/restore; all 37 selection negatives then passed, including exact restoration and two partial-transaction tests. The deliberately out-of-range material index is tested through the raw guard and restored before requesting evaluated geometry, rather than asking native Blender to shade malformed data.

Earlier hypotheses of repeated-load accumulation or Edit Mode topology change were not established. The successful isolated Edit Mode fixture recorded no fingerprint change. Both crash traces and failed logs/scripts remain; the positive supported repeated registration/reopen sequence is independently replayed in a fresh process. This is bounded evidence, not a universal crash-free usage claim.

## Guarded panel revision
After the first unpublished action-only acceptance, owner found accepted labels could still draw on a foreign/unowned scene. The mapper made the minimal verify-plus-opt-in Panel.draw guard and re-exported all four viewers without changing canonical data or selection behavior. This final bundle's three native phases and six direct draw controls passed afresh. Earlier setup/crash evidence is under provenance/initial_qa; it is neither hidden nor relabeled as a final-runtime failure. Exact stale-polygon-wrapper diagnosis and correction above remain applicable.
