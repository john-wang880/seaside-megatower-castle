# v003：双塔样板窗洞

这是局部立面样板阶段，不是整塔扩展或最终成品。v001与v002保留在原目录和历史提交中。

## 恢复工程

1. 下载本目录三个 `seaside-castle-v003.zip.part00*` 分片和 `restore_checkpoint.py`。
2. 运行 `python3 restore_checkpoint.py`，核验分片和完整ZIP并解压到 `restored/`。
3. 用Blender 5.2.2 LTS打开 `restored/海边巨塔城堡_v003_双塔样板窗洞.blend`。

ZIP保存28项封存成果及原MANIFEST.json/SHA256SUMS.txt，共30文件。模型原字节保留；分片没有损失细节。其他脚本、预览和报告在目录中展开以便浏览。

`PAYLOAD_SHA256SUMS.txt`校验解包后的载荷；本目录`SHA256SUMS.txt`校验仓库可见文件。

## 本轮范围与证据

- 主副塔各一段共8个真凹深尖拱窗，主次分格与后退窗格；不是贴黑面。
- 保留v002的59份网格、58份材质、原对象变换、相机、灯光、世界与曝光；3个原墙体对象隐藏保留。
- 3替换网格及4新增网格闭合；8窗后壁射线、4处次肋承托接触、重开及66网格重跑一致性均已核验。
- 六张同机位前后PNG已净化元数据。最终三张渲染的输入SHA与封存模型一致。

详见 `reports/V003_SAMPLE_REVIEW.md` 和 `reports/REBUILD_V003.md`。v004择段扩展是后续工作，不在此检查点中。

14天项目从北京时间2026-10-18 00:14起，至少推进至2026-11-01 00:14，仍在进行中。

模型SHA-256：`37329013c72ba07e7434b67e6963dbab62eb61bb4b7ec97db0f20594ce488cf9`

完整ZIP SHA-256：`76696ef3d7e8042241b7806288d997ee8795ee533053ac29778f79c6f0e7bb9f`

## 远端恢复验收

固定提交：https://github.com/john-wang880/seaside-megatower-castle/commit/235cf9e35ae7bfd3611062cc8197823d02cb4fab

38件新增/更新仓库文件逐字节读回一致，三片ZIP恢复及解包载荷校验通过。远端恢复模型重新通过Blender基线保留核验，7网格闭合、8窗真实凹深射线、4处次肋承托接触复核通过。详细证据见 reports/github_restore_validation.json。
