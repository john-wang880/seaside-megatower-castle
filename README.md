# 海边巨塔城堡 · 持续精修

最新检查点：**[v025 背面回折框架重复表面清理](checkpoints/v025/README.md)**。

完成剩余四组、20个已确认构件的重复共面表面清理，保留之前v024成果。背面阶梯及回折体面恢复连贯灰石，真实凹部、外轮廓、倒角、原有体积、材质与照明保持；不是填墙、新支撑或通路修改。

- **[累计 v023→v025 原光照前后图](checkpoints/v025/previews/rear_cumulative_v023_v025.png)** · [本轮对照](checkpoints/v025/previews/rear_pair_v024_v025.png) · [当前全景](checkpoints/v025/previews/hero_after.png)
- [恢复与可逆对照](checkpoints/v025/README.md) · [程序复现](checkpoints/v025/REPRODUCE.md)
- [恢复清单](checkpoints/v025/MANIFEST.json) · [持续计划](CONTINUATION.md)

完整克隆仓库（含model_chunks），运行 `python checkpoints/v025/restore_checkpoint.py`，逐块及整文件SHA-256验证后用兼容Blender5.2.3 LTS打开。先新版远端独立恢复/重验，再撤旧当前载荷；Git历史保留，不强推。

## 可选：当前模型检查副本

[检查工具与 Windows / Linux 说明](scripts/current_inspection/README.md)：审核当前模型哈希与13个视角，新增本次实际背面机位，另存手动书签副本；不改原工程、不自动执行/渲染，不自动降低质量。原生Windows未实测，未知未来版本拒绝。旧v024工具可从固定提交 `0d332990a252bbb2d51f73e69bdefd34e2931c19` 恢复，不把旧验证改称新版结果。

## 历史呈现与工具（不是v025影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
