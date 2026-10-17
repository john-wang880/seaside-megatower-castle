# 海边巨塔城堡 / Seaside Megatower Castle

A highly detailed, beautiful, and monumental seaside castle project.

## Latest checkpoint: v004

新增14扇真实凹深窗，总数22；主塔正面4/4/2、副塔2/4/2，东侧各仅中段2窗。保持主次层级和大片实墙。 v003原66网格、58材质、对象变换、相机、灯光、世界与曝光不变；7个新/替代网格闭合，14窗真实凹深射线通过；工程重开和可重跑验证通过。

See [checkpoints/v004](checkpoints/v004/README.md) for full restoration, controlled previews, scripts and technical records. This checkpoint is part of ongoing refinement; earlier versions remain intact.

Verified v004 fixed-commit readback, complete restoration and Blender reopening passed. All seven new/replacement meshes are closed, and fourteen new windows passed actual recess-depth ray checks.

https://github.com/john-wang880/seaside-megatower-castle/commit/f1d4612999fa590e4d47ab04452fa7ae7492af86

## Previous checkpoint: v003

The dual-tower sample adds eight genuinely recessed pointed-arch windows with secondary divisions and recessed tracery, while preserving the v002 base geometry, materials and lighting. This is a local sample, not a completed tower-wide refinement. See [checkpoints/v003](checkpoints/v003/README.md) for source restoration, six controlled before/after previews, rerunnable scripts and review reports. Selective v004 expansion remains future work.

Verified v003 fixed-commit readback, full restoration, Blender reopening, seven closed-mesh checks, eight recess-depth ray tests and four rib-contact checks passed.

https://github.com/john-wang880/seaside-megatower-castle/commit/235cf9e35ae7bfd3611062cc8197823d02cb4fab

## Previous checkpoint: v002

The first structural art pass adds differentiated tower crowns and a closed, reshaped western shore. The baseline remains preserved. Full fixed-commit readback, ZIP restoration, Blender reopening, baseline-preservation checks, and closed-shore topology checks passed.

Verified v002 source: https://github.com/john-wang880/seaside-megatower-castle/commit/2e2bed12271a634ad1e6dcd199fce7db20f9f053

Open [checkpoints/v002](checkpoints/v002/README.md) for restoration instructions, reviewed previews, rerunnable scripts, and the stage review. v003 is a proposal, not yet implemented.

## Restore the editable baseline

The verified Blender baseline is preserved inside a ZIP archive. Repository copies of the ZIP are split into two parts to stay within the upload interface's request-size limit. No project detail is removed by splitting.

1. Download or clone this entire repository, including both `.zip.part001` and `.zip.part002` files.
2. Run `python3 restore_backup.py` from the repository directory. Python 3 is sufficient; no extra packages are required.
3. The script validates each archive part, reconstructs the original ZIP, safely extracts it into `restored/`, and verifies the internal SHA-256 manifest.
4. Open `restored/海边巨塔城堡_Dots轻量版.blend` with Blender 5.2.2 LTS or a compatible newer release.

Materials are procedural. The inspected scene contains no external images or linked libraries. Render output uses the relative `renders/` directory.

## Baseline and privacy checks

This baseline preserves the supplied lightweight scene before artistic changes. A new Blender copy replaces personal file-browser and render-output paths with relative paths. The preview pixels are unchanged; personal source-path metadata was removed. The original unsanitized delivery archive is not published.

The cleaned project was saved and reopened successfully in Blender 5.2.2 LTS. It contains 60 objects, 53 meshes, and 54 materials. Mesh vertex coordinates and topology, object identities, camera identities, and material identities matched the source.

## Project duration and progress

The project begins at 2026-10-18 00:14 Beijing time and must continue for at least 14 days, through 2026-11-01 00:14. The goal is an extremely detailed, beautiful, monumental 3D scene. Composition, buildings, terrain, materials, and lighting may all be revised.

`TASK_LOG.md` in the repository root is the current project log. Documents inside the ZIP reflect the archive's packaging checkpoint. Record actual edits, render checks, problems, and backup commits daily; a failed operation or a waiting period is not a completed milestone.

## Rebuild the environment

Blender 5.2.2 LTS for Linux x64 was installed from the official source. The installer is excluded from this repository.

- Archive: https://download.blender.org/release/Blender5.2/blender-5.2.2-linux-x64.tar.xz
- Checksums: https://download.blender.org/release/Blender5.2/blender-5.2.2.sha256
- Verified installer SHA-256: `84098912789dc450e95697c4184fb8a90acbe5111c2ba4aede3fecb57806a168`

## Versioning

Keep scripts and documentation in Git. Save significant scene checkpoints and representative previews with clear dates. Update the task log and checksums for every substantive revision. Binary history can grow quickly; reassess Git LFS or suitable checkpoint storage as the project grows.

## Publication verification

The complete baseline backup was committed and independently downloaded again from its fixed commit. All nine repository files matched the staged files byte for byte. Both archive parts, the reconstructed ZIP, and every extracted payload file passed SHA-256 verification. The restored Blender project reopened successfully in Blender 5.2.2 LTS with 60 objects, 53 meshes, and 54 materials.

Verified source checkpoint: https://github.com/john-wang880/seaside-megatower-castle/commit/c934a844fe8599bbee859f3588da7481be932d6f

Archive SHA-256: `64a394e5fd9e610002602be56f867acf872a8bb23ad590c1fa87496b6d71ca91`

The current root task log and checksums include this verification record. The archive itself retains its original packaging-time documents. No artistic edits are included in this baseline.
