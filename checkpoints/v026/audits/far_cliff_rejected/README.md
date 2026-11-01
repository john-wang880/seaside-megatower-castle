# Rejected far-cliff buttress trial — accepted model remains V026

Parent, owner and independent art director rejected the single same-camera actual east comparison. The proposed added rock reads as a **pale triangular engineered fin**, not a coherent geological shoulder. Retain V026efcd. The working label “v027” identifies this rejected experiment only; it is not a released/current model version. No hero/rear render or color/shape/offset loop followed rejection.

Technical QA passed for the172triangle added closed asset and actual cliff/water attachment, but that does not establish artistic value. This was a deliberate macroform alternative, not a defect repair. Every original plateau/rim/lip/terrain/path/forest/material/world/light remained intact. Combined occupied volume was not falsely described as globally welded terrain.

## Archived evidence

- `builder/`: exact successful executed standalone builder, pinned plan/profiles/envelope/helper and receipt; candidate .blend intentionally omitted (~47MB).
- `diagnostics/`: exact pre-save self-crossing failure source/log/actual triangles. The correction adds32buried return points, retaining all56original vertices and exposed shape bit-exact; no tolerance or style amplification.
- `visual/before` and `visual/after`: full original1200×866 actual PNGs and receipts, unchanged lighting. Before is exact historical V026, after is the rejected d8candidate. `comparison.json` verifies effective settings equal except output path. No crop/retouch/AI edits.
- `visual/render_east.py` and manifest/helper: exact executed candidate renderer. Historical baseline renderer/manifest retained separately. Unexecuted hero/rear recipes deliberately excluded.
- `brief/`: original read-only feasibility and broader art direction; their earlier “not authorized” wording records chronology before parent’s one-trial authorization, not a new permission or current acceptance.
- `qa/`:31 compact independent QA payloads plus pinned manifest;10 exact executed scripts/helpers, source/solid/contact/water/touch/control reports and initial14-crossing proof. TechnicalPASS does not supersede visual rejection. Full15MB scene geometry exports are intentionally omitted with hashes recorded; explicit fresh-workspace regeneration/replay instructions are included.

## Reproduce only for evidence review

Restore exact accepted source from fixed history, not an assumed latest manifest:

```sh
git -C /path/to/repository worktree add --detach /path/to/new-v026-history b9015e58605c5a6d211bd7a977ad5fed542f8769
python /path/to/new-v026-history/checkpoints/v026/restore_checkpoint.py --repository-root /path/to/new-v026-history --output /path/to/new-input/castle_v026.blend
PYTHONDONTWRITEBYTECODE=1 /path/to/existing/blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys; sys.dont_write_bytecode=True' --python /path/to/package/builder/build.py -- --source /path/to/new-input/castle_v026.blend --output /path/to/new-output/rejected-candidate.blend --report /path/to/new-output/rejected-build.json
```

Use existingBlender5.2.3, non-optimized Python, new output/report in existing parents and ordinary quoted paths. Exact builder dependencies are adjacent and pinned; no private work imports are required. Builder raw-source restoration and positive occupied overlap are distinct claims. The exact executed renderer requires the original candidate fileSHA; separately saved rebuilds can differ in metadata bytes and must first pass semantic equivalence under an explicitly identified adapter rather than silently replacing its hash guard. No fresh rebuild, nativeWindows, remote publication or future acceptance is claimed here.

Paths inside original receipts remain honest executed provenance. The corresponding baseline image/receipt/manifest and candidate worker/helper are now included under `visual/`; no old working directory is required merely to inspect evidence. Candidate.blend is not included; reproducible code is not equivalent to having archived its exact binary. Do not promote this trial to current model or perform additional tuning without new direction.
