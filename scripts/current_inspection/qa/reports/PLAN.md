# Optional v027 inspection-copy tree quality — independent QA design

Design only. No Blender, model save, render, or implementation in this pass. Accepted source remains SHA 37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255. Historical v019 quality files remain frozen; their source pin and standalone viewer marker are not reusable for the latest copy.

## Allowed operation and baseline

Default export remains OFF (no quality controls enabled), per owner architecture. Explicit HIGH preserves current accepted v027; explicit LOW enables the optional paired mode. LOW disables only viewport/render evaluation of `V019 candidate | original foliage rollback mask` on `V010 | woodland boughs with gate exit clearance`; it hides viewport/render of `V019 candidate | articulated conifer foliage` AND `V019 candidate | connected conifer boughs`. Original wood remains unchanged and visible. Exactly six Boolean flags plus explicitly owned mode metadata may change. No new vertex weights, mesh copies, material changes, LOD geometry, collection hiding, camera changes, automatic save or script execution.

The v027 file already retains the original full foliage mesh. It is sufficient for runtime LOW reconstruction without loading a historical model. However current-source-only equality is not an independent proof of v018 lineage. For QA, use byte-pinned c46 historical v018 once, comparing the target foliage raw/evaluated geometry, attributes, effective material slots/graphs, world transform, and associated retained original wood. Compare LOW's non-target scene against v027, NOT all of v018. An archived exact semantic reference could substitute only with documented c46 extraction provenance and full fields; prior pass Boolean or vertex count alone cannot.

## Native acceptance, after explicit slot grant

1. Pin source, tool/runtime, catalog, embedded manual Text, export receipt, baseline and new viewer hashes. Reuse current latest-manifest/source guards. Export to new paths; reopen HIGH and LOW with automatic scripts disabled. Marker is provenance, not post-user-edit certification.
2. Snapshot all emitted deep categories, raw arrays/attributes/deform weights, materials, objects, world/lights, cameras, collections and view-layer/local visibility. Normalize ONLY exact owned Text/marker and six state flags. All earlier source modifiers/groups/weights and hidden original forest remain exact. HIGH evaluated visible scene equals v027 plus the already-reviewed inspection cameras. LOW removes only the two authored meshes and replaces target evaluation with original lineage; retained authored raw geometry is still exact.
3. Verify exact owned 298 weights at indices [90395,90693), group identity/index, and entire modifier stack. Require vertex-group mode, no armature, inverted Mask, threshold .5, smoothing off, native settings unchanged. Any LOW evaluated deform normalization must enumerate actual exact owned values first; do not drop all weights or unknown attributes. Preserve the narrow historical three-Traveler evaluated UI-edge exception only if reproduced and separately reported.
4. Preserve all 16 camera catalog records/data/poses/projection and existing inspection collection/Text behavior. Tree transitions must not change scene camera, viewport perspective/local camera, rendering settings, world or lights. Interleave all bookmark selections with HIGH/LOW; each operation may change only its own established allowance. Capture camera state immediately before each tree transition rather than resetting to hero to hide drift.
5. Repeated HIGH/HIGH/LOW/LOW/HIGH and fresh reopen in both saved modes: no object/data duplication, no ghost bough wood, no changed materials/transforms, no accumulated state. Register twice, invoke actual Python operators in valid and foreign scene/view-layer contexts, unregister twice; no unrelated class removal or handlers. Background API success is not native GUI-click testing.
6. Effective visibility must be validated for target and both authored meshes in EVERY relevant view layer: collection and layer ancestors, exclusion, hide_viewport/hide_render, hide_get, multiple memberships. Refuse unsupported multiple paths or instancing/dependencies rather than guessing or unhiding. A hidden HIGH object is allowed only by the exact paired LOW flags, not by arbitrary ancestors or local eye state.

## Negative cases and atomicity

- Untagged canonical; stale source/latest catalog; missing/foreign marker or Text; missing/renamed owned object/group/Mask; name/class collision.
- Wrong/extra weight, wrong Mask mode/group/inversion/threshold/order or smoothing; mixed flags or metadata mismatch; mutated original foliage/wood/material/world transform detected by acceptance QA.
- Hidden target or either object's local eye; hidden/excluded ancestors in a non-active layer; multiple membership; collection instance/dependency creating another visible high-tree occurrence.
- Source/output/report alias and hardlink/symlink; pre-existing/foreign output; unsupported publication filesystem; -O; injected second-publication failure/foreign inode replacement. Only owned temporary/published inodes may be rolled back.
- Every refused transition leaves pre-call flags, mode marker, all camera state and other scene state unchanged. Verify rollback after an injected mid-transition failure, not only preflight rejection.

## Scope and stop condition

Pass means reversible single-tree display state on a fresh exact inspection copy, HIGH current v027 and LOW original-tree lineage; not whole-scene v018 rollback or cleanup of user edits. Both meshes remain stored: no file-size or load-memory savings claim. No performance estimate or pixel-identity claim without new measurements. No render is requested for this design task. Existing v019 same-camera pixel comparisons remain historical evidence, not new v027 render proof. Stop after parent reviews architecture and authorizes bounded implementation/native validation.
