# V018 interior route · gaze revision V2 — pilot pending

**No completed route video.** V1's25-frame pilot was technically valid but rejected
for close-wall/lantern-dominated turn framing. Its immutable code, frames and
receipts remain separate; no generic approval or frame migration carries over.

V2 retains the same accepted v018 model, all336 camera positions/timestamps,
human-eye heights, speed profile, original80sample quality and actual lighting.
Only approach/turn gaze changes: it tracks the real near-corridor opening at
(4.45,39.5), then settles north. Arrival gaze remains exactly unchanged.
The source is never saved. No architectural opening is invented or enlarged.

## Evidence

- Source SHA256: `c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`.
- Original framing failure is not excused by collision-free camera geometry.
- Four actual V2 previews under`feasibility/` are **640×462,16samples**, not final
  pilot quality. Frame76 now reveals corridor/stairs; frame83 centers the route.
  Earlier frame58 naturally includes the near doorway edge while approaching.
- Evaluated-scene sightlines to the actual opening passed at every affected
  rendered pose and1001dense0–10s samples. These are center-ray checks, not
  mathematical all-pixel/continuous visibility proof.
- Independent exact quintic extrema: maxyawrate26.45413°/s,
  maxyawacceleration26.71523°/s²; polynomialjoins areC2. A tiny0.000483°
  angular overshoot past90° is measured and disclosed, not clamped silently.
- Spatial/time functions are unchanged, rebinding the independent continuous
  .12m camera/head proxy proof. Eyeheight remains1.559375…1.740625m.
  Max3Dspeed1.4772m/s; unchanged XYcircle joins areC1, with bounded
  .27223m/s² lateral acceleration jumps—not globallyzero-jerk movement.
- `historical_v1_arrival/` contains original V1 frames303–310 and336 with
  original receipts. Their recipes match V2 exactly, but they remain **V1
  comparative evidence**, NOT V2 renders. No cross-identity frame reuse.

## Immutable staged run, only after verified Git checkpoint and owner GO

Target28seconds/12fps/336 actual frames,960×694, original80samples. Exact scene
frame stays1; only temporary camera changes. Original world/light/exposure/cache
and saved3-thread defaults stay untouched; cloud renderer uses8threads.
First-to-last pose timestamps0…335/12=27.9167s; lastframehold makes28s.

Keep`final_plan.json`, `final_motion.py`, `render_final_frame.py`,
`orbit_common.py`, and`run_final_orbit.py` together. Use a **fresh outputdirectory**:

```bash
python /path/to/this/package/run_final_orbit.py --stage pilot \
  --source /path/to/castle_v018.blend \
  --blender /path/to/blender-5.2.3-linux-x64/blender \
  --output-dir /path/to/work/interior_preview_v018/final_v2
```

`--dry-run` does not render or create outputs. The pilot consists of exactly
**1–8,54–61,76–83,336**: entrance, earlier anticipation/peak, former failure turn,
and final pose. It automatically stops after25 validatedframes and writes
`pilot_complete.json`. No remaining311 frames or video are generated then.

Full continuation requires a **new explicit owner decision** after actual pilot
sequence review. The separate approvalJSON must contain`approved:true`, exact
`identity` from this run's`run_identity.json`, `approved_indices` equal to its
25planindices, and`pilot_complete_sha256` matching its actual completion receipt.
Then invoke`--stage full --approval-file /path/approved.json`. The runner verifies
all25 same-identity pilotframes and skips them; it never silently adopts V1 PNGs.

Exclusive flock and active-Blender preflight prevent duplicate heavy workers.
Fresh Blender processes render sequentially with autoexec off. Unique attempts
are validated before atomicpromotion; existing valid frames are never overwritten.
Invalid/incomplete outputs are quarantined, not trusted. Durable journal entries,
source/plan/worker/runner/motion/validator hashes and per-frame PNG/metadata hashes
support resume. Source, actual camera matrix/gate/clip/nearplane, frame1, quality,
PNGdimensions/bytes and decodedpixels are checked before any skip.

After336verifiedframes only, installedffmpeg producesH.264/yuv420p12fps/CRF18,
noaudio and no synthetic frame interpolation. ffprobe verifies336frames,28s,
960×694 and12fps. Actual fullvideo review remainsrequired before delivery.
Blender5.2.3LTS, Python/Pillow/NumPy andffmpeg/ffprobe already available; noinstallation.

A25-frame pilot is expected~30–50minutes based on V1 actual timings. Fullbatch
estimated6–10hours, notguaranteed. Back up actual completed PNG+JSON files to
preserve computation across machine loss; scripts alone only enable rerender.

## Independent reproducibility

`check_gaze_v2.py` uses explicit CLI paths (see`--help`) for new/old plan+motion,
oldcontinuousproof andoutputreport; historical inputs are included. It derives
exact polynomial extrema and checks continuous spatial functions byAST identity,
not merely point comparisons. Actual sightline probes accept`--report` and do
not save models. `test_motion_plan.py` has9 puretests; `test_resume_validation.py`
has10 syntheticchecks. Approval-gate rejection is also tested without Blender.
No final animation or successful pilot is claimed by this package.
