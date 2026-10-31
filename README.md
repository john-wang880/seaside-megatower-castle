# 海边巨塔城堡 · 持续精修

当前最新已验证检查点：[v010 入口前室实体验证与局部修复](checkpoints/v010/README.md)。

恢复：下载/克隆整个仓库（包含 model_chunks），运行 python checkpoints/v010/restore_checkpoint.py，使用 Blender 5.2.3 LTS 打开 restored/castle_v010.blend。所有内容块及完整模型都有 SHA-256 校验，恢复保持原始压缩模型的精确字节。

本轮修复东侧末端平台与实体基座重叠，新增真正清空的前室和有意关闭的拱门；修复局部地形穿出及西门树枝。新增实体占用测试，旧上向射线不足以证明通行。内院路线仍未贯通。它是阶段成果，不是全场景完成版。

- [恢复清单](checkpoints/v010/MANIFEST.json)
- [中性诊断照明·优化前](checkpoints/v010/previews/v009_east_neutral.png) / [同机位·优化后](checkpoints/v010/previews/v010_east_neutral.png)
- [后续路线与恢复约定](CONTINUATION.md)
- [阶段历史](TASK_LOG.md)

旧版本从当前文件列表撤下后仍保存在 Git 历史中。不会重写历史或永久清除旧提交。
