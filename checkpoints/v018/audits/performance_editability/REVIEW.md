# Read-only performance / editability assessment — v018

## Decision
No cleanup candidate recommended. There is no demonstrated orphan purge or redundant-heavy-forest opportunity in the current source. Small exact lantern mesh duplicates exist, but consolidating them changes linked-edit semantics for negligible demonstrated benefit; no saved-byte or runtime improvement was measured. Keep canonical v018 unchanged.

## Actual inventory (Blender 5.2.3, source opened read-only)
- File35,962,496bytes, source SHA c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd, unchanged after audit.
-202 mesh datablocks used by214 mesh objects;66 materials,5 cameras,7 lights. No zero-user or fake-user-only candidates in these categories.
-Zero images/actions/node-groups/curves/textures: no packed-image or animation-cache purge target.
-17 collections, none empty.29 hidden mesh objects are preserved historical/editable baselines; visibility is not evidence of disposability. The original full forest and trunks are intentionally retained. v011's deleted intermediates are not current candidates.
-12 modifiers: eight BEVEL, three level1 SUBSURF, one SOLIDIFY. Nonzero visible effects or editable preserved originals; no disabled-in-both-modes/no-op stack identified. Removing/applying them would change editing capabilities and requires separate geometry evidence; no performance claim is supported here.

## Exact resource duplicates, bounded significance
Full mesh-content hashes include coordinates, topology, normals, attributes, deform weights, shape keys, UV metadata, material slot identities and custom properties. Seven groups of identical lantern-part mesh payloads contain30 redundant datablocks in principle, totaling954 duplicate vertices and690 duplicate polygons. These are actual element counts, **not estimated saved file bytes, memory or render-time savings**. Groups are recorded verbatim in `inventory.json`.

Some stair-part resources already have two users. Consolidation of the rest would make formerly independent edits propagate to other lantern parts. If a later explicit linked-fixture editing request justifies it, a candidate could map these exact groups to shared meshes while preserving all object transforms/material overrides and evaluated geometry, compare source-aware deep snapshots, render identical cameras and measure actual saved file/runtime. That is not justified merely to create another version now.

Materials all have users. This audit did not prove duplicate material node graphs, so it makes no material-dedup claim. Datablock users can include dependency references; absence of zero users is not a proof every resource contributes pixels, nor authorization to remove hidden history.

## Limits / evidence
`audit.py`, `audit.log`, `inventory.json`. One read-only Blender inventory, no model save, deletion, bake, render, Git write or benchmark. Existing collections retain version/functional names for reversibility. Generic cleanup or renaming risks breaking exact-name recovery/validation scripts and is not a demonstrated editability improvement.
