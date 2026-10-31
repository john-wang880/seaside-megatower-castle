# 海边巨塔城堡 · 持续精修

当前最新已验证检查点：[v009 西侧林地台阶与桥头连接](checkpoints/v009/README.md)。

恢复：下载/克隆整个仓库（包含 model_chunks），运行 python checkpoints/v009/restore_checkpoint.py，使用 Blender 5.2.3 LTS 打开 restored/castle_v009.blend。所有内容块及完整模型都有 SHA-256 校验，恢复保持原始压缩模型的精确字节。

本轮完成西侧林地贴地入口、9级宽台阶、入岩承托与桥头门槛连接；东入口之后的内院路线与局部植被清理仍待优化。它是阶段成果，不是全场景完成版。

- [恢复清单](checkpoints/v009/MANIFEST.json)
- [中性诊断照明·优化前](checkpoints/v009/previews/v008_neutral.png) / [同机位·优化后](checkpoints/v009/previews/v009_neutral.png)
- [后续路线与恢复约定](CONTINUATION.md)
- [阶段历史](TASK_LOG.md)

旧版本从当前文件列表撤下后仍保存在 Git 历史中。不会重写历史或永久清除旧提交。
