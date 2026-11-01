# V026 actual exterior orbit — complete and independently checked

All96 actual Blender frames completed at2026-11-01 22:13:59UTC. The8-second12fps960×694 H264 video is included in `final/`; source/lighting/camera/quality are unchanged. Owner and independent art director accept the four storyboards covering all96frames, with expected end-arc bridge partial occlusion retained. This is not playback/flicker certification or full-resolution inspection of every frame. Final independent encoded-video QA passed; remote backup verified from fresh commit `efffa7188bd423e6cd1534b9b36f4d7b444cf52e` (see `evidence/remote/VERIFIED.json`). The mean same-index compression error is1.71/255 (maximum frame mean1.77/255). Frame2 raw RGB error slightly favored neighboring frame1; multiscale luminance comparisons support intended frame2. This caveat is preserved rather than overstated as a mathematical universal frame-order or temporal-flicker certificate.

## Included and omitted recovery data

- `final/castle_v026_partial_orbit.mp4`: complete lossy video, SHA3dddfc0904deb3472c79a4ef4a7e02b315527efde00640482c702c4cdf4b0b74.
- All96 original metadata receipts in deterministic `frame_metadata.zip`, with member hashes; frames_complete and journal retained.
- Five exact raw landmark PNGs1/25/49/72/96. Frame49 is reused from `pilot/frame_0049/image.png`, not duplicated; `final/landmarks.json` maps every image/receipt.
- `final_review/`: actual cost report and four storyboards. These are visual review aids, not an exact raw-frame backup.
- Runtime/evidence/pilot package remains byte-exact; below is the prior approval-stage documentation, preserved as chronology.

**Not all raw images are archived here.** All96 raw PNGs (~72MB) remain in the local workspace, but this Git package includes only the five landmarks, video and receipts. If a reset removes an unbacked PNG, metadata cannot reconstruct it: it must rerender under a valid identity. H264 decoding is lossy and must not be relabeled as exact original PNG recovery. Remote backup is only confirmed after owner fresh-fetch checks.

---

## Earlier pilot-stage documentation (historical)

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

## Independent final QA and replay limits

`evidence/final_qa/check_final.py` is the exact clean executed script (SHA99ff4e148ed2e4447f3a8045ce13231c47be253c022186e9b170f4931eab4571); the complete chain reran under `python -B -W error` and passed. `final_report.json` SHA3a6354b63626f0a4b03a34899c63b286d518e5701a818aabe16a47edb6e13336 records96frames/12fps/8s/960×694, no audio, strictdecode, no identical decoded duplicates, actual-source comparison and central-shift/duplicate negative controls. Initial raw-RGB ambiguity/failure and earlier escape-warning script/log remain separately preserved as superseded evidence, not acceptance.

Full raw-source frame comparison requires all96originalPNG+metadata in the local run layout, source model and matching cache identity; this limited Git package cannot replay that entire test without restoring/rerendering omitted rawPNG. InstalledNumPy/Pillow/ffmpeg/ffprobe are additional QA dependencies, not auto-installed. Archived video bytes/PTS/codec/strictdecode and included landmarkPNG hashes can be independently checked from the package. Never infer missing raw images from a passing historical report.
