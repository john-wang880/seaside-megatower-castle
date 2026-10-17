# v004：双塔层级窗群

这是持续精修项目的阶段检查点，非最终成品。先前版本和历史提交均保留。

## 恢复工程

1. 下载本目录 3 个 `seaside-castle-v004.zip.part00*` 分片和 `restore_checkpoint.py`。
2. 运行 `python3 restore_checkpoint.py`，核验分片、完整ZIP和内部载荷，解压到 `restored/`。
3. 用Blender 5.2.2 LTS打开 `restored/海边巨塔城堡_v004_双塔层级窗群.blend`。

ZIP保留28项成果和原MANIFEST.json/SHA256SUMS.txt，共30文件。模型字节原样保存；分片没有降低精度。其他脚本、预览和报告在目录中展开以便浏览。

`PAYLOAD_SHA256SUMS.txt`用于解包后的原始载荷；本目录`SHA256SUMS.txt`用于仓库展示和分片文件。

## 实际范围与验证

新增14扇真实凹深窗，总数22；主塔正面4/4/2、副塔2/4/2，东侧各仅中段2窗。保持主次层级和大片实墙。

v003原66网格、58材质、对象变换、相机、灯光、世界与曝光不变；7个新/替代网格闭合，14窗真实凹深射线通过；工程重开和可重跑验证通过。

阶段说明与重建方法见`reports/`；受控同机位前后预览见`previews/`。最终渲染记录的模型输入SHA与本检查点一致。PNG路径元数据已净化，像素内容未修改。

下一步：v005开始主体石砌尺寸、低对比块色、接缝和粗糙度校准；不改变已锁定窗群和照明。

14天项目自北京时间2026-10-18 00:14起，至少推进至2026-11-01 00:14，仍在进行中。

模型SHA-256：`e23172759e1742f2de0f2d9244629b7e1c0491fd1a6d2b39e1d977f01c15fa58`

完整ZIP SHA-256：`f2fb3dc2c7a7b5f4e4c67a11600bcf8f9a1ce6196384d0913c144c57bb2c941d`

## 远端恢复验收

固定提交：https://github.com/john-wang880/seaside-megatower-castle/commit/f1d4612999fa590e4d47ab04452fa7ae7492af86

38件新增/更新仓库文件逐字节读回一致，三片ZIP恢复及解包载荷校验通过。远端恢复模型重新通过Blender基线保留核验，7个新/替代网格闭合，14个新增窗口实际凹深射线复核通过。详细证据见 reports/github_restore_validation.json。
