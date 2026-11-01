# V020 square exhibition portrait A

Actual native Blender camera still, not a model revision. Source SHA256 `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`; unchanged world, lights, exposure and geometry. Owner/art director selected A from exactly four low-cost actual camera studies. This is a concentrated square exhibition composition, **not a replacement for the full-site landscape hero**.

Final: `polished_A/image.png`, 2400×2400, original80 Cycles samples, CPU8threads. `polished_review.json` records full-image and native-pixel crown/bridge/coast inspection. `polish_camera_check.json` proves identical selected A camera recipe; resolution600→2400 and preview16→original80 samples are the intended quality changes. No image generation, retouching, supersampling, source save, or new camera search.

## Reproduce

Linux Blender5.2.3 required; workers use standard Unix `resource` telemetry. Native Windows execution is not claimed. No dependencies are installed automatically. Run with ordinary non-optimized Python (guards use assertions):

```sh
python run_polished.py --source /absolute/path/castle_v020.blend --blender /absolute/path/blender --output-dir /absolute/path/new-output
```

The output parent must exist and output directory must not exist. Runtime worker/helper/manifest live beside the wrapper and have no scratch-directory import dependencies. Source hash is pinned; all originalquality/world/light settings are checked. `run_polished.py` launches one fresh Blender and records script/manifest/helper hashes, source hash, command, image hash and elapsedtime. Source never saved.

Optional four-preview reproduction:

```sh
python run_previews.py --source /absolute/path/castle_v020.blend --blender /absolute/path/blender --output-dir /absolute/path/new-preview-set
```

Preview poses/aspects are explicit in `views.json`;16samples only, not final quality. This bounded still harness assumes one operator/coordinator and unchanged code/helper. Completed receipts/source/manifest/worker/image are checked before skipping; invalid partial outputs stop. It is not the hardened production film runner and does not claim orphan-safe multi-process coordination.

## Evidence/provenance

Receipts copied unchanged retain execution-time absolute scratch paths as provenance, not dependencies. `previews/complete.json` pins executed preview code/helper/manifest. The initial pre-render guard failure (80→16 mirrored Cycles custom-property samples also needed updating) produced no image; corrected worker generated all four archived previews. No source or pose changed in that recovery.

`composition_review.png` shows four new16sample previews and historical80sample V020 hero at comparable displayed area, uniformly downsampled without exposure/color edits. The historical reference is not a fifth newrender. `composition_review.json` preserves source hashes and scale metadata. Scratch composition/preflight scripts are not bundled as portable tools; executed image workers and camera manifests are self-contained. Bounds/projection data are limited framing evidence, not an occlusion proof.

Individual runtime/memory measurements are observations, not controlled performance benchmarks. Publication/remote verification belongs to the owner; this archive makes no claim that remote backup is complete.
