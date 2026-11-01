# Existing path surface conformance — actual visual evidence

Practical actual comparison passed owner/parent/art-direction gates; broadhero preservation review positive. Rebuild and remote verification remain owner-controlled and are not claimed here. Original review JSON preserves chronological pending states.

Before V022 SHA: `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`.
Reviewed after SHA: `c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51`.

Only existing path surface conformance is represented: no tree changes, new entrance, new route or accessibility certification. Practical camera is elevated stand/path inspection, not a human-eye walkthrough. Before images are exact historical V022 renders; after images are fresh candidate actual renders. Original80samples, world, lighting and exposure retained; paired settings match except output filepath. Technical terrain/footprint/material preservation proof belongs to independent QA, not image inference.

Full original images in `../../previews`. Bilingual pair uniformly rescales to50% using LANCZOS, labels outside pixels; no painting, exposure or color correction. Original receipt paths record historical execution, not runtime dependencies.

## Reproduce

Workers/helper/manifests in this directory are unchanged executed self-contained files. Linux Blender5.2.3 and standard Unix `resource` telemetry required; no actual Windows claim. Use non-optimized Python guards. Explicit source and fresh output folder required; output parent must exist.

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python render_stand.py -- --source /path/to/candidate.blend --source-sha c4b1dda3b8f70e4c8cb0171834b2150b6d7610f6296847362fd204b2dfa7ad51 --manifest views.json --view stand --output-dir /path/to/new-output
```

For broadhero substitute `render_hero.py`, `hero_views.json`, `--view hero`. For baseline use originalV022 source andSHA. All1200×866/80samples/CPU8threads; no source save. Timings/RSS are observations, not benchmark claims. Scratch orchestrators/composition scripts and bulk logs/cache are omitted rather than advertised as portable tools.
