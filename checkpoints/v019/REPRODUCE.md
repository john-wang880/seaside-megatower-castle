# 恢复、验收证据与程序复现的区别

## 字节精确恢复（发布封装后可独立执行）

本模型SHA为`e71778349c4c65eafbda3eb0a3d0753cd11e1b368a3456c4de1db2f4c0f8647a`。使用本目录`restore_checkpoint.py`和维护者提供的MANIFEST/内容块恢复；不需要独立树资产、失败候选或旧工作目录。模型内已经包含最终两个新网格，可从这个精确恢复的.blend中手动导出它们。这是恢复已验收网格，**不是重新运行程序生成的独立证明**。

## 历史原场景

在仓库历史提交`89cce41`中恢复v018，检查源SHA为`c46b581a759c1b6d494fb3b31e9a7c42f749b6dfbdde1c00befbfebd9ef44cfd`。不要因当前树仅保留最新检查点，就误称旧版丢失；Git历史保持不变。

## 执行过的生成器与验证器：精确保留，不冒充自包含工具

`scripts/executed/create_conifer.py`是最终执行过的生成器原文。它仍使用原工作路径，并读取历史失败树`work/conifer_specialist/pre_attachment_repair/isolated_conifer.blend`，仅用于位置偏移对照诊断。这个失败二进制不发布，因此此脚本**不是当前发布树内自包含的一键重建工具**。不为了消除该依赖而未经验证改写几何生成代码。后续如制作可移植生成器，必须独立验证产生网格与本检查点一致。

`scripts/executed/verify_attachments.py`、`validate_frame_repair.py`和`audit_tube_folds.py`也保留历史工作路径/对照输入；其中最后一个从工作目录载入`validate_new_geometry.py`代码前缀。原文用于审计执行方式，不能直接在任意目录运行。

`scripts/integrate_conifer.py`支持显式source/asset/output/report/snapshot-helper参数，输入独立资产最终SHA为`641651d02c994d2c65dc3b79dae2704ad9509af455b8a039aa46620f293faf88`。该资产未重复发布为第二份.blend；本地精确资产上的整合已执行通过，见`reports/integration.json`。从生产模型导出的新资产即使几何相同，也不能冒充这个原始资产SHA。

`scripts/executed/validate_preservation.py`及其负例测试仍固定这个独立资产SHA，用于当时验证新网格与独立输入一致。发布目录保留其真实报告，不声称缺少该输入时仍能直接端到端重跑。生产恢复验证应独立比较恢复模型SHA和源/新网格语义收据；维护者负责相应发布验收，不把旧资产依赖验证器悄悄改成放宽版本。

## 可直接复用的实际几何检查参数

`validate_new_geometry.py`接受`--candidate --mapping --route-report --report`；映射来自`reproduction/component_contact_mapping.json.gz`，用标准Python gzip解压到新临时文件后使用。`reproduction/v018_route_envelope.json`为固定源v018路线范围；检查只限该范围。具体完整参数接口见执行脚本的argparse部分。需要Blender提供的Python/NumPy/mathutils，不引入外部下载依赖。

`reproduction/source_components.json`是原25个叶簇的完整顶点/面映射。`attachment_mapping.json.gz`为生成器根部映射。压缩报告以gzip保存，解压内容保持原始JSON字节；`STAGING_FILES.json`记录发布前暂存内容哈希。

## 状态与历史限制

`reports/`保存当时实测报告，某些报告内绝对工作路径或“视觉尚待审”是执行时原始上下文，不应篡改成事后结果。技术通过与实际画面对比通过由最终验收收据汇总。开放背面针叶、原始开放端主干及已知路线范围限制均保留。无整体森林或结构安全认证。
