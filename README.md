# 海边巨塔城堡 · 持续精修

最新检查点：[v016 离岸小塔台阶承托](checkpoints/v016/README.md)。

补齐原8块悬空台阶的岩体承托与短平台，原塔身、原台阶、材质和灯光完整保留。4个新增实体、19处连接、6,027个独立贴岩内部采样及来源/通路回归通过；不是结构承载或全岛可通行认证。

- [当前整体全景](checkpoints/v016/previews/hero_final.png)
- [小塔修复后实际照明](checkpoints/v016/previews/marker_after_actual.png) · [修复前](checkpoints/v016/previews/marker_before_actual.png)
- **[八秒实际外景局部环绕视频](checkpoints/v016/presentation/orbit/README.md)**
- **[当前七视角实渲拼图](checkpoints/v016/navigation/gallery/README.md)**
- **[七视角导航与可选查看副本](checkpoints/v016/navigation/README.md)**
- [恢复清单](checkpoints/v016/MANIFEST.json) · [验证范围](checkpoints/v016/README.md) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v016/restore_checkpoint.py`，用Blender5.2.3LTS打开。逐块/整文件SHA-256验证，精确恢复原字节。

v016已从提交`a76a0b0677815964cd3534ad02853b452ef7fcb5`独立远端恢复并验证通过，见[恢复报告](checkpoints/v016/reports/remote_validation.json)。当前只留最新检查点，旧版Git历史保留；不强推、不永久删除历史。导航七张均已重新渲染自当前v016，旧图仍保留于Git历史。

- [不改画质的云端线程性能对照](checkpoints/v016/performance/thread_abba/README.md)：单机80采样全景8线程约快2.39倍，像素完全一致；默认不变，CPU总时间略增。
