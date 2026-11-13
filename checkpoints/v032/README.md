# S32 · Seven-tree branch-cluster grove

A bounded refinement of seven existing foreground/midground conifers, not a whole-forest replacement. New irregular, overlapping twig-end foliage masses replace coarse diamond/flat-tier foliage in this grove. Tree locations, original stems, source materials, castle/rooms, coast, paths, world, lights and original cameras remain. The two-berth S31 room and all preceding accepted work are retained.

## Model and views
Open `candidate.blend` with automatic scripts disabled, using Blender 5.2.3 LTS. `before.png` / `after.png` are a matching moderate architectural grove view in original lighting, not a calibrated eye-height/ground clearance claim. `overview_before.png` / `overview_after.png` preserve the source overview camera and lighting. No AI-generated images or world/exposure retune.

Fourteen new mesh objects contain 16,958 triangle equivalents. Original foliage is preserved behind an additional reversible MASK and vertex group (1,841 complete-component vertices); original prior V019 rollback mask remains. Seven source axes: 127510, 100450, 72640, 17700, 97980, 48440, 26170. Assignment of original connected foliage clumps to tree axes is a documented nearest-axis heuristic, not recovery of original procedural tree IDs. Exact raw/evaluated mapping and no cross-mask faces were checked before changes.

The first prototype had an excessively sparse fishbone silhouette and some crown-envelope overshoot. It was rejected. The revised tree grammar uses thicker, unevenly offset small foliage masses rather than thin repeated fans. A branch-axis-aware affine fit keeps each new crown within its original assigned crown AABB without hard per-vertex clipping. The local change is intentionally restrained; unmodified foreground trees remain visibly stylized. This is not photorealistic needle modeling.

## Verification and boundaries
- Independent CPU checks: each new component closed, opposite edge incidence, positive signed volume, no degenerate triangles; exact declared source-crown AABB containment. Overlapping foliage/wood shells are intentional; not a globally manifold union or complete self-intersection certification.
- 481 foliage masses each have a sampled point strictly inside both the leaf component and an added wood component. These are positive geometric overlap witnesses, not physical fastening/strength certification.
- All 158 new branches cross the actual original stem-side triangle interiors between their end caps. IMPORTANT: original stems have open ends, so the attempted closed-original-solid predicate was **not established** and remains recorded in `INDEPENDENT_ATTACHMENT.json`; only the separate actual-side-surface connection predicate passes. Original stems were not silently capped/rebuilt.
- Two original path surfaces are exactly matched between pinned old source, S31 evaluated geometry and the archived trace. Every new component is separated from the conservative path triangles' 2.1-upward body boxes by at least 14.292755 scene units. Five retained west-castle object domains are separated, and current dependency-graph mesh/instance bounds overlapping the grove were inventoried. These are finite-scope exclusions, not global collision certification or real-world safety.
- Native save/reopen verifies exact reviewed added arrays, precise mask ownership, unchanged source complement, and complete rollback in supported scene/collection snapshot categories. No claim to every Blender API field.
- Fresh source-only build is compared in all supported scene and collection categories. Serialization hashes need not match; geometric/state semantics must.

## Source-only reproduction
Required accepted S31 source SHA256: `a9ececee22e0cb9295698e8baed6e60b7c7fabe2df5b55ca1f3cb545e4bfb9d6`.
Restore S31 from fixed Git commit `95dc7a94f9bd39f22dc3df8d5c0e245443495e54`: extract its entire `checkpoints/v031/` folder in a separate checkout and run its `restore.py`. Input is restored `native/candidate.blend`. Old payload remains recoverable from Git history even if withdrawn from the current tree.

Copy `build.py`, `geometry.py`, and `SCOPE.json` to a fresh output folder. Run:
```
BLENDER -b -t 2 --disable-autoexec --python-exit-code 1 --python NEW_FOLDER/build.py -- ABS_S31_SOURCE.blend
```
Then run this package's `compare_rebuild.py` with `-- ABS_ACCEPTED_S32.blend ABS_REBUILT_S32.blend`. For native saved/source rollback: `check_native.py -- ABS_S31_SOURCE.blend ABS_S32.blend`. These validation scripts do not save source models. CPU audits use bundled `inputs/` pins and the saved geometry/context exports. Python 3 plus numpy is needed for CPU audits; Blender contains its own numpy.

## Continuing work
Do not add more tiers or sharpen this same grove just to create versions. Do not automatically apply the seven-tree recipe to 522 trees or import the rejected r01 coast along with it. Any next coherent grove must be justified in original-light context, preserve specific existing stems and routes, and establish its own exact mask/source boundaries and visible benefit. Frozen historic inspection tools and movies retain their old version identity; no claim of updated compatibility.

Back up full model, reproducible scripts, previews and checks, then reconstruct from the actual remote commit and verify before withdrawing an obsolete current payload. Preserve history; never force push. Stop starting new iterations at 2026-11-30 12:24:59 UTC. Scene units have not been physically calibrated.
