# v027 检查副本：可选单棵树 HIGH / LOW

验收工程保持不变；这是独立、可选的浏览副本，不生成新模型版本。16个检查书签不变。**不传 `--tree-mode` 时为 OFF：不启用树切换按钮，保留原始场景状态。** OFF不是低质量。

## 导出新副本

先从当前仓库恢复已验收v027工程。使用已有Blender5.2.3和新的输出文件名：

```sh
"$blender" --background --factory-startup --disable-autoexec --python-exit-code 1 --python-expr 'import sys; sys.dont_write_bytecode=True' --python "$repo/scripts/current_inspection/export_inspection.py" -- --repository-root "$repo" --source "$restored_v027" --output "$new_viewer" --report "$new_report" --tree-mode HIGH
```

- `--tree-mode HIGH`：启用按钮，默认显示验收版精细树。
- `--tree-mode LOW`：启用按钮，明确选择默认显示原始低细节树。
- 删除整个 `--tree-mode HIGH` 参数对：普通检查副本，不启用切换。

输出`.blend`和`.json`报告必须不存在，父目录须存在；不会覆盖源文件。工具锁定真实最新v027清单与源SHA `37c0db0e67d0a0a57b7542c899f687d129a6b31208b43e03857a1f3d9e88a255`，拒绝旧源、未知未来版本、错误目录/别名/符号链接和已存在输出。不要伪造清单。普通Python运行，不使用`-O`。不下载或安装软件。

## 手动使用

打开派生副本，继续禁用自动执行。在Text Editor选择 `INSPECT27 | Run manually for bookmarks.py`，检查后手动运行。在3D视图N侧栏的 **Castle检查** 中选择HIGH或LOW。16书签可在两种模式下使用，不改变树模式。重开文件后仍需手动运行文本；不安装插件、不自动执行、不自动保存或渲染。

只切换西侧入口旁已在v019改进的**一棵树**：原叶簇Mask的视口/渲染开关，加两个新树对象的视口/渲染隐藏开关，共六个布尔状态。原树干、森林布局、其他对象、灯光和相机不变。

HIGH对应当前v027验收树；LOW对应历史v018原叶簇的目标树几何，不表示整个场景退回v018。历史c46只用于独立谱系验证，用户运行按钮无需旧模型。高细节网格在LOW文件中仍然保留，**不是缩小文件或删除网格的工具，也没有承诺加载内存、Windows速度或实测性能提升**。

混合开关、错误权重/Mask、隐藏祖先集合、局部眼睛隐藏、多集合路径或集合实例会拒绝操作，不会偷偷取消其他隐藏设置。侧栏“Paired flags”只是开关状态标签，不是几何认证；执行切换时仍进行完整检查。这也不是撤销后来编辑的按钮。若手动修改场景导致操作拒绝，可以卸载本工具自己注册的界面；不能接管其他脚本的注册类。重新导出精确源副本是可靠恢复方式。

## 验证范围与历史

本次独立验收已通过（见reports/SUMMARY.json和modes.json）：13类原始状态、27项原生拒绝控制、每种模式16书签、8项独立纯Python控制；还包含OFF/HIGH/LOW重新打开、原始数据与可见几何比较、16书签交错操作、重复切换/注册、失败回滚与拒绝控制。旧的检查副本验收不能代替本次树切换验收。原生Windows界面/文件系统和桌面点击未实测；Linux后台API测试不等于GUI自动化。

旧版当前工具保留在固定Git `030ecda`；历史 `checkpoints/v019/quality` 不改。普通OFF导出保持原始场景语义，不要求新旧派生文件字节哈希相同。源版本/相机配方的历史哈希仍保留原义，不改写为当前验收记录。

若同一Blender进程先打开OFF副本，再打开启用切换的副本，旧界面注册可能与新运行时不同，工具会拒绝接管。请先卸载原副本自己注册的界面，或重启Blender后打开目标副本；不要强行删除其他脚本类或开启全局自动执行。同一副本内HIGH↔LOW正常切换不需要重启。此版本没有性能基准测试或提速保证。

可重复运行的纯测试保留：`test_preflight.py`18项、`tests/test_preflight_independent.py`24项、`test_tree_pure.py`9项，以及独立QA的`qa/test_compare.py`8项。运行前设置`PYTHONDONTWRITEBYTECODE=1`。18项测试只把已退役检查QA的硬编码计数断言改为读取当前质量QA的16目录断言；原执行文件留存provenance。
