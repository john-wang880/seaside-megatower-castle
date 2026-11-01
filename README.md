# 海边巨塔城堡 · 持续精修

最新检查点：**[v020 西侧入口石作门槛](checkpoints/v020/README.md)**。

为入口增加克制的分块石拱和两段短侧墙压顶接缝；原开口、道路、森林、材质和照明不变。实际接近与斜侧视角可读，整体构图仍由城堡主塔主导。是局部工艺丰富，不是整座城堡重做或工程安全认证。

- [实际原光照前后图与说明](checkpoints/v020/README.md) · [复现步骤](checkpoints/v020/REPRODUCE.md)
- [恢复清单](checkpoints/v020/MANIFEST.json) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v020/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块和整文件SHA-256验证，精确恢复原字节。已从远端`61482c2`精确恢复并复验，[验证收据](checkpoints/v020/reports/remote/VERIFIED.json)记录完整提交。随后撤下旧版当前模型载荷，Git历史保留。

v019单株精细树冠保留，其原有资源代价不变；没有扩展全森林。v020仅增加6,078工程字节。原树仍可在自己的副本中手动切换；[旧v019 HIGH/LOW工具](checkpoints/v019/quality/README.md)严格绑定历史版本，请先按其中说明恢复固定历史工作树，不要输入v020。

## 历史呈现与工具（不是v020影片）
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含本次树冠修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
