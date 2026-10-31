# 海边巨塔城堡 · 持续精修

最新检查点：[v012 入口至北侧有顶露台](checkpoints/v012/README.md)。

下载/克隆完整仓库（包含 model_chunks），运行 `python checkpoints/v012/restore_checkpoint.py`，用 Blender 5.2.3 LTS 打开生成的模型。标准 Python 恢复脚本逐块及整文件校验 SHA-256，保持模型字节精确一致。

入口新增 L 形走廊和20级台阶，到达现有北侧有顶露台；不是全城堡可导航完成版。原始网格、完整森林、材质和最终场景照明保留；塔楼上部几何没有改变。v011移除4份无依赖隐藏中间副本，v012在其上增加真实内部通路。

- [模型清单](checkpoints/v012/MANIFEST.json)
- [入口诊断图](checkpoints/v012/previews/v012_east.png)
- [转角诊断图](checkpoints/v012/previews/v012_bend.png)
- [露台诊断图](checkpoints/v012/previews/v012_terrace.png)
- [原照明全景](checkpoints/v012/previews/v012_hero.png)
- [验证证据及适用边界](checkpoints/v012/README.md)
- [后续计划](CONTINUATION.md)

v011已从远端提交8d10c409独立恢复验证。v012本地新鲜恢复及重开已通过；本次发布后还须独立远端恢复，结果另行记录。远端验证完成前保留旧检查点；完成后旧版仅从当前目录撤下，仍可从Git历史恢复，不清除历史。
