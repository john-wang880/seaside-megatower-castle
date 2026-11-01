# V020 reviewed candidate visual evidence

Candidate SHA: `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614`.
Baseline V019 SHA: `e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a`.

Approach and oblique passed owner/art-director visual review; hero preservation review is positive. This evidence describes the reviewed candidate, **not completed rebuild/remote acceptance**. Original staged review JSON records the chronological gates, including earlier holds now resolved by subsequent images.

Before approach/hero images are exact previously rendered V019 references; before oblique is a new matching-camera V019 render. All after images are actual current candidate renders. Receipts are copied byte-for-byte and retain original scratch paths as historical provenance, not runtime dependencies. Comparison JSON verifies matching settings except output filepath. Resource timings are individual observations, not a controlled benchmark.

Contact sheets use uniform 50% LANCZOS downscale, labels outside images, no exposure or color editing. Original full-resolution images are retained alongside them.

## Reproduce an individual actual still (Linux Blender 5.2.3)

The unchanged tested workers and local `preservation_support.py` are self-contained. They require Blender Python and Unix `resource`; they are not claimed Windows-portable. Source file and its exact SHA are explicit arguments. An output parent must exist, but the output directory itself must not exist.

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python render_one.py -- --source /path/to/candidate.blend --source-sha 673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614 --manifest views.json --view hero --output-dir /path/to/new-output
```

For approach use `--view approach`; for oblique use `render_oblique_one.py`, `oblique_views.json`, `--view oblique`. For the baseline supply the V019 source and SHA above. Workers retain original world/light/exposure/80-sample settings and do not save source models.

Scratch orchestration and composition scripts contain work-directory assumptions and are deliberately not presented as portable scripts. The copied workers/configs suffice for fresh actual images. No logs or cache payload are included.
