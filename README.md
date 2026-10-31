# 海边巨塔城堡 · 持续精修

最新检查点：**[v017 主冠屋面瓦片层次](checkpoints/v017/README.md)**。

四坡面补齐克制的错缝瓦片层次和收边，原屋体、铜脊、尖杆、角尖塔、材质与灯光完整保留。6,032块闭合瓦片，来源/实际交接/负控制/重复构建/路线回归及导航检查通过；不是防水或承载工程认证。

- [屋面修改前](checkpoints/v017/previews/crown_before_v016.png) · **[修改后实际近景](checkpoints/v017/previews/crown_after_v017.png)**
- [当前整体全景](checkpoints/v017/previews/hero_after_v017.png)
- [八视角导航与可选查看副本](checkpoints/v017/navigation/README.md)
- [恢复清单](checkpoints/v017/MANIFEST.json) · [验证范围](checkpoints/v017/README.md) · [持续计划](CONTINUATION.md)
- [上一版v016八秒真实局部环绕视频](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)（尚未包含v017屋面层次，保留于历史）

克隆完整仓库（含model_chunks），运行 `python checkpoints/v017/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块/整文件SHA-256验证，精确恢复原字节。

本版已从提交`6fd51224b13aca639e64b236fe8f1ae8da9068d4`独立远端恢复并通过检查，见[恢复验证](checkpoints/v017/reports/remote_validation.json)。当前只保留最新模型载荷；旧版Git历史保留，不强推、不永久删除历史。导航当前冠部/全景为v017，另外六张明确是v016原区域参考，不把旧图冒充新渲染。
