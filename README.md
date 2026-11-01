# 海边巨塔城堡 · 持续精修

最新检查点：**[v026 主塔侧面重复黑带清理](checkpoints/v026/README.md)**。

清理两个原构件的重复表面，消除横跨三层的假黑槽；保留主塔原有体积、深色石材、窗洞、檐带、轮廓及照明。隐藏共享来源保持，可精确恢复历史版本。

- **[同机位原光照对照](checkpoints/v026/previews/lateral_pair_bilingual.png)** · [当前正面](checkpoints/v026/previews/hero_after.png) · [当前背面](checkpoints/v026/previews/rear_after.png)
- [恢复说明](checkpoints/v026/README.md) · [固定来源与程序复现](checkpoints/v026/REPRODUCE.md) · [恢复清单](checkpoints/v026/MANIFEST.json)
- [v024/v025旧邻接保证更正与证据](checkpoints/v026/audits/coplanar_method/README.md)：旧BVH零结果不再作为无共面接触保证；真实既有接触如实记录，不自动清掉合理阴影。

完整克隆仓库（含model_chunks），运行 `python checkpoints/v026/restore_checkpoint.py`，逐块及整文件SHA-256验证后用兼容Blender5.2.3 LTS打开，保持自动脚本执行关闭。先新版远端精确恢复/重验，再撤旧当前载荷，Git历史保留、不强推。

## 可选：当前模型检查副本

[手动书签工具](scripts/current_inspection/README.md)审核当前哈希及14个机位，包括新侧面检查视角，另存副本；不改原模型，不自动执行/渲染/降低质量。原生Windows未实测，未知未来版本拒绝运行。旧v025工具可从固定提交 `06cf897ea73fa105ba27cb7dd79af6df18587c9a` 恢复。

## 历史呈现与工具（不是v026影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [当前v026外景环绕更新计划与真实试帧](checkpoints/v026/presentation/orbit/README.md)：原40°镜头路径不变，试帧已验收，完整96帧已批准、待远端备份后启动；目前不是已完成影片。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
