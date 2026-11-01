# Independent completed V2 audit

Prepared while the sole render owner renders. Do not run until all 336 frames are complete. No Blender or encoding in these tools. No approval writes. Pinned accepted source and V2 plan; old V1 frames may not be substituted.

1. `python check_frames.py --archive <frozen V2 archive> --output <final_v2> --source <canonical v018 blend> --report <frames.json>`
2. After owner completes encoding and releases heavy work: `python check_video.py --output <final_v2> --video <existing mp4> --frames-report <frames.json> --report <video.json>`

Frame audit validates all 336 indices/receipts/decoded PNG hashes/settings/camera poses, source/code identity and completion receipt. Sequence metrics are descriptive, not a flicker acceptance rule. Video audit performs ffprobe and full decode, checks 336 decoded frames, 12fps timestamps, 28s/960×694/H264/yuv420p/no audio, and compares every decoded frame to the same-index verified PNG. Conservative per-frame encoding MAE<5/255 and channel bias<3/255 are screening bounds, not quality proof; failures require investigation rather than loosening silently. No real-time playback capability is claimed.

Remaining final review: inspect actual entrance/bend/stair-ascent/arrival/end and temporal clips at actual cadence where supported. Preserve the C1 translational lateral-acceleration caveat and camera-only 0.12m sphere scope; not articulated gait/accessibility. Existing VIDEO_QA_PLAN.md provides the broader review checklist.

Lossy decoded duplicates are reported with exact indices, distinct original PNG provenance and same-index compression errors. They are not automatically called fabrication: eased subpixel motion can quantize identically. A triangle-inequality consistency check compares each source pair against its two measured encoding errors; violations fail. Exact frame count/timestamps/order and source PNG identity remain mandatory. Nine pure-function tests cover indices, timing, compression boundaries and legitimate/inconsistent duplicate handling.
