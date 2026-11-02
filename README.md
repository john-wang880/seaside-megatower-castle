# 海边巨塔城堡 · 持续精修

最新检查点：**[v030 有用途的储藏室](checkpoints/v030/README.md)**。两排三格木架和四只带盖储物箱，让v029连通空壳成为可辨认的储物目的地。本地源工程重建、完整独立几何／语义QA、实际图像验收与20书签检查工具验证通过；**远端精确恢复、源重建和完整模型／工具重放已通过**，见[核验记录](checkpoints/v030/reports/remote/VERIFIED.json)。

保留2.94宽中央工作通道、原门洞及回程视线；原灯光、世界、曝光和建筑不变。箱体在原照明下自然偏暗，不宣称每只箱子都清晰可见。没有新增房间、外门、完整环路或结构安全认证。

- [进入储藏室](checkpoints/v030/previews/stores_entry.png) · [回望原接待室](checkpoints/v030/previews/stores_return.png) · [房间关系](checkpoints/v030/previews/doorway.png) · [当前全景](checkpoints/v030/previews/hero.png)
- [恢复说明](checkpoints/v030/README.md) · [源工程复现](checkpoints/v030/REPRODUCE.md) · [独立QA](checkpoints/v030/qa/README.md)

完整克隆含model_chunks，运行`python -B checkpoints/v030/restore_checkpoint.py`，逐块及整文件SHA验证后用已有Blender5.2.3打开，保持自动脚本执行关闭。验收SHA：`9f020b7ec6eda309d674653598b169f65ba5dc1d1f194ffa31323f6393feda35`。源v029固定历史提交`d753ba032b1d3138a1d0c34e13b0caee40b3d92f`；旧v029当前载荷已在新版本远端验证通过后撤下，固定历史仍可恢复，Git历史不清除、不强推。

## 景观整体重做：继续设计，未替换当前模型

[第一轮整体构图 B0 研究归档](checkpoints/v030/studies/landscape_b0/README.md)已完成技术验证与实际双视图比较，但因树林过于稀疏、大树尺度失衡及海岸构图收益不足而未采纳。当前仍是v030；后续根据原树林分布和真正内凹的外围海湾另立整体方案，不把低多边形树冠代理当作最终树木。

## 可选：当前模型检查／编辑选择副本

[手动检查工具](scripts/current_inspection/README.md)绑定当前哈希与20个已审查书签，另存副本，不改原模型，不自动执行或渲染。未知未来版本、错源、覆盖和路径别名拒绝运行。

`--tree-mode HIGH/LOW`只手动切换入口旁单棵树；LOW仍保留高细节网格，不承诺缩小文件或特定速度。`--editing-index`默认关闭，启用后提供六组51个可见目标条目：局部连通壳体、接待室灯具、入口顶棚、HIGH树、储藏室灯具、新木架／箱体。灯具组不含LIGHT对象；六个储物对象是独立摆放设施，不是墙体。选择不是独立搬移／删除共享宿主的许可。

四份副本、13类源保护、27质量负控、37选择负控、6面板案例和64次LOW拒绝均通过；原生Windows和真实桌面点击未实测。不会借工具更新修改模型或自动渲染。

## 已选择的后续两条方向

- **丰富内部探索**：接待室与服务储物目的地已连接并布置，后续空间必须有实际用途与清晰连接，不靠随意复制房间／堆道具。
- **整体升级海岛景观**：[当前设计研究](checkpoints/v030/planning/README.md)结合迎风松林、开阔进路与连续岩岸。尚未实施树林／海岸重做；原V2提案的六处微小原体积外失已定位；局部保守浮点包络通过CPU包含／嵌入检查，映射保护空间也已核对，仍待林带支持／冠幅与实际场景验收，尚不是发布的景观模型。

[v024/v025旧邻接保证更正](checkpoints/v026/audits/coplanar_method/README.md)继续保留：旧BVH零结果不是无共面接触保证。当前范围以各版有限证明为准，不声称全球无重叠或全城堡可通行。

## 历史呈现与工具（不是v030影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v026八秒外景局部环绕](checkpoints/v026/presentation/orbit/README.md)：96帧真实Blender渲染，960×694、12fps、原40°镜头路径与照明不变；不是360°或内廊漫游。完整解码与来源逐帧检查通过。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
