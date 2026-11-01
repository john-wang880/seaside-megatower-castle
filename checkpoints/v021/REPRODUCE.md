> **历史v021文档。** 当前最新模型见[仓库首页](../../README.md)。本版模型清单/载荷在新版远端验证后从当前树撤下，保留于固定提交`743e140423c3838d0288109df64d40d258f6877b`。如需执行下面的v021恢复/工具命令，先在新目录运行`git worktree add --detach ../castle-v021-history 743e140423c3838d0288109df64d40d258f6877b`，并进入该历史工作树；不要在当前树把新模型传给旧SHA绑定工具。

# v021复现与来源

精确恢复优先使用`restore_checkpoint.py`。程序重建只是独立核查配方，不替代验收归档。

## 唯一历史模型输入

```sh
git worktree add --detach ../castle-v020-history 23fd4aaaceb64996913bfa3ff4109fc149737b9d
python ../castle-v020-history/checkpoints/v020/restore_checkpoint.py
```
工作树目录必须是新路径。来源SHA须为673dbbad…77614；本历史恢复命令已在云端实际验证。

## 自包含构建和检查

`reproduce/README.md`说明使用已有Blender5.2.3，从精确来源和本包计划创建新输出。没有私有候选或额外资产依赖，不联网、不安装、不渲染、不发布。输出必须不存在；错误输入/已有输出/源别名/优化Python模式在加载模型前拒绝。

候选最初用正常Python模式生成；原执行脚本保存在`reports/executed_build/`。发布配方将“禁止-O”的检查由会被-O移除的assert改为明确RuntimeError，不改几何算法。已用新历史恢复来源在独立中文/空格目录真实重建，并与457完成12类完整语义精确比较。清洁的九步公开验证链和五类负例均通过，见`reports/repeat/`；保留执行前冻结文档/报告中的当时状态，不将准备阶段写成已经通过。

`qa/README.md`列出完整来源、属性、并集、六平面、原生遮罩状态和五类负例检查。不同SHA的重建保存必须先与固定457验收模型进行完整语义比较，不能仅凭调用者提供SHA就视为接受。需要同时检查进程退出码和所有JSON门限。

实际运行与中文/空格路径验证限云端Linux/Blender5.2.3；不冒充原生Windows运行测试。旧版展陈渲染工具也仍有各自明确的平台边界。

为使验证目录也保持无编译缓存，可在每个Blender的`--python`参数前加入`--python-expr "import sys; sys.dont_write_bytecode=True"`。仅设置PYTHONDONTWRITEBYTECODE在本机Blender内不足以阻止导入缓存；模型和已列出的脚本载荷不受该缓存影响。
