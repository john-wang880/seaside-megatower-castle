# 海边巨塔城堡 · 持续精修

最新检查点：[v015 门叶静态铰接支撑](checkpoints/v015/README.md)。

克隆完整仓库（含model_chunks），运行 `python checkpoints/v015/restore_checkpoint.py`，用Blender5.2.3LTS打开。逐块和整文件SHA-256验证，精确恢复原字节。

四组小型锻铁铰接构件补齐原开启门叶与石门框之间的悬空连接。原门叶、建筑、材质及全部灯光保留；28处连接、碰撞/通路/来源保留/重复构建检查通过。仅静态构造连接，不是运动机构或承载认证。

- [铰接近景（临时补光诊断，非工程实际灯光）](checkpoints/v015/previews/after_hinge_DIAGNOSTIC.png)
- [入口实际照明回归](checkpoints/v015/previews/after_door_actual.png)
- [来源v014整体全景参考](checkpoints/v015/previews/unchanged_source_v014_hero.png)
- [恢复清单](checkpoints/v015/MANIFEST.json)
- [证据及边界](checkpoints/v015/README.md)
- [持续计划](CONTINUATION.md)

旧版仅从当前目录撤下，Git历史保留。新版本独立远端恢复通过后才清理旧当前载荷；不强推、不清除历史。
