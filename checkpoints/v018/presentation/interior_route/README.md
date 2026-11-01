# V018 bounded interior route — prepared, NOT a completed video

Approved target: **28 seconds,12fps,336 genuine Blender frames,960×694**, original
80-sample quality. Camera begins just inside the entrance, rounds the L-turn,
ascends the north stair, ends at the tested terrace and looks through its real
lateral opening toward woodland/west tower/sea. No source geometry, lamps,
world, exposure, saved defaults or source file changes. No audio, fabricated
intermediate frames, diagnostic fill, cloud hiding or fake teleport.

Source: `castle_v018.blend`, SHA256
`c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`.
Exact Blender runtime: **5.2.3 LTS**. Rendering uses8 cloud threads; source saves3.
Original maxbounces8/adaptive.035/min12/denoise/cache-off retained. Source scene
stays at frame1; separate per-frame temporary cameras provide actual motion.

## Evidence and movement limits

`final_motion.py` is portable pure analytic geometry/time/gaze. `final_plan.json`
bakes all336 exact recipes and expected rendering settings. First-to-last pose
is27.9166667seconds (timestamps0…335/12), then the final image lasts1/12second,
so video duration is exactly28seconds. No hidden timing compression.

Nominal human-eye height1.65m; exact floor-relative bounds1.559375…1.740625m.
The stabilized ascent smoothly approaches/leaves a constant stair slope.
Continuous head/camera proxy radius.12m and actual near-plane corners are tested;
this is **not an articulated human gait, full-body or accessibility certificate**.
The accepted route ends inside the bounded terrace, not throughout the castle.

Maximum sampled3Dspeed1.4772m/s, horizontal1.4141m/s; tightturn speed.35m/s.
Time-based quintic gaze peaks44.95°/s,36.86°/s²; start/end angular velocity and
acceleration are continuous. The retained XYstraight–circle joins are C1,
not globallyC2: lateral acceleration changes by.27223m/s² at those two joins.
This bounded residual is disclosed; no zero-jerk motion claim.

Original five plus corrected two feasibility stills are under `feasibility/`:
**640×462,16samples**, not final quality. Entrance/stairs are readable in actual
light; the old terminal wall-view is dark. Corrected gaze reveals an actual
opening without changing camera position or scene lighting. The old failed
turn/wall views remain as honest evidence, not recommended final poses.

## Required staged run

Keep these portable scripts and plan together. First wait for owner's verified
Git checkpoint and explicit launch signal. Example from repository root:

```bash
python checkpoints/v018/presentation/interior_route/run_final_orbit.py \
  --stage pilot \
  --source work/v018/castle_v018.blend \
  --blender /workspace/scratch/8bdb2666bb6b/tools/blender-5.2.3-linux-x64/blender \
  --output-dir work/interior_preview_v018/final
```

`--dry-run` reads/validates only, never starts Blender or creates outputs.
The pilot renders three contiguous8-frame windows: **1–8,76–83,303–310**, plus exactfinalpose**336**.
They sample entrance, peak turn-gaze/tight corner entry, and the real daylight
opening reveal—not merely the first2seconds or an already settled finish.
**The runner then stops** after writing `pilot_complete.json`. Review movement,
close-wall framing, actual shadows, noise/flicker and the finite-acceleration
turn before accepting the remaining311frames. No final video is claimed yet.

After an explicit owner pilot acceptance, save a JSON approval receipt containing
`approved:true`, the full exact `identity` from `run_identity.json`,
`approved_indices` equal to the25indices in theplan, and
`pilot_complete_sha256` matching the actual pilot completion receipt, plus decisionnotes. It is not generated automatically. Resume using `--stage full` and
`--approval-file /path/pilot_approval.json`. The runner checks that all25pilot
frames still validate, then reuses them rather than rerendering them. A changed
plan/source/code requires a new run directory and review, not silent migration.

## Reproducibility, lock, recovery and encoding

Single runner uses an exclusive flock and refuses any other active Blender.
Each actual frame starts a fresh sequential Blender process with autoexec off.
Source/plan/code hashes identify the run. Unique attempts are validated then
atomically promoted; valid frames are never overwritten. Invalid/incomplete
finalfolders are quarantined; abandoned attempts remain for diagnosis. Source,
recipe, camera pose, sensor/gate/clip, quality, PNG bytes/dimensions and decoded
pixels are checked before a frame is skipped on resume. `journal.jsonl` is
append-only with durable flush; authoritative per-frame receipts support recovery
even if a final journal line was interrupted.

Completedframe PNG+JSON must themselves be backed up to survive machine loss.
Scripts alone do not preserve computation: missing frames will be rerendered.
No other Blender or heavy rendering runs alongside this job. Python/Pillow,
ffmpeg/ffprobe and Linux flock are required; no new software installation.

Only after336verifiedframes does ffmpeg create H.264/yuv420p12fps/CRF18 MP4,
no audio and no interpolation. ffprobe checks336frames,28seconds,960×694 and
12fps. `video.json` records output/frame-set hashes; full decode/visual QA still
follows before delivery. Pilot images are not a completed route movie.

Estimated final rendering6–10hours, scene-dependent; actual pilot timings should
update that estimate. Initial640×462/16sample frames averaged58seconds with
synchronization dominating. No guarantee of zero denoising shimmer; pilot/full
sequence review is required. This package adds no model version.

## Independent audit reproduction (no Blender)

From repository root, substituting the packagepath if working locally:
```
python checkpoints/v018/presentation/interior_route/independent_audit/validate_final_motion.py \
  --plan checkpoints/v018/presentation/interior_route/final_motion_plan.json \
  --motion-code checkpoints/v018/presentation/interior_route/final_motion.py \
  --route-report checkpoints/v018/reports/route_envelope.json \
  --report /new/path/final_motion_audit.json
```
The source-matched route report is an existing separately validated artifact;
continuous camera proofs reuse its collision-free prism union and are bounded
by that geometry evidence, not a fresh claim about every castle surface.
Seven pure motion tests and ten synthetic resume-validation checks run without
Blender. The full stage also rejects missing explicit pilot approval.
