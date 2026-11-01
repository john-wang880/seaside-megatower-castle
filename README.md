# 海边巨塔城堡 · 持续精修

最新检查点：**[v021 中央桥墩重叠表面清理](checkpoints/v021/README.md)**。

消除中央桥墩长黑缝与分叉状黑脚的渲染伪影。它们来自重复共面表面，不是缺少支撑：仅做精确并集表面替换，原体积、轮廓、拱洞、道路和光照不变，没有填洞或加柱。

- **[实际原光照前后图](checkpoints/v021/previews/bridge_pair_bilingual.png)** · [当前全景](checkpoints/v021/previews/hero_after.png)
- [恢复与可逆对照](checkpoints/v021/README.md) · [程序复现](checkpoints/v021/REPRODUCE.md)
- [恢复清单](checkpoints/v021/MANIFEST.json) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v021/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块及整文件SHA-256验证。先追加新版，远端独立恢复/重验后再撤旧当前载荷；Git历史保留，不强推。已从远端`7aef44a`精确恢复并复验，见[验证收据](checkpoints/v021/reports/remote/VERIFIED.json)。

v019精细树冠、v020西侧入口石作均保留；本版只增加2,891工程字节，不宣称性能提速、结构工程安全或全城可达。

## 历史呈现与工具（不是v021影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含本次桥墩表面清理，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含本次树冠修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。
