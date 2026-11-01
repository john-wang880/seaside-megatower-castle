# Provenance and recovery boundary

Historical V016 film and its46 archived files remain unchanged. They depict source `d44a4cde…`, not current V026. The new recipe retains all96 historical camera poses/composition and rendering quality, but pins current source `efcd894a…`, new runtime identities and additional world/light/projection validation. Historical frames, receipts or approvals are not migrated or relabeled as current renders.

Current planned output is a new directory. At this documentation stage no current-source production frame or film has been rendered. A successful one-frame pilot means only frame49 passed under the new identity; it is not a completed96-frame film. A later separately authorized full run can reuse that exact validated PNG+metadata and render the other95 frames.

## What a checkpoint can recover

- Recipe/code/plan/source hashes recover intended work and let source/model restoration be verified.
- Per-frame metadata/journal recover provenance and progress records, **not missing image pixels**.
- A frame can be skipped only when its actual PNG and metadata are present and both pass source/code/quality/camera/lighting checks, PNG hash and decoded dimensions.
- If a cloud workspace reset removes PNGs and no explicit PNG backup exists, those frames must be rendered again. Do not infer a recoverable image from a metadata receipt, thumbnail, old video, or filename.
- A completed encoded video can be delivered/played after its own checks but is lossy and is not a replacement for original PNGs in exact resume validation.

Safe resume retains failed attempt folders/logs and quarantines invalid completed frames. Never edit source/code/identity or delete a held lock to force progress. Only the same runtime/source/plan/cache identity can reuse valid frames. A changed recipe needs a new output namespace and new actual review. The worker lease protects cooperating runs with the same configured cache; it is not a global guarantee across unrelated manual Blender or different namespaces.

Backing up recipe/manifests alone does not imply frame/video backup. Any final publication should state explicitly which of raw PNGs, receipts and encoded video were actually archived and freshly verified remotely.
