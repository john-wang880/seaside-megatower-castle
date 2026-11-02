# 海边巨塔城堡 · 持续精修

最新检查点：**[v027 首段内廊浅尖拱石肋](checkpoints/v027/README.md)**。

三道浅尖拱及高墙头石带，形成可抬头检查的连贯石构顶棚。原墙、地面、灯、转角、路线和外部建筑不变；不是加房间或改历史漫游镜头。外部hero重渲染与v026像素完全一致，此结论仅限该机位。

- **[同机位原照明对照](checkpoints/v027/previews/inspection_pair.png)** · [室内检查图](checkpoints/v027/previews/inspection_after.png) · [当前全景](checkpoints/v027/previews/hero_after.png)
- [恢复说明](checkpoints/v027/README.md) · [程序复现](checkpoints/v027/REPRODUCE.md) · [恢复清单](checkpoints/v027/MANIFEST.json)
- [v024/v025旧邻接保证更正](checkpoints/v026/audits/coplanar_method/README.md)继续保留：旧BVH零结果不是无共面接触保证，真实既有接触如实记录。

完整克隆含model_chunks，运行 `python checkpoints/v027/restore_checkpoint.py`，逐块及整文件SHA256验证后用Blender5.2.3 LTS打开，保持自动脚本执行关闭。先新版远端精确恢复/重验，再撤旧当前载荷；Git历史保留，不强推。

## 可选：当前模型检查副本

[手动书签工具](scripts/current_inspection/README.md)明确绑定当前哈希及16个已审查机位，新增自然站立抬头内廊检查角度；另存副本，不改原模型、不自动执行/渲染。原生Windows未实测，未知未来版本拒绝运行。旧v026的15书签工具及源模型可从固定提交 `054bc322fed3ad54080471901566c3b1c96d8e8e` 恢复。

当前工具另支持明确选择 `--tree-mode HIGH` 或 `LOW`，在副本里手动切换入口旁单棵树；不传参数时不启用该功能。LOW保留高细节网格，不缩小文件、不承诺速度；原工程v027不变。原始16书签工具在固定提交 `030ecda3f64a161c181a307f2639251eab34f556` 保留。

## 历史呈现与工具（不是v027影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v026八秒外景局部环绕](checkpoints/v026/presentation/orbit/README.md)：96帧真实Blender渲染，960×694、12fps、原40°镜头路径与照明不变；不是360°或内廊漫游。完整解码与来源逐帧检查通过。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
