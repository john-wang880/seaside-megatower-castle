# Optional HIGH/LOW one-tree viewer — actual visual and resource check

Prepared only. Await validated separate viewer files, their explicit hashes, and owner's exclusive Blender slot. Canonical accepted model remains untouched; this is not a new model version.

- Reuse `render_one.py`, `views.json`, `preservation_support.py` byte-for-byte from reviewed V019 actual comparison.
- Two fresh sequential Blender processes: HIGH then LOW, actual west approach(-99,38,32)→(-79,38,26.5),38mm,1200×866,original80samples/adaptive.035/min12/maxbounces8/denoise,8threads,original world/lights/exposure/sourceframe1. No scene save or lighting adjustment.
- HIGH decoded pixels compared against published V019 candidate approach; LOW against original V018 baseline approach. PNG metadata differences irrelevant; image mode/dimensions, decodedpixelhash, max and mean channel differences recorded. Any mismatch is evidence to diagnose, not silently called equivalent or rerendered away.
- Inspect both images for ghost old foliage/trunk, visible quality-mode consistency and preserved route clearance. Technical object/mask/source tests remain separate validator responsibility.
- Record per-process scene-load and render wall/CPU time, after-load and final peak RSS plus outer process time. One ordered pair, not randomized/repeated speed benchmark.
- HIGH meshes remain stored in both viewer files; do not claim file-size savings or guaranteed scene-load memory reduction. Only observed evaluated/render costs may differ.
- No Windows runtime/UI claim and no new UI screenshot. No long film or additional angles.

`run_modes.py --help` documents explicit paths and hashes. `--dry-run` verifies inputs without starting Blender; output directory must be new. No auto-retry/overwrite. Wait for owner GO before running.
