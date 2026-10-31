# v016 · 八秒实际外景局部环绕

**[下载 / 播放 MP4](final/castle_v016_partial_orbit.mp4)** · [首帧](final/preview_frames/frame_0001.png) · [中段](final/preview_frames/frame_0049.png) · [末帧](final/preview_frames/frame_0096.png)

96张真实Blender渲染帧，960×694、12fps、8秒；40度前侧局部环绕，不是360度或人物步行。原80采样、世界/灯光/曝光保留，仅临时相机移动，源模型未改。总运行107.5分钟，无音频、无AI补帧/插帧。

全96帧来源/配方/质量/PNG检查通过；H.264/yuv420p视频全帧解码并逐一对照原图，无缺帧、96原始帧各不相同。H.264为有损编码，不宣称与PNG逐像素相同。人工检查了若干静帧，未使用实时GUI播放；不能保证细微时域降噪闪烁不存在。

备份范围：成品MP4、96帧元数据原字节ZIP、全部帧哈希、5张最终样帧及完整恢复/渲染脚本。约72MB全套PNG中间帧仍在工作区，未存入仓库；若机器丢失需按配方重新渲染缺失帧，不能把只有哈希当作图像备份。模型本身保持原字节精确恢复。

Approved target: **8 seconds, 12 fps, 96 actual Blender frames, 960×694**.
A 40-degree frontal partial arc, not a 360-degree orbit or walking simulation.
The source scene remains at frame 1. Only the temporary camera moves. Original
80 samples, adaptive threshold .035, minimum 12 samples, max bounces 8,
denoising, world, lights, exposure and persistent-data setting are preserved.
Eight render threads are a cloud-only override; the source model is never saved.
No audio, generated/interpolated intermediate frames, diagnostic relighting,
cloud hiding or image repainting.

Source SHA256: `d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb`.
Requires matching official Blender **5.2.3 LTS**, Python with Pillow, Linux flock,
and installed ffmpeg/ffprobe for H.264 encoding. Tested host affinity:9 logical CPUs.

## Run / resume
From repository root, first restore canonical v016 per root README. Use an explicit new local output directory:

```bash
python checkpoints/v016/presentation/orbit/run_final_orbit.py \
  --source /path/to/castle_v016.blend \
  --blender /path/to/blender \
  --output-dir /path/to/orbit-output
```

Add `--dry-run` to inspect completed/pending counts without writes or Blender.
The same command resumes safely. Relocated scripts accept absolute source,
Blender and output paths. Keep `final_plan.json`, `orbit_common.py`,
`render_final_frame.py` and `run_final_orbit.py` together and unchanged.

The output lock rejects a competing runner. Existing unrelated Blender processes
also block launching each frame. Fresh Blender processes render sequentially.
Each frame is rendered into a unique attempt directory, verified, then atomically
promoted to `frames/frame_0001` through `frame_0096`. Verified frames are skipped,
never overwritten. Incomplete or invalid final folders are quarantined before a
fresh attempt. Failed attempts/logs remain inspectable; rerunning retries missing
frames. Source, plan, worker/validator/runner hashes identify the run. A changed
recipe or implementation requires a new output directory, not mixed provenance.

`journal.jsonl` records frame starts/completions/skips/failures with durable flush.
Validation checks source SHA, plan/worker hash, settings, frozen scene frame,
camera pose, PNG hash, decoded dimensions and pixels. `frames_complete.json`
collects all 96 receipts. **The scripts/manifests alone cannot restore rendered
PNG files after machine loss**: copy completed frames and metadata when backing
up; otherwise safely resume by re-rendering missing frames.

After all96 valid frames, ffmpeg encodes `castle_v016_partial_orbit.mp4` as
H.264/yuv420p,12fps,CRF18,no audio. ffprobe verifies96 decoded frames,8 seconds,
960×694,H.264 and12fps before publication. `video.json` records video/frame-manifest
hashes and probe results. `--skip-encode` stops after verified PNGs.

## Feasibility evidence and limits

The five keyframe_renders previews are historical low-resolution feasibility images, not the final80sample sequence. `path_plan.json` contains conservative geometry-bound projection tests at all96
positions. Five real previews passed visual review. This does not prove every
intermediate frame is free of occlusion or temporal denoising artifacts; review
the completed video. The offshore marker naturally emerges from behind the main
headland. The meadow extends beyond the image; this is not an entire-island survey.

Measured640×462/16sample previews averaged57.85s/frame, dominated by synchronization.
Final original-quality rendering is estimated110–150minutes, not guaranteed.
No long render was launched during preparation. `test_resume_validation.py`
uses temporary synthetic fixtures only; ten validation checks passed, including
wrong source/recipe/code/quality/pose, corrupted PNG and incomplete output.

## Full source-frame comparison
`qa_final_video.py` reproduces every-frame encoding/source comparison with Python NumPy/Pillow and ffmpeg, expecting a complete locally rendered `final/frames/` directory next to this script. The archive alone deliberately lacks those96PNG intermediates; first re-render/resume into that directory or use the original local outputs. `final/final_qa.json` records the performed comparison. Archive verification can independently decode the deliveredMP4 and check all metadata/hash receipts without rebuilding the model.
