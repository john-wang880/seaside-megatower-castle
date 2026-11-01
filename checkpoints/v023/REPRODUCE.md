# v023复现与来源

精确恢复优先使用`restore_checkpoint.py`；程序重建是配方核查，不替代验收归档。

## 唯一历史输入
```sh
git worktree add --detach ../castle-v022-history a80fdd6bc589f03159c23cc3cfaea1cfbdb2adc3
python ../castle-v022-history/checkpoints/v022/restore_checkpoint.py
```
使用新工作树路径，必须得到99156d…a9dfd2来源。来源已从固定Git对象独立恢复，未借用私有历史候选。

## 自包含构建和检查

`reproduce/README.md`提供已有Blender5.2.3的独立构建配方。代码/计划冻结；输入SHA、输出不存在、路径别名和优化Python模式在模型修改前拒绝。只需要精确来源及本包，没有外部纹理/私有资产、安装或自动发布。

`qa/README.md`规定完整源状态、1392面补集属性、真实地形叠分、边界/材质、回退及负例。重建保存若SHA不同，必须先与固定c4b验收模型逐项比较完整持久化/求值语义，不得仅提供任意候选SHA就视为通过。检查退出码及JSON门限。

Blender每次在`--python`前使用`--python-expr "import sys; sys.dont_write_bytecode=True"`，以免在冻结配方旁创建缓存。仅设置宿主PYTHONDONTWRITEBYTECODE在本机Blender不足。实际测试限云端Linux/Blender5.2.3，不冒充原生Windows运行。

几何数值以场景坐标单位记录，保留float32残余量化误差，非现实工程计量或严格有理数计算。已有路径是开放表现面；不得把局部地表关系检查转述成整座城堡可达/安全认证。

## 已执行独立复现
固定Git来源在独立中文/空格目录重建为c177f5…9472fb；保存元数据不同，但与c4验收模型完整持久化/求值语义一致。冻结公开QA在新隔离目录完成5次Blender及3次Python调用，2个模型状态负例、7个导出实际几何负例及5个数学测试通过；模型与全部代码/目录清单不变、无缓存。见`reports/rebuild/`和`reports/repeat/`。精确归档保留c4原验收字节，不用重建文件覆盖。13核心、8预检、3计划算术测试另行通过。
