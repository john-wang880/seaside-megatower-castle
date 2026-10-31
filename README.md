# 海边巨塔城堡 · 持续精修

最新检查点：[v013 真实内廊灯笼](checkpoints/v013/README.md)。

克隆完整仓库（含model_chunks），运行 `python checkpoints/v013/restore_checkpoint.py`，用Blender5.2.3LTS打开生成工程。每块及完整模型均校验SHA-256，恢复保持精确原字节。

沿入口—L形转角—20级台阶通往北侧有顶露台，新增4具真实壁灯笼和局部暖光，让原本近黑的内廊可读。原世界、太阳、曝光、灯光及全部来源几何保持不变；**新增局部照明是实际场景改动，不是诊断补光**。不是全城堡导航完成版。

- [入口实际照明](checkpoints/v013/previews/v013_east_portal.png)
- [内廊实际照明](checkpoints/v013/previews/v013_bend_highres.png)
- [整体全景](checkpoints/v013/previews/v013_hero_highres.png)
- [模型清单](checkpoints/v013/MANIFEST.json)
- [验证和适用边界](checkpoints/v013/README.md)
- [后续计划](CONTINUATION.md)

v013已从提交 `4ae18fdeb15b1d4ac950e21d7fbb99870e596ed1` 独立下载恢复验证，所有上述检查及10项存储测试通过，见[远端验证报告](checkpoints/v013/reports/remote_validation.json)。当前树只留最新检查点；旧v012及此前版本仍可从Git历史恢复，不强推、不清除历史。
