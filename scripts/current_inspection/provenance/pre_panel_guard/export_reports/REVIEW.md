# v028 editable-scene workflow review — read-only

## Evidence / limits
Accepted source `work/v028/castle_v028.blend`, SHA256 `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096`. Native Blender 5.2.3 inventory session 75942 exited 0. Source hash identical before/after; no save/render. `inventory.py`, `inventory.log`, `inventory.json` record actual canonical state, not an inferred collection layout. This is workflow evidence, not whole-scene edit safety certification.

269 objects, 28 collections, one `ViewLayer`. Every object has one collection membership. 29 objects are not visible in this layer. Five original cameras exist; canonical contains no embedded Text. Saved active object is `V027 | three pointed bays with high wall bands`; active scene camera is `V002 | full coastal skyline camera`. Current separate inspection exporter supplies the reviewed 18 bookmarks, manual UI and optional tree modes; those preview cameras are NOT already canonical objects.

## Concrete confusion and unsafe shortcuts
1. Five **accepted** v019–v023 collections still bear `UNACCEPTED` names; several objects say `candidate`. This retained provenance is not current acceptance status. Searching for accepted work by label alone is misleading. Do not silently rename tested canonical data: an explicit manual selection label can give users an accurate accepted-function entry point without breaking name-bound guards/history.
2. Historical rollback originals are not consolidated in one backup collection. They coexist with current geometry in architecture/version collections and use both global `hide_viewport` and per-layer eye hiding, with `hide_render`. Blind Alt-H or collection isolation is not a supported rollback: it may expose originals alongside replacements.
3. Visible source objects are often **mixed current geometry plus masked historical components**, not discardable backups. `V008 | gallery with genuine eastern approach portal` has BEVEL → V024 Mask → V025 Mask; order matters. V012 foundation/ashlar/east lining each carry the V028 mask, while other V012 hosts carry V021/V022 masks. Forest source has its V019 mask; path source its V023 mask; main shaft its V026 mask. Disabling a mask alone reintroduces originals without removing corresponding additions.
4. The room collection contains four meshes but only `V028 | local receiving chamber shell` is the compact local chamber. The other three `outside chamber guard` meshes retain large source foundation/ashlar/lining regions. Selecting the whole collection as a room-edit group risks accidentally moving unrelated architecture.
5. Room lantern collection has 20 meshes plus two actual lights. A material or geometry selection command should not silently include lights. Single-user mesh data does not mean single-user materials: existing stone/wood/foliage graphs remain shared. Selection is navigation, not permission to transform an assembly or edit its material globally.

## Recommended bounded improvement — separate inspection copy only
Add a small manual **Select accepted geometry** section, not canonical collection restructuring. Four explicit sets in `SELECTION_PROPOSAL.json`:
- Receiving chamber local shell: 1 mesh (exclude outside-guard remnants).
- Room lantern bodies: 20 meshes (exclude the 2 lights).
- Entrance ceiling bays: 1 mesh.
- Near foreground HIGH tree: 2 meshes; refuse while LOW or otherwise hidden, never restore visibility automatically.

All nominated meshes are actually visible, one-user and separately named in accepted source. Display a short shared-material/assembly warning. Do not call them isolated, independently movable or safe-to-delete assets.

Initial minimal action: Object-mode-only, explicit select/deselect + deterministic active object. Optional separate **Frame selected** can be proposed later, but initial selection-only avoids changing any reviewed camera or viewport pose. Existing bookmarks remain the framing mechanism. No collection moves, object renames, masks, visibility, light/material changes, local-view isolation, edit-mode changes, autoexecution, new cameras or new geometry.

Preflight before any selection mutation: pinned tagged inspection copy/runtime; exact target names/types/data identity; all targets present in active view layer, actually visible and selectable, accepted single collection paths, no hidden ancestors/instances/foreign substitutions. Fail closed if source state is edited or HIGH targets hidden. Never auto-unhide. Reject Edit Mode rather than trying to exit and potentially commit edits. Snapshot selection/active-object state; restore on partial failure.

## Required future tests (not implemented / not run)
- OFF/HIGH/LOW: existing 18 bookmark and tree APIs unchanged; HIGH-tree selection refusal in LOW leaves all state unchanged.
- Successful actions modify only documented selection/active-object fields; exact mesh/attributes/material/light/world/camera/collection/mask/weight and viewport state preservation.
- Repetition adds no objects; no stale selection leakage; correct deterministic active object.
- Missing/renamed/shared/replaced target, local-eye/ancestor/excluded-layer/hide-select, Edit Mode, untagged/stale runtime and injected partial selection failure refuse/rollback.
- Owned registration/unregistration recovery remains intact after ordinary edits; no global autoexec.

This closes discovery with a concrete selection-access proposal. No implementation authority assumed; no further native work required for the proposal.
