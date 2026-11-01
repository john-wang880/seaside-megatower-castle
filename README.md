# 海边巨塔城堡 · 持续精修

最新检查点：**[v018 西塔低屋帽瓦片层次](checkpoints/v018/README.md)**。

西塔八角屋帽加入克制的错缝石板瓦层次，保留低矮简单轮廓、铜脊、尖杆、原材质与灯光。2,096块闭合瓦片；实际交接、来源保持、负控制、重复构建、旧路线回归和九视角导航检查通过。这是近景细节改进，不是全景大改或建筑工程认证。

- [修改前](checkpoints/v018/previews/west_cap_before_v017.png) · **[修改后实际近景](checkpoints/v018/previews/west_cap_after_v018.png)**
- [当前整体全景](checkpoints/v018/previews/hero_after_v018.png)
- [九视角导航与可选查看副本](checkpoints/v018/navigation/README.md)
- [恢复清单](checkpoints/v018/MANIFEST.json) · [验证范围](checkpoints/v018/README.md) · [持续计划](CONTINUATION.md)
- [历史v016八秒真实局部环绕](https://github.com/john-wang880/seaside-megatower-castle/blob/9d417969f97c309665fb37067a81785c0aa225a0/checkpoints/v016/presentation/orbit/README.md)（不含v017/v018屋面层次）

克隆完整仓库（含model_chunks），运行 `python checkpoints/v018/restore_checkpoint.py`，用兼容Blender5.2.3LTS打开。逐块/整文件SHA-256验证，精确恢复原字节。

已从提交`3322030e311e8857c4b9d444b4a122027f7643e1`独立恢复并复验，见[远端验证](checkpoints/v018/reports/remote_validation.json)。当前只保留最新模型载荷；旧版Git历史保留，不强推、不永久清除历史。前景针叶试验因损失树冠体量已拒绝，未改当前森林。图片来源明确区分：西塔屋帽/全景v018，主冠参考v017，六张路线/小塔参考v016。
