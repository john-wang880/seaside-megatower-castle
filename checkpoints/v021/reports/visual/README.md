# V021 accepted local appearance — visual evidence

Actual bridge comparison and broad hero passed owner/art-direction review. **Rebuild and remote verification remain owner-controlled; this archive does not claim remote completion.** Original review/provenance JSON is copied unchanged and preserves chronological pending gates; this wrapper records the later visual acceptance.

Before model SHA: `673dbbadca22d3dd45dc2f2eb5bde4a9e66851c1ca137da5c2570efc67c77614` (V020).
After candidate SHA: `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`.

Full original PNGs are under `../../previews`. Bridge before is the original feasibility render, hero before is the exact historical published V020 image, not newly rendered references. After images are actual native candidate renders at identical camera, quality, world/lights/exposure. Paired comparisons check every captured settings field except output filepath. Receipts retain original execution paths as historical provenance, not imported runtime dependencies.

The bilingual pair uniformly rescales each1200×866 image to600×433 using LANCZOS, with labels outside images. No color/exposure edits, painting or retouching. Technical meaning: identical occupied union shape, duplicate exposed surfaces removed; no new support or filling. Geometry preservation proof lives in the independent technical audit, not inferred solely from these images.

## Reproduce one actual view

Unchanged tested workers, helper and manifests are self-contained in this directory. Linux Blender5.2.3 is required (`resource` telemetry is Unix-only); no native Windows claim. Use non-optimized Python/Blender scripts because guards use assertions. Existing source and explicit fresh output directory required; output parent must already exist.

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python render_arch.py -- --source /path/to/candidate.blend --source-sha 457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9 --manifest views.json --view arch --output-dir /path/to/new-arch-output
```

For hero use `render_hero.py`, `hero_views.json`, `--view hero`. For before supply original V020 file and673 SHA above. All views1200×866, original80samples, CPU8threads, unchanged lights/world/view. No source save. No scratch orchestrators/composition scripts are advertised as portable tools, and no logs/cache payload are included. Individual timing/RSS observations are not a controlled benchmark.
