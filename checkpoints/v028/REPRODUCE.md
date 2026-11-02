# v028 复现与独立验证

当前状态：固定 Git 历史源的完整三阶段重建及公共语义／模型 QA 已通过，本地分块恢复已通过。18书签工具三模式原生验证已通过；远端精确复取、完整原生QA与工具重放已通过，详见 [远端核验记录](reports/remote/VERIFIED.json)。

## 1. 从固定历史恢复准确源

需已有 Python、Git 和 Blender5.2.3；本配方不下载、安装、渲染或发布。请给所有新路径创建父目录，输出目录本身不得存在；含空格和中文的路径必须加引号。

```sh
git -C '/path/to/repository' worktree add --detach '/path/to/new-v027-history' 91b0082b4443aa9a3539e742813bb37ddcc099da
python -B '/path/to/new-v027-history/checkpoints/v027/restore_checkpoint.py' \
  --repository-root '/path/to/new-v027-history' \
  --output '/existing/input/castle_v027.blend'
```

完整历史仓库需同时包含检查点和共享 `model_chunks`。输入必须为47,773,404字节、SHA256 `37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255`，不能用最新版本、旧未加灯中间文件或近似替代。

## 2. 显式重建至新目录

配方目录为 `checkpoints/v028/reproduce/`。

```sh
PYTHONDONTWRITEBYTECODE=1 python -B '/path/to/reproduce/reproduce.py' \
  --source '/existing/input/castle_v027.blend' \
  --blender '/absolute/path/to/blender-5.2.3-linux-x64/blender' \
  --output-dir '/existing/parent/new rebuild 中文'
```

控制器校验源、Blender版本和完整配方清单，解压并验证公共源导出，执行冻结几何配方、集成脚本及已修正的灯具平移脚本。它保留中间状态、日志、返回码和哈希；失败不转为接受状态。输出主模型为 `castle_receiving_chamber.blend`，记录为 `REPRODUCTION.json`。不覆盖原源，不把旧模型自动升级。

几何生成必须匹配冻结有效载荷；输入／代码变化、错误版本、路径别名或符号链接、已有输出及进程失败均拒绝。子进程关闭自动脚本执行并禁用字节码。原配方的9项纯测试不等于全原生模型 QA。

## 3. 独立公共 QA 与重建语义比较

已有主机 Python 需能使用 NumPy，原生部分使用已有 Blender5.2.3；不自动安装。公共包位于 `qa/`。对不同保存字节的重建，必须提供准确接受候选作语义参考：

```sh
PYTHONDONTWRITEBYTECODE=1 python -B '/path/to/qa/run_qa.py' \
  --blender '/absolute/path/to/blender-5.2.3-linux-x64/blender' \
  --source '/existing/input/castle_v027.blend' \
  --candidate '/existing/parent/new rebuild 中文/castle_receiving_chamber.blend' \
  --candidate-sha '填写该新保存文件的完整SHA256' \
  --accepted '/restored/accepted/castle_v028.blend' \
  --reference-export '/path/to/reproduce/native.json.gz' \
  --output-dir '/existing/parent/new QA 中文'
```

接受候选必须准确匹配 `f0d135e0c6e554b5ae7c520ef9ccefc61e2a7c4abc3129eef1d3d4118bca8096`。不能为了新保存哈希不同而改弱内部源／身份约束；`--accepted` 先比较完整持久及求值语义，再执行全部后续检查。

正常候选检查包含2次原生调用、13次 Python调用；重建语义比较另加1次原生调用，均不渲染。检查覆盖独立单元边界、112张远面／8个受影响面域、各宿主体积、原生父面三角化、有限正接触、连续身体与近裁剪代理、显式共面扫描、灯具几何／接触和可回退性。另含6项实际几何负控、10项精确边界数学控、9项显式共面控及14项运行器纯控制。

模型坐标存为float32：1038个名义单元合并为948个保存坐标单元；3个严格共线派生三角形在正面积父面完全覆盖证明后记录，不是“近零删面”或容差放宽。只规范化3个历史 SUBSURF 旅人对象的已知派生边选择 UI 状态，不豁免原始数据。

原有各宿主之间的继承重叠保留；局部护域帽面是相反朝向的内部划分，不声称全局焊接或全场景无共面。身体、相机与接触证明不等于人类步态、全地板可达性、承载能力或法规认证。

Linux后台执行是测试环境；Windows原生执行及桌面点击未实测。静态文档和历史影片不能代替最终保存模型及独立验证；本地模型与工具原生检查已通过，远端精确复取及完整原生QA／工具重放也已单独通过，报告见 [核验记录](reports/remote/VERIFIED.json)。

## 本次已完成的隔离验证记录

固定提交 `91b0082b4443aa9a3539e742813bb37ddcc099da` → 精确v027源37c0 → 新保存 `6105bfa5f599f6fc04458c8e92bdd2a3f8c6f3762159a8cdbe50ca6b2b1d172c`。公共QA包c1f9a87b完整3次原生＋13次Python链通过；保存语义准确匹配接受候选f0d，且几何／路线／灯具／相机检查通过。本地150块引用（129唯一块）恢复通过；本次新增块15,507,901B，与模型文件增加32,887B分开记录。冻结配方与QA文档的早期状态作为执行时间线保留。18书签工具原生检查已通过，远端终验已通过；详见 [核验记录](reports/remote/VERIFIED.json)。

### 检查副本原生验证

三模式均通过：18个手动书签／17个新增检查相机，13类源状态、保存重开及手动操作验证，27项负控和8项QA控制通过。只作用于独立检查副本；源工程、不自动执行和原生Windows未实测边界不变。远端验证已通过；详见 [核验记录](reports/remote/VERIFIED.json)。
