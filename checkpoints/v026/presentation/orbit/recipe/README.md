# V026 exterior partial orbit — new opt-in recipe

**Not a completed V026 video.** Current authorization is one representative production-quality frame49 after code/preflight review. Full96-frame rendering requires a separate owner decision after the pilot's actual image and cost review. No render has yet been performed by this recipe at this documentation stage.

The96 camera poses,40°partial exterior arc,960×694 resolution,12fps/8s duration and original80sample/adaptive/bounce/denoise quality match the immutable historical V016 recipe. This is not360°, a walkthrough, or an architectural edit. Input is accepted V026 SHA `efcd894acdc045a30f845f05267662957b656bc7fe0ee4cf48c05fc798b610ee`,47,680,699bytes. Original scene frame1 is fixed. Lighting/world/exposure are unchanged; full world/light graph and transform digest is checked before/after each render. Camera basis, projection and DOF are checked, not only forward direction.

## Requirements and authority

Linux, existing Blender5.2.3, Python with Pillow for lossless PNG validation; no auto-install. ffmpeg/ffprobe are required only if full encoding is requested. Current cloud profile8threads on9logical-affinity CPUs is explicit; no saved model setting changes. Frozen historic files remain untouched.

Configure one writable **existing** per-user cache root consistently for all cooperating runs. The stable worker-held lease is `$XDG_CACHE_HOME/seaside-castle/orbit-execution.lock`, acquired before source loading. It survives coordinator death and serializes this recipe across output roots using that same configuration. Never delete/recreate the lease to bypass another worker. Changing cache configuration changes identity; different users/cache namespaces/manual Blender are not globally excluded. `/proc` checking is an additional visible-process advisory, not a universal namespace guarantee. The output coordinator separately holds `runner.lock` through the run.

Example cloud-only pilot (replace paths appropriately; output parent and cache must already exist):

```sh
XDG_CACHE_HOME=/path/to/writable-cache python -B /path/to/recipe/run_final_orbit.py --source /path/to/castle_v026.blend --blender /path/to/existing/blender --output-dir /path/to/new-orbit-output --pilot-frame 49 --dry-run
XDG_CACHE_HOME=/path/to/writable-cache python -B /path/to/recipe/run_final_orbit.py --source /path/to/castle_v026.blend --blender /path/to/existing/blender --output-dir /path/to/new-orbit-output --pilot-frame 49
```

The pilot renders exactly one actual frame, validates PNG/source/recipe/quality/runtime/camera/lighting, writes `pilot_frame49.json`, then returns without a full manifest or encode. Repeating pilot verifies/skips valid49. After explicit later approval, replace `--pilot-frame 49` with `--full` using exactly the same source/code/plan/cache/output identity; verified49 is reused, not relabeled. `--skip-encode` can retain frames-only full output. No implicit full mode exists.

## Integrity and recovery

`RUNTIME_BINDINGS.json` pins five runtime files. Plan bytes are separately pinned in runtime guards; run identity binds complete code/plan/source and lease path. Rechecks occur after authoritative output lock, before and after each frame, and before final/encoded publication. Input/source/recipe aliases, symlinks, unknown nonempty output and mismatched identities fail closed. Optimized Python is refused because inherited validators use assertions. Blender starts factory-empty with autoexec disabled, explicit Python exit-code1 and no-bytecode setup; worker acquires execution lease before opening source. Source is never saved.

Completed frames are decoded and rechecked, not trusted by filename. Invalid completed folders are moved to quarantine; failed attempt directories/logs are retained for diagnosis. A crashed coordinator does not cause a valid orphan output to be adopted blindly; the worker lease protects its execution and subsequent resume validates only finalized frames. Keep source, code, receipts and lock files intact. A runtime change requires a new identity/output, not receipt migration.

Full encoding, if later approved, uses96actual PNGs without interpolation/audio, H264/yuv420p, exact12fps PTS/8seconds checks and strict full ffmpeg decode. The pilot does not exercise video encoding; no video-success claim follows from fixture tests.

## Tests and evidence

CPU-only fixtures currently cover18 frame-validation cases and12 guard/resume cases, including exact pilot stop, verified resume, corrupt-image quarantine, altered source/recipe/worker/runner, camera roll/sensor/shift/DOF, late NaN matrix/time and negative time, paths and output locks. Synthetic PNGs are fixtures, never production frames. Independent review and actual Linux pilot remain separate gates. Compatibility rays are finite samples, not a proof that every pixel is unobstructed; cloud/forest and near-facade occlusion remain actual-scene presentation conditions.
