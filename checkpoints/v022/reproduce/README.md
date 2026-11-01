# 西塔最低高墙段单条外肋：固定配方重建

本包仅重建已审阅的完整最低墙段单条外肋方案，不扩展到整座塔，也不重新调整接缝。13石段、18mm浅缝、10mm倒角、28/35mm内缩连续背衬；原材质和原肋上下延续段、倾斜端面保持。原8顶点通过独立反向Mask保留，新增一个336顶点/356面网格。不是v021的等体积并集；倒角和浅缝有意减少少量表面体积。

## 唯一模型输入

原始已接受v021，SHA256：
`457348497ba7dade666a909c029f6641a0945012f264fe088b8f06513a937ae9`。
固定Git历史提交：`743e140423c3838d0288109df64d40d258f6877b`。使用该提交`checkpoints/v021`的检查点恢复说明取得原模型。无需任何私有候选、旧工作目录或外部资产；本构建器不联网、不安装软件。

## 显式执行

使用现有Blender **5.2.3 Linux**，保留`--disable-autoexec`和`--python-exit-code 1`。不宣称Windows或其他版本已经测试。所有三个输出文件必须不存在；路径可以包含空格/中文。

```sh
"/absolute/path/to/blender" --background --threads 8 --disable-autoexec --python-exit-code 1 \
 --python-expr "import sys; sys.dont_write_bytecode=True" \
 --python "/absolute/path/to/rebuild/scripts/build.py" -- \
 --source "/absolute/path/to/source v021.blend" \
 --plan "/absolute/path/to/rebuild/plan.json" \
 --output "/absolute/path/to/new result/rebuilt.blend" \
 --report "/absolute/path/to/new result/build.json" \
 --source-snapshot "/absolute/path/to/new result/source_snapshot.json"
```

这是一项主动选择的本地重建命令，不需要另行申请维护者许可。不会保存源文件、渲染、发布、修改Git、自动接受新版本。除Blender自带模块，仅依赖标准Python及同目录`deep_snapshot.py`和本包`plan.json`。

成功要求进程退出0，报告八项`checks`全true，`source_unchanged`true，输出SHA与实际文件相同。源、计划、脚本、助手SHA在开始/保存前后绑定。不可被Python`-O`删除的显式RuntimeError保护保持启用；拒绝已存在输出、路径别名和符号链接。模型通过临时文件和排他硬链接发布。

## 证据和状态

`python test_preflight.py`：8个纯Python失败控制，包括错误源、已存在模型/报告/快照、输入输出别名、输出报告别名、符号链接和优化模式；无需Blender。
`python test_plan.py`：固定目标8顶点、13段完整区间、12道18mm接缝等算术约束。

`scripts/build.py`和`deep_snapshot.py`是首次实际执行的精确文件，未改几何配方。`evidence/code_provenance.json`绑定原执行哈希。第一次99156d…候选通过关键独立技术验收和实际图像艺术审阅；**本包的新隔离重建尚待执行**，纯测试不等于重新生成模型。后续模型文件字节可能不同，需独立全持久/求值语义比较证明几何等价，不能仅比文件大小或旧报告。完整邻接/接触负例和实际图像验收由独立报告记录，不由本说明替代。

`source_snapshot.json`是原场景的深语义基线。生成器局部检查并非完整场景/求值属性认证；不得扩大已有极窄UI缓存例外。复制文件仅按`RECIPE_FILES.json`，排除日志、缓存、模型；完成后的运行收据可另行追加在证据目录之外，不改变已执行冻结配方。

## 可逆回退

同时关闭原对象上的`V022 candidate | original outer rib rollback mask`视图/渲染开关，并隐藏`V022 candidate | complete lower-tier west outer rib`对象的视图/渲染。原始8顶点/6面仍保留；不要只切换一半，也不要删除原始网格。此回退不撤销用户此后任意模型编辑。
