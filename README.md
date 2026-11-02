# 海边巨塔城堡 · 持续精修

最新检查点：**[v028 下层接待／守卫室](checkpoints/v028/README.md)**。完整复现、语义／几何QA、本地分块恢复及18书签工具原生验证已通过；**远端精确恢复及完整原生QA／工具重放已通过**（[远端核验记录](checkpoints/v028/reports/remote/VERIFIED.json)）。

从原通道侧面进入一间克制的8×8下层房间，保留两根实体方墩与一条顶带，新增两盏同风格暖灯。是明确授权的局部室内扩建，不是缺陷修复或全城堡室内完成；场景尺寸不作工程／无障碍认证。原外观、世界／曝光和既有灯具保持，全景无可见回归但并非像素完全相同。

- [房间入口](checkpoints/v028/previews/doorway.png) · [反向连接](checkpoints/v028/previews/reverse_connection.png) · **[同机位通道对照](checkpoints/v028/previews/connection_pair.png)** · [当前全景](checkpoints/v028/previews/hero.png)
- [恢复说明](checkpoints/v028/README.md) · [程序复现](checkpoints/v028/REPRODUCE.md) · [恢复清单](checkpoints/v028/MANIFEST.json)
- [v024/v025旧邻接保证更正](checkpoints/v026/audits/coplanar_method/README.md)继续保留：旧BVH零结果不是无共面接触保证，既有接触如实记录。

完整克隆含model_chunks，运行 `python -B checkpoints/v028/restore_checkpoint.py`，逐块及整文件SHA256验证后用已有Blender5.2.3 LTS打开，保持自动脚本执行关闭。验收SHA为 `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096`。新版远端精确恢复／完整原生QA及工具重放已通过，旧版固定历史91b0082继续可恢复；旧路径撤除须作为后续独立操作验证，不因本声明自动视为已撤除。Git历史保留，不强推。

## 可选：当前模型检查副本

[手动书签工具](scripts/current_inspection/README.md)明确绑定当前哈希和18个已审查机位，包含房间入口及修正站立反向角度；另存副本，不改原模型、不自动执行／渲染。三模式、13类源状态、保存重开及27项负控／8项QA控制通过。原生Windows未实测；未知未来版本拒绝运行。

工具保留可选 `--tree-mode HIGH` 或 `LOW`，只在副本中切换入口旁单棵树；默认不启用。LOW保留高细节网格，不缩小文件或承诺速度。此前v027源与工具从固定提交 `91b0082b4443aa9a3539e742813bb37ddcc099da` 恢复；v026旧工具历史 `054bc322fed3ad54080471901566c3b1c96d8e8e` 与原始v027十六书签历史 `030ecda3f64a161c181a307f2639251eab34f556` 继续保留。

## 可选：编辑选择索引（不新增模型版本）

[当前检查工具](scripts/current_inspection/README.md)新增显式 `--editing-index`，默认关闭，仅在另存的检查副本中手动运行面板。四个选择集为接待室局部壳体、20个房间灯具网格（不含2个实际灯光）、入口顶棚石肋及入口旁HIGH树；LOW或隐藏目标拒绝选择，不自动取消隐藏，不给原工程改名。详见[选择索引指南](scripts/current_inspection/EDIT_INDEX_GUIDE.md)。

选择不是独立搬移／删除许可：材质可能共享，房间集合中的大范围原建筑残部不属于局部壳体选择集，历史Mask宿主不可当作普通备份删除。原v028模型及其哈希不变。本地验证及严格增量提交 `8a88b1e5a37fb0989a01532029edc9dd6939db9a` 的全新远端复取／模型恢复、4次导出和3组原生QA重放已通过，见[远端核验记录](checkpoints/v028/audits/editability/REMOTE_VERIFIED.json)。最终守卫版通过73项纯测试，另有6个原生面板边界案例通过；这是有限测试范围，不是广泛无崩溃保证，原生Windows仍未实测。

## 历史呈现与工具（不是v028影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v026八秒外景局部环绕](checkpoints/v026/presentation/orbit/README.md)：96帧真实Blender渲染，960×694、12fps、原40°镜头路径与照明不变；不是360°或内廊漫游。完整解码与来源逐帧检查通过。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
