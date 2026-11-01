# Single western rib — actual visual evidence

The practical whole-tier candidate passed owner, parent and art-direction gates; broad hero preservation review is positive. Rebuild/remote acceptance remains owner-controlled and is not claimed here. Earlier review JSON retains chronological pending states.

Before V021 SHA: `457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`.
After reviewed candidate SHA: `99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2`.

Only one existing rib receives restrained stone coursing; no propagation to other ribs is implied. Practical and hero after images are fresh actual native renders. Before practical and hero images are exact historical source-V021 references, not newly rendered baselines. Receipt hashes/settings preserve their source identities. Pair settings match except output filepath. Source lighting/world/exposure and original80samples unchanged.

Full PNGs in `../../previews`; bilingual pair uses uniform50% LANCZOS scaling only, labels outside pixels, no brightness/color editing. Source paths in unchanged receipts/composition metadata are historical provenance, not runtime imports.

## Reproduce a view

Unchanged tested workers/helper/manifests in this directory have no scratch imports. Linux Blender5.2.3 and standard Unix `resource` required; no native Windows claim. Run non-optimized Python guards; output directory must be new and its parent must exist.

```sh
blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python render_tier.py -- --source /path/to/candidate.blend --source-sha 99156d901f9d498b86bae4834a642d1d9110dc6e4e3a4273bca64fda17a9dfd2 --manifest views.json --view tier --output-dir /path/to/new-output
```

For hero substitute `render_hero.py`, `hero_views.json`, `--view hero`. For baseline use originalV021 source/SHA. All1200×866/80samples/8threads; no source save. Runtime/RSS measurements are observations, not controlled performance claims. No scratch orchestration/composition scripts or bulk logs advertised as portable tools. Technical preservation proofs belong to the separate independent QA.
