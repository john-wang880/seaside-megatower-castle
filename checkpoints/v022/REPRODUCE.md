> **历史v022文档。** 当前最新模型见[仓库首页](../../README.md)。本版模型清单/载荷在新版远端验证后从当前树撤下，固定历史提交`a80fdd6bc589f03159c23cc3cfaea1cfbdb2adc3`保留原始完整恢复资料。如需下面v022命令，先运行`git worktree add --detach ../castle-v022-history a80fdd6bc589f03159c23cc3cfaea1cfbdb2adc3`并进入该新历史工作树，不把当前新模型交给旧SHA绑定工具。

# v022复现与来源

精确恢复优先使用`restore_checkpoint.py`。程序重建是独立配方核查，不替代验收归档。

## 历史来源
```sh
git worktree add --detach ../castle-v021-history 743e140423c3838d0288109df64d40d258f6877b
python ../castle-v021-history/checkpoints/v021/restore_checkpoint.py
```
工作树目录必须不存在；源SHA必须为457348497…37ae9。固定历史来源已从Git对象独立恢复并校验。

## 构建和检查

`reproduce/README.md`提供自包含已有Blender5.2.3配方，仅需准确源文件与本包，不依赖私有工作目录。错误输入、已有输出、输入/输出别名及优化Python模式拒绝。执行配方与归档脚本一致，不重写历史版本。

`qa/README.md`说明逐步执行源状态、完整属性、几何、连续背衬、接触、回退及五类负例。不同保存字节的重建必须先以固定991验收模型进行完整持久化/求值语义比较，再运行其他检查；只传任意SHA不代表验收。检查进程退出码和每个JSON门限。

每个Blender调用在`--python`前使用`--python-expr "import sys; sys.dont_write_bytecode=True"`，避免解释器在冻结配方旁产生缓存。仅设置宿主PYTHONDONTWRITEBYTECODE在本机Blender中不足以阻止缓存。

实际运行限云端Linux/Blender5.2.3；中文/空格路径与重复构建另附报告，不冒充原生Windows测试。无安装、联网下载、自动渲染或发布动作。

## 已执行的独立核查
固定Git来源在独立中文/空格目录真实重建，得到2ea4b0…a67d（保存元数据不同）；与991验收模型的完整持久化/求值语义一致。冻结公开QA包在新隔离目录完成八次Blender调用、五类负例，模型及全部包文件/目录清单不变、无缓存。详见`reports/rebuild/`和`reports/repeat/`。精确归档仍是991，不用重建保存覆盖。13核心测试、8预检负例和1计划算术测试通过。
