# 海边巨塔城堡 · 持续精修

当前最新已验证检查点：[v011 源数据保留的性能整理](checkpoints/v011/README.md)。

恢复：下载/克隆整个仓库（包含 model_chunks），运行 python checkpoints/v011/restore_checkpoint.py，使用 Blender 5.2.3 LTS 打开 restored/castle_v011.blend。所有内容块及完整模型都有 SHA-256 校验，恢复保持原始压缩模型的精确字节。

本轮只清理无依赖的隐藏中间林木副本，完整原始森林和最新可见几何保留。工程缩小39.80%，两张同机位实渲与v010逐像素相同。西侧台阶、东侧清空前室均保留；内院仍止于关闭的门，不是全场景完成版。

- [恢复清单](checkpoints/v011/MANIFEST.json)
- [东入口中性诊断图](checkpoints/v011/previews/v011_east_neutral.png) / [原照明全景](checkpoints/v011/previews/v011_hero_original_lighting.png)
- [后续路线与恢复约定](CONTINUATION.md)
- [阶段历史](TASK_LOG.md)

旧版本从当前文件列表撤下后仍保存在 Git 历史中。不会重写历史或永久清除旧提交。
