# 海边巨塔城堡 · 持续精修

最新检查点：**[v022 西塔一根完整层间石肋](checkpoints/v022/README.md)**。

西塔最低高身层的一根外侧石肋，补上13段克制的石作接缝和细倒角。原有竖向轮廓、窗洞、材质色域和照明保留；实际同机位能读出石块尺度，不把局部近景工艺夸大为整塔改造。

- **[实际原光照前后图](checkpoints/v022/previews/practical_pair_bilingual.png)** · [当前全景](checkpoints/v022/previews/hero_after.png)
- [恢复与可逆对照](checkpoints/v022/README.md) · [程序复现](checkpoints/v022/REPRODUCE.md)
- [恢复清单](checkpoints/v022/MANIFEST.json) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v022/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块及整文件SHA-256验证。先追加新版，远端独立恢复/重验后再撤旧当前载荷；Git历史保留，不强推。

v019精细树冠、v020西侧入口、v021桥墩重叠表面清理均保留；本版只增加11,032工程字节，不宣称性能提速、结构工程安全或全城可达。压缩分块的Git历史新增量仍约13.3MB，不与工程净增字节混淆。

## 历史呈现与工具（不是v022影片）
- [v020方形2400像素展陈图及相机配方](https://github.com/john-wang880/seaside-megatower-castle/tree/23fd4aaaceb64996913bfa3ff4109fc149737b9d/checkpoints/v020/presentation/exhibition)：原照明，未包含后续桥墩表面清理和石肋分段，原版本如实保留。
- [v018内廊至露台28秒影片与来源](https://github.com/john-wang880/seaside-megatower-castle/blob/89cce41edf648eef6487d54ee1ce2a46bbb0ae17/checkpoints/v018/presentation/interior_route/STATUS.md)，336真实帧；不含后续树冠、入口、桥墩和石肋修改。
- [v018独立便携重渲染工具](checkpoints/v018/presentation/portable_interior/README.md)：仍绑定历史v018；原生Windows未实测，不会自动重渲染或降低质量。
- [历史v016八秒局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)，不含后续屋面和树冠。

已从远端提交`5571b5fe5c7501b801a9455662e6d7aad18fd51f`独立恢复991验收模型，1021项根校验、13核心/8预检/1计划测试及七步公开Blender检查（含五类负例）通过。见[远端验证收据](checkpoints/v022/reports/remote/VERIFIED.json)。
