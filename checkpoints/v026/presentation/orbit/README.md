# V026 actual exterior orbit — pilot backed-up package

**Full96frames authorized, not started in this package.** Parent and independent art director accepted the actual frame49 at2026-11-01 20:20UTC. The exact current-source pilot PNG and receipt are included; the other95frames and final video do not yet exist here. Single-frame measurement75.34seconds suggests roughly2hours for remaining rendering, plus encode/QA, not a guarantee.

This is the unchanged40°partial orbit,960×694,12fps/8seconds, original80samples and lighting, now on acceptedV026. It is not a360tour, interior walkthrough, new model version or claim that oldV016film represents current geometry. Historical46files are unchanged; camera/source/runtime proofs and independent CPU tests are in `evidence/`. Exact production runtime and bindings are in `recipe/`.

## Restore and run

Restore model bytes from fixed Git history rather than a possibly removed latest manifest:

```sh
git -C /path/to/repository worktree add --detach /path/to/new-v026-history b9015e58605c5a6d211bd7a977ad5fed542f8769
python /path/to/new-v026-history/checkpoints/v026/restore_checkpoint.py --repository-root /path/to/new-v026-history --output /path/to/new-input/castle_v026.blend
PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME=/path/to/existing-writable-cache python -B /path/to/package/recipe/run_final_orbit.py --source /path/to/new-input/castle_v026.blend --blender /path/to/existing/blender --output-dir /path/to/new-output --pilot-frame 49
```

Use Linux/existingBlender5.2.3 and installedPillow; no auto-install. Full encoding additionally needs existingffmpeg/ffprobe. The recipe is explicitly cloud8threads/9CPUaffinity. Output parent/cache must exist; output must be new or exact matching identity. The above fresh-output command rerenders pilot49 honestly. To resume the existing cloud run after remote backup GO, the owner uses the same approved cache/output identity and `--full`; its already verified frame49 is reused. The archived cloud receipt's cache path is provenance, not an instruction to write into unavailable private paths on another machine. Never relabel identity to force reuse.

For a public independent CPU replay:

```sh
python -B /path/to/package/evidence/independent/test_independent.py --recipe /path/to/package/recipe --historical-plan /path/to/package/evidence/compatibility/historical_final_plan.json --report /path/to/new-independent-report.json
```

`recipe/README.md` and its recovery supplement preserve earlier preparation-stage text as chronology; this top-levelSTATUS is the latest staged state. No runtime bytes changed after pilot.

## Recovery and backup limits

Only frame49 rawPNG is included. Missing future PNGs must rerender unless explicitly backed up; metadata/journals do not reconstruct pixels. An encodedH264video is lossy, not a substitute for exact original frames. Remote backup is not claimed complete until owner fresh-fetch verification. Full film rendering starts only after that backup gate. Same-identity resume, per-user execution lease, outputlock, strict source/runtime/PNG checks and no-autoexec rules are documented in `recipe/PROVENANCE_AND_RECOVERY.md`.

## Finite visual review and environment changes

Acceptance covers one actual representative still, not temporal continuity or every unrendered view. Full sequence still requires all96frame validation and motion/video review. The configured cache lease path is identity-bound: a new environment that cannot preserve that exact path must create a new output identity and rerender, never rewrite old receipts or silently adopt cached frames. Metadata alone cannot recover missing PNGs.

The independent `actual_pilot.json` is preserved byte-exact. Any earlier “full unapproved” wording there records its review time; top-levelSTATUS and parent approval at20:20UTC supersede that historical authority state. The audit source `evidence/compatibility/compatibility.py` is exact executed provenance with local workspace paths, not a portable CLI; its mapping is documented next to it. Production `recipe/` is the portable self-contained execution payload.
