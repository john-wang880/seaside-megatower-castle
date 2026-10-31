# 海边巨塔城堡 · 持续精修

最新检查点：[v014 上段阶梯导向灯](checkpoints/v014/README.md)。

克隆完整仓库（含model_chunks），运行 `python checkpoints/v014/restore_checkpoint.py`，用Blender5.2.3LTS打开恢复文件。逐块/整文件SHA-256验证，精确恢复原字节。

在保留原4灯的基础上新增1具低功率上阶导向灯，复用已有网格；没有移动旧灯，也没有改建筑、世界、太阳或曝光。改善上阶辨识，附近终点地面仅小幅改善，**不宣称整个露台或前方房间已经照亮**。

- [上阶实际照明](checkpoints/v014/previews/v014_terrace_final.png)
- [整体全景](checkpoints/v014/previews/v014_hero_final.png)
- [下段阶梯回归图](checkpoints/v014/previews/v014_bend_review.png)
- [恢复清单](checkpoints/v014/MANIFEST.json)
- [验证证据与适用边界](checkpoints/v014/README.md)
- [持续计划](CONTINUATION.md)

v013远端备份已验证；v014本地新鲜恢复、60处灯具连接、建筑碰撞、通路/来源保留/重复构建和10项存储测试通过。发布后独立远端恢复通过才撤旧当前载荷；历史永久保留，不强推或清除历史。
