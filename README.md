# 海边巨塔城堡 · 持续精修

最新检查点：**[v024 背面阶梯构件重复表面清理](checkpoints/v024/README.md)**。

清理六个实际倒角实体之间的重复共面表面，消除背面一组墨黑阶梯色块。既有体积、轮廓、倒角、材质和照明保持；不是补建后墙、新增支撑或修改路线。其他四组、20 个构件仍明确留待后续判断。

- **[同机位原光照前后图](checkpoints/v024/previews/rear_pair_bilingual.png)** · [当前正面全景](checkpoints/v024/previews/hero_after.png)
- [恢复与可逆对照](checkpoints/v024/README.md) · [程序复现](checkpoints/v024/REPRODUCE.md)
- [恢复清单](checkpoints/v024/MANIFEST.json) · [持续计划](CONTINUATION.md)

完整克隆仓库（含 model_chunks），运行 `python checkpoints/v024/restore_checkpoint.py`，逐块及整文件 SHA-256 验证后用兼容 Blender 5.2.3 LTS 打开。先新版远端独立恢复/重验，再撤旧当前载荷；Git 历史保留，不强推。

## 可选：当前模型检查副本

[检查工具与 Windows / Linux 说明](scripts/current_inspection/README.md)：明确审核当前模型哈希与 12 个已有视角，另存手动书签副本；不改原工程、不自动执行或渲染，不自动降低质量。原生 Windows 未实测。未知未来版本拒绝运行，须先审核目录。旧 v023 工具可从固定提交 `4a7cd90ceb9d545de67951cae536e2c4604a547a` 恢复，不把旧验证改称新版结果。

## 历史呈现与工具（不是v024影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
