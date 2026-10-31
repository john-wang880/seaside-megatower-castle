# v009 — 西侧林地到桥头门槛

9 级宽台阶（每级升高0.2，踏面长2.0，净宽3.2）沿岩面承托到 z27.4 门槛。入口小平台贴合实际地形；两侧连续低护墙。清除与通路确实冲突的6棵完整树，原始林木对象隐藏保留，其他树不改。原87个网格、64个材质、灯光、相机及世界均保留。

## 恢复
克隆或下载整个仓库（包含 `model_chunks`），运行：

```
python checkpoints/v009/restore_checkpoint.py
```

得到 `checkpoints/v009/restored/castle_v009.blend`。标准Python逐块与整文件校验；Blender5.2.3LTS已验证重开。模型SHA256：`180f4abca9f39e5e66df48a61ac16be7f044ca99d840b9c840c79a8dbf4b1a95`。

## 证据
- `reports/geometry.json`：135处踏面、岩体嵌入及2.1净空采样；35处入口平台采样；新建筑网格闭合、正体积。
- `reports/landing.json`：门槛接缝高差小于0.002。
- `reports/preservation.json`、`repeat_preservation.json`：原件保留、重开、重复构建可见几何一致。
- `reports/west_gate_regression.json`、`east_approach_regression.json`：v007门洞及v008东侧台阶回归。
- `previews/v008_neutral.png` / `v009_neutral.png`：同机位、中性诊断照明的前后对照。实际模型和材质；临时换光检查，最终工程的原灯光未改。

重建：在v008恢复文件上运行 `scripts/refine_v009.py`，参数 `--output <新文件.blend> --report <报告.json> --trees checkpoints/v009/reports/tree_clearance_spec.json`。勿覆盖来源。

## 尚未完成
东侧平台之后的内院路线尚未贯通；远端可见局部植被碎片待下一版清理。检查是建模质量测试，不是建筑安全或施工认证。历史版本保留Git历史；每次远端恢复通过后才撤掉当前树旧快照。
