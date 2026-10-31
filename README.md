# 海边巨塔城堡 · 持续精修

最新检查点：[v016 离岸小塔台阶承托](checkpoints/v016/README.md)。

补齐原8块悬空台阶的岩体承托与短平台，原塔身、原台阶、材质和灯光完整保留。4个新增实体、19处连接、6,027个独立贴岩内部采样及来源/通路回归通过；不是结构承载或全岛可通行认证。

- [当前整体全景](checkpoints/v016/previews/hero_final.png)
- [小塔修复后实际照明](checkpoints/v016/previews/marker_after_actual.png) · [修复前](checkpoints/v016/previews/marker_before_actual.png)
- **[七视角导航与可选查看副本](checkpoints/v016/navigation/README.md)**
- [恢复清单](checkpoints/v016/MANIFEST.json) · [验证范围](checkpoints/v016/README.md) · [持续计划](CONTINUATION.md)

克隆完整仓库（含model_chunks），运行 `python checkpoints/v016/restore_checkpoint.py`，用Blender5.2.3LTS打开。逐块/整文件SHA-256验证，精确恢复原字节。

v016本地验证完成；本次发布后独立远端恢复通过才撤旧当前载荷。来源v015已验证，Git历史保留；不强推、不永久删除历史。导航中的5张旧路线图明确保留v015出处，当前全景/小塔图为v016，不将旧图冒充新渲染。
