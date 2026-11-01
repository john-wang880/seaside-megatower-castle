# 海边巨塔城堡 · 持续精修

最新检查点：**[v023 既有路径局部贴地修正](checkpoints/v023/README.md)**。

修正一小段粗路面三角形穿入地形造成的草色碎片，使原路径在阴影中连续可读。保留原线路、铺面/苔边材质、树木和照明；没有新建入口、延长路线或替换整条路，不宣称全路线可达。

- **[实际原光照前后图](checkpoints/v023/previews/practical_pair_bilingual.png)** · [当前全景](checkpoints/v023/previews/hero_after.png)
- [恢复与可逆对照](checkpoints/v023/README.md) · [程序复现](checkpoints/v023/REPRODUCE.md)
- [恢复清单](checkpoints/v023/MANIFEST.json) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v023/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块及整文件SHA-256验证。先新版远端独立恢复/重验，再撤旧当前载荷；Git历史保留，不强推。

原120个三角形局部细分成800个贴地面，原始网格保留，其他1392个路面和全场景状态不改。完整表面检查而非只查顶点；浮点边界残余明确记录。工程净增17,146字节不等于Git历史增长量，本轮新压缩块仍约13.27MB。所有尺度以作者场景坐标为准，不是现实工程计量。

## 可选：当前模型检查副本

[检查工具与 Windows / Linux 操作说明](scripts/current_inspection/README.md)：验证当前恢复模型后，另存带 12 个手动相机书签的检查副本，方便查看入口、内廊、塔冠、桥墩、石肋及路径。原工程不改，不自动执行脚本、渲染或降低质量。原生 Windows 尚未实测；未知后续版本拒绝运行，须先审核相机目录。

## 历史呈现与工具（不是v023影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理、石肋分段和路径修正，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩、石肋和路径修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。

已从远端`389770297a21ef2401917e83807e0122711b8df9`独立恢复c4验收模型，1168项根校验、13核心/8预检/3计划测试及公开QA的4次Blender+3次Python调用（含九类负例和五数学测试）通过。见[远端验证收据](checkpoints/v023/reports/remote/VERIFIED.json)。
