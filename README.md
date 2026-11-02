# 海边巨塔城堡 · 持续精修

最新检查点：**[v029 接待室 → 连通储藏空间（空壳阶段）](checkpoints/v029/README.md)**。本地源工程重建、完整独立几何／语义QA、实际图像验收及20书签检查工具原生验证通过；**远端精确恢复、源工程重建与完整QA／工具重放已通过**，见[远端核验记录](checkpoints/v029/reports/remote/VERIFIED.json)。

在原接待室东侧接入一间7×4.5的狭长服务空间，新增两盏错位暖灯，保留原路线和外观。**这是连通空壳，不是已经布置完成的仓库**；下一步才是有用途的货架／储物。没有新增外门、全城堡环路或结构安全认证。

- [进入新空间](checkpoints/v029/previews/stores_entry.png) · [回望原接待室](checkpoints/v029/previews/stores_return.png) · [新旧房间关系](checkpoints/v029/previews/doorway.png) · [当前全景](checkpoints/v029/previews/hero.png)
- [恢复说明](checkpoints/v029/README.md) · [源工程复现](checkpoints/v029/REPRODUCE.md) · [独立QA](checkpoints/v029/qa/README.md)

完整克隆含model_chunks，运行`python -B checkpoints/v029/restore_checkpoint.py`，逐块及整文件SHA验证后用已有Blender5.2.3打开，保持自动脚本执行关闭。验收SHA：`4f838529d32cbf6a0314cc0a23b3dd1703b73d80c5db146fb4d323697b882df5`。旧v028从固定历史提交`f3f56c21c97c9a76c79050c709790611681ae2b8`可恢复；旧v028当前载荷在新版本远端恢复通过后撤下，固定历史仍可恢复；Git历史不清除、不强推。

## 可选：当前模型检查／编辑选择副本

[手动检查工具](scripts/current_inspection/README.md)绑定当前哈希及**20个已审查书签**，含新空间入口和回望机位。另存副本，不改原模型，不自动执行或渲染。未知未来版本、错源、覆盖与路径别名拒绝运行。

`--tree-mode HIGH/LOW`仅手动切换入口旁单棵树；LOW仍保留高细节网格，不承诺缩小文件或特定速度。`--editing-index`默认关闭，启用后提供五组可见目标：两个连通房间局部壳体、原接待室20灯具网格、入口顶棚、HIGH树、新储藏空间20灯具网格；两组灯具均不包含实际LIGHT对象。共享材质、合并宿主及隐藏回滚都有明确限制，选择不是独立搬移／删除许可。

本地四份副本、13类源保护、27质量负控、37选择负控、6面板案例、64次LOW拒绝及77纯测试通过；原生Windows和真实桌面点击未实测。全新远端工具重放也已通过；最终当前树撤旧仍单独核对。

## 已选择的后续两条方向

- **丰富内部探索**：新房间先形成连通目的地，再加入有用途的储物设施，保留工作通道和灯位；不靠随意新增房间或道具堆砌。
- **整体升级海岛景观**：[构图／依赖计划](checkpoints/v029/planning/README.md)结合迎风松林、开阔进路与连续岩岸。本版只完成源几何调查和规划，尚未实施树林／海岸重做。

[v024/v025旧邻接保证更正](checkpoints/v026/audits/coplanar_method/README.md)继续保留：旧BVH零结果不是无共面接触保证。当前范围以各版有限证明为准，不声称全球无重叠或全城堡可通行。

## 历史呈现与工具（不是v029影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v026八秒外景局部环绕](checkpoints/v026/presentation/orbit/README.md)：96帧真实Blender渲染，960×694、12fps、原40°镜头路径与照明不变；不是360°或内廊漫游。完整解码与来源逐帧检查通过。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
